"""Tests for the story generation module.

This module tests the StoryGenerator class and its functionality.
"""

import os
import pytest
from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from src.story_generation.generator import StoryGenerator, StoryParameters
from src.utils.exceptions import StoryGenerationError


@pytest.fixture
def mock_generative_model(mocker: "MockerFixture") -> Any:
    """Fixture to mock the GenerativeModel class.
    
    Args:
        mocker: pytest-mock fixture
        
    Returns:
        MagicMock: Mocked GenerativeModel
    """
    mock = mocker.patch("src.story_generation.generator.GenerativeModel")
    mock_instance = mock.return_value
    
    # Setup mock response
    mock_response = mocker.MagicMock()
    mock_response.text = "Solar panels hummed as Maya and her AI assistant planned the next community garden. Together, they transformed forgotten spaces into thriving ecosystems."
    mock_instance.generate_content.return_value = mock_response
    
    return mock_instance


@pytest.fixture
def mock_aiplatform(mocker: "MockerFixture") -> Any:
    """Fixture to mock the aiplatform initialization.
    
    Args:
        mocker: pytest-mock fixture
        
    Returns:
        MagicMock: Mocked aiplatform
    """
    return mocker.patch("src.story_generation.generator.aiplatform.init")


@pytest.fixture
def mock_credential_manager(mocker: "MockerFixture") -> Any:
    """Fixture to mock the CredentialManager.
    
    Args:
        mocker: pytest-mock fixture
        
    Returns:
        MagicMock: Mocked CredentialManager
    """
    mock = mocker.patch("src.story_generation.generator.CredentialManager")
    mock_instance = mock.return_value
    mock_instance.get_gcp_credentials.return_value = {
        "project_id": "mock-project-id",
        "location": "mock-location"
    }
    return mock_instance


def test_story_generator_initialization(
    mock_aiplatform: Any,
    mock_credential_manager: Any,
    mock_generative_model: Any,
) -> None:
    """Test that StoryGenerator initializes correctly.
    
    Args:
        mock_aiplatform: Mocked aiplatform
        mock_credential_manager: Mocked CredentialManager
        mock_generative_model: Mocked GenerativeModel
    """
    generator = StoryGenerator()
    
    # Verify credentials were loaded
    mock_credential_manager.get_gcp_credentials.assert_called_once()
    
    # Verify aiplatform was initialized
    mock_aiplatform.assert_called_once_with(
        project="mock-project-id",
        location="mock-location",
    )
    
    assert generator.model == mock_generative_model


def test_create_solarpunk_prompt() -> None:
    """Test that the prompt creation includes all required elements."""
    generator = StoryGenerator()
    
    # Create parameters
    params = StoryParameters(
        max_chars=280,
        themes=["renewable energy", "community gardens"],
        characters=3,
        setting="coastal",
        ai_role="guardian",
        tone="inspiring"
    )
    
    # Generate the prompt
    prompt = generator._create_solarpunk_prompt(params)
    
    # Check for the presence of key elements
    assert "solarpunk" in prompt.lower()
    assert "280 characters" in prompt
    assert "renewable energy, community gardens" in prompt
    assert "coastal" in prompt
    assert "guardian" in prompt
    assert "inspiring" in prompt


def test_generate_story_success(
    mock_generative_model: Any,
) -> None:
    """Test successful story generation.
    
    Args:
        mock_generative_model: Mocked GenerativeModel
    """
    generator = StoryGenerator()
    
    # Generate a story
    story, metadata = generator.generate_story()
    
    # Verify the model was called
    mock_generative_model.generate_content.assert_called_once()
    
    # Check the returned story
    assert story == "Solar panels hummed as Maya and her AI assistant planned the next community garden. Together, they transformed forgotten spaces into thriving ecosystems."
    
    # Check metadata
    assert "model" in metadata
    assert "parameters" in metadata
    assert "timestamp" in metadata
    assert metadata["parameters"]["max_chars"] == 280


def test_generate_story_character_limit(
    mock_generative_model: Any,
    mocker: "MockerFixture",
) -> None:
    """Test that stories are truncated to fit character limits.
    
    Args:
        mock_generative_model: Mocked GenerativeModel
        mocker: pytest-mock fixture
    """
    generator = StoryGenerator()
    
    # Create a mock response with a story that exceeds the character limit
    long_story = "Solar panels hummed as Maya and her AI assistant planned the next community garden. " * 10
    mock_response = mocker.MagicMock()
    mock_response.text = long_story
    mock_generative_model.generate_content.return_value = mock_response
    
    # Generate a story
    story, metadata = generator.generate_story()
    
    # Check that the story was truncated
    assert len(story) <= 280
    assert metadata["parameters"]["actual_chars"] <= 280


def test_validate_story() -> None:
    """Test the story validation functionality."""
    generator = StoryGenerator()
    
    # Test a valid story
    valid_story = (
        "Solar panels hummed as Maya and her AI companion Sol worked on the community garden system. "
        "Through collaboration, they created a solution that brought people together."
    )
    
    is_valid, issues = generator.validate_story(valid_story)
    assert is_valid
    assert len(issues) == 0
    
    # Test an invalid story
    invalid_story = (
        "After the climate disaster and ecological collapse, the few survivors "
        "gathered in the ruins of the old city. The apocalypse had changed everything."
    )
    
    is_valid, issues = generator.validate_story(invalid_story)
    assert not is_valid
    assert len(issues) > 0
    assert any("disaster" in issue for issue in issues)
    assert any("apocalypse" in issue for issue in issues)
    assert any("collapse" in issue for issue in issues)


@pytest.mark.skip(reason="This test calls the actual API and should be run manually")
def test_live_story_generation() -> None:
    """Test generating a story with the actual API.
    
    This test is skipped by default and should be run manually.
    """
    generator = StoryGenerator()
    
    params = StoryParameters(
        max_chars=280,
        themes=["urban farming", "renewable energy", "community"],
        setting="urban",
        ai_role="collaborative",
        tone="hopeful"
    )
    
    story, metadata = generator.generate_story(params)
    
    # Basic checks
    assert len(story) > 0
    assert len(story) <= 280  # Ensure it fits in a tweet
    
    # Check if the story contains key themes
    assert any(theme.lower() in story.lower() for theme in params.themes)
    
    print(f"\nGenerated Story ({len(story)} chars):\n")
    print(story)
    print("\nMetadata:", metadata) 