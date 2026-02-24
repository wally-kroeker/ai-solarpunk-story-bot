"""
Integration tests for the refactored prompt generation system.

Tests the integration between world data, continuity, and prompt generation.
"""

from typing import TYPE_CHECKING
import pytest
import tempfile
import os
import json

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from src.ai_story_tweet_generator import generate_story_prompt, WORLD_DATA, CONTINUITY_MANAGER
from src.ai_solarpunk.continuity import Character


class TestPromptIntegration:
    """Test the integration of world data, continuity, and prompt generation."""

    def test_generate_prompt_with_era_0(self) -> None:
        """Test prompt generation with Era 0 (Tipping Point)."""
        prompt = generate_story_prompt(era_id=0, use_existing_character=False)
        
        # Check that prompt contains Era 0 elements
        assert "Tipping Point" in prompt
        assert "Community Organizer" in prompt or "Pod Pioneer" in prompt
        assert "Prototype Presence Pods" in prompt or "Vertical Farming" in prompt
        assert "Featured technologies in this world:" in prompt
        assert "Story premise:" in prompt
        assert "Themes to explore:" in prompt
        assert "Potential conflicts:" in prompt
        assert "Write a brief solarpunk micro-story" in prompt

    def test_generate_prompt_with_era_1(self) -> None:
        """Test prompt generation with Era 1 (Extinction Burst)."""
        prompt = generate_story_prompt(era_id=1, use_existing_character=False)
        
        # Check that prompt contains Era 1 elements
        assert "Extinction Burst" in prompt
        assert "Open-Source Presence Pods" in prompt or "Data & Water Scarcity Tech" in prompt
        assert "Featured technologies in this world:" in prompt

    def test_generate_prompt_with_invalid_era(self) -> None:
        """Test that invalid era ID raises appropriate error."""
        with pytest.raises(ValueError, match="Era with ID 999 not found"):
            generate_story_prompt(era_id=999, use_existing_character=False)

    def test_generate_prompt_with_existing_character(self) -> None:
        """Test prompt generation with an existing character."""
        # Add a test character to continuity
        test_character = Character(
            name="Test Maya",
            archetype="Pod Pioneer",
            faction="Community Resilience Networks",
            backstory="Test backstory for Maya",
            appearance="Test appearance"
        )
        CONTINUITY_MANAGER.add_character(test_character)
        
        # Add a story event for this character
        CONTINUITY_MANAGER.add_story_event(
            "Test Event",
            "Test Maya did something important",
            ["Test Maya"],
            0
        )
        
        # Generate prompt with existing character
        prompt = generate_story_prompt(
            era_id=0, 
            use_existing_character=True, 
            character_name="Test Maya"
        )
        
        # Check that prompt contains character details
        assert "Test Maya" in prompt
        assert "Pod Pioneer" in prompt
        assert "Test backstory for Maya" in prompt
        assert "Test Maya did something important" in prompt
        assert "New story premise:" in prompt
        assert "Continue the story of Test Maya" in prompt

    def test_generate_prompt_with_random_existing_character(self) -> None:
        """Test prompt generation with random existing character selection."""
        # Ensure there's at least one character in continuity
        test_character = Character(
            name="Random Test Character",
            archetype="Community Organizer",
            faction="Community Resilience Networks",
            backstory="Random test backstory",
            appearance="Random test appearance"
        )
        CONTINUITY_MANAGER.add_character(test_character)
        
        # Generate prompt with random existing character
        prompt = generate_story_prompt(era_id=0, use_existing_character=True)
        
        # Should contain character-related content
        assert "Continue the story of" in prompt
        assert "Recent history:" in prompt

    def test_generate_prompt_no_existing_characters(self) -> None:
        """Test that new character prompt is generated when no characters exist."""
        # Create a temporary continuity manager with no characters
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"characters": [], "story_events": [], "last_story_id": 0}, f)
            temp_file = f.name
        
        try:
            from src.ai_solarpunk.continuity import ContinuityManager
            temp_manager = ContinuityManager(temp_file)
            
            # Temporarily replace the global manager
            original_manager = CONTINUITY_MANAGER
            import src.ai_story_tweet_generator
            src.ai_story_tweet_generator.CONTINUITY_MANAGER = temp_manager
            
            # Generate prompt - should create new character since none exist
            prompt = generate_story_prompt(era_id=0, use_existing_character=True)
            
            # Should contain new character creation elements
            assert "Create a new character who is a" in prompt
            assert "Featured technologies in this world:" in prompt
            
            # Restore original manager
            src.ai_story_tweet_generator.CONTINUITY_MANAGER = original_manager
            
        finally:
            os.unlink(temp_file)

    def test_prompt_variability(self) -> None:
        """Test that multiple prompt generations produce different content."""
        prompts = []
        for _ in range(5):
            prompt = generate_story_prompt(era_id=0, use_existing_character=False)
            prompts.append(prompt)
        
        # Check that we get some variety in prompts
        unique_prompts = set(prompts)
        assert len(unique_prompts) > 1, "Prompts should vary across generations"

    def test_era_specific_content_isolation(self) -> None:
        """Test that era-specific content doesn't leak between eras."""
        prompt_era_0 = generate_story_prompt(era_id=0, use_existing_character=False)
        prompt_era_1 = generate_story_prompt(era_id=1, use_existing_character=False)
        
        # Era 0 specific content should not appear in Era 1
        assert "Prototype Presence Pods" in prompt_era_0
        assert "Prototype Presence Pods" not in prompt_era_1
        
        # Era 1 specific content should not appear in Era 0
        assert "Open-Source Presence Pods" in prompt_era_1
        assert "Open-Source Presence Pods" not in prompt_era_0

    def test_world_data_integration(self) -> None:
        """Test that world data is properly integrated and accessible."""
        # Verify that WORLD_DATA is populated
        assert len(WORLD_DATA) >= 2, "Should have at least 2 eras"
        
        # Verify Era 0 structure
        era_0 = next((era for era in WORLD_DATA if era.id == 0), None)
        assert era_0 is not None, "Era 0 should exist"
        assert era_0.name == "Tipping Point"
        assert len(era_0.technologies) > 0
        assert len(era_0.archetypes) > 0
        assert len(era_0.plot_seeds) > 0
        
        # Verify Era 1 structure
        era_1 = next((era for era in WORLD_DATA if era.id == 1), None)
        assert era_1 is not None, "Era 1 should exist"
        assert era_1.name == "Extinction Burst"
        assert len(era_1.technologies) > 0
        assert len(era_1.archetypes) > 0
        assert len(era_1.plot_seeds) > 0

    def test_continuity_manager_integration(self) -> None:
        """Test that continuity manager is properly integrated and functional."""
        # Test that CONTINUITY_MANAGER is accessible
        assert CONTINUITY_MANAGER is not None
        
        # Test basic functionality
        initial_count = len(CONTINUITY_MANAGER.get_all_characters())
        
        test_character = Character(
            name="Integration Test Character",
            archetype="Test Archetype",
            faction="Test Faction",
            backstory="Test backstory",
            appearance="Test appearance"
        )
        
        CONTINUITY_MANAGER.add_character(test_character)
        assert len(CONTINUITY_MANAGER.get_all_characters()) == initial_count + 1
        
        # Test story event functionality
        event_id = CONTINUITY_MANAGER.add_story_event(
            "Integration Test Event",
            "Test event summary",
            ["Integration Test Character"],
            0
        )
        
        history = CONTINUITY_MANAGER.get_character_history("Integration Test Character")
        assert len(history) > 0
        assert history[-1].summary == "Test event summary"

    def test_prompt_format_consistency(self) -> None:
        """Test that generated prompts follow consistent format."""
        # Test new character prompt format
        new_char_prompt = generate_story_prompt(era_id=0, use_existing_character=False)
        
        assert "You are a solarpunk flash-fiction writer." in new_char_prompt
        assert "Goal: One tweet ≤240 characters." in new_char_prompt
        assert "Create a new character who is a" in new_char_prompt
        assert "Write a brief solarpunk micro-story" in new_char_prompt
        
        # Test existing character prompt format (if characters exist)
        characters = CONTINUITY_MANAGER.get_all_characters()
        if characters:
            existing_char_prompt = generate_story_prompt(
                era_id=0, 
                use_existing_character=True, 
                character_name=characters[0].name
            )
            
            assert "You are a solarpunk flash-fiction writer." in existing_char_prompt
            assert "Goal: One tweet ≤240 characters." in existing_char_prompt
            assert "Continue the story of" in existing_char_prompt
            assert "Write a brief solarpunk micro-story" in existing_char_prompt 