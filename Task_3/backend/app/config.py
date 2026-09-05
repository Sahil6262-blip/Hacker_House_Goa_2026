from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

TASK_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=TASK_ROOT / ".env", extra="ignore")

    app_env: str = "development"
    allowed_origins: str = "http://localhost:5174"
    face_provider: str = "opencv"
    max_upload_mb: int = 8
    search_provider: str = "bing_visual_search"
    bing_visual_search_key: str = ""
    bing_visual_search_url: str = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    search_timeout_seconds: float = 20
    blockchain_provider: str = "local_ledger"
    local_ledger_path: str = "data/local_chain.json"

    @property
    def ledger_path(self) -> Path:
        path = Path(self.local_ledger_path)
        return path if path.is_absolute() else TASK_ROOT / path

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
