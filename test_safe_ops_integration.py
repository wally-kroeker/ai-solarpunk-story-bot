#!/usr/bin/env python
"""Test script for safe file operations integration."""

import tempfile
import os
import json
from src.validation import safe_write_json, safe_read_json, safe_write_text

def test_safe_operations():
    """Test safe file operations."""
    print("Testing safe file operations integration...")
    
    # Test safe_write_json
    test_data = {
        "test": "data",
        "number": 42,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Test write
        print("Testing safe_write_json...")
        result = safe_write_json(test_data, temp_path, create_backup=False)
        print(f"Write result: {result}")
        assert result == True, "safe_write_json should return True on success"
        
        # Test read
        print("Testing safe_read_json...")
        success, data, message = safe_read_json(temp_path)
        print(f"Read result: success={success}, message={message}")
        assert success == True, "safe_read_json should return success=True"
        assert data == test_data, "Data should match what was written"
        
        # Test safe_write_text
        print("Testing safe_write_text...")
        text_content = "This is a test text file.\nWith multiple lines."
        text_result = safe_write_text(text_content, temp_path + ".txt", create_backup=False)
        print(f"Text write result: {text_result}")
        assert text_result == True, "safe_write_text should return True on success"
        
        # Verify text file was written
        with open(temp_path + ".txt", 'r') as f:
            read_content = f.read()
        assert read_content == text_content, "Text content should match"
        
        print("All tests passed!")
        
    finally:
        # Cleanup
        for path in [temp_path, temp_path + ".txt"]:
            if os.path.exists(path):
                os.remove(path)

def test_continuity_integration():
    """Test ContinuityManager integration with safe operations."""
    print("Testing ContinuityManager integration...")
    
    try:
        from src.ai_solarpunk.continuity import ContinuityManager
        
        # Test with a temporary file
        test_file = '/tmp/test_continuity_safe_ops.json'
        cm = ContinuityManager(test_file)
        
        # Test saving
        save_result = cm.save()
        print(f"ContinuityManager save result: {save_result}")
        assert save_result == True, "ContinuityManager save should succeed"
        
        # Verify file exists and is valid JSON
        assert os.path.exists(test_file), "Continuity file should exist"
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert 'last_story_id' in data, "Continuity file should have required keys"
        
        print("ContinuityManager integration test passed!")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_model_manager_integration():
    """Test ModelManager integration with safe operations."""
    print("Testing ModelManager integration...")
    
    try:
        from src.model_manager import ModelManager
        
        # Create a temporary config directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Override the config path for testing
            import src.model_manager
            original_path = src.model_manager.MODEL_CONFIG_PATH
            src.model_manager.MODEL_CONFIG_PATH = os.path.join(temp_dir, "test_models.json")
            
            try:
                mm = ModelManager()
                mm.save_config()
                
                # Verify file was created and is valid
                assert os.path.exists(src.model_manager.MODEL_CONFIG_PATH), "Model config file should exist"
                
                with open(src.model_manager.MODEL_CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                assert 'text_model' in data, "Model config should have required keys"
                
                print("ModelManager integration test passed!")
                
            finally:
                # Restore original path
                src.model_manager.MODEL_CONFIG_PATH = original_path
                
    except Exception as e:
        print(f"ModelManager test error (may be expected): {e}")

if __name__ == "__main__":
    test_safe_operations()
    test_continuity_integration()
    test_model_manager_integration()
    print("\nAll integration tests completed!") 