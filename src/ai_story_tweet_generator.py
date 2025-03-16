#!/usr/bin/env python
"""
AI Solarpunk Story Tweet Generator

This script implements the complete flow for the AI Solarpunk Story Twitter Bot:
1. Randomly selects a setting and style (or uses provided ones)
2. Generates a solarpunk micro-story with that setting
3. Optionally extracts key elements from the story to create an image prompt
4. Generates an image using that prompt with the specified style
5. Optionally posts both the story and image to Twitter
"""

import os
import random
import logging
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, NamedTuple

# Import our modules
from src.story_generator import StoryGenerator, StoryParameters
from src.image_generator import ImageGenerator, ImageParameters
from src.twitter_client import TwitterClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Available options
SETTINGS = ["urban", "coastal", "forest", "desert", "rural", "mountain", "arctic", "island"]
STYLES = ["photographic", "digital-art", "watercolor"]
FEATURES = ["story", "image", "post"]  # Can be combined

# Project root directory for saving files
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
STORIES_DIR = OUTPUT_DIR / "stories"
PREVIEW_DIR = OUTPUT_DIR / "previews"

# Ensure output directories exist
for directory in [IMAGES_DIR, STORIES_DIR, PREVIEW_DIR]:
    os.makedirs(directory, exist_ok=True)

class GenerationResult(NamedTuple):
    """Container for generation results."""
    success: bool
    story: Optional[str] = None
    story_metadata: Optional[Dict] = None
    image_path: Optional[str] = None
    image_metadata: Optional[Dict] = None
    tweet_id: Optional[str] = None
    error: Optional[str] = None

def select_random_setting() -> str:
    """Randomly select a setting from the available options."""
    return random.choice(SETTINGS)

def select_random_style() -> str:
    """Randomly select an image style from the available options."""
    return random.choice(STYLES)

def generate_story(setting: str) -> Tuple[str, Dict[str, Any]]:
    """Generate a solarpunk micro-story with the given setting."""
    logger.info(f"Generating story with setting: {setting}")
    
    try:
        # Initialize the story generator
        story_generator = StoryGenerator()
        
        # Create story parameters with the specified setting
        params = StoryParameters(setting=setting)
        
        # Generate the story
        story, metadata = story_generator.generate_story(params)
        
        # Save the story to a file
        timestamp = int(time.time())
        story_file = STORIES_DIR / f"story_{setting}_{timestamp}.txt"
        with open(story_file, 'w') as f:
            f.write(story)
        
        logger.info(f"Story generated successfully ({len(story)} characters)")
        logger.info(f"Story saved to {story_file}")
        
        return story, metadata
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise

def extract_image_prompt(story: str) -> str:
    """Extract key elements from the story to create an image prompt."""
    logger.info("Extracting image prompt from story")
    
    try:
        # Initialize a new story generator
        story_generator = StoryGenerator()
        
        # System and user prompts for extracting visual elements
        system_prompt = """
        You are an AI assistant helping to extract visual elements from a solarpunk 
        micro-story to create an image prompt. Focus on:
        1. The setting and environment
        2. Key visual elements and objects
        3. The overall mood and atmosphere
        4. Colors, lighting, and time of day
        5. Any distinctive architectural or technological features
        
        Create a concise, descriptive prompt that captures the visual essence of the story.
        The prompt should work well for digital art generation.
        """
        
        user_prompt = f"""
        Here is a solarpunk micro-story:
        
        {story}
        
        Extract the key visual elements and create a concise image generation prompt
        that captures the essence of this story. The prompt should be suitable for
        generating a digital art illustration.
        """
        
        # Use the Gemini model directly
        response = story_generator.model.generate_content(
            [system_prompt, user_prompt],
            generation_config={"temperature": 0.7, "max_output_tokens": 256}
        )
        
        # Extract the image prompt from the response
        image_prompt = response.text.strip()
        
        logger.info(f"Image prompt created: {image_prompt[:100]}...")
        return image_prompt
    except Exception as e:
        logger.error(f"Error creating image prompt: {e}")
        # Fallback to a simple prompt based on the story
        fallback_prompt = f"Solarpunk scene inspired by: {story[:150]}"
        logger.info(f"Using fallback prompt: {fallback_prompt}")
        return fallback_prompt

def generate_image(story: str, setting: str, style: str, image_prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Generate an image based on the story and optional image prompt."""
    logger.info(f"Generating image with setting: {setting}, style: {style}")
    
    try:
        # Initialize the image generator
        image_generator = ImageGenerator()
        
        # Create image parameters with specified style
        params = ImageParameters(style=style)
        
        # Prepare a save path
        timestamp = int(time.time())
        save_path = str(IMAGES_DIR / f"image_{setting}_{style}_{timestamp}.png")
        
        # Use the provided prompt or the story directly
        prompt = image_prompt if image_prompt else story
        
        # Generate the image
        images, metadata = image_generator.generate_image(
            prompt,
            setting,
            params,
            save_path=save_path
        )
        
        logger.info(f"Image generated and saved to {save_path}")
        return save_path, metadata
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise

def post_to_twitter(story: str, image_path: str) -> str:
    """Post the story and image to Twitter."""
    logger.info("Posting story and image to Twitter")
    
    try:
        # Initialize the Twitter client
        twitter_client = TwitterClient()
        
        # Upload the image
        media_id = twitter_client.upload_media(image_path)
        
        # Post the tweet with the story and image
        tweet_id = twitter_client.post_tweet(story, media_ids=[media_id])
        
        logger.info(f"Successfully posted tweet with ID: {tweet_id}")
        return tweet_id
    except Exception as e:
        logger.error(f"Error posting to Twitter: {e}")
        raise

def save_preview(result: GenerationResult) -> str:
    """Save a preview of the generation results."""
    timestamp = int(time.time())
    preview_file = PREVIEW_DIR / f"preview_{timestamp}.json"
    
    preview_data = {
        "timestamp": timestamp,
        "story": result.story,
        "story_metadata": result.story_metadata,
        "image_path": result.image_path,
        "image_metadata": result.image_metadata,
        "tweet_id": result.tweet_id,
        "error": result.error
    }
    
    with open(preview_file, 'w') as f:
        json.dump(preview_data, f, indent=2)
    
    return str(preview_file)

def run_generation(
    setting: Optional[str] = None,
    style: Optional[str] = None,
    features: Optional[List[str]] = None,
    preview_only: bool = False
) -> GenerationResult:
    """Run the complete or partial generation flow based on specified features."""
    try:
        # 1. Set defaults and validate inputs
        if not setting or setting == "random":
            setting = select_random_setting()
            logger.info(f"Randomly selected setting: {setting}")
            
        if not style or style == "random":
            style = select_random_style()
            logger.info(f"Randomly selected style: {style}")
            
        if not features:
            features = ["story", "image", "post"]
        
        result = GenerationResult(success=False)
        
        # 2. Generate story if requested
        if "story" in features:
            story, story_metadata = generate_story(setting)
            result = result._replace(
                story=story,
                story_metadata=story_metadata
            )
        
        # 3. Generate image if requested
        if "image" in features and result.story:
            # Optionally extract image prompt
            image_prompt = extract_image_prompt(result.story)
            
            # Generate image
            image_path, image_metadata = generate_image(
                result.story,
                setting,
                style,
                image_prompt
            )
            result = result._replace(
                image_path=image_path,
                image_metadata=image_metadata
            )
        
        # 4. Post to Twitter if requested and not preview only
        if "post" in features and not preview_only and result.story and result.image_path:
            tweet_id = post_to_twitter(result.story, result.image_path)
            result = result._replace(tweet_id=tweet_id)
        
        # 5. Save preview if requested
        if preview_only:
            preview_file = save_preview(result)
            logger.info(f"Preview saved to: {preview_file}")
        
        return result._replace(success=True)
        
    except Exception as e:
        error_msg = f"Error in generation flow: {str(e)}"
        logger.error(error_msg)
        return GenerationResult(success=False, error=error_msg)

def post_from_preview(preview_file: str) -> bool:
    """Post content from a previously generated preview file."""
    logger.info(f"Posting from preview file: {preview_file}")
    
    try:
        # Load the preview data
        with open(preview_file, 'r') as f:
            preview_data = json.load(f)
        
        # Verify we have the required data
        if not preview_data.get('story') or not preview_data.get('image_path'):
            raise ValueError("Preview file missing required story or image data")
            
        # Check if image file exists
        if not os.path.exists(preview_data['image_path']):
            raise FileNotFoundError(f"Image file not found: {preview_data['image_path']}")
        
        # Post to Twitter
        tweet_id = post_to_twitter(preview_data['story'], preview_data['image_path'])
        
        # Update the preview file with the tweet ID
        preview_data['tweet_id'] = tweet_id
        preview_data['posted'] = True
        preview_data['post_timestamp'] = int(time.time())
        
        with open(preview_file, 'w') as f:
            json.dump(preview_data, f, indent=2)
        
        logger.info(f"Successfully posted preview content, tweet ID: {tweet_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error posting from preview: {e}")
        return False

def main():
    """Main function to parse arguments and run the flow."""
    parser = argparse.ArgumentParser(description="AI Solarpunk Story Tweet Generator")
    parser.add_argument(
        "--setting",
        type=str,
        choices=SETTINGS + ["random"],
        default="random",
        help="Setting for the story (random by default)"
    )
    parser.add_argument(
        "--style",
        type=str,
        choices=STYLES + ["random"],
        default="digital-art",
        help="Style for the image (digital-art by default)"
    )
    parser.add_argument(
        "--features",
        type=str,
        nargs="+",
        choices=FEATURES,
        default=["story", "image", "post"],
        help="Features to include in generation"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate preview only, don't post to Twitter"
    )
    parser.add_argument(
        "--post-preview",
        type=str,
        help="Post content from a preview file"
    )
    
    args = parser.parse_args()
    
    if args.post_preview:
        success = post_from_preview(args.post_preview)
        return 0 if success else 1
    
    result = run_generation(
        setting=args.setting,
        style=args.style,
        features=args.features,
        preview_only=args.preview
    )
    
    if result.success:
        logger.info("Generation completed successfully!")
        return 0
    else:
        logger.error(f"Generation failed: {result.error}")
        return 1

if __name__ == "__main__":
    exit(main()) 