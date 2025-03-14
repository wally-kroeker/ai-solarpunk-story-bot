"""Twitter bot module integrating story generation, image generation, and Twitter posting.

This module provides the main functionality for the AI-powered Twitter bot,
combining story generation, image generation, and Twitter posting into a
cohesive workflow.
"""

import os
import time
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta

# Import project modules
try:
    from src.story_generator import StoryGenerator, StoryParameters
    from src.image_generator import ImageGenerator, ImageParameters
    from src.twitter_client import TwitterClient
except ImportError:
    from story_generator import StoryGenerator, StoryParameters
    from image_generator import ImageGenerator, ImageParameters
    from twitter_client import TwitterClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Output directories
STORY_OUTPUT_DIR = PROJECT_ROOT / "output" / "stories"
IMAGE_OUTPUT_DIR = PROJECT_ROOT / "output" / "images"
POST_OUTPUT_DIR = PROJECT_ROOT / "output" / "posts"

# Create output directories if they don't exist
STORY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
POST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TwitterBot:
    """Twitter bot for generating and posting solarpunk stories with images."""
    
    def __init__(self) -> None:
        """Initialize the Twitter bot with story, image, and Twitter clients."""
        try:
            self.story_generator = StoryGenerator()
            self.image_generator = ImageGenerator()
            self.twitter_client = TwitterClient()
            
            # Store post history
            self.post_history: List[Dict[str, Any]] = []
            
            logger.info("Twitter bot initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize Twitter bot: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def generate_post(
        self, 
        setting: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete post with story and image.
        
        Args:
            setting: Optional setting override (urban, coastal, forest, desert, rural)
            style: Optional image style override (photographic, digital-art, watercolor)
            
        Returns:
            Dictionary with post data including story, image, and metadata
        """
        # Define available settings and image styles
        available_settings = ["urban", "coastal", "forest", "desert", "rural"]
        available_styles = ["photographic", "digital-art", "watercolor"]
        
        # Select random setting and style if not specified
        if not setting:
            setting = random.choice(available_settings)
        if not style:
            style = random.choice(available_styles)
        
        # Setting-specific themes
        themes_map = {
            "urban": ["renewable energy", "community gardens", "local production"],
            "coastal": ["ocean conservation", "floating communities", "tidal energy"],
            "forest": ["forest stewardship", "ecological monitoring", "natural architecture"],
            "desert": ["water conservation", "solar power", "desert greening"],
            "rural": ["sustainable agriculture", "community ownership", "regenerative practices"]
        }
        
        # Get themes for the selected setting
        themes = themes_map.get(setting, themes_map["urban"])
        
        try:
            # Generate a story
            logger.info(f"Generating story with setting: {setting}, themes: {themes}")
            
            story_params = StoryParameters(
                max_chars=280,  # Twitter character limit
                themes=themes,
                setting=setting,
                ai_role="collaborative",
                tone="hopeful"
            )
            
            story_text, story_metadata = self.story_generator.generate_story(story_params)
            
            # Generate a timestamp for filenames
            timestamp = int(time.time())
            
            # Save the story to file
            story_path = STORY_OUTPUT_DIR / f"{setting}_{timestamp}.txt"
            with open(story_path, 'w') as f:
                f.write(story_text)
            
            logger.info(f"Story saved to {story_path}")
            
            # Generate an image based on the story
            logger.info(f"Generating image with style: {style}")
            
            image_params = ImageParameters(
                style=style,
                samples=1,
                add_watermark=True
            )
            
            # Create a path for the image
            image_path = IMAGE_OUTPUT_DIR / f"{setting}_{style}_{timestamp}.png"
            
            # Generate and save the image
            images, image_metadata = self.image_generator.generate_image(
                story=story_text,
                setting=setting,
                params=image_params,
                save_path=str(image_path)
            )
            
            logger.info(f"Image saved to {image_path}")
            
            # Combine metadata
            post_data = {
                "story": story_text,
                "image_path": str(image_path),
                "setting": setting,
                "style": style,
                "themes": themes,
                "timestamp": timestamp,
                "story_metadata": story_metadata,
                "image_metadata": image_metadata,
                "posted": False,
                "tweet_id": None
            }
            
            # Save the post data
            post_path = POST_OUTPUT_DIR / f"post_{timestamp}.json"
            with open(post_path, 'w') as f:
                # Convert any non-serializable objects to strings
                serializable_post_data = self._make_json_serializable(post_data)
                json.dump(serializable_post_data, f, indent=2)
            
            logger.info(f"Post data saved to {post_path}")
            
            # Store in post history
            self.post_history.append(post_data)
            
            return post_data
            
        except Exception as e:
            error_msg = f"Failed to generate post: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def post_to_twitter(self, post_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post a story and image to Twitter.
        
        Args:
            post_data: Optional post data to use (if not provided, will generate a new post)
            
        Returns:
            Dictionary with tweet data including tweet ID and metadata
        """
        try:
            # Generate a new post if none provided
            if not post_data:
                post_data = self.generate_post()
            
            # Extract data from the post
            story_text = post_data["story"]
            image_path = post_data["image_path"]
            
            # Upload the image to Twitter
            logger.info(f"Uploading image to Twitter: {image_path}")
            media_id = self.twitter_client.upload_media(image_path)
            
            # Post the tweet with the image
            logger.info(f"Posting tweet with story: {story_text[:50]}...")
            tweet_data = self.twitter_client.post_tweet(
                text=story_text,
                media_ids=[media_id]
            )
            
            # Update post data with tweet information
            post_data["posted"] = True
            post_data["tweet_id"] = tweet_data["id"]
            post_data["tweet_data"] = tweet_data
            
            # Update the saved post data
            timestamp = post_data["timestamp"]
            post_path = POST_OUTPUT_DIR / f"post_{timestamp}.json"
            with open(post_path, 'w') as f:
                # Convert any non-serializable objects to strings
                serializable_post_data = self._make_json_serializable(post_data)
                json.dump(serializable_post_data, f, indent=2)
            
            logger.info(f"Tweet posted successfully! Tweet ID: {tweet_data['id']}")
            
            return tweet_data
            
        except Exception as e:
            error_msg = f"Failed to post to Twitter: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _make_json_serializable(self, data: Any) -> Any:
        """Make data JSON serializable by converting non-serializable objects to strings.
        
        Args:
            data: Data to convert
            
        Returns:
            JSON serializable data
        """
        if isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, (datetime, Path)):
            return str(data)
        elif hasattr(data, "__dict__"):
            return str(data)
        else:
            return data


# Testing functions
def test_generate_post(setting: Optional[str] = None, style: Optional[str] = None) -> Dict[str, Any]:
    """Test generating a post with story and image.
    
    Args:
        setting: Optional setting override
        style: Optional style override
        
    Returns:
        Dictionary with post data
    """
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Generate a post
        print(f"Generating post with setting: {setting or 'random'}, style: {style or 'random'}")
        post_data = bot.generate_post(setting, style)
        
        # Display results
        print("\n" + "="*80)
        print("SOLARPUNK STORY:")
        print(post_data["story"])
        print("-"*80)
        print(f"Setting: {post_data['setting']}")
        print(f"Style: {post_data['style']}")
        print(f"Image saved to: {post_data['image_path']}")
        print("="*80)
        
        return post_data
        
    except Exception as e:
        logger.error(f"Failed to test post generation: {str(e)}")
        raise


def test_post_to_twitter(setting: Optional[str] = None, style: Optional[str] = None) -> Dict[str, Any]:
    """Test posting to Twitter.
    
    Args:
        setting: Optional setting override
        style: Optional style override
        
    Returns:
        Dictionary with tweet data
    """
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Generate a post with the specified settings
        post_data = bot.generate_post(setting, style)
        
        # Display generated content
        print("\n" + "="*80)
        print("GENERATED SOLARPUNK STORY:")
        print(post_data["story"])
        print("-"*80)
        print(f"Setting: {post_data['setting']}")
        print(f"Style: {post_data['style']}")
        print(f"Image saved to: {post_data['image_path']}")
        print("="*80)
        
        # Confirm posting
        print("\nPreparing to post to Twitter...")
        confirmation = input("Post this to Twitter? (yes/no): ")
        
        if confirmation.lower() in ["yes", "y"]:
            # Post to Twitter
            tweet_data = bot.post_to_twitter(post_data)
            print(f"Posted successfully! Tweet ID: {tweet_data['id']}")
            return tweet_data
        else:
            print("Posting cancelled.")
            return {"cancelled": True}
        
    except Exception as e:
        logger.error(f"Failed to test posting to Twitter: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    print("AI-Powered Twitter Bot - Test Tool")
    print("==================================")
    
    # Check for command line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run src/twitter_bot.py [generate|post] [setting] [style]")
        print("  - generate: Generate a post without posting to Twitter")
        print("  - post: Generate a post and post it to Twitter (with confirmation)")
        print("  - setting: Optional setting (urban, coastal, forest, desert, rural)")
        print("  - style: Optional image style (photographic, digital-art, watercolor)")
        sys.exit(1)
    
    # Parse command line arguments
    command = sys.argv[1]
    
    # Get optional setting and style
    setting = sys.argv[2] if len(sys.argv) > 2 else None
    style = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate setting and style if provided
    valid_settings = ["urban", "coastal", "forest", "desert", "rural"]
    valid_styles = ["photographic", "digital-art", "watercolor"]
    
    if setting and setting not in valid_settings:
        print(f"Invalid setting: {setting}")
        print(f"Valid settings: {', '.join(valid_settings)}")
        sys.exit(1)
    
    if style and style not in valid_styles:
        print(f"Invalid style: {style}")
        print(f"Valid styles: {', '.join(valid_styles)}")
        sys.exit(1)
    
    try:
        if command == "generate":
            # Test generating a post
            test_generate_post(setting, style)
            sys.exit(0)
        
        elif command == "post":
            # Test posting to Twitter
            test_post_to_twitter(setting, style)
            sys.exit(0)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1) 