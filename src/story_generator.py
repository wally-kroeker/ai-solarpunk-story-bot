"""Story generation module using OpenAI o3.

This module provides functionality for generating solarpunk stories
with a positive vision of the future, sized to fit X character limits.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
from src.ai_solarpunk.clients import openai_story_client
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# X (Twitter) character limits
X_FREE_CHAR_LIMIT = 280

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class StoryParameters:
    """Parameters for story generation.
    
    Attributes:
        max_chars: Maximum characters allowed in the story (default: X_FREE_CHAR_LIMIT)
        setting: Environmental setting for the story (default: "urban")
        primary_tech: The single primary eco-tech or practice for the story
        themes: Optional list of themes for the story (kept for potential compatibility, but primary_tech is preferred)
        ai_role: Optional AI role for the story (default: None)
        secondary_theme: Optional secondary cross-cutting theme.
    """
    max_chars: int = 280 # Note: Prompt now requests <=240, this acts as an upper limit.
    setting: str = "urban"
    primary_tech: str = "sustainability" # Default primary tech
    themes: Optional[List[str]] = None # Kept for potential compatibility
    ai_role: Optional[str] = None
    secondary_theme: Optional[str] = None


class StoryGenerator:
    """Generator for solarpunk micro-stories using OpenAI o3 only."""
    
    def __init__(self) -> None:
        """Initialize the story generator (OpenAI only)."""
        logger.info("StoryGenerator configured to use OpenAI o3 provider only.")
    
    def generate_story(self, params: StoryParameters) -> Tuple[str, Dict[str, Any]]:
        """Generate a solarpunk micro-story based on the provided parameters using OpenAI o3."""
        prompt = (
            f"Write a solarpunk micro-story set in a {params.setting} environment. "
            f"Theme: {params.primary_tech}. "
            f"The story must be positive, hopeful, and fit within {params.max_chars} characters. "
            f"It should be suitable for a Twitter post."
        )
        logger.info("Using OpenAI o3 model for story generation.")
        story = asyncio.run(openai_story_client.generate_story(prompt))
        # Truncate to fit Twitter's character limit
        if len(story) > params.max_chars:
            story = story[:params.max_chars]
        metadata = {
            "setting": params.setting,
            "theme": params.primary_tech,
            "char_count": len(story),
            "timestamp": int(time.time()),
            "provider": "openai-o3"
        }
        return story, metadata


def generate_test_stories() -> None:
    """Generate sample stories with various settings for testing."""
    # Initialize the generator
    generator = StoryGenerator()
    
    # Create parameters for different types of stories
    settings = ["urban", "coastal", "forest", "desert", "rural"]
    themes_list = [
        ["renewable energy", "community gardens", "localized production"],
        ["ocean conservation", "floating communities", "tidal energy"],
        ["forest stewardship", "ecological monitoring", "natural architecture"],
        ["water conservation", "solar power", "desert greening"],
        ["sustainable agriculture", "community ownership", "appropriate technology"]
    ]
    
    for i, (setting, themes) in enumerate(zip(settings, themes_list)):
        try:
            # Test with a single setting
            if len(sys.argv) > 1 and sys.argv[1] not in ["all", setting]:
                continue
                
            # Generate a story with specific parameters
            params = StoryParameters(
                max_chars=280,
                setting=setting,
                primary_tech=themes[0]
            )
            
            logger.info(f"Generating story {i+1}/{len(settings)}: {setting} setting")
            story, metadata = generator.generate_story(params)
            
            # Display the generated story
            print("\n" + "="*80)
            print(f"SOLARPUNK MICRO-STORY - {setting.upper()} SETTING")
            print("="*80)
            print(story)
            print("-"*80)
            print(f"Character count: {len(story)}/280 | Setting: {setting}")
            print(f"Theme: {themes[0]}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error generating story with {setting} setting: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("Solarpunk Story Generator - Testing Tool")
    print("========================================")
    print("Usage: uv run src/story_generator.py [setting|all]")
    print("Available settings: urban, coastal, forest, desert, rural")
    print("If no setting is specified, all settings will be tested.")
    
    generate_test_stories() 