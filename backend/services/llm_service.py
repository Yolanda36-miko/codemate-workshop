"""
Unified LLM Provider Base Layer (Phase 5A)

Supports three providers:
- mock:     Returns preset data from mock_responses.json (default)
- openai:   OpenAI-compatible API (lazy imports)
- anthropic: Anthropic Messages API (lazy imports)

Usage:
    from services.llm_service import get_llm
    llm = get_llm()
    resp = llm.chat([{"role": "user", "content": "Hello"}], task="general")
"""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChatResponse:
    content: str
    model: str = "mock"
    usage: Optional[dict] = None
    finish_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# JSON safe parser
# ---------------------------------------------------------------------------

def safe_parse_json(raw: str) -> Optional[dict | list]:
    """
    Safely extract JSON from LLM output.
    Strategy (tried in order):
      1. Direct json.loads on the whole string
      2. Extract from ```json ... ``` code blocks
      3. Extract outermost { } or [ ] pair
    Returns None on failure — never raises.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None

    text = raw.strip()

    # 1) Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2) ```json ... ``` code block
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 3) Extract outermost { } or [ ]
    for start_char, end_char in (("{", "}"), ("[", "]")):
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (json.JSONDecodeError, ValueError):
                pass

    return None


# ---------------------------------------------------------------------------
# Abstract LLM Provider
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> ChatResponse:
        """Send a chat completion request.  Must be overridden."""
        ...

    def chat_json(self, messages: list[dict], **kwargs) -> Optional[dict | list]:
        """
        Send a chat request and parse the response as JSON.
        Default implementation: call chat() then safe_parse_json.
        Returns None if parsing fails.
        """
        resp = self.chat(messages, **kwargs)
        result = safe_parse_json(resp.content)
        if result is None:
            logger.warning(
                "chat_json failed to parse JSON from response (model=%s, len=%d): %.200s...",
                resp.model, len(resp.content), resp.content,
            )
        return result


# ---------------------------------------------------------------------------
# Mock Provider
# ---------------------------------------------------------------------------

_MOCK_DATA_CACHE: Optional[dict] = None


def _load_mock_data() -> dict:
    global _MOCK_DATA_CACHE
    if _MOCK_DATA_CACHE is not None:
        return _MOCK_DATA_CACHE
    path = DATA_DIR / "mock_responses.json"
    try:
        with open(path, encoding="utf-8") as f:
            _MOCK_DATA_CACHE = json.load(f)
    except Exception as e:
        logger.warning("Failed to load mock_responses.json: %s", e)
        _MOCK_DATA_CACHE = {}
    return _MOCK_DATA_CACHE


class MockProvider(LLMProvider):
    """
    Mock LLM provider — returns preset data from data/mock_responses.json.

    Supported task values:
      profile_chat, generate_resources, generate_path,
      assessment_feedback, tutor_chat
    Falls back to a generic greeting for unknown tasks.
    """

    def chat(self, messages: list[dict], task: str = "general", **kwargs) -> ChatResponse:
        mock_data = _load_mock_data()

        task_map = {
            "profile_chat": "profile_chat",
            "generate_resources": "resources",
            "generate_path": "path",
            "assessment_feedback": "assessment",
            "tutor_chat": "tutor",
        }

        data_key = task_map.get(task)
        if data_key and data_key in mock_data:
            content = json.dumps(mock_data[data_key], ensure_ascii=False, indent=2)
        else:
            content = json.dumps({
                "message": "Mock LLM response",
                "task": task,
                "note": "This is a mock response. Set LLM_PROVIDER=openai or LLM_PROVIDER=anthropic to use real LLM.",
            }, ensure_ascii=False, indent=2)

        return ChatResponse(content=content, model="mock", finish_reason="stop")


# ---------------------------------------------------------------------------
# OpenAI Provider (lazy import)
# ---------------------------------------------------------------------------

class OpenAIProvider(LLMProvider):
    """OpenAI-compatible API provider. SDK is imported lazily on first call."""

    def __init__(self) -> None:
        self._client: Optional[object] = None
        self._model: str = settings.OPENAI_MODEL
        self._max_retries: int = settings.LLM_MAX_RETRIES
        self._timeout: int = settings.LLM_REQUEST_TIMEOUT

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI  # type: ignore
            except ImportError:
                raise ImportError(
                    "openai package is not installed. Run: pip install openai"
                )
            base_url = settings.OPENAI_BASE_URL or None
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=base_url,
                timeout=self._timeout,
            )
        return self._client

    def chat(self, messages: list[dict], task: str = "general", **kwargs) -> ChatResponse:
        for attempt in range(self._max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    **kwargs,
                )
                choice = resp.choices[0]
                return ChatResponse(
                    content=choice.message.content or "",
                    model=resp.model,
                    usage=resp.usage.model_dump() if resp.usage else None,
                    finish_reason=choice.finish_reason,
                )
            except Exception as e:
                logger.warning(
                    "OpenAI chat attempt %d/%d failed: %s",
                    attempt + 1, self._max_retries + 1, e,
                )
                if attempt >= self._max_retries:
                    raise

        # Unreachable, but keep type checker happy
        raise RuntimeError("OpenAI chat: all retries exhausted")


# ---------------------------------------------------------------------------
# Anthropic Provider (lazy import)
# ---------------------------------------------------------------------------

class AnthropicProvider(LLMProvider):
    """Anthropic Messages API provider. SDK is imported lazily on first call."""

    def __init__(self) -> None:
        self._client: Optional[object] = None
        self._model: str = settings.ANTHROPIC_MODEL
        self._max_retries: int = settings.LLM_MAX_RETRIES
        self._timeout: int = settings.LLM_REQUEST_TIMEOUT

    @property
    def client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic  # type: ignore
            except ImportError:
                raise ImportError(
                    "anthropic package is not installed. Run: pip install anthropic"
                )
            self._client = Anthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                timeout=self._timeout,
            )
        return self._client

    @staticmethod
    def _to_anthropic_messages(messages: list[dict]) -> tuple[Optional[str], list[dict]]:
        """Convert OpenAI-style messages to Anthropic format. Returns (system, messages)."""
        system = None
        converted = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
            else:
                converted.append(m)
        return system, converted

    def chat(self, messages: list[dict], task: str = "general", **kwargs) -> ChatResponse:
        system, api_messages = self._to_anthropic_messages(messages)

        for attempt in range(self._max_retries + 1):
            try:
                kwargs.pop("temperature", None)  # Anthropic uses top_p/top_k
                create_kwargs = {
                    "model": self._model,
                    "messages": api_messages,
                    "max_tokens": 4096,
                    **kwargs,
                }
                if system:
                    create_kwargs["system"] = system

                resp = self.client.messages.create(**create_kwargs)

                # Extract text from content blocks
                content = ""
                for block in resp.content:
                    if hasattr(block, "text"):
                        content += block.text

                return ChatResponse(
                    content=content,
                    model=resp.model,
                    usage=resp.usage.model_dump() if resp.usage else None,
                    finish_reason=resp.stop_reason,
                )
            except Exception as e:
                logger.warning(
                    "Anthropic chat attempt %d/%d failed: %s",
                    attempt + 1, self._max_retries + 1, e,
                )
                if attempt >= self._max_retries:
                    raise

        raise RuntimeError("Anthropic chat: all retries exhausted")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_LLM_INSTANCE: Optional[LLMProvider] = None


def get_llm() -> LLMProvider:
    """
    Return the configured LLM provider (singleton).

    Provider selection:
      - LLM_PROVIDER=mock        → MockProvider (default)
      - LLM_PROVIDER=openai      → OpenAIProvider (falls back to mock if no API key)
      - LLM_PROVIDER=anthropic   → AnthropicProvider (falls back to mock if no API key)

    In mock mode, no external SDK imports are triggered.
    Real providers are lazy: SDK is imported on first chat() call.
    """
    global _LLM_INSTANCE
    if _LLM_INSTANCE is not None:
        return _LLM_INSTANCE

    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning(
                "LLM_PROVIDER=%s but OPENAI_API_KEY is empty — falling back to MockProvider",
                settings.LLM_PROVIDER,
            )
            _LLM_INSTANCE = MockProvider()
        else:
            try:
                _LLM_INSTANCE = OpenAIProvider()
            except Exception as e:
                logger.warning("Failed to init OpenAIProvider: %s — falling back to MockProvider", e)
                _LLM_INSTANCE = MockProvider()

    elif provider_name == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            logger.warning(
                "LLM_PROVIDER=%s but ANTHROPIC_API_KEY is empty — falling back to MockProvider",
                settings.LLM_PROVIDER,
            )
            _LLM_INSTANCE = MockProvider()
        else:
            try:
                _LLM_INSTANCE = AnthropicProvider()
            except Exception as e:
                logger.warning("Failed to init AnthropicProvider: %s — falling back to MockProvider", e)
                _LLM_INSTANCE = MockProvider()

    else:
        if provider_name not in ("mock", ""):
            logger.warning(
                "Unknown LLM_PROVIDER=%r — using MockProvider", settings.LLM_PROVIDER,
            )
        _LLM_INSTANCE = MockProvider()

    return _LLM_INSTANCE
