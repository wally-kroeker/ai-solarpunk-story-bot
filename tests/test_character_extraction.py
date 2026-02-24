"""
Unit tests for the character extraction module.

Tests the extraction of character information from story text and
the parsing of LLM responses.
"""

from typing import TYPE_CHECKING
import pytest
from unittest.mock import AsyncMock, patch

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from src.ai_solarpunk.character_extraction import (
    parse_extraction_result,
    extract_story_summary_and_title,
    extract_character_details,
    extract_and_update_character
)
from src.ai_solarpunk.continuity import Character, ContinuityManager


class TestParseExtractionResult:
    """Test the parsing of LLM extraction results."""

    def test_parse_basic_fields(self) -> None:
        """Test parsing of basic character fields."""
        extraction_text = """Name: Maya Chen
Appearance: Asian-American woman in her 30s with paint-stained overalls
Traits: innovative, practical, community-minded
Backstory: Former urban planner who helped design the first neighborhood presence pods
Summary: Maya deployed her first community presence pod in Oakland"""
        
        result = parse_extraction_result(extraction_text)
        
        assert result['name'] == 'Maya Chen'
        assert result['appearance'] == 'Asian-American woman in her 30s with paint-stained overalls'
        assert result['traits'] == 'innovative, practical, community-minded'
        assert result['backstory'] == 'Former urban planner who helped design the first neighborhood presence pods'
        assert result['summary'] == 'Maya deployed her first community presence pod in Oakland'

    def test_parse_traits_with_brackets(self) -> None:
        """Test parsing of traits that include brackets or quotes."""
        extraction_text = """Name: Alex Rivera
Traits: ["innovative", "stubborn", "visionary"]
Backstory: Tech entrepreneur"""
        
        result = parse_extraction_result(extraction_text)
        
        assert result['name'] == 'Alex Rivera'
        assert result['traits'] == 'innovative, stubborn, visionary'
        assert result['backstory'] == 'Tech entrepreneur'

    def test_parse_empty_fields(self) -> None:
        """Test parsing when some fields are empty."""
        extraction_text = """Name: Unknown Character
Appearance: 
Traits: mysterious
Backstory: No background information available"""
        
        result = parse_extraction_result(extraction_text)
        
        assert result['name'] == 'Unknown Character'
        assert result['appearance'] == ''
        assert result['traits'] == 'mysterious'
        assert result['backstory'] == 'No background information available'

    def test_parse_malformed_input(self) -> None:
        """Test parsing of malformed input."""
        extraction_text = """This is not formatted correctly
Some random text without colons
Name Maya Chen
Appearance: Still works though"""
        
        result = parse_extraction_result(extraction_text)
        
        # Should only extract lines with colons
        assert result.get('name') is None
        assert result['appearance'] == 'Still works though'


class TestExtractStoryElements:
    """Test story element extraction functions."""

    @pytest.mark.asyncio
    async def test_extract_summary_and_title_existing_character(self) -> None:
        """Test extracting summary and title for existing character."""
        story_text = "Maya worked late into the night, calibrating the presence pod's sensors."
        character_name = "Maya Chen"
        
        mock_response = "Title: Midnight Calibration\nSummary: Maya spent the night fine-tuning her presence pod's sensor array."
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            
            title, summary = await extract_story_summary_and_title(story_text, character_name)
            
            assert title == "Midnight Calibration"
            assert summary == "Maya spent the night fine-tuning her presence pod's sensor array."
            
            # Verify the prompt included the character name
            call_args = mock_llm.call_args[0][0]
            assert character_name in call_args
            assert story_text in call_args

    @pytest.mark.asyncio
    async def test_extract_summary_and_title_new_character(self) -> None:
        """Test extracting summary and title for new character."""
        story_text = "A young engineer discovered an innovative solution to urban pollution."
        
        mock_response = "Title: The Innovation\nSummary: An engineer found a breakthrough solution for city air quality."
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            
            title, summary = await extract_story_summary_and_title(story_text)
            
            assert title == "The Innovation"
            assert summary == "An engineer found a breakthrough solution for city air quality."

    @pytest.mark.asyncio
    async def test_extract_character_details(self) -> None:
        """Test extracting detailed character information."""
        story_text = "Dr. Sarah Kim, a biomimicry researcher with silver-streaked hair, developed a new water purification system inspired by moss."
        era_id = 0
        
        # Mock the character extraction response
        char_extraction_response = """Name: Dr. Sarah Kim
Appearance: Middle-aged researcher with silver-streaked hair
Traits: scientific, innovative, nature-inspired, methodical
Backstory: A biomimicry researcher who studies natural systems to solve human problems"""
        
        # Mock the archetype selection response (using valid Era 0 archetype)
        archetype_response = "Pod Pioneer"
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            # Set up side effects for two calls
            mock_llm.side_effect = [char_extraction_response, archetype_response]
            
            result = await extract_character_details(story_text, era_id)
            
            assert result['name'] == 'Dr. Sarah Kim'
            assert result['appearance'] == 'Middle-aged researcher with silver-streaked hair'
            assert result['traits'] == 'scientific, innovative, nature-inspired, methodical'
            assert 'biomimicry researcher' in result['backstory']
            assert result['archetype'] == 'Pod Pioneer'

    @pytest.mark.asyncio
    async def test_extract_character_details_invalid_era(self) -> None:
        """Test handling of invalid era ID."""
        story_text = "A character in a story."
        era_id = 999  # Invalid era
        
        with pytest.raises(ValueError, match="Era with ID 999 not found"):
            await extract_character_details(story_text, era_id)

    @pytest.mark.asyncio
    async def test_extract_character_details_invalid_archetype(self) -> None:
        """Test handling when LLM returns invalid archetype."""
        story_text = "A character story."
        era_id = 0
        
        char_extraction_response = "Name: Test Character\nAppearance: Generic\nTraits: test\nBackstory: Test"
        invalid_archetype_response = "Invalid Archetype Name"
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = [char_extraction_response, invalid_archetype_response]
            
            result = await extract_character_details(story_text, era_id)
            
            # Should use first available archetype when invalid one is returned
            assert result['archetype'] in ['Pod Pioneer', 'Community Organizer']


class TestExtractAndUpdateCharacter:
    """Test the main character extraction and update function."""

    @pytest.mark.asyncio
    async def test_update_existing_character(self) -> None:
        """Test updating an existing character."""
        story_text = "Maya installed new sensors in the community pod."
        era_id = 0
        character_name = "Maya Chen"
        
        # Create a test continuity manager with existing character
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_continuity.json')
        continuity_manager = ContinuityManager(temp_file)
        existing_character = Character(
            name="Maya Chen",
            archetype="Pod Pioneer", 
            faction="Community Resilience Networks",
            backstory="Urban planner",
            appearance="Asian-American woman"
        )
        continuity_manager.add_character(existing_character)
        
        mock_title_summary = "Title: Sensor Installation\nSummary: Maya upgraded the community pod with new sensor technology."
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_title_summary
            
            result = await extract_and_update_character(
                story_text, era_id, continuity_manager, character_name
            )
            
            assert result == existing_character
            assert result.name == "Maya Chen"
            
            # Verify story event was added
            history = continuity_manager.get_character_history("Maya Chen")
            assert len(history) == 1
            assert history[0].title == "Sensor Installation"

    @pytest.mark.asyncio
    async def test_update_nonexistent_character(self) -> None:
        """Test trying to update a character that doesn't exist."""
        story_text = "A story about someone."
        era_id = 0
        character_name = "Nonexistent Character"
        
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_continuity.json')
        continuity_manager = ContinuityManager(temp_file)
        
        result = await extract_and_update_character(
            story_text, era_id, continuity_manager, character_name
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_new_character(self) -> None:
        """Test creating a new character from story text."""
        story_text = "Engineer Alex Rivera built the city's first vertical farm using recycled materials."
        era_id = 0
        
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_continuity.json')
        continuity_manager = ContinuityManager(temp_file)
        
        # Mock responses for title/summary extraction
        title_summary_response = "Title: First Vertical Farm\nSummary: Alex built the city's pioneering vertical farm from recycled materials."
        
        # Mock responses for character detail extraction
        char_details_response = """Name: Alex Rivera
Appearance: Young engineer with calloused hands and dirt under fingernails
Traits: resourceful, environmental, innovative, practical
Backstory: An engineer passionate about sustainable urban agriculture"""
        
        archetype_response = "Pod Pioneer"
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            # Set up the sequence of responses
            mock_llm.side_effect = [
                title_summary_response,  # For title/summary extraction
                char_details_response,   # For character details
                archetype_response       # For archetype classification
            ]
            
            result = await extract_and_update_character(
                story_text, era_id, continuity_manager
            )
            
            assert result is not None
            assert result.name == "Alex Rivera"
            assert result.archetype == "Pod Pioneer"
            assert "engineer" in result.backstory.lower()
            
            # Verify character was added to continuity
            all_characters = continuity_manager.get_all_characters()
            assert len(all_characters) == 1
            assert all_characters[0].name == "Alex Rivera"
            
            # Verify story event was added
            history = continuity_manager.get_character_history("Alex Rivera")
            assert len(history) == 1
            assert history[0].title == "First Vertical Farm"

    @pytest.mark.asyncio
    async def test_extraction_failure_handling(self) -> None:
        """Test handling of extraction failures."""
        story_text = "A story."
        era_id = 0
        
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_continuity.json')
        continuity_manager = ContinuityManager(temp_file)
        
        with patch('src.ai_solarpunk.character_extraction.generate_llm_response', new_callable=AsyncMock) as mock_llm:
            # Simulate an API failure
            mock_llm.side_effect = Exception("API Error")
            
            result = await extract_and_update_character(
                story_text, era_id, continuity_manager
            )
            
            assert result is None
            
            # Verify no characters were added
            all_characters = continuity_manager.get_all_characters()
            assert len(all_characters) == 0 