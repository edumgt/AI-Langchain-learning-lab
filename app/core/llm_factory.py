from __future__ import annotations
import requests
from app.core import settings

def _reachable(url: str, timeout: int = 3) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False

def pick_provider() -> str:
    p = (settings.LLM_PROVIDER or "auto").lower()
    if p in ("ollama", "openai_compatible", "openai"):
        return p

    if settings.OLLAMA_BASE_URL and _reachable(settings.OLLAMA_BASE_URL.rstrip("/") + "/api/tags"):
        return "ollama"
    if settings.OPENAI_COMPAT_BASE_URL and _reachable(settings.OPENAI_COMPAT_BASE_URL.rstrip("/") + "/models"):
        return "openai_compatible"
    if settings.OPENAI_API_KEY:
        return "openai"
    return "ollama"

def build_chat_model(temperature: float = 0.2, streaming: bool = False):
    provider = pick_provider()

    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=temperature,
            timeout=settings.OLLAMA_TIMEOUT_SEC,
            streaming=streaming,
        )

    if provider == "openai_compatible":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.OPENAI_COMPAT_API_KEY,
            base_url=settings.OPENAI_COMPAT_BASE_URL,
            model=settings.OPENAI_COMPAT_MODEL,
            temperature=temperature,
            streaming=streaming,
        )

    from langchain_openai import ChatOpenAI
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is empty but provider=openai")
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        streaming=streaming,
    )

def build_embeddings():
    provider = pick_provider()

    if provider == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_EMBED_MODEL)

    if provider == "openai_compatible":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=settings.OPENAI_COMPAT_API_KEY,
            base_url=settings.OPENAI_COMPAT_BASE_URL,
            model="text-embedding-3-small",
        )

    from langchain_openai import OpenAIEmbeddings
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is empty but embeddings need OpenAI")
    return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small")

def provider_name() -> str:
    return pick_provider()
