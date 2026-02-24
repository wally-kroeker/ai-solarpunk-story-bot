import pytest
from typing import Dict, Any
from src.ai_solarpunk import world_parser

class DummyAIClient:
    """Dummy AI client to mock schema extraction."""
    def __init__(self, output: Dict[str, Any]):
        self.output = output
    def call(self, document: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        return self.output

def test_validate_schema_output_valid() -> None:
    """Test that validation passes for a complete schema output."""
    schema = {"world_name": {}, "description": {}, "technology": {}}
    output = {"world_name": "Test World", "description": "A world.", "technology": ["Tech"]}
    assert world_parser.validate_schema_output(output, schema) is None

def test_validate_schema_output_missing_fields() -> None:
    """Test that validation fails if required fields are missing or empty."""
    schema = {"world_name": {}, "description": {}, "technology": {}}
    output = {"world_name": "", "description": "A world."}
    error = world_parser.validate_schema_output(output, schema)
    assert error is not None
    assert "world_name" in error and "technology" in error

def test_load_world_document(tmp_path) -> None:
    """Test loading a world document from file."""
    file_path = tmp_path / "test_world.txt"
    content = "Hello, world!"
    file_path.write_text(content, encoding="utf-8")
    loaded = world_parser.load_world_document(str(file_path))
    assert loaded == content

def test_parse_and_validate_world_document(monkeypatch) -> None:
    """Test the full parse-and-validate flow with a mocked AI call."""
    schema = {"world_name": {}, "description": {}, "technology": {}}
    output = {"world_name": "Test World", "description": "A world.", "technology": ["Tech"]}
    # Patch the AI call to return our output
    monkeypatch.setattr(world_parser, "call_ai_to_populate_schema", lambda doc, sch: output)
    # Write a dummy document
    import tempfile
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as f:
        f.write("Dummy doc")
        f.flush()
        result = world_parser.parse_and_validate_world_document(f.name, schema)
    assert result == output 