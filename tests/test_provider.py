import pytest
from devlens.llm.openai_provider import OpenAIProvider


def test_openai_model_is_not_hardcoded(monkeypatch):
    monkeypatch.delenv("DEVLENS_OPENAI_MODEL", raising=False)
    with pytest.raises(ValueError, match="DEVLENS_OPENAI_MODEL"):
        OpenAIProvider()
