"""
client.py
---------
Thin, safe wrapper around the Google Gemini API.

Features:
- Reads API key from environment (never hardcoded)
- Automatic retries on transient errors (via tenacity)
- Token counting via genai.count_tokens
- Clear exceptions for common failure modes
- Same LLMResponse interface as before, so nothing else in the app needs to change
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import google.generativeai as genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Approximate prices per 1M tokens (USD). Gemini free tier = $0.
# Update if Google changes pricing: https://ai.google.dev/pricing
_PRICING_PER_1M = {
    "gemini-2.0-flash":       {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash-lite":  {"input": 0.0375, "output": 0.15},
    "gemini-1.5-pro":         {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash":       {"input": 0.075, "output": 0.30},
}


class LLMError(Exception):
    """Raised for any LLM-related failure that the caller should handle."""


@dataclass
class LLMResponse:
    """Result of a chat completion."""
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    finish_reason: str | None = None

    def __str__(self) -> str:
        return self.text


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD using the paid tier prices. Free tier -> keep for reference."""
    pricing = _PRICING_PER_1M.get(model, _PRICING_PER_1M["gemini-2.0-flash"])
    return (
        (input_tokens / 1_000_000) * pricing["input"]
        + (output_tokens / 1_000_000) * pricing["output"]
    )


def _to_gemini_history(history: Iterable[dict]) -> list[dict]:
    """Convert our internal history format to Gemini's format."""
    out = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "assistant":
            role = "model"
        if role not in {"user", "model"}:
            continue
        out.append({"role": role, "parts": [content]})
    return out


class LLMClient:
    """Wrapper around Google Gemini chat."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model

        if not self.api_key or self.api_key.startswith("PASTE"):
            raise LLMError(
                "Gemini API key is missing or still a placeholder. "
                "Set GEMINI_API_KEY in your .env file."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"LLMClient (Gemini) initialized with model={self.model_name}")

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _generate(self, contents, system_instruction: str | None, generation_config):
        """Internal call with retries."""
        model = self.model
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction,
            )
        return model.generate_content(contents, generation_config=generation_config)

    def chat(
        self,
        user_message: str,
        *,
        system_prompt: str | None = None,
        history: Iterable[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = 1024,
    ) -> LLMResponse:
        """Send a chat request to Gemini and return an LLMResponse."""
        if not user_message or not user_message.strip():
            raise LLMError("user_message cannot be empty.")

        contents: list[dict] = []
        if history:
            contents.extend(_to_gemini_history(history))
        contents.append({"role": "user", "parts": [user_message]})

        generation_config = {"temperature": temperature}
        if max_tokens is not None:
            generation_config["max_output_tokens"] = max_tokens

        try:
            response = self._generate(contents, system_prompt, generation_config)
        except Exception as e:
            msg = str(e)
            if "API key" in msg or "invalid" in msg.lower() or "permission" in msg.lower():
                raise LLMError(
                    f"Authentication failed with Gemini. Check your GEMINI_API_KEY. Details: {msg}"
                ) from e
            if "quota" in msg.lower() or "rate" in msg.lower():
                raise LLMError(
                    f"Rate limit / quota error from Gemini: {msg}"
                ) from e
            raise LLMError(f"Gemini API error: {msg}") from e

        text = ""
        try:
            text = response.text or ""
        except Exception:
            try:
                parts = response.candidates[0].content.parts
                text = "".join(p.text for p in parts if hasattr(p, "text"))
            except Exception:
                text = "(no text returned)"

        input_tokens = 0
        output_tokens = 0
        finish_reason = None
        try:
            usage = response.usage_metadata
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0
        except Exception:
            pass
        try:
            finish_reason = str(response.candidates[0].finish_reason)
        except Exception:
            pass

        cost = _estimate_cost(self.model_name, input_tokens, output_tokens)

        logger.info(
            f"Gemini chat OK | model={self.model_name} "
            f"in={input_tokens} out={output_tokens} "
            f"cost=${cost:.6f} (free tier = $0)"
        )

        return LLMResponse(
            text=text,
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost,
            finish_reason=finish_reason,
        )


def count_tokens(text: str, model: str | None = None) -> int:
    """Count tokens using Gemini's tokenizer. Falls back to a rough estimate."""
    try:
        settings = get_settings()
        m = model or settings.gemini_model
        generative_model = genai.GenerativeModel(m)
        result = generative_model.count_tokens(text)
        return int(result.total_tokens)
    except Exception:
        return max(1, len(text) // 4)