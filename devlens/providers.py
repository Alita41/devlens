from __future__ import annotations
import os
from devlens.llm.local import LocalProvider


def get_provider():
    provider = os.getenv("DEVLENS_LLM_PROVIDER", "local").lower().strip()
    if provider == "openai":
        from devlens.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    return LocalProvider()
