import numpy as np
import requests


class ProviderNotSupport(Exception):
    """
    Raise when client call embedding model's provider which is not supported
    """


class ModelNotSupport(Exception):
    """
    Raise when client call embedding model which is not supported
    """


class OllamaServerError(Exception):
    """Raise when the Ollama server cannot complete a request."""


def call_llm(api: str, provider: str, model: str, prompt: str | list[str]):
    if provider == "ollama":
        try:
            if model == "embeddinggemma":
                response = requests.post(
                    f"{api}/api/embed",
                    json={
                        "model": model,
                        "input": prompt,
                    },
                    timeout=120,
                )
                response.raise_for_status()

                embeddings = np.array(response.json()["embeddings"], dtype=np.float32)

                return embeddings

            elif model == "qwen3:4b":
                response = requests.post(
                    f"{api}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=200,
                )
                response.raise_for_status()

                return response.json()["response"]

            else:
                raise ModelNotSupport
        except requests.ConnectionError as error:
            raise OllamaServerError(
                "Unable to connect to the Ollama Server. "
                "Please check the Ollama/Pinggy URL and try again."
            ) from error
        except requests.Timeout as error:
            raise OllamaServerError(
                "The Ollama Server took too long to respond. Please try again later."
            ) from error
        except requests.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else "unknown"
            raise OllamaServerError(
                f"The Ollama Server returned HTTP error {status_code}. "
                "Please check the server and make sure the model is installed."
            ) from error
        except requests.RequestException as error:
            raise OllamaServerError(
                "An error occurred while calling the Ollama Server. Please try again."
            ) from error

    else:
        raise ProviderNotSupport
