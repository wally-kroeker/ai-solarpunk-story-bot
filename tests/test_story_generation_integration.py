import os
import subprocess
import sys
from pathlib import Path
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

def api_keys_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

@pytest.mark.skipif(not api_keys_available(), reason="OPENAI_API_KEY not set")
def test_story_generation_integration(tmp_path: Path) -> None:
    """Integration test for world-data/continuity story generation via CLI."""
    script = Path("src/ai_story_tweet_generator.py")
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate a story for Era 0 with a new character
    result1 = subprocess.run([
        sys.executable, str(script),
        "--era-id", "0",
        "--output-dir", str(output_dir),
        "--features", "story",
        "--preview"
    ], capture_output=True, text=True)
    assert result1.returncode == 0, f"First generation failed: {result1.stderr}"
    preview_files = list((output_dir.parent / "previews").glob("preview_*.json"))
    assert preview_files, "No preview file generated for Era 0"
    with open(preview_files[-1], "r") as f:
        preview_data = f.read()
    assert "story" in preview_data, "Preview file missing story content"

    # 2. Generate a story for Era 1, using the same character (should use continuity)
    # Get the character name from continuity.json
    continuity_path = output_dir.parent / "continuity.json"
    assert continuity_path.exists(), "Continuity file not found after first generation"
    import json
    with open(continuity_path, "r") as f:
        continuity = json.load(f)
    assert continuity["characters"], "No characters found in continuity after first generation"
    char_name = continuity["characters"][0]["name"]

    result2 = subprocess.run([
        sys.executable, str(script),
        "--era-id", "1",
        "--output-dir", str(output_dir),
        "--features", "story",
        "--use-existing-character",
        "--character-name", char_name,
        "--preview"
    ], capture_output=True, text=True)
    assert result2.returncode == 0, f"Second generation failed: {result2.stderr}"
    preview_files2 = list((output_dir.parent / "previews").glob("preview_*.json"))
    assert len(preview_files2) >= 2, "No new preview file generated for Era 1"
    with open(preview_files2[-1], "r") as f:
        preview_data2 = f.read()
    assert "story" in preview_data2, "Preview file missing story content for Era 1"

    # Clean up
    for f in preview_files + preview_files2:
        try:
            os.remove(f)
        except Exception:
            pass
    try:
        os.remove(continuity_path)
    except Exception:
        pass 