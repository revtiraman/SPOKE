"""Central configuration for Spoke — loaded from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    # LLM API keys
    hf_api_token: str = Field(default="", alias="HF_API_TOKEN")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    # Models
    main_brain_model: str = Field(default="moonshotai/Kimi-K2-Instruct", alias="MAIN_BRAIN_MODEL")
    planner_model: str = Field(default="deepseek-ai/DeepSeek-R1", alias="PLANNER_MODEL")
    coder_model: str = Field(default="Qwen/Qwen3-Coder-30B-A3B-Instruct", alias="CODER_MODEL")
    fast_model: str = Field(default="meta-llama/Llama-3.3-70B-Instruct", alias="FAST_MODEL")
    tiny_model: str = Field(default="Qwen/Qwen3-4B", alias="TINY_MODEL")

    # Anthropic
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # Sandbox
    sandbox_type: str = Field(default="subprocess", alias="SANDBOX_TYPE")
    e2b_api_key: str = Field(default="", alias="E2B_API_KEY")

    # GitHub
    github_token: str = Field(default="", alias="GITHUB_TOKEN")

    # Pipeline
    max_debug_retries: int = Field(default=5, alias="MAX_DEBUG_RETRIES")
    execution_timeout_seconds: int = Field(default=120, alias="EXECUTION_TIMEOUT_SECONDS")
    max_video_duration_seconds: int = Field(default=180, alias="MAX_VIDEO_DURATION_SECONDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # App
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    demo_mode: bool = Field(default=False, alias="DEMO_MODE")

    # Paths
    storage_dir: Path = BASE_DIR / "storage"
    generated_dir: Path = BASE_DIR / "storage" / "generated"
    logs_dir: Path = BASE_DIR / "logs"
    db_path: Path = BASE_DIR / "storage" / "sessions.db"

    model_config = {"env_file": ".env", "populate_by_name": True}

    def model_post_init(self, __context) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def hf_base_url(self) -> str:
        t = self.hf_api_token
        if t.startswith("gsk_"):
            return "https://api.groq.com/openai"
        if t.startswith("csk-"):
            return "https://api.cerebras.ai"
        if t.startswith("AIza"):
            return "https://generativelanguage.googleapis.com/v1beta/openai"
        if t.startswith("together_"):
            return "https://api.together.xyz"
        if t.startswith("sk-or-"):
            return "https://openrouter.ai/api"
        return "https://router.huggingface.co"

    @property
    def has_hf(self) -> bool:
        return bool(self.hf_api_token and self.hf_api_token != "hf_your_token_here")

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_e2b(self) -> bool:
        return bool(self.e2b_api_key)


settings = Settings()
