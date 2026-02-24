import pytest
from typing import Any
from src.ai_solarpunk import world_parser
import os

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '../../examples/worlds')

@pytest.mark.parametrize("filename", [
    "example_world.yaml",
    "example_world.json",
    "example_world.md"
])
def test_load_and_validate_example_world(filename: str) -> None:
    """Test loading and validating each example world document."""
    path = os.path.join(EXAMPLES_DIR, filename)
    schema = world_parser.WORLD_SCHEMA
    # Patch the AI call to return a mock valid schema (simulate AI extraction)
    def mock_ai_call(document: str, schema: Any) -> dict:
        # Minimal valid output for test
        return {"world_name": "Test", "description": "desc", "technology": ["Tech"], "social_structures": ["Soc"], "character_archetypes": ["Arch"], "cultures": ["Cult"], "environment": {"climate": "", "geography": "", "notable_locations": []}, "themes": ["Theme"]}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(world_parser, "call_ai_to_populate_schema", mock_ai_call)
    try:
        result = world_parser.parse_and_validate_world_document(path, schema)
        assert isinstance(result, dict)
        assert "world_name" in result
    finally:
        monkeypatch.undo()

def test_invalid_world_document(tmp_path) -> None:
    """Test that an invalid world document raises a validation error."""
    # Write a minimal invalid document
    file_path = tmp_path / "invalid_world.yaml"
    file_path.write_text("world_name: ", encoding="utf-8")
    schema = world_parser.WORLD_SCHEMA
    def mock_ai_call(document: str, schema: Any) -> dict:
        return {"description": "desc"}  # Missing required fields
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(world_parser, "call_ai_to_populate_schema", mock_ai_call)
    try:
        with pytest.raises(ValueError):
            world_parser.parse_and_validate_world_document(str(file_path), schema)
    finally:
        monkeypatch.undo() 