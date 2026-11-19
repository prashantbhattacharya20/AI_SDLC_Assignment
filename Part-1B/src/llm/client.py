"""Groq LLM Client implementation with bounded exponential backoff.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 4: LLM Client Layer)
"""

import asyncio
import json
import time
from typing import Any, Protocol, runtime_checkable

from groq import (
    APIConnectionError,
    APITimeoutError,
    AsyncGroq,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

from src.config import get_settings
from src.llm.exceptions import ProviderUnavailableError


@runtime_checkable
class LLMClient(Protocol):
    """Abstract protocol for code review LLM providers."""

    async def generate_review(self, prompt: str) -> dict[str, Any]:
        """Generate structured code review findings from a prompt."""
        ...


class GroqClient:
    """Official Groq SDK client adapter with bounded exponential backoff.

    The GroqClient is the sole owner of retry logic. It retries transient errors
    (rate limits, network timeouts, recoverable malformed responses) at most 2 times
    with exponential backoff (~1s, ~2s). Permanent errors (auth, permissions) fail immediately.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_id: str | None = None,
        client: Any | None = None,
        max_retries: int | None = None,
        backoff_factor: float | None = None,
    ):
        settings = get_settings() if api_key is None else None
        self.api_key = api_key or (settings.GROQ_API_KEY.get_secret_value() if settings else "")
        self.model_id = model_id or (settings.MODEL_ID if settings else "openai/gpt-oss-120b")
        self.max_retries = max_retries if max_retries is not None else (settings.GROQ_MAX_RETRIES if settings else 2)
        self.backoff_factor = (
            backoff_factor if backoff_factor is not None else (settings.GROQ_BACKOFF_FACTOR if settings else 1.0)
        )

        # Support dependency injection of client for unit testing
        if client is not None:
            self.client = client
        else:
            self.client = AsyncGroq(api_key=self.api_key)

    async def generate_review(self, prompt: str) -> dict[str, Any]:
        """Execute review prompt with strict JSON mode and retry handling."""
        start_time = time.perf_counter()
        retry_count = 0

        while True:
            try:
                chat_completions = self.client.chat.completions
                response = await chat_completions.create(
                    model=self.model_id,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an automated, highly precise static code analysis system. "
                                "You review code for defects across Bug, Security, Performance, and "
                                "Maintainability categories. You must respond strictly in JSON format "
                                "with a root 'findings' array matching the requested schema."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )

                content = response.choices[0].message.content or "{}"
                parsed_json = json.loads(content)

                latency_ms = int((time.perf_counter() - start_time) * 1000)

                prompt_tokens = response.usage.prompt_tokens if hasattr(response, "usage") and response.usage else 0
                completion_tokens = (
                    response.usage.completion_tokens if hasattr(response, "usage") and response.usage else 0
                )
                total_tokens = response.usage.total_tokens if hasattr(response, "usage") and response.usage else 0

                return {
                    "parsed": parsed_json,
                    "raw_content": content,
                    "telemetry": {
                        "model_id": self.model_id,
                        "latency_ms": latency_ms,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "retry_count": retry_count,
                    },
                }

            except (AuthenticationError, PermissionDeniedError) as perm_err:
                # Permanent failure: DO NOT RETRY
                raise perm_err

            except (
                RateLimitError,
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                json.JSONDecodeError,
            ) as transient_err:
                if retry_count < self.max_retries:
                    retry_count += 1
                    # Exponential backoff: ~1s for retry 1, ~2s for retry 2
                    delay = self.backoff_factor * (2 ** (retry_count - 1))
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise ProviderUnavailableError(
                        message=f"Groq API unavailable after {retry_count} retries: {str(transient_err)}"
                    ) from transient_err
            except Exception as generic_err:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.backoff_factor * (2 ** (retry_count - 1))
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise ProviderUnavailableError(
                        message=f"Groq API error after {retry_count} retries: {str(generic_err)}"
                    ) from generic_err
