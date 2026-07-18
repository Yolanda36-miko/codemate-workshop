import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "CodeMate 智学工坊"
    APP_VERSION: str = "0.1.0"

    # Focus course — the single course this platform centers on
    FOCUS_COURSE: str = "数据结构与算法"
    FOCUS_COURSE_CODE: str = "data_structures"

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    # DeepSeek (OpenAI-compatible API)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    # Common
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    LLM_REQUEST_TIMEOUT: int = int(os.getenv("LLM_REQUEST_TIMEOUT", "60"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./codemate.db")
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000",
    ).split(",")


settings = Settings()
