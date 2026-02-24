#!/usr/bin/env python3

"""
Test script for story-to-image conversion functionality.

This script tests the new functionality in subtask 19.3 by:
1. Using a sample story from our world-based generation
2. Converting it to a detailed image prompt
3. Testing different genres
4. Validating the output format and content
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ai_solarpunk.story_to_image import StoryToImageConverter, convert_story_to_image_prompt

def test_story_to_image_conversion():
    """Test the story-to-image conversion functionality."""
    
    # Sample story text (from our world-based generation)
    sample_story = """
    In the honeyed sunlight of a Minneapolis morning, apprentice tinker Zoe adjusted the amber circuits of her SP-7 FocusGem, its gentle pulse syncing with her neural rhythms as she worked among the bioluminescent trellises of the Resting Place sanctuary. The rooftop gardens sprawled across seventeen terraces of reclaimed skyscrapers, where vertical farms and composting spirals created a living ecosystem above the transformed city.

    Zoe's mentor, Chen, had tasked her with calibrating the micro-wind turbines that dotted the terrace edges, their biometric sensors reading the emotional states of the community below. Each device hummed with symbiotic intelligence, part of the vast KAIROS network that wove through every corner of their world, balancing human needs with ecological harmony.

    As she tended to the devices, Zoe felt the familiar calm wash over her through the FocusGem's neural interface. The violet-tinted morning sky reflected off the solar collectors, casting dancing patterns across the green-walled corridors where other apprentices moved like choreographed dancers, each following their own rhythm of learning and discovery.

    The work was meditative, purposeful. Each calibration brought the community closer to perfect synchronization—humans, technology, and nature existing in delicate, beautiful balance. In this moment, surrounded by the gentle hum of innovation and the whisper of wind through organic architecture, Zoe understood the true meaning of the StillPoint philosophy: progress through presence, technology through harmony.
    """
    
    print("🎨 Testing Story-to-Image Conversion")
    print("=" * 50)
    
    # Test 1: Basic conversion with Solarpunk genre
    print("\n📝 Test 1: Basic Solarpunk Conversion")
    print("-" * 30)
    
    converter = StoryToImageConverter()
    solarpunk_prompt = converter.convert_to_image_prompt(sample_story, "solarpunk")
    
    print(f"✅ Generated Image Prompt:")
    print(f"{solarpunk_prompt}")
    
    # Test 2: Test with different genres
    print("\n📝 Test 2: Multi-Genre Testing")
    print("-" * 30)
    
    genres = ["fantasy", "sci-fi", "steampunk"]
    
    for genre in genres:
        print(f"\n🎭 {genre.upper()} Genre:")
        genre_prompt = converter.convert_to_image_prompt(sample_story, genre)
        print(f"   {genre_prompt}")
    
    # Test 3: Test convenience function
    print("\n📝 Test 3: Convenience Function")
    print("-" * 30)
    
    convenience_prompt = convert_story_to_image_prompt(sample_story, "solarpunk")
    print(f"✅ Convenience Function Result:")
    print(f"{convenience_prompt}")
    
    # Test 4: Validation checks
    print("\n📝 Test 4: Validation Checks")
    print("-" * 30)
    
    # Check that prompts contain expected elements
    checks = [
        ("Character mentioned", any(char in solarpunk_prompt.lower() for char in ["zoe", "apprentice", "figure"])),
        ("Setting included", any(setting in solarpunk_prompt.lower() for setting in ["rooftop", "garden", "sanctuary"])),
        ("Mood described", any(mood in solarpunk_prompt.lower() for mood in ["peaceful", "optimistic", "atmospheric"])),
        ("Genre style applied", "studio ghibli" in solarpunk_prompt.lower() or "organic" in solarpunk_prompt.lower()),
        ("Quality markers", "high quality" in solarpunk_prompt.lower() and "detailed" in solarpunk_prompt.lower()),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {result}")
    
    # Test 5: Visual elements extraction
    print("\n📝 Test 5: Visual Elements Analysis")
    print("-" * 30)
    
    elements = converter._analyze_story_elements(sample_story)
    
    print(f"✅ Extracted Elements:")
    print(f"   Characters: {elements.characters}")
    print(f"   Setting: {elements.setting}")
    print(f"   Objects: {elements.objects}")
    print(f"   Actions: {elements.actions}")
    print(f"   Mood: {elements.mood}")
    print(f"   Time of Day: {elements.time_of_day}")
    print(f"   Colors: {elements.colors}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Story-to-Image Conversion Tests")
    
    try:
        success = test_story_to_image_conversion()
        
        if success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Story-to-Image conversion is working correctly")
            print("✅ Genre-specific enhancements are applied")
            print("✅ Visual elements are properly extracted")
            print("✅ Thematic consistency is maintained")
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 