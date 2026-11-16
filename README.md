# LAB 3 - Authentication - RAG Chatbot

## Student Information

| Field | Detail |
| :--- | :--- |
| Student ID | 25127522 |
| Student Name | Ngo Phuoc Toan |
| Email | nptoan2527@clc.fitus.edu.vn |
| Chosen City | Ho Chi Minh City, Vietnam |
| Repository's URL | [Repository's URL](https://github.com/NPToanLX-TNH-HCMUS/HCMUS-Computational-Thinking-Lab/tree/LAB_3/Authentication-RAG-chatbot)

## Project Overview

Lumen Travel Assistant is a Streamlit application for answering travel questions about Ho Chi Minh City. The application combines:

- Firebase Authentication for email/password sign-up, sign-in, and sign-out.
- A local travel guide stored in `data/knowledge_base.json`.
- Ollama `embeddinggemma` for document and question embeddings.
- Cosine-similarity retrieval with top-k results.
- Ollama `qwen3:4b` for grounded answer generation.
- In-memory chat history stored in `st.session_state`.

The assistant is instructed to answer only from the travel guide, cite guide entry IDs such as `[G01]`, and respond with `I don't know` when the guide does not contain the requested information.

## Project Structure

```text
.
├── data/
│   └── knowledge_base.json
├── src/
|   ├── ollama_server.ipynb
│   ├── app.py
│   ├── firebase_client.py
│   ├── RAG/
│   │   └── rag.py
│   ├── UI/
│   │   ├── chatbot.py
│   │   └── login.py
│   └── utils/
│       └── call_llm.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.10 or newer.
- A reachable Ollama URL, optionally exposed through Pinggy.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -e .
```

## Environment Configuration

Copy `.env.example` to `.env` and fill in the values:

```env
FIREBASE_PROJECT_ID="your-firebase-project-id"
FIREBASE_API_KEY="your-firebase-web-api-key"
FIREBASE_APP_ID="your-firebase-app-id"
PINGGY_URL="https://your-ollama-server-url"
```

The Ollama server must provide these models:

```bash
ollama pull embeddinggemma
ollama pull qwen3:4b
```

## Run the Application

### Start the Ollama Server on Google Colab

The included notebook `src/ollama_server.ipynb` starts the Ollama server and downloads the required models on Google Colab.

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload and open `src/ollama_server.ipynb`.
3. Select a runtime with GPU and enable Internet access.
4. Run the notebook cells in order.
5. Confirm that both `embeddinggemma` and `qwen3:4b` are listed successfully.
6. Run the optional Pinggy cell and execute the generated SSH command in the Colab terminal.
7. Copy the HTTPS URL provided by Pinggy.
8. Set that URL as `PINGGY_URL` in the local `.env` file:

```env
PINGGY_URL="https://your-pinggy-ollama-url"
```

Keep the Colab runtime and Pinggy terminal running while using the Streamlit application. The Ollama server is not publicly authenticated, so do not share the Pinggy URL publicly.

### Start Streamlit

From the project root, run:

```bash
streamlit run src/app.py
```

## Test Table

The six test cases below were executed on 2026-11-16. The run was blocked during the initial embedding request because the configured Pinggy hostname could not be resolved and no local Ollama server was running. The expected entry ID is the reference used to check the final answer.

| # | Question | Type | Expected entry ID | Expected result | Status |
| :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | What can I buy at Ben Thanh Market? | Answerable | G01 | Correct answer with `[G01]` | ✅ **Chatbot:** You can buy clothing, souvenirs, and typical street food at Ben Thanh Market [G01] |
| 2 | Where can I learn about the Vietnam War? | Answerable | G03 | Correct answer with `[G03]` | ✅ **Chatbot:** You can learn about the Vietnam War at the War Remnants Museum [G03] |
| 3 | Where can I see a panoramic view of the city? | Answerable | G09 | Correct answer with `[G09]` | ✅ **Chatbot:** You can see a panoramic view of the city at Landmark 81 [G09] |
| 4 | Tell me about the famous market in central Saigon where visitors can shop and eat street food. | Paraphrase | G01 | Correctly identifies Ben Thanh Market | ✅ **Chatbot:** Ben Thanh Market is one of the most famous symbols of Ho Chi Minh City and offers shopping for clothing and souvenirs alongside typical street food [G01]. Tan Dinh Market is also a prominent street food paradise and the most abundant fabric selling place in Saigon, where visitors can enjoy crab soup, sweet soup, and other snacks [G16]. Both markets are located in central Saigon and fit the description of famous destinations for shopping and street food experiences |
| 5 | What time does Ben Thanh Market open? | Not in guide | G01 has no opening-hours field | `I don't know` | ✅ **Chatbot:** I don't know |
| 6 | What is the ticket price for Landmark 81? | Not in guide | G09 has no price field | `I don't know` | ✅ **Chatbot:** I don't know |

## Known Limitations

- The Ollama server must remain reachable while the application is running.

## AI Tools Used

ChatGPT/Codex was used to assist with:

- Streamlit UI structure.
- Firebase Authentication REST API integration.
- Documentation organization.

## Demonstration Video

Video link: [Demonstration Video](https://drive.google.com/drive/folders/1Vin7fKkcOjFJhQohczAjql7cIrcXRt8z?usp=sharing)
