#!/usr/bin/env python
"""Debug script for ContinuityManager."""

import traceback
import os

def test_continuity_debug():
    """Debug the ContinuityManager error."""
    print("Testing ContinuityManager...")
    
    try:
        from src.ai_solarpunk.continuity import ContinuityManager
        print("Import successful")
        
        # Test with a temporary file
        test_file = '/tmp/debug_continuity.json'
        print(f"Creating ContinuityManager with file: {test_file}")
        
        cm = ContinuityManager(test_file)
        print("ContinuityManager created successfully")
        
        # Check the safe_write_json function is imported correctly
        from src.validation import safe_write_json
        print(f"safe_write_json type: {type(safe_write_json)}")
        print(f"safe_write_json callable: {callable(safe_write_json)}")
        
        # Test saving
        print("Attempting to save...")
        save_result = cm.save()
        print(f"Save result: {save_result}")
        
        # Check if file was created
        if os.path.exists(test_file):
            print(f"File was created: {test_file}")
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"File content: {content[:200]}...")
        else:
            print("File was not created")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists('/tmp/debug_continuity.json'):
            os.remove('/tmp/debug_continuity.json')

if __name__ == "__main__":
    test_continuity_debug() 