import os


def test_get_llm_reads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    from llm import get_llm

    llm = get_llm()
    assert llm.model_name == "gpt-4o-mini"
    assert llm.openai_api_key.get_secret_value() != "test-key"
    assert llm.openai_api_key.get_secret_value().startswith("sk-")
