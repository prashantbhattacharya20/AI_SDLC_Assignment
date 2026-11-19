"""Unit tests for GroqClient and bounded exponential backoff retry logic (T007)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from groq import (
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
)


@pytest.mark.asyncio
async def test_groq_client_success_initial_attempt():
    from src.llm.client import GroqClient

    mock_raw_client = MagicMock()
    mock_chat = AsyncMock()
    mock_chat.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"findings": []}'))],
        usage=MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )
    mock_raw_client.chat.completions = mock_chat

    client = GroqClient(api_key="gsk_test_key", client=mock_raw_client)
    result = await client.generate_review("Review this code")

    assert result["parsed"] == {"findings": []}
    assert result["telemetry"]["retry_count"] == 0
    assert result["telemetry"]["model_id"] == "openai/gpt-oss-120b"
    assert mock_chat.create.call_count == 1


@pytest.mark.asyncio
async def test_groq_client_retry_on_transient_error():
    from src.llm.client import GroqClient

    mock_raw_client = MagicMock()
    mock_chat = AsyncMock()

    # Fail on first attempt with RateLimitError, succeed on second attempt
    success_resp = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"findings": []}'))],
        usage=MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )
    MagicMock()
    mock_chat.create.side_effect = [
        RateLimitError(message="Rate limit exceeded", response=MagicMock(status_code=429), body={}),
        success_resp,
    ]
    mock_raw_client.chat.completions = mock_chat

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        client = GroqClient(api_key="gsk_test_key", client=mock_raw_client)
        result = await client.generate_review("Review this code")

        assert result["parsed"] == {"findings": []}
        assert result["telemetry"]["retry_count"] == 1
        assert mock_chat.create.call_count == 2
        mock_sleep.assert_called_once()
        assert 0.9 <= mock_sleep.call_args[0][0] <= 1.5


@pytest.mark.asyncio
async def test_groq_client_no_retry_on_permanent_error():
    from src.llm.client import GroqClient

    mock_raw_client = MagicMock()
    mock_chat = AsyncMock()
    mock_chat.create.side_effect = AuthenticationError(
        message="Invalid API Key", response=MagicMock(status_code=401), body={}
    )
    mock_raw_client.chat.completions = mock_chat

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        client = GroqClient(api_key="gsk_invalid_key", client=mock_raw_client)
        with pytest.raises(AuthenticationError):
            await client.generate_review("Review this code")

        assert mock_chat.create.call_count == 1
        mock_sleep.assert_not_called()


@pytest.mark.asyncio
async def test_groq_client_exhausted_retries():
    from src.llm.client import GroqClient
    from src.llm.exceptions import ProviderUnavailableError

    mock_raw_client = MagicMock()
    mock_chat = AsyncMock()
    # 1 initial + 2 retries = 3 calls total, all failing
    mock_chat.create.side_effect = APIConnectionError(request=MagicMock())
    mock_raw_client.chat.completions = mock_chat

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        client = GroqClient(api_key="gsk_test_key", client=mock_raw_client)
        with pytest.raises(ProviderUnavailableError):
            await client.generate_review("Review this code")

        assert mock_chat.create.call_count == 3
        assert mock_sleep.call_count == 2
