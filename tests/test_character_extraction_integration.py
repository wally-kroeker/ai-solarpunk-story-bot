import os
import pytest
from pathlib import Path
from typing import TYPE_CHECKING
from src.ai_solarpunk.continuity import ContinuityManager
from src.ai_solarpunk.character_extraction import extract_and_update_character_sync

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

def api_keys_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

@pytest.mark.skipif(not api_keys_available(), reason="OPENAI_API_KEY not set")
def test_character_extraction_and_continuity(tmp_path: Path) -> None:
    """Integration test for character extraction and continuity update."""
    # Setup continuity manager with a temp file
    continuity_path = tmp_path / "continuity.json"
    cm = ContinuityManager(str(continuity_path))
    era_id = 0
    # Sample story introducing a new character
    story1 = (
        "In the grassroots lab, Dr. Mira Sol adjusted the prototype Presence Pod. "
        "Her hands trembled with excitement as the device hummed to life, "
        "casting soft light across her hopeful face."
    )
    # Extract and update continuity
    char1 = extract_and_update_character_sync(story1, era_id, cm)
    assert char1 is not None, "Character extraction failed for new character"
    # Check character is in continuity
    all_chars = cm.get_all_characters()
    assert any(c.name == char1.name for c in all_chars), "Character not added to continuity"
    # Check story event is logged
    history = cm.get_character_history(char1.name)
    assert history, "No story event logged for new character"
    # Follow-up story for the same character
    story2 = (
        f"After her breakthrough, {char1.name} faced skepticism from the city council. "
        "She stood firm, her resolve shining as brightly as the Pod's gentle glow."
    )
    char2 = extract_and_update_character_sync(story2, era_id, cm, existing_character_name=char1.name)
    assert char2 is not None, "Character extraction failed for existing character"
    # Check history is updated
    history2 = cm.get_character_history(char1.name)
    assert len(history2) >= 2, "Character history not updated after follow-up story"
    # Clean up
    try:
        os.remove(continuity_path)
    except Exception:
        pass 