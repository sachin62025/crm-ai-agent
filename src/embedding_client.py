import requests
import json
# from src import config
from . import config


# This custom class bypasses the problematic LangChain client and makes a direct,
# clean API call that the Nebius server will accept.
class DirectNebiusEmbeddings:
    """
    A custom embedding client that makes a direct API call to a Nebius
    OpenAI-compatible endpoint.
    """

    def __init__(self, model_name, api_key, api_base):
        self.model_name = model_name
        self.api_key = api_key
        # Ensure the URL is correctly formed for the /embeddings endpoint
        self.url = f"{api_base.rstrip('/')}/embeddings"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Handles embedding a list of texts."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"input": texts, "model": self.model_name}

        # We print the URL we are about to call for final debugging
        print(f"--- Making direct API call to: {self.url} ---")
        response = requests.post(self.url, headers=headers, data=json.dumps(payload))

        # This will raise an error if the request failed
        response.raise_for_status()

        response_data = response.json()

        embeddings = [item["embedding"] for item in response_data["data"]]
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Handles embedding a single text (query)."""
        return self.embed_documents([text])[0]


def get_embedding_model():
    """
    This function now returns our reliable, direct client.
    """
    return DirectNebiusEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME,
        api_key=config.NEBIUS_API_KEY,
        api_base=config.NEBIUS_API_BASE,
    )
