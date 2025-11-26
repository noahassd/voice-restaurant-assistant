from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass
class AppConfig:
    mode: Mode = Mode.LOCAL
    # Pour plus tard : clés API, URLs, etc.
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"


config = AppConfig()
