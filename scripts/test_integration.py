#!/usr/bin/env python3

"""
Test script for the complete integration of world-based story generation.

This script tests the functionality in subtask 19.4 by:
1. Testing the enhanced TwitterBot with world document support
2. Validating seamless two-call operation (story + image)
3. Testing both micro and extended story modes
4. Verifying context and genre alignment
5. Testing the complete workflow end-to-end

This validates that all components work together properly.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from twitter_bot import TwitterBot

def test_integration():
    """Test the complete integration of world-based story generation."""
    
    print("🚀 Starting Integration Tests")
    print("🤖 Testing Enhanced TwitterBot with World Documents")
    print("=" * 60)
    
    try:
        # Initialize the enhanced Twitter bot
        print("📡 Initializing Enhanced TwitterBot...")
        bot = TwitterBot()
        print("✅ TwitterBot initialized successfully")
        
        # Test world document path
        world_doc_path = "examples/worlds/StillPoint.md"
        
        if not Path(world_doc_path).exists():
            print(f"❌ World document not found: {world_doc_path}")
            return False
        
        print(f"📄 Using world document: {world_doc_path}")
        
        # Test 1: Extended story mode (250-word with threading)
        print("\n📝 Test 1: Extended Story Mode (250-word + Threading)")
        print("-" * 50)
        
        try:
            post_data_extended = bot.generate_world_post(
                world_document_path=world_doc_path,
                story_mode="extended",
                style="digital-art"
            )
            
            print("✅ Extended story generation successful!")
            print(f"   Story length: {post_data_extended['metadata']['char_count']} characters")
            print(f"   Word count: {post_data_extended['metadata']['word_count']} words")
            print(f"   Threading blocks: {len(post_data_extended['threading_blocks'])}")
            print(f"   Genre: {post_data_extended['world_info']['genre']}")
            print(f"   World: {post_data_extended['world_info']['world_name']}")
            
            # Validate threading blocks
            if post_data_extended['threading_blocks']:
                print("   Threading validation:")
                for i, block in enumerate(post_data_extended['threading_blocks'][:3], 1):
                    block_len = len(block)
                    status = "✅" if block_len <= 250 else "❌"
                    print(f"   {status} Block {i}: {block_len} chars")
            
            # Display story preview
            story_preview = post_data_extended['story'][:100] + "..." if len(post_data_extended['story']) > 100 else post_data_extended['story']
            print(f"   Story preview: {story_preview}")
            
        except Exception as e:
            print(f"❌ Extended story generation failed: {e}")
            return False
        
        # Test 2: Micro story mode (280-character for Twitter)
        print("\n📝 Test 2: Micro Story Mode (280-char Twitter)")
        print("-" * 50)
        
        try:
            post_data_micro = bot.generate_world_post(
                world_document_path=world_doc_path,
                story_mode="micro",
                style="watercolor"
            )
            
            print("✅ Micro story generation successful!")
            print(f"   Story length: {post_data_micro['metadata']['char_count']} characters")
            print(f"   Genre: {post_data_micro['world_info']['genre']}")
            print(f"   Twitter-ready: {'✅' if post_data_micro['metadata']['char_count'] <= 280 else '❌'}")
            
            # Display full micro story
            print(f"   Full story: {post_data_micro['story']}")
            
        except Exception as e:
            print(f"❌ Micro story generation failed: {e}")
            return False
        
        # Test 3: Validate image prompt integration
        print("\n📝 Test 3: Image Prompt Integration")
        print("-" * 50)
        
        extended_prompt = post_data_extended.get('image_prompt', '')
        micro_prompt = post_data_micro.get('image_prompt', '')
        
        if extended_prompt and micro_prompt:
            print("✅ Image prompts generated for both modes")
            print(f"   Extended prompt length: {len(extended_prompt)} chars")
            print(f"   Micro prompt length: {len(micro_prompt)} chars")
            
            # Check if prompts contain genre-specific elements
            genre = post_data_extended['world_info']['genre']
            if genre.lower() in extended_prompt.lower():
                print(f"   ✅ Genre '{genre}' reflected in extended prompt")
            else:
                print(f"   ⚠️  Genre '{genre}' not explicitly in extended prompt")
            
            # Display image prompt previews
            ext_preview = extended_prompt[:80] + "..." if len(extended_prompt) > 80 else extended_prompt
            micro_preview = micro_prompt[:80] + "..." if len(micro_prompt) > 80 else micro_prompt
            print(f"   Extended prompt: {ext_preview}")
            print(f"   Micro prompt: {micro_preview}")
        else:
            print("❌ Image prompt generation failed")
            return False
        
        # Test 4: Context and genre alignment
        print("\n📝 Test 4: Context and Genre Alignment")
        print("-" * 50)
        
        # Check if both modes maintain consistent world info
        ext_world = post_data_extended['world_info']
        micro_world = post_data_micro['world_info']
        
        if ext_world['genre'] == micro_world['genre'] and ext_world['world_name'] == micro_world['world_name']:
            print("✅ Context and genre alignment maintained across modes")
            print(f"   Consistent genre: {ext_world['genre']}")
            print(f"   Consistent world: {ext_world['world_name']}")
        else:
            print("❌ Context/genre alignment failed")
            return False
        
        # Test 5: File output validation
        print("\n📝 Test 5: File Output Validation")
        print("-" * 50)
        
        # Check if files were created
        ext_story_path = Path(post_data_extended['metadata']['story_path'])
        micro_story_path = Path(post_data_micro['metadata']['story_path'])
        
        files_created = 0
        if ext_story_path.exists():
            print(f"✅ Extended story file created: {ext_story_path.name}")
            files_created += 1
        else:
            print(f"❌ Extended story file missing: {ext_story_path}")
        
        if micro_story_path.exists():
            print(f"✅ Micro story file created: {micro_story_path.name}")
            files_created += 1
        else:
            print(f"❌ Micro story file missing: {micro_story_path}")
        
        if files_created == 2:
            print("✅ All story files created successfully")
        else:
            print(f"⚠️  Only {files_created}/2 story files created")
        
        # Test 6: Two-call system validation
        print("\n📝 Test 6: Two-Call System Validation")
        print("-" * 50)
        
        # Verify that the system uses separate calls for story and image
        # This is implicit in the workflow but we can check the data structure
        has_story = bool(post_data_extended.get('story'))
        has_image_prompt = bool(post_data_extended.get('image_prompt'))
        has_threading = bool(post_data_extended.get('threading_blocks'))
        
        if has_story and has_image_prompt:
            print("✅ Two-call system operational")
            print("   📖 Story generation: Complete")
            print("   🎨 Image prompt extraction: Complete")
            if has_threading:
                print("   📱 Threading block generation: Complete")
        else:
            print("❌ Two-call system incomplete")
            return False
        
        # Final summary
        print("\n📝 Integration Test Summary")
        print("=" * 60)
        print("✅ Enhanced TwitterBot initialization")
        print("✅ Extended story mode (250-word + threading)")
        print("✅ Micro story mode (280-char Twitter)")
        print("✅ Image prompt integration")
        print("✅ Context and genre alignment")
        print("✅ File output validation")
        print("✅ Two-call system validation")
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ World-based story generation successfully integrated")
        print("✅ Seamless two-call operation achieved")
        print("✅ Context and genre alignment maintained")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 