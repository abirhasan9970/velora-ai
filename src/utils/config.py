"""Application configuration loader.

Reads from:
1. Streamlit Secrets (when running on Streamlit Cloud)
2. Environment variables / .env file (for local development)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ==== PROJECT ROOT ====
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Settings:
    """Application settings."""
    app_env: str
    log_level: str
    max_upload_mb: int
    llm_provider: str
    gemini_api_key: str
    gemini_model: str


def _get_secret(name: str) -> str | None:
    """Get a value from Streamlit Secrets first, then environment variables."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass

    value = os.getenv(name)
    if value is not None and value.strip() != "":
        return value

    return None


def _get_int(name: str, default: int) -> int:
    raw = _get_secret(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(
            f"Environment variable {name} must be an integer, got: {raw!r}"
        )


def load_settings() -> Settings:
    """Read environment variables into a Settings object."""
    api_key = _get_secret("GEMINI_API_KEY") or ""

    return Settings(
        app_env=_get_secret("APP_ENV") or "development",
        log_level=(_get_secret("LOG_LEVEL") or "INFO").upper(),
        max_upload_mb=_get_int("MAX_UPLOAD_MB", 50),
        llm_provider=(_get_secret("LLM_PROVIDER") or "gemini").lower(),
        gemini_api_key=api_key,
        gemini_model=_get_secret("GEMINI_MODEL") or "gemini-2.0-flash",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings