import json
import os
from unittest.mock import patch, mock_open

import pytest

from src.ai_solarpunk.continuity import (
    Character,
    Continuity,
    ContinuityManager,
    StoryEvent,
) 


def test_load_or_create_new_file():
    """Test that a new continuity file is created when none exists."""
    with patch("os.path.exists", return_value=False):
        with patch("builtins.open", mock_open()) as mock_file:
            manager = ContinuityManager("dummy_path/continuity.json")
            # The manager should create a default Continuity object
            assert manager.continuity.last_story_id == 0
            assert manager.continuity.characters == []
            assert manager.continuity.story_log == []
            # It should not try to open or write a file on initialization
            mock_file.assert_not_called()


def test_load_or_create_existing_file():
    """Test that an existing continuity file is loaded correctly."""
    mock_data = {
        "last_story_id": 1,
        "characters": [
            {
                "name": "Kael",
                "archetype": "Pod Pioneer",
                "backstory": "A former data-miner who found enlightenment.",
                "appearance": "Calm eyes, worn-out gear.",
                "faction": "Mindfulness Innovators",
                "traits": ["calm", "intuitive"],
                "story_appearances": [1],
            }
        ],
        "story_log": [
            {
                "id": 1,
                "title": "First Light",
                "summary": "Kael activates a new Pod.",
                "era": 0,
                "characters": ["Kael"],
                "timestamp": "2024-01-01T12:00:00",
            }
        ],
    }
    mock_json = json.dumps(mock_data)

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_json)) as mock_file:
            manager = ContinuityManager("dummy_path/continuity.json")
            assert manager.continuity.last_story_id == 1
            assert len(manager.continuity.characters) == 1
            assert manager.continuity.characters[0].name == "Kael"
            assert len(manager.continuity.story_log) == 1
            assert manager.continuity.story_log[0].id == 1
            mock_file.assert_called_once_with("dummy_path/continuity.json", 'r', encoding='utf-8')


def test_load_or_create_corrupted_file():
    """Test that a new continuity is created if the file is corrupted."""
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="{invalid_json}")) as mock_file:
            with patch("builtins.print") as mock_print:
                manager = ContinuityManager("dummy_path/continuity.json")
                assert manager.continuity.last_story_id == 0
                assert manager.continuity.characters == []
                assert manager.continuity.story_log == []
                mock_print.assert_called_once()


def test_save():
    """Test that the continuity data is saved correctly."""
    manager = ContinuityManager("dummy_path/continuity.json")
    manager.continuity.last_story_id = 5
    
    m = mock_open()
    with patch("os.makedirs") as mock_makedirs:
        with patch("builtins.open", m):
            manager.save()
            mock_makedirs.assert_called_once_with(os.path.dirname("dummy_path/continuity.json"), exist_ok=True)
            m.assert_called_once_with("dummy_path/continuity.json", 'w', encoding='utf-8')
            
            handle = m()
            written_data = json.loads(handle.write.call_args.args[0])
            
            assert written_data["last_story_id"] == 5


@pytest.fixture
def manager():
    """Fixture to create a clean ContinuityManager for each test."""
    with patch("os.path.exists", return_value=False):
        # Start with a fresh manager that doesn't try to load a file
        return ContinuityManager("dummy_path/continuity.json")


def test_add_and_get_character(manager: ContinuityManager):
    """Test adding a new character and retrieving them."""
    char = Character(
        name="Jora",
        archetype="Data Healer",
        backstory="Heals corrupted data streams.",
        appearance="Fingers that dance over light.",
    )
    with patch.object(manager, "save") as mock_save:
        manager.add_character(char)
        
        assert len(manager.continuity.characters) == 1
        assert manager.get_character("Jora") is not None
        assert manager.get_character("jora") is not None  # Case-insensitivity
        mock_save.assert_called_once()

        # Test adding the same character again (should not duplicate)
        manager.add_character(char)
        assert len(manager.continuity.characters) == 1


def test_add_and_get_story_event(manager: ContinuityManager):
    """Test adding a story event and retrieving it."""
    manager.add_character(Character("Roric", "a", "b", "c"))
    
    with patch.object(manager, "save") as mock_save:
        story_id = manager.add_story_event(
            title="Whispers in the Mesh",
            summary="Roric finds a hidden message.",
            characters=["Roric"],
            era=1,
        )
        
        assert story_id == 1
        assert manager.continuity.last_story_id == 1
        
        event = manager.get_story_event(1)
        assert event is not None
        assert event.title == "Whispers in the Mesh"
        
        # Check that the character's history was updated
        roric = manager.get_character("Roric")
        assert roric.story_appearances == [1]

        mock_save.assert_called() # Called by add_character and add_story_event


def test_get_character_history(manager: ContinuityManager):
    """Test retrieving the story history for a character."""
    manager.add_character(Character("Nia", "a", "b", "c"))
    manager.add_story_event("Event 1", "Nia does a thing.", ["Nia"], 0)
    manager.add_story_event("Event 2", "Another character's story.", ["Zane"], 0)
    manager.add_story_event("Event 3", "Nia returns.", ["Nia"], 1)

    history = manager.get_character_history("Nia")
    assert len(history) == 2
    assert history[0].id == 1
    assert history[1].id == 3

    # Test history for a character with no events
    manager.add_character(Character("Zane", "x", "y", "z"))
    zane_history = manager.get_character_history("Zane")
    assert len(zane_history) == 1 # From event 2

    # Test history for non-existent character
    no_history = manager.get_character_history("Unknown")
    assert no_history == [] 