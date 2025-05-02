import pytest
import asyncio
from typing import TYPE_CHECKING
from pytest_mock.plugin import MockerFixture
from _pytest.logging import LogCaptureFixture
from unittest.mock import AsyncMock

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch

import src.ai_solarpunk.clients.openai_story_client as openai_story_client

@pytest.mark.asyncio
async def test_generate_story_success(mocker: MockerFixture, caplog: LogCaptureFixture) -> None:
    """Test successful story generation with OpenAI client."""
    mock_response = mocker.MagicMock()
    mock_choice = mocker.MagicMock()
    mock_choice.message.content = "A hopeful solarpunk story."
    mock_response.choices = [mock_choice]
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
    result = await openai_story_client.generate_story("Tell me a story.", api_key="test-key")
    assert result == "A hopeful solarpunk story."

@pytest.mark.asyncio
async def test_generate_story_error_and_retry(mocker: MockerFixture) -> None:
    """Test error and retry logic in OpenAI story client."""
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    # Fail twice, succeed on third
    async def fail_then_succeed(*args, **kwargs):
        if fail_then_succeed.counter < 2:
            fail_then_succeed.counter += 1
            raise Exception("API error")
        mock_response = mocker.MagicMock()
        mock_choice = mocker.MagicMock()
        mock_choice.message.content = "Recovered story."
        mock_response.choices = [mock_choice]
        return mock_response
    fail_then_succeed.counter = 0
    mock_openai.return_value.chat.completions.create = AsyncMock(side_effect=fail_then_succeed)
    result = await openai_story_client.generate_story("Try again.", api_key="test-key")
    assert result == "Recovered story."

@pytest.mark.asyncio
async def test_generate_story_all_failures(mocker: MockerFixture) -> None:
    """Test that all retries exhausted raises exception."""
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    mock_openai.return_value.chat.completions.create = AsyncMock(side_effect=Exception("API down"))
    with pytest.raises(Exception):
        await openai_story_client.generate_story("Fail always.", api_key="test-key") 