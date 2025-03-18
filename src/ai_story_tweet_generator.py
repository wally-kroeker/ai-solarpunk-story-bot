#!/usr/bin/env python
"""
AI Solarpunk Story Tweet Generator

This script implements the complete flow for the AI Solarpunk Story Twitter Bot:
1. Randomly selects a setting
2. Generates a solarpunk micro-story with that setting
3. Extracts key elements from the story to create an image prompt
4. Generates an image using that prompt with digital-art style
5. Posts both the story and image to Twitter

When running as a systemd service, it uses service-specific logging and configuration.
"""

import os
import random
import logging
import logging.handlers
import time
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

# Import our modules
from src.story_generator import StoryGenerator, StoryParameters
from src.image_generator import ImageGenerator, ImageParameters
from src.twitter_client import TwitterClient

# Project root directory for saving files
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
STORIES_DIR = OUTPUT_DIR / "stories"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(STORIES_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Available settings - these should match what the story generator accepts
SETTINGS = ["urban", "coastal", "forest", "desert", "rural", "mountain", "arctic", "island"]

# Initialize logger at module level
logger = logging.getLogger(__name__)

def setup_logging(is_service: bool = False) -> None:
    """
    Configure logging based on whether we're running as a service or not.
    
    Args:
        is_service: Whether the script is running as a systemd service
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    if is_service:
        # When running as a service, log to both file and systemd journal
        log_file = LOG_DIR / "ai_story_generator.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
    else:
        # For interactive use, just log to console
        logging.basicConfig(level=logging.INFO, format=log_format)

def select_random_setting() -> str:
    """
    Randomly select a setting from the available options.
    
    Returns:
        str: Randomly selected setting
    """
    return random.choice(SETTINGS)

def generate_story(setting: str) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a solarpunk micro-story with the given setting.
    
    Args:
        setting: The setting to use for the story
        
    Returns:
        Tuple[str, Dict[str, Any]]: The generated story and metadata
    """
    logger.info(f"Generating story with setting: {setting}")
    
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

def extract_image_prompt(story: str) -> str:
    """
    Extract key elements from the story to create an image prompt.
    
    Args:
        story: The generated story text
        
    Returns:
        str: An image prompt based on the story
    """
    logger.info("Extracting image prompt from story")
    
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
    try:
        # Generate content with the prompt
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

def generate_image(story: str, setting: str, image_prompt: str) -> str:
    """
    Generate an image based on the story and image prompt.
    
    Args:
        story: The generated story
        setting: The story setting
        image_prompt: The extracted image prompt
        
    Returns:
        str: Path to the generated image
    """
    logger.info(f"Generating image with setting: {setting}")
    
    # Initialize the image generator
    image_generator = ImageGenerator()
    
    # Create image parameters with digital-art style
    params = ImageParameters(style="digital-art")
    
    # Prepare a save path
    timestamp = int(time.time())
    save_path = str(IMAGES_DIR / f"image_{setting}_{timestamp}.png")
    
    try:
        # Generate the image using the extracted prompt instead of the story
        images, metadata = image_generator.generate_image(
            image_prompt,  # Use the extracted prompt instead of the story
            setting,
            params,
            save_path=save_path  # Specify save path explicitly
        )
        
        # The image should be saved at the specified path
        logger.info(f"Image generated and saved to {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise

def post_to_twitter(story: str, image_path: str) -> bool:
    """
    Post the story and image to Twitter.
    
    Args:
        story: The generated story
        image_path: Path to the generated image
        
    Returns:
        bool: Success status
    """
    logger.info("Posting story and image to Twitter")
    
    # Initialize the Twitter client
    twitter_client = TwitterClient()
    
    try:
        # Upload the image
        media_id = twitter_client.upload_media(image_path)
        
        # Post the tweet with the story and image
        tweet_id = twitter_client.post_tweet(story, media_ids=[media_id])
        
        logger.info(f"Successfully posted tweet with ID: {tweet_id}")
        return True
    except Exception as e:
        logger.error(f"Error posting to Twitter: {e}")
        return False

def run_complete_flow(setting: Optional[str] = None) -> bool:
    """
    Run the complete flow: generate story, create image prompt,
    generate image, and post to Twitter.
    
    Args:
        setting: Optional setting to use (random if not provided)
        
    Returns:
        bool: Success status
    """
    try:
        # 1. Select a setting if not provided
        if not setting or setting == "random":
            setting = select_random_setting()
            logger.info(f"Randomly selected setting: {setting}")
        
        # 2. Generate the story
        story, story_metadata = generate_story(setting)
        
        # 3. Extract an image prompt from the story
        image_prompt = extract_image_prompt(story)
        
        # 4. Generate the image
        image_path = generate_image(story, setting, image_prompt)
        
        # 5. Post to Twitter
        success = post_to_twitter(story, image_path)
        
        return success
    except Exception as e:
        logger.error(f"Error in flow: {e}")
        return False

def main():
    """Main function to parse arguments and run the flow."""
    parser = argparse.ArgumentParser(description="AI Solarpunk Story Tweet Generator")
    parser.add_argument(
        "--setting",
        choices=SETTINGS + ["random"],
        default="random",
        help="Setting for the story (default: random)"
    )
    parser.add_argument(
        "--service",
        action="store_true",
        help="Running as a systemd service"
    )
    args = parser.parse_args()
    
    # Set up logging based on execution context
    setup_logging(args.service)
    
    try:
        success = run_complete_flow(args.setting)
        if success:
            logger.info("Flow completed successfully")
            sys.exit(0)
        else:
            logger.error("Flow failed")
            sys.exit(1)
    except Exception as e:
        logger.exception("Critical error in main flow")
        sys.exit(2)

if __name__ == "__main__":
    main() 