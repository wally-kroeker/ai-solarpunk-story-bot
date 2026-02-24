#!/usr/bin/env python
"""Debug script for safe file operations."""

import traceback
from src.validation import safe_write_json

def test_debug():
    """Debug the callable error."""
    print("Starting debug test...")
    
    # Simple data
    data = {"test": "value", "number": 123}
    
    # Test without validation first
    print("Testing safe_write_json without validation...")
    result1 = safe_write_json(
        data=data,
        file_path="/tmp/debug_test1.json",
        create_backup=False
    )
    print(f"Result without validation: {result1}")
    
    # Test with a simple validation function
    print("Testing safe_write_json with simple validation...")
    def simple_validate(test_data):
        print(f"Validation function called with: {test_data}")
        return True, "OK"
    
    try:
        result2 = safe_write_json(
            data=data,
            file_path="/tmp/debug_test2.json",
            create_backup=False,
            validate_func=simple_validate
        )
        print(f"Result with simple validation: {result2}")
    except Exception as e:
        print(f"Error with simple validation: {e}")
        traceback.print_exc()
    
    # Test with ContinuityManager validation function
    print("Testing with ContinuityManager-like validation...")
    try:
        from src.validation import ContinuityFileValidator
        
        def debug_validate(data_to_validate):
            print(f"Debug validation called with type: {type(data_to_validate)}")
            try:
                # Validate top-level structure
                is_valid, error_msg = ContinuityFileValidator._validate_top_level(data_to_validate)
                print(f"Top-level validation: {is_valid}, {error_msg}")
                return is_valid, error_msg
            except Exception as e:
                print(f"Validation exception: {e}")
                return False, str(e)
        
        # Create a more continuity-like data structure
        continuity_data = {
            "last_story_id": 0,
            "characters": [],
            "story_log": []
        }
        
        result3 = safe_write_json(
            data=continuity_data,
            file_path="/tmp/debug_test3.json",
            create_backup=False,
            validate_func=debug_validate
        )
        print(f"Result with continuity validation: {result3}")
        
    except Exception as e:
        print(f"Error with continuity validation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_debug() 