from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_env: str = "dev"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    pst_neo4j_batch_size: int = 100
    pst_neo4j_continue_on_batch_error: bool = False

    neo4j_uri: str = Field(default="neo4j://your-neo4j-host:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="change_me")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    dnabot_base_url: str = "http://localhost:8080"
    dnabot_model: str = "default"
    dnabot_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
