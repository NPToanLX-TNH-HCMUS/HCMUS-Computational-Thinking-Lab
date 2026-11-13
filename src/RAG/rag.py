import json
from pathlib import Path

import numpy as np
import streamlit as st

try:
    from utils.call_llm import call_llm
except ImportError:
    from ..utils.call_llm import call_llm

INPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base.json"
)
THRES_HOLD_SEARCH = 0.2


def __json_preprocessing(input_path: str) -> list[str]:
    """
    Kind of "chunking" from a big JSON file into list[str]
    """
    with open(input_path, "r", encoding="utf-8") as file:
        knowledge = json.load(file)

    text = [
        json.dumps(
            record,
            ensure_ascii=False,
            separators=(",", ": "),
        )
        for record in knowledge
    ]
    return knowledge, text


@st.cache_resource
def knowledge_embedding(
    api: str,
    provider: str,
    embedding_model: str,
    input_path: str,
):
    knowledge, text = __json_preprocessing(input_path)

    embeddings = call_llm(
        api,
        provider,
        embedding_model,
        text,
    )

    return knowledge, text, np.asarray(embeddings, dtype=np.float32)


class Retriever:
    PROMPT_TEMPLATE = """
    You are an exclusive, friendly, active travel assistant for Lumen Travel. Your task is to answer the user's travel questions based ONLY on the provided Context below.
    Strict Rules:
    1. NO HALLUCINATION: You must only use the information explicitly stated in the Context. Do not invent, guess, or assume any information, especially opening hours, prices, or external facts.
    2. CITATION REQUIRED: Every time you use information from a context entry, you must append its exact ID in brackets at the end of the sentence (e.g., [G01], [G05]).
    3. MISSING INFORMATION: If the provided Context does not contain the answer to the user's question, you must reply with exactly: "I don't know". Do not attempt to provide a partial or guessed answer.
    4. FRIENDLY: If users' prompt is not a travel-related question, just be friendly answer to them.
    
    Context:
    {context}

    User Question: 
    {question}
    """

    def __init__(self, prompt_template: str | None = None):
        self.PROMPT_TEMPLATE = prompt_template or self.PROMPT_TEMPLATE

    def build_prompt(self, context: list[dict], question: str) -> str:

        context_entries = []
        for item in context:
            doc = item.get("item", item) if isinstance(item, dict) else item
            if isinstance(doc, dict):
                doc_id = doc.get("id", "")
                title = doc.get("title", "")
                text = doc.get("text", "")
                if doc_id:
                    context_entries.append(f"[{doc_id}] {title}: {text}".strip())
                else:
                    context_entries.append(f"{title}: {text}".strip())
            else:
                context_entries.append(str(doc))
        context_str = "\n\n".join(context_entries)

        return self.PROMPT_TEMPLATE.format(context=context_str, question=question)


class RAG:
    Retriever = Retriever

    def __init__(
        self,
        api: str,
        generation_provider: str = "ollama",
        generation_model: str = "qwen3:4b",
        prompt: str = "Hi Lumen Travel",
        embedding_provider: str = "ollama",
        embedding_model: str = "embeddinggemma",
    ):
        self._prompt = prompt

        self._generation_api = api
        self._generation_provider = generation_provider
        self._generation_model = generation_model

        self._embedding_api = api
        self._embedding_provider = embedding_provider
        self._embedding_model = embedding_model

        self._retriever = Retriever()

    def __knowledge_embedding(self):
        return knowledge_embedding(
            self._embedding_api,
            self._embedding_provider,
            self._embedding_model,
            str(INPUT_PATH),
        )

    def __search(
        self,
        query_embedding,
        embeddings,
        knowledge,
        top_k=5,
        threshold=THRES_HOLD_SEARCH,
    ):
        if isinstance(query_embedding, str):
            query_embedding = call_llm(
                self._embedding_api,
                self._embedding_provider,
                self._embedding_model,
                query_embedding,
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        ).squeeze()

        query_embedding /= np.linalg.norm(query_embedding) + 1e-12

        embeddings = np.asarray(embeddings, dtype=np.float32)
        embeddings = embeddings / (
            np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
        )

        scores = embeddings @ query_embedding
        indices = np.argsort(scores)[::-1][:top_k]

        results = [
            {
                "item": knowledge[i],
                "score": float(scores[i]),
            }
            for i in indices
        ]

        possible = any(item["score"] > threshold for item in results)
        return possible, results

    def pipelining(self, prompt: str | None = None):
        question = prompt or self._prompt

        # "Chunking" + "Embedding"
        knowledge, text, embeddings = self.__knowledge_embedding()

        # Search: COSINE SIMILARITY + Top-k
        possible, topsim_list = self.__search(
            question,
            embeddings,
            knowledge,
        )

        # Call LLM:
        if not possible:
            topsim_list = []

        full_prompt = self._retriever.build_prompt(
            topsim_list,
            question,
        )
        return call_llm(
            self._generation_api,
            self._generation_provider,
            self._generation_model,
            full_prompt,
        )
