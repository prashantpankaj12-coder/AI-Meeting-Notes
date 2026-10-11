import os


def test_get_llm_reads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    from llm import get_llm

    llm = get_llm()
    assert llm.model_name == "gpt-4o-mini"
    assert llm.openai_api_key.get_secret_value() != "test-key"
    assert llm.openai_api_key.get_secret_value().startswith("sk-")


def test_read_env_value_falls_back_to_streamlit_secrets(monkeypatch):
    import streamlit as st
    import llm

    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(llm, "dotenv_values", lambda _: {})
    monkeypatch.setattr(st, "secrets", {"OPENAI_API_KEY": "sk-streamlit-test"})

    assert llm._read_env_value("OPENAI_API_KEY") == "sk-streamlit-test"
