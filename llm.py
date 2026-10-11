import os

from dotenv import dotenv_values, load_dotenv
from langchain_openai import ChatOpenAI

_PLACEHOLDER_VALUES = {
    "",
    "test-key",
    "test_key",
    "changeme",
    "your_openai_api_key",
    "dummy",
}


def _read_env_value(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    normalized = value.strip() if isinstance(value, str) else ""
    if normalized and normalized.lower() not in {v.lower() for v in _PLACEHOLDER_VALUES}:
        return normalized

    dotenv_values_result = dotenv_values(".env")
    value_from_dotenv = dotenv_values_result.get(name)
    if isinstance(value_from_dotenv, str):
        normalized = value_from_dotenv.strip()
        if normalized and normalized.lower() not in {v.lower() for v in _PLACEHOLDER_VALUES}:
            os.environ[name] = normalized
            return normalized

    try:
        import streamlit as st
        from streamlit.errors import StreamlitSecretNotFoundError
    except ImportError:
        return default

    try:
        value_from_secrets = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        return default

    if isinstance(value_from_secrets, str):
        normalized = value_from_secrets.strip()
        if normalized and normalized.lower() not in {v.lower() for v in _PLACEHOLDER_VALUES}:
            return normalized

    return default


def get_llm(model: str | None = None, **kwargs):
    """Create a configured OpenAI chat model from environment variables."""
    load_dotenv()

    api_key = _read_env_value("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Add it to Streamlit Cloud app Settings > Secrets, "
            "your environment, or a local .env file."
        )

    model_name = model or _read_env_value("OPENAI_MODEL", "gpt-4o-mini")
    default_kwargs = {
        "model": model_name,
        "api_key": api_key,
        "temperature": 0,
        "max_retries": 1,
        "timeout": 60,
    }
    default_kwargs.update(kwargs)
    return ChatOpenAI(**default_kwargs)
