"""Backward-compatible proxy module for OpenRouter AI Client.

Exposes OpenRouterClient under both OpenRouterClient and GeminiClient identifiers
to maintain backward compatibility across existing tests and legacy references.
"""

from utils.openrouter_client import (
    OpenRouterClient,
    get_openrouter_client,
    OpenRouterClient as GeminiClient,
    get_openrouter_client as get_gemini_client,
    get_openrouter_client as get_ai_client,
    OPENROUTER_BASE_URL,
    DEFAULT_OPENROUTER_MODEL
)

__all__ = [
    "OpenRouterClient",
    "get_openrouter_client",
    "GeminiClient",
    "get_gemini_client",
    "get_ai_client",
    "OPENROUTER_BASE_URL",
    "DEFAULT_OPENROUTER_MODEL"
]
