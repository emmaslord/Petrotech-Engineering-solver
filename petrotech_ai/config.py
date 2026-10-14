
"""Configuration for the PetroTech AI Core."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PROVIDER = "groq"

SUPPORTED_PROVIDERS = ("groq", "ollama")


def get_provider() -> str:
    """Return the configured AI provider."""
    provider = os.getenv("PETROTECH_AI_PROVIDER", DEFAULT_PROVIDER)
    provider = provider.strip().lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported AI provider: {provider}. "
            f"Choose one of: {', '.join(SUPPORTED_PROVIDERS)}."
        )

    return provider


def get_groq_api_key() -> str | None:
    """Read the Groq key from the environment or Streamlit secrets."""
    key = os.getenv("GROQ_API_KEY")

    if key and key.strip():
        return key.strip()

    try:
        import streamlit as st

        key = st.secrets.get("GROQ_API_KEY")
        if isinstance(key, str) and key.strip():
            return key.strip()
    except Exception:
        # Streamlit secrets may be unavailable outside a Streamlit app.
        pass

    return None


def get_ollama_base_url() -> str:
    """Return the local Ollama API address."""
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
