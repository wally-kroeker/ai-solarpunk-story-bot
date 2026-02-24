#!/usr/bin/env python
"""Detailed debug script for safe file operations."""

import traceback
import inspect

def test_detailed_debug():
    """Trace the exact error location."""
    print("Starting detailed debug...")
    
    # Test safe_write_json directly with validation
    from src.validation import safe_write_json, ContinuityFileValidator
    
    data = {
        "last_story_id": 0,
        "characters": [],
        "story_log": []
    }
    
    # Create validation function outside any class context
    def my_validator(test_data):
        print(f"my_validator called with: {type(test_data)}")
        try:
            is_valid, error_msg = ContinuityFileValidator._validate_top_level(test_data)
            print(f"Validation result: {is_valid}, {error_msg}")
            return is_valid, error_msg
        except Exception as e:
            print(f"Validation exception: {e}")
            return False, str(e)
    
    print(f"my_validator type: {type(my_validator)}")
    print(f"my_validator callable: {callable(my_validator)}")
    
    # Test calling the validator directly
    print("Testing validator directly...")
    direct_result = my_validator(data)
    print(f"Direct validator result: {direct_result}")
    
    # Test safe_write_json with manual parameters
    print("Testing safe_write_json with manual parameters...")
    try:
        # Inspect the safe_write_json function signature
        sig = inspect.signature(safe_write_json)
        print(f"safe_write_json signature: {sig}")
        
        result = safe_write_json(
            data=data,
            file_path="/tmp/debug_detailed.json",
            create_backup=False,
            validate_func=my_validator
        )
        print(f"safe_write_json result: {result}")
        
    except Exception as e:
        print(f"Error in safe_write_json: {e}")
        traceback.print_exc()
    
    # Now test the exact same thing but without any validation
    print("Testing safe_write_json without validation...")
    try:
        result2 = safe_write_json(
            data=data,
            file_path="/tmp/debug_detailed_no_val.json",
            create_backup=False
        )
        print(f"safe_write_json without validation result: {result2}")
        
    except Exception as e:
        print(f"Error in safe_write_json without validation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_debug() 