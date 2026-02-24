"""Story generation module using OpenAI o3.

This module provides functionality for generating solarpunk stories
with a positive vision of the future, sized to fit X character limits
or for longer 250-word stories with threading support.
"""

import os
import time
import logging
import re
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
from src.ai_solarpunk.clients import openai_story_client
from src.ai_solarpunk.world_parser import parse_world_document_for_stories
import asyncio
from dotenv import load_dotenv

# Import centralized error handling
from src.error_handler import (
    CentralizedErrorHandler, 
    handle_errors, 
    ErrorCategory
)

# Load environment variables from .env file
load_dotenv()

# Initialize centralized error handler
error_handler = CentralizedErrorHandler()

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

@dataclass
class WorldStoryParameters:
    """Parameters for world-based 250-word story generation with threading.
    
    Attributes:
        world_data: Parsed world document data from world_parser
        genre: Genre of the story (extracted from world_data)
        target_word_count: Exact word count target (default: 250)
        include_threading: Whether to generate threading blocks (default: True)
        include_image_prompt: Whether to generate image prompt (default: True)
        setting_elements: Optional specific elements to focus on
    """
    world_data: Dict[str, Any]
    genre: str = "solarpunk"
    target_word_count: int = 250
    include_threading: bool = True
    include_image_prompt: bool = True
    setting_elements: Optional[List[str]] = None

def build_world_story_prompt(world_data: Dict[str, Any], genre: str, setting_elements: List[str] = None) -> str:
    """Build a comprehensive prompt for world-based story generation.
    
    Args:
        world_data: Parsed world document data
        genre: Genre for the story
        setting_elements: Optional specific elements to focus on
        
    Returns:
        Formatted prompt string for story generation
    """
    # Extract story elements from world data
    story_elements = world_data.get('story_elements', {})
    genre_elements = world_data.get('genre_elements', {})
    
    # Get key world information
    world_name = story_elements.get('world_name', 'this world')
    setting = story_elements.get('setting', 'unknown location')
    characters = story_elements.get('characters', [])[:2]  # Use first two character types
    technologies = story_elements.get('technology', [])[:2]  # Use first two technologies
    theme = story_elements.get('theme', 'survival')
    plot_seed = story_elements.get('plot_seed', 'A hero emerges in times of need')
    
    # Get genre-specific elements
    aesthetic = genre_elements.get('aesthetic', 'contemporary realism')
    tech_level = genre_elements.get('tech_level', 'modern')
    conflict_type = genre_elements.get('conflict_type', 'human drama')
    
    # Build character context
    character_context = ""
    if characters:
        if len(characters) >= 2:
            character_context = f"Feature character types: {characters[0]} and {characters[1]}"
        else:
            character_context = f"Feature character type: {characters[0]}"
    
    # Build technology context
    tech_context = ""
    if technologies:
        tech_context = f"Key technologies to show: {', '.join(technologies[:3])}"
    
    # Build setting context with optional specific elements
    setting_context = f"Setting: {setting}"
    if setting_elements:
        setting_context += f" (focus on: {', '.join(setting_elements)})"
    
    prompt = f"""You are a master storyteller specializing in {genre} fiction with expertise in creating engaging, character-driven narratives.

WORLD CONTEXT:
World: {world_name}
{world_data.get('description', 'A rich, complex world with its own unique elements.')[:200]}...

{character_context}
{tech_context}
{setting_context}
Central theme: {theme}
Plot foundation: {plot_seed}

AESTHETIC GUIDANCE:
Style: {aesthetic}
Technology level: {tech_level}
Typical conflicts: {conflict_type}

TASK: Write a compelling {genre} story that:
1. Is EXACTLY 250 words (count carefully - this is critical for threading)
2. Creates vivid, relatable characters with clear motivations
3. Shows the world's unique elements through action and dialogue (don't just tell)
4. Has a clear narrative arc: setup, conflict, resolution
5. Includes sensory details and at least some dialogue
6. Demonstrates the themes and technologies naturally through the story
7. Captures the {genre} aesthetic and mood

REQUIRED OUTPUT FORMAT:

STORY:
[Write your exactly 250-word story here]

THREADING_BLOCKS:
[Break the story into Twitter-sized chunks of 250 characters or less each]
Block 1: [First 250 characters or less]
Block 2: [Next 250 characters or less]
Block 3: [Continue until complete]

IMAGE_PROMPT:
[Provide a detailed visual description for AI image generation including:
- Main character appearance, pose, and expression
- Specific setting details and atmosphere
- Key technology/elements visible in the scene
- Mood, lighting, and time of day
- Artistic style reflecting {genre} aesthetic: {aesthetic}]

Generate an engaging {genre} story that brings this world to life."""

    return prompt

class StoryGenerator:
    """Generator for solarpunk micro-stories and world-based 250-word stories using OpenAI o3/o4."""
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def __init__(self) -> None:
        """Initialize the story generator (OpenAI only)."""
        logger.info("StoryGenerator configured to use OpenAI o3/o4 provider only.")
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def generate_story(self, params: StoryParameters) -> Tuple[str, Dict[str, Any]]:
        """Generate a solarpunk micro-story based on the provided parameters using OpenAI o3."""
        try:
            prompt = (
                f"Write a solarpunk micro-story set in a {params.setting} environment. "
                f"Theme: {params.primary_tech}. "
                f"The story must be positive, hopeful, and fit within {params.max_chars} characters. "
                f"It should be suitable for a Twitter post."
            )
            logger.info("Using OpenAI o3 model for story generation.")
            
            # Generate story with AI
            story = asyncio.run(openai_story_client.generate_story(prompt))
            
            # Validate story was generated
            if not story or not isinstance(story, str):
                raise ValueError("Generated story is empty or invalid")
            
            # Truncate to fit Twitter's character limit
            if len(story) > params.max_chars:
                logger.warning(f"Story length {len(story)} exceeds max {params.max_chars}, truncating")
                story = story[:params.max_chars]
            
            metadata = {
                "setting": params.setting,
                "theme": params.primary_tech,
                "char_count": len(story),
                "timestamp": int(time.time()),
                "provider": "openai-o3"
            }
            
            logger.info(f"Successfully generated story with {len(story)} characters")
            return story, metadata
            
        except Exception as e:
            error_handler.handle_error(
                e, 
                context={
                    "operation": "story_generation",
                    "params": params.__dict__,
                    "prompt_length": len(prompt) if 'prompt' in locals() else 0
                },
                category=ErrorCategory.RECOVERABLE
            )
            # Re-raise to let decorator handle recovery
            raise
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def generate_world_story(self, params: WorldStoryParameters) -> Dict[str, Any]:
        """Generate a 250-word story with threading blocks and image prompt based on world data.
        
        Args:
            params: WorldStoryParameters containing world data and generation options
            
        Returns:
            Dictionary containing:
                - story: The generated 250-word story
                - word_count: Actual word count
                - threading_blocks: List of Twitter-sized text blocks
                - image_prompt: Detailed description for image generation
                - metadata: Generation metadata
        """
        try:
            # Build the prompt for story generation
            prompt = build_world_story_prompt(
                params.world_data, 
                params.genre, 
                params.setting_elements or []
            )
            
            logger.info(f"Generating {params.target_word_count}-word {params.genre} story from world data")
            
            # Generate the story with threading blocks and image prompt
            response_text = asyncio.run(openai_story_client.generate_story(prompt, model="o3"))
            
            # Parse the response
            story, threading_blocks, image_prompt = self._parse_story_response(response_text)
            
            # Validate and enhance the story
            word_count = len(story.split())
            
            if not self._validate_250_word_count(word_count):
                logger.warning(f"Story word count {word_count} is not exactly 250 words")
            
            # Validate threading blocks character counts
            if not self._validate_threading_blocks(threading_blocks):
                logger.warning("Threading blocks exceed character limits, auto-generating new blocks")
                threading_blocks = self._auto_generate_threads(story)
            
            # Build metadata
            metadata = {
                "world_name": params.world_data.get('world_name', 'Unknown World'),
                "genre": params.genre,
                "target_word_count": params.target_word_count,
                "actual_word_count": word_count,
                "threading_blocks_count": len(threading_blocks),
                "timestamp": int(time.time()),
                "provider": "openai-o3",
                "world_elements_used": {
                    "setting": params.world_data.get('story_elements', {}).get('setting'),
                    "characters": params.world_data.get('story_elements', {}).get('characters'),
                    "technologies": params.world_data.get('story_elements', {}).get('technology')
                }
            }
            
            result = {
                "story": story,
                "word_count": word_count,
                "threading_blocks": threading_blocks,
                "image_prompt": image_prompt,
                "metadata": metadata
            }
            
            logger.info(f"Successfully generated world story: {word_count} words, {len(threading_blocks)} threads")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                e, 
                context={
                    "operation": "world_story_generation",
                    "world_name": params.world_data.get('world_name', 'Unknown'),
                    "genre": params.genre,
                    "target_word_count": params.target_word_count
                },
                category=ErrorCategory.RECOVERABLE
            )
            raise
    
    def _parse_story_response(self, response_text: str) -> Tuple[str, List[str], str]:
        """Extract story, threading blocks, and image prompt from API response.
        
        Args:
            response_text: Raw response from the AI model
            
        Returns:
            Tuple of (story, threading_blocks, image_prompt)
        """
        # Extract the main story
        story_match = re.search(r"STORY:\s*(.*?)(?:\n\n(?:THREADING_BLOCKS:|IMAGE_PROMPT:)|\Z)", 
                               response_text, re.DOTALL)
        story = story_match.group(1).strip() if story_match else ""
        
        # Extract threading blocks
        threading_blocks = []
        threading_section = re.search(r"THREADING_BLOCKS:(.*?)(?:\n\n(?:IMAGE_PROMPT:)|\Z)", 
                                     response_text, re.DOTALL)
        if threading_section:
            block_text = threading_section.group(1)
            block_matches = re.findall(r"Block \d+:\s*(.*?)(?=\nBlock \d+:|\Z)", block_text, re.DOTALL)
            threading_blocks = [block.strip() for block in block_matches]
        
        # Extract image prompt
        image_prompt_match = re.search(r"IMAGE_PROMPT:\s*(.*?)(?:\Z)", response_text, re.DOTALL)
        image_prompt = image_prompt_match.group(1).strip() if image_prompt_match else ""
        
        return story, threading_blocks, image_prompt
    
    def _validate_250_word_count(self, word_count: int) -> bool:
        """Validate that story is exactly 250 words.
        
        Args:
            word_count: Number of words in the story
            
        Returns:
            True if word count is exactly 250
        """
        return word_count == 250
    
    def _validate_threading_blocks(self, blocks: List[str]) -> bool:
        """Validate that all threading blocks are ≤250 characters.
        
        Args:
            blocks: List of threading block strings
            
        Returns:
            True if all blocks are valid length
        """
        return all(len(block) <= 250 for block in blocks)
    
    def _auto_generate_threads(self, story: str) -> List[str]:
        """Automatically generate threading blocks of ≤250 characters each.
        
        Args:
            story: The full story text to break into threads
            
        Returns:
            List of threading blocks suitable for Twitter
        """
        blocks = []
        remaining_text = story
        
        while remaining_text:
            # If remaining text fits in one block, add it
            if len(remaining_text) <= 250:
                blocks.append(remaining_text)
                break
                
            # Find a good breaking point near 250 characters
            break_point = 250
            
            # Try to break at sentence end first
            while break_point > 150:  # Don't go below 150 to avoid tiny blocks
                if (break_point < len(remaining_text) and 
                    remaining_text[break_point] in ['.', '!', '?'] and 
                    break_point + 1 < len(remaining_text) and
                    remaining_text[break_point + 1].isspace()):
                    break_point += 1  # Include the space after punctuation
                    break
                break_point -= 1
                
            # If no good sentence break found, try breaking at word boundary
            if break_point <= 150:
                break_point = 250
                while break_point > 0 and break_point < len(remaining_text):
                    if remaining_text[break_point].isspace():
                        break
                    break_point -= 1
                    
            # If still no good break found, just break at 250
            if break_point <= 0:
                break_point = min(250, len(remaining_text))
                
            blocks.append(remaining_text[:break_point].strip())
            remaining_text = remaining_text[break_point:].strip()
            
        return blocks


@handle_errors(
    category=ErrorCategory.RECOVERABLE
)
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
            error_handler.handle_error(
                e,
                context={
                    "operation": "test_story_generation",
                    "setting": setting,
                    "story_index": i
                },
                category=ErrorCategory.WARNING
            )
            logger.error(f"Error generating story with {setting} setting: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("Solarpunk Story Generator - Testing Tool")
    print("========================================")
    print("Usage: uv run src/story_generator.py [setting|all]")
    print("Available settings: urban, coastal, forest, desert, rural")
    print("If no setting is specified, all settings will be tested.")
    
    generate_test_stories() 