import pytest
import asyncio
from typing import TYPE_CHECKING
from pytest_mock.plugin import MockerFixture
from _pytest.logging import LogCaptureFixture
from pathlib import Path
from unittest.mock import AsyncMock

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch

import src.ai_solarpunk.clients.openai_image_client as openai_image_client

@pytest.mark.asyncio
async def test_generate_image_success(mocker: MockerFixture, tmp_path: Path, caplog: LogCaptureFixture) -> None:
    """Test successful image generation with OpenAI client."""
    mock_response = mocker.MagicMock()
    mock_data = mocker.MagicMock()
    import base64
    image_bytes = b"fakeimagebytes"
    mock_data.b64_json = base64.b64encode(image_bytes).decode()
    mock_response.data = [mock_data]
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    mock_openai.return_value.images.generate = AsyncMock(return_value=mock_response)
    result = await openai_image_client.generate_image(
        "Draw a solarpunk city.", api_key="test-key", output_dir=tmp_path
    )
    assert result.exists()
    assert result.parent == tmp_path

@pytest.mark.asyncio
async def test_generate_image_error_and_retry(mocker: MockerFixture, tmp_path: Path) -> None:
    """Test error and retry logic in OpenAI image client."""
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    # Fail twice, succeed on third
    async def fail_then_succeed(*args, **kwargs):
        if fail_then_succeed.counter < 2:
            fail_then_succeed.counter += 1
            raise Exception("API error")
        mock_response = mocker.MagicMock()
        mock_data = mocker.MagicMock()
        import base64
        image_bytes = b"recoveredimage"
        mock_data.b64_json = base64.b64encode(image_bytes).decode()
        mock_response.data = [mock_data]
        return mock_response
    fail_then_succeed.counter = 0
    mock_openai.return_value.images.generate = AsyncMock(side_effect=fail_then_succeed)
    result = await openai_image_client.generate_image(
        "Try again.", api_key="test-key", output_dir=tmp_path
    )
    assert result.exists()

@pytest.mark.asyncio
async def test_generate_image_all_failures(mocker: MockerFixture, tmp_path: Path) -> None:
    """Test that all retries exhausted raises exception."""
    mock_openai = mocker.patch("openai.AsyncOpenAI")
    mock_openai.return_value.images.generate = AsyncMock(side_effect=Exception("API down"))
    with pytest.raises(Exception):
        await openai_image_client.generate_image(
            "Fail always.", api_key="test-key", output_dir=tmp_path
        ) 