#!/usr/bin/env python3
"""
Test script for world-based 250-word story generation with threading support.

This script tests the new functionality in subtask 19.2 by:
1. Loading the StillPoint.md world document
2. Generating a 250-word story with threading blocks
3. Validating the output format and content
4. Displaying the results for manual verification
"""

import sys
import os
from pathlib import Path
import asyncio
import json

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from story_generator import StoryGenerator, WorldStoryParameters
from ai_solarpunk.world_parser import parse_world_document_for_stories

def test_world_story_generation():
    """Test the world-based story generation functionality."""
    
    print("="*80)
    print("TESTING WORLD-BASED 250-WORD STORY GENERATION")
    print("="*80)
    
    # Path to the StillPoint world document
    world_doc_path = Path(__file__).parent.parent / "examples" / "worlds" / "StillPoint.md"
    
    if not world_doc_path.exists():
        print(f"❌ ERROR: World document not found at {world_doc_path}")
        return False
    
    print(f"📄 Loading world document: {world_doc_path}")
    
    try:
        # Parse the world document
        world_data = parse_world_document_for_stories(str(world_doc_path))
        
        print(f"✅ Successfully parsed world document")
        print(f"   World: {world_data.get('world_name', 'Unknown')}")
        print(f"   Genre: {world_data.get('genre', 'Unknown')}")
        print(f"   Plot seeds: {len(world_data.get('plot_seeds', []))}")
        
        # Create story parameters
        params = WorldStoryParameters(
            world_data=world_data,
            genre=world_data.get('genre', 'solarpunk'),
            target_word_count=250,
            include_threading=True,
            include_image_prompt=True
        )
        
        print(f"\n🎯 Generating {params.target_word_count}-word {params.genre} story...")
        
        # Initialize story generator
        generator = StoryGenerator()
        
        # Generate the story
        result = generator.generate_world_story(params)
        
        # Display results
        print("\n" + "="*80)
        print("📖 GENERATED STORY")
        print("="*80)
        print(result['story'])
        
        print(f"\n📊 STORY METRICS")
        print("-"*40)
        print(f"Word count: {result['word_count']}/250")
        print(f"Threading blocks: {len(result['threading_blocks'])}")
        
        if result['word_count'] == 250:
            print("✅ Word count target achieved!")
        else:
            print(f"⚠️  Word count off by {abs(250 - result['word_count'])} words")
        
        print(f"\n🧵 THREADING BLOCKS")
        print("-"*40)
        for i, block in enumerate(result['threading_blocks'], 1):
            char_count = len(block)
            status = "✅" if char_count <= 250 else "❌"
            print(f"Block {i} ({char_count}/250 chars) {status}:")
            print(f"  {block}")
            print()
        
        print(f"🖼️  IMAGE PROMPT")
        print("-"*40)
        print(result['image_prompt'])
        
        print(f"\n📋 METADATA")
        print("-"*40)
        metadata = result['metadata']
        print(f"World: {metadata['world_name']}")
        print(f"Genre: {metadata['genre']}")
        print(f"Provider: {metadata['provider']}")
        print(f"World elements used:")
        for key, value in metadata['world_elements_used'].items():
            print(f"  {key}: {value}")
        
        # Validation summary
        print(f"\n✅ VALIDATION SUMMARY")
        print("-"*40)
        
        validations = []
        
        # Check word count
        if result['word_count'] == 250:
            validations.append("✅ Exact 250-word count")
        else:
            validations.append(f"⚠️  Word count: {result['word_count']} (target: 250)")
        
        # Check threading blocks
        all_blocks_valid = all(len(block) <= 250 for block in result['threading_blocks'])
        if all_blocks_valid:
            validations.append("✅ All threading blocks ≤250 characters")
        else:
            validations.append("❌ Some threading blocks exceed 250 characters")
        
        # Check image prompt
        if result['image_prompt'].strip():
            validations.append("✅ Image prompt generated")
        else:
            validations.append("❌ No image prompt generated")
        
        # Check story content
        if result['story'].strip():
            validations.append("✅ Story content generated")
        else:
            validations.append("❌ No story content generated")
        
        for validation in validations:
            print(validation)
        
        # Overall success
        success = (result['word_count'] == 250 and 
                  all_blocks_valid and 
                  result['image_prompt'].strip() and 
                  result['story'].strip())
        
        if success:
            print(f"\n🎉 TEST PASSED: All validation criteria met!")
            return True
        else:
            print(f"\n⚠️  TEST PARTIALLY PASSED: Some criteria not met")
            return False
        
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the test."""
    print("World-Based Story Generation Test")
    print("Testing implementation of subtask 19.2\n")
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Run the test
    success = test_world_story_generation()
    
    if success:
        print(f"\n🎉 All tests passed! World-based story generation is working correctly.")
    else:
        print(f"\n⚠️  Tests completed with some issues. Check output above for details.")

if __name__ == "__main__":
    main() 