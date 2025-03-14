"""Tests for the story generation module.

This module tests the functionality of the StoryGenerator class.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

import yaml

from src.api.gemini import GeminiProClient
from src.story_generation import StoryGenerator


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Fixture providing mock configuration.
    
    Returns:
        Mock configuration dictionary
    """
    return {
        "story": {
            "max_length": 280,
            "genres": ["fantasy", "sci-fi", "mystery"],
            "prompt_template": "Generate a creative one-sentence story in the {genre} genre."
        },
        "content_filter": {
            "enabled": True,
            "inappropriate_words": ["inappropriate", "banned"]
        }
    }


@pytest.fixture
def mock_config_file(mock_config: Dict[str, Any], tmp_path: Any) -> str:
    """Fixture creating a temporary config file.
    
    Args:
        mock_config: Mock configuration dictionary
        tmp_path: Pytest fixture for temporary directory
        
    Returns:
        Path to the temporary config file
    """
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(mock_config, f)
    return str(config_file)


@pytest.fixture
def mock_gemini_client() -> MagicMock:
    """Fixture providing a mock GeminiProClient.
    
    Returns:
        Mock GeminiProClient
    """
    mock_client = MagicMock(spec=GeminiProClient)
    mock_client.retry_with_backoff.return_value = "A brave knight ventured into the dark forest, unaware of the ancient magic that awaited him."
    return mock_client


@pytest.fixture
def story_generator(mock_gemini_client: MagicMock, mock_config_file: str) -> StoryGenerator:
    """Fixture providing a StoryGenerator with mocked dependencies.
    
    Args:
        mock_gemini_client: Mock GeminiProClient
        mock_config_file: Path to mock config file
        
    Returns:
        StoryGenerator instance
    """
    return StoryGenerator(
        gemini_client=mock_gemini_client,
        config_path=mock_config_file
    )


def test_initialization(story_generator: StoryGenerator, mock_config: Dict[str, Any]) -> None:
    """Test StoryGenerator initialization.
    
    Args:
        story_generator: StoryGenerator instance
        mock_config: Mock configuration dictionary
    """
    assert story_generator.genres == mock_config["story"]["genres"]
    assert story_generator.prompt_template == mock_config["story"]["prompt_template"]
    assert story_generator.content_filter_enabled == mock_config["content_filter"]["enabled"]
    assert story_generator.inappropriate_words == set(mock_config["content_filter"]["inappropriate_words"])


def test_select_random_genre(story_generator: StoryGenerator, mock_config: Dict[str, Any]) -> None:
    """Test random genre selection.
    
    Args:
        story_generator: StoryGenerator instance
        mock_config: Mock configuration dictionary
    """
    genre = story_generator.select_random_genre()
    assert genre in mock_config["story"]["genres"]


def test_format_prompt(story_generator: StoryGenerator) -> None:
    """Test prompt formatting.
    
    Args:
        story_generator: StoryGenerator instance
    """
    prompt = story_generator.format_prompt("fantasy")
    assert "fantasy" in prompt
    assert prompt == "Generate a creative one-sentence story in the fantasy genre."


def test_clean_story(story_generator: StoryGenerator) -> None:
    """Test story cleaning.
    
    Args:
        story_generator: StoryGenerator instance
    """
    # Test quotation removal
    assert story_generator.clean_story('"Test story"') == "Test story."
    
    # Test capitalization
    assert story_generator.clean_story("test story") == "Test story."
    
    # Test punctuation
    assert story_generator.clean_story("Test story") == "Test story."
    assert story_generator.clean_story("Test story.") == "Test story."
    assert story_generator.clean_story("Test story!") == "Test story!"


def test_validate_story(story_generator: StoryGenerator) -> None:
    """Test story validation.
    
    Args:
        story_generator: StoryGenerator instance
    """
    # Valid story
    is_valid, reason = story_generator.validate_story("This is a valid story.")
    assert is_valid is True
    assert reason is None
    
    # Empty story
    is_valid, reason = story_generator.validate_story("")
    assert is_valid is False
    assert "empty" in reason.lower()
    
    # Too long story
    long_story = "x" * 300
    is_valid, reason = story_generator.validate_story(long_story)
    assert is_valid is False
    assert "length" in reason.lower()
    
    # Inappropriate content
    is_valid, reason = story_generator.validate_story("This story has inappropriate content.")
    assert is_valid is False
    assert "inappropriate" in reason.lower()


def test_generate_story(story_generator: StoryGenerator, mock_gemini_client: MagicMock) -> None:
    """Test story generation.
    
    Args:
        story_generator: StoryGenerator instance
        mock_gemini_client: Mock GeminiProClient
    """
    # Mock the validate_story method to always return valid
    with patch.object(story_generator, 'validate_story', return_value=(True, None)):
        story, genre = story_generator.generate_story("fantasy")
        
        # Check that the genre was used
        assert genre == "fantasy"
        
        # Check that the gemini client was called with the correct prompt
        mock_gemini_client.retry_with_backoff.assert_called_once()
        
        # Check that the story was cleaned and returned
        assert story == "A brave knight ventured into the dark forest, unaware of the ancient magic that awaited him."


def test_generate_story_random_genre(story_generator: StoryGenerator, mock_gemini_client: MagicMock) -> None:
    """Test story generation with random genre.
    
    Args:
        story_generator: StoryGenerator instance
        mock_gemini_client: Mock GeminiProClient
    """
    # Mock the validate_story method to always return valid
    with patch.object(story_generator, 'validate_story', return_value=(True, None)):
        with patch.object(story_generator, 'select_random_genre', return_value="mystery"):
            story, genre = story_generator.generate_story()
            
            # Check that the random genre was used
            assert genre == "mystery"


def test_generate_story_validation_failure(story_generator: StoryGenerator, mock_gemini_client: MagicMock) -> None:
    """Test story generation with validation failure.
    
    Args:
        story_generator: StoryGenerator instance
        mock_gemini_client: Mock GeminiProClient
    """
    # Mock validate_story to always fail, then succeed on the third attempt
    validation_results = [(False, "Mock failure"), (False, "Mock failure"), (True, None)]
    mock_validate = MagicMock(side_effect=validation_results)
    
    with patch.object(story_generator, 'validate_story', mock_validate):
        story, genre = story_generator.generate_story("fantasy")
        
        # Check that the story was generated after multiple attempts
        assert mock_gemini_client.retry_with_backoff.call_count == 3
        assert story == "A brave knight ventured into the dark forest, unaware of the ancient magic that awaited him."


def test_generate_story_all_validation_failures(story_generator: StoryGenerator, mock_gemini_client: MagicMock) -> None:
    """Test story generation with all validation attempts failing.
    
    Args:
        story_generator: StoryGenerator instance
        mock_gemini_client: Mock GeminiProClient
    """
    # Mock validate_story to always fail
    with patch.object(story_generator, 'validate_story', return_value=(False, "Mock failure")):
        with pytest.raises(ValueError) as excinfo:
            story_generator.generate_story("fantasy")
        
        # Check that the correct error was raised
        assert "Failed to generate a valid story" in str(excinfo.value)
        assert mock_gemini_client.retry_with_backoff.call_count == 3 