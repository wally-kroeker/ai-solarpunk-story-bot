"""Generate a solarpunk tweet-length story.

This example script generates a solarpunk story that fits within 
X (Twitter) character limits and can be posted directly to X.

Run with:
    uv run examples/generate_tweet.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.story_generation.generator import StoryGenerator, StoryParameters

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main() -> None:
    """Generate a tweet-length solarpunk story."""
    try:
        # Initialize the story generator
        generator = StoryGenerator()
        
        # Define story parameters
        params = StoryParameters(
            max_chars=280,  # X free account limit
            themes=["urban farming", "renewable energy", "community"],
            setting="urban",
            ai_role="collaborative",
            tone="hopeful"
        )
        
        # Generate a story
        story, metadata = generator.generate_story(params)
        
        # Display results
        print("\n" + "="*80)
        print(f"SOLARPUNK MICRO-STORY ({len(story)} characters):")
        print("="*80)
        print(story)
        print("="*80)
        print(f"Character count: {len(story)}/280")
        print("="*80)
        
        # Validate the story
        is_valid, issues = generator.validate_story(story)
        if not is_valid:
            print("\nWARNING: Story has the following issues:")
            for issue in issues:
                print(f" - {issue}")
        
    except Exception as e:
        logging.error(f"Error generating story: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 