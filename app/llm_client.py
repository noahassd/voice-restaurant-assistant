from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests

from .config import config, Mode


class LLMClient(ABC):
    """Interface générique pour un client LLM."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        messages : liste de { "role": "system" | "user" | "assistant", "content": str }
        retourne : texte généré par le modèle
        """
        raise NotImplementedError


class LocalOllamaLLMClient(LLMClient):
    """Client LLM pour usage local avec Ollama."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url or config.ollama_base_url
        self.model = model or config.ollama_model

    def generate(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Format standard d’Ollama : {'message': {'content': '...'}}
        return data["message"]["content"]


def get_llm_client() -> LLMClient:
    """Factory pour choisir le backend (local ou cloud)."""
    if config.mode == Mode.LOCAL:
        return LocalOllamaLLMClient()
    else:
        # TODO: implémenter un client Cloud (Google / OpenAI)
        raise NotImplementedError("Client LLM cloud non encore implémenté.")
