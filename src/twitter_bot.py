#!/usr/bin/env python
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
    from src.story_generator import StoryGenerator, StoryParameters, WorldStoryParameters
    from src.image_generator import ImageGenerator, ImageParameters
    from src.twitter_client import TwitterClient
    from src.ai_solarpunk.world_parser import parse_world_document_for_stories
    from src.ai_solarpunk.story_to_image import convert_story_to_image_prompt
    # Import centralized error handling
    from src.error_handler import (
        error_handler, 
        handle_errors,
        ErrorCategory, 
        ErrorSeverity,
        logger as error_logger
    )
    # Import safe file operations
    from src.validation import safe_write_json
except ImportError:
    from story_generator import StoryGenerator, StoryParameters, WorldStoryParameters
    from image_generator import ImageGenerator, ImageParameters
    from twitter_client import TwitterClient
    from ai_solarpunk.world_parser import parse_world_document_for_stories
    from ai_solarpunk.story_to_image import convert_story_to_image_prompt
    # Import centralized error handling
    from error_handler import (
        error_handler, 
        handle_errors,
        ErrorCategory, 
        ErrorSeverity,
        logger as error_logger
    )
    # Import safe file operations
    from validation import safe_write_json

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
    
    @handle_errors(
        category=ErrorCategory.CRITICAL,
        severity=ErrorSeverity.HIGH,
        user_message="Failed to initialize Twitter bot. Please check API credentials and network connectivity."
    )
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
            error_context = {
                'initialization_stage': 'twitter_bot_init',
                'error_type': type(e).__name__
            }
            
            error_result = error_handler.handle_error(
                error=e,
                context=error_context,
                category=ErrorCategory.CRITICAL,
                severity=ErrorSeverity.HIGH,
                user_message="Failed to initialize Twitter bot. Please check API credentials and network connectivity."
            )
            
            logger.error(f"Twitter bot initialization failed: {error_result['error_id']}")
            raise
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE,
        severity=ErrorSeverity.MEDIUM,
        user_message="Post generation encountered an error. Attempting recovery with fallback options."
    )
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
                ai_role="collaborative"
            )
            
            story_text, story_metadata = self.story_generator.generate_story(story_params)
            
            # Generate a timestamp for filenames
            timestamp = int(time.time())
            
            # Save the story to file using safe file operations
            story_path = STORY_OUTPUT_DIR / f"{setting}_{timestamp}.txt"
            try:
                with open(story_path, 'w') as f:
                    f.write(story_text)
                logger.info(f"Story saved to {story_path}")
            except Exception as file_error:
                error_context = {
                    'operation': 'story_file_save',
                    'file_path': str(story_path),
                    'setting': setting,
                    'timestamp': timestamp
                }
                
                error_result = error_handler.handle_error(
                    error=file_error,
                    context=error_context,
                    category=ErrorCategory.FILE_IO,
                    severity=ErrorSeverity.MEDIUM,
                    user_message="Failed to save story file. Story will be available in memory."
                )
                
                logger.warning(f"Story file save failed: {error_result['error_id']}")
                # Continue without saving file - story is still in memory
            
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
            try:
                images, image_metadata = self.image_generator.generate_image(
                    story=story_text,
                    setting=setting,
                    params=image_params,
                    save_path=str(image_path)
                )
                
                logger.info(f"Image saved to {image_path}")
            except Exception as image_error:
                error_context = {
                    'operation': 'image_generation',
                    'image_path': str(image_path),
                    'setting': setting,
                    'style': style,
                    'story_length': len(story_text)
                }
                
                error_result = error_handler.handle_error(
                    error=image_error,
                    context=error_context,
                    category=ErrorCategory.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    user_message="Image generation failed. Post will continue with text only."
                )
                
                logger.warning(f"Image generation failed: {error_result['error_id']}")
                # Set default values for failed image generation
                images = []
                image_metadata = {"error": "Image generation failed", "error_id": error_result['error_id']}
                image_path = None
            
            # Combine metadata
            post_data = {
                "story": story_text,
                "image_path": str(image_path) if image_path else None,
                "setting": setting,
                "style": style,
                "themes": themes,
                "timestamp": timestamp,
                "story_metadata": story_metadata,
                "image_metadata": image_metadata,
                "posted": False,
                "tweet_id": None
            }
            
            # Save the post data using safe file operations
            post_path = POST_OUTPUT_DIR / f"post_{timestamp}.json"
            try:
                # Convert any non-serializable objects to strings
                serializable_post_data = self._make_json_serializable(post_data)
                
                success = safe_write_json(
                    data=serializable_post_data,
                    file_path=str(post_path),
                    backup_enabled=True
                )
                
                if success:
                    logger.info(f"Post data saved to {post_path}")
                else:
                    logger.warning(f"Failed to save post data to {post_path}")
                    
            except Exception as post_save_error:
                error_context = {
                    'operation': 'post_data_save',
                    'file_path': str(post_path),
                    'timestamp': timestamp
                }
                
                error_result = error_handler.handle_error(
                    error=post_save_error,
                    context=error_context,
                    category=ErrorCategory.FILE_IO,
                    severity=ErrorSeverity.LOW,
                    user_message="Failed to save post metadata. Post generation completed successfully."
                )
                
                logger.warning(f"Post data save failed: {error_result['error_id']}")
                # Continue without saving metadata - post data is still in memory
            
            # Store in post history
            self.post_history.append(post_data)
            
            return post_data
            
        except Exception as e:
            error_context = {
                'operation': 'generate_post',
                'setting': setting,
                'style': style,
                'themes': themes,
                'error_type': type(e).__name__
            }
            
            error_result = error_handler.handle_error(
                error=e,
                context=error_context,
                category=ErrorCategory.RECOVERABLE,
                severity=ErrorSeverity.MEDIUM,
                user_message="Post generation encountered an error. Attempting recovery with fallback options."
            )
            
            logger.error(f"Post generation failed: {error_result['error_id']}")
            raise
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE,
        severity=ErrorSeverity.MEDIUM,
        user_message="World-based post generation encountered an error. Attempting recovery with fallback options."
    )
    def generate_world_post(
        self, 
        world_document_path: str,
        story_mode: str = "extended",  # "micro" or "extended"
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete post using world document context.
        
        Args:
            world_document_path: Path to the world document (e.g., examples/worlds/StillPoint.md)
            story_mode: "micro" for 280-char Twitter posts, "extended" for 250-word stories with threading
            style: Optional image style override (photographic, digital-art, watercolor)
            
        Returns:
            Dictionary with post data including story, image, threading blocks, and metadata
        """
        # Available image styles
        available_styles = ["photographic", "digital-art", "watercolor", "stylized", "solarpunk-nouveau"]
        
        # Select random style if not specified
        if not style:
            style = random.choice(available_styles)
        
        try:
            # Parse the world document
            logger.info(f"Loading world document: {world_document_path}")
            world_data = parse_world_document_for_stories(world_document_path)
            
            genre = world_data.get('genre', 'solarpunk').lower()
            world_name = world_data.get('world_name', 'Unknown World')
            
            logger.info(f"World loaded: {world_name} (genre: {genre})")
            
            # Generate timestamp for filenames
            timestamp = int(time.time())
            
            if story_mode == "extended":
                # Generate 250-word story with threading blocks
                logger.info("Generating 250-word story with threading blocks")
                
                world_params = WorldStoryParameters(
                    world_data=world_data,
                    genre=genre,
                    target_word_count=250,
                    include_threading=True,
                    include_image_prompt=True
                )
                
                # Use the new world-based story generation
                story_result = self.story_generator.generate_world_story(world_params)
                
                if story_result is None:
                    raise Exception("Failed to generate world story - received None result")
                
                story_text = story_result['story']
                threading_blocks = story_result.get('threading_blocks', [])
                ai_image_prompt = story_result.get('image_prompt', '')
                
                # Also generate story-to-image conversion for enhanced prompts
                story_image_prompt = convert_story_to_image_prompt(
                    story_text, 
                    genre=genre,
                    world_data=world_data
                )
                
                # Combine AI-generated and story-extracted prompts
                combined_prompt = f"{ai_image_prompt} {story_image_prompt}"
                
                logger.info(f"Generated story: {len(story_text)} characters")
                logger.info(f"Threading blocks: {len(threading_blocks)}")
                
            else:
                # Generate micro-story for direct Twitter posting
                logger.info("Generating micro-story for Twitter")
                
                # Use traditional generation but with world context
                story_elements = world_data.get('story_elements', {})
                themes = story_elements.get('themes', ['sustainability', 'community', 'technology'])
                
                story_params = StoryParameters(
                    max_chars=280,
                    themes=themes[:3],  # Limit to 3 themes
                    setting=world_data.get('environments', ['urban'])[0],
                    ai_role="collaborative"
                )
                
                story_text, story_metadata = self.story_generator.generate_story(story_params)
                threading_blocks = []
                
                # Generate image prompt from the micro-story
                combined_prompt = convert_story_to_image_prompt(
                    story_text,
                    genre=genre,
                    world_data=world_data
                )
            
            # Save the story to file
            story_filename = f"world_{genre}_{story_mode}_{timestamp}.txt"
            story_path = STORY_OUTPUT_DIR / story_filename
            
            try:
                with open(story_path, 'w') as f:
                    f.write(story_text)
                    if threading_blocks:
                        f.write(f"\n\n--- Threading Blocks ---\n")
                        for i, block in enumerate(threading_blocks, 1):
                            f.write(f"{i}. {block}\n")
                logger.info(f"Story saved to {story_path}")
            except Exception as file_error:
                logger.warning(f"Story file save failed: {file_error}")
            
            # Generate an image using the enhanced prompt
            logger.info(f"Generating image with style: {style}")
            
            image_params = ImageParameters(
                style=style,
                samples=1,
                add_watermark=True
            )
            
            # Create a path for the image
            image_filename = f"world_{genre}_{style}_{timestamp}.png"
            image_path = IMAGE_OUTPUT_DIR / image_filename
            
            # Generate and save the image using the combined prompt
            try:
                images, image_metadata = self.image_generator.generate_image(
                    story=combined_prompt,  # Use enhanced prompt instead of story text
                    parameters=image_params,
                    save_path=str(image_path)
                )
                
                logger.info(f"Image generated and saved to {image_path}")
                
                # Verify the image was created
                if image_path.exists():
                    image_url = str(image_path)
                else:
                    image_url = None
                    logger.warning("Image file was not found after generation")
                    
            except Exception as image_error:
                error_context = {
                    'operation': 'image_generation', 
                    'world_document': world_document_path,
                    'genre': genre,
                    'style': style,
                    'prompt_length': len(combined_prompt)
                }
                
                error_result = error_handler.handle_error(
                    error=image_error,
                    context=error_context,
                    category=ErrorCategory.RECOVERABLE,
                    severity=ErrorSeverity.MEDIUM,
                    user_message="Image generation failed. Continuing with story-only post."
                )
                
                logger.error(f"Image generation failed: {error_result['error_id']}")
                image_url = None
                image_metadata = {}
            
            # Create post data
            post_data = {
                "story": story_text,
                "image_url": image_url,
                "story_mode": story_mode,
                "world_info": {
                    "world_name": world_name,
                    "genre": genre,
                    "document_path": world_document_path
                },
                "threading_blocks": threading_blocks,
                "image_prompt": combined_prompt,
                "metadata": {
                    "timestamp": timestamp,
                    "story_path": str(story_path),
                    "image_path": str(image_path) if image_path else None,
                    "style": style,
                    "word_count": len(story_text.split()),
                    "char_count": len(story_text),
                    "world_data": world_data
                }
            }
            
            # Store in post history
            self.post_history.append(post_data)
            
            # Save post data to file using safe operations
            post_filename = f"world_post_{genre}_{story_mode}_{timestamp}.json"
            post_path = POST_OUTPUT_DIR / post_filename
            
            try:
                serializable_data = self._make_json_serializable(post_data)
                safe_write_json(serializable_data, str(post_path))
                logger.info(f"Post data saved to {post_path}")
            except Exception as json_error:
                logger.warning(f"Post data save failed: {json_error}")
            
            logger.info("World-based post generation completed successfully")
            return post_data
        
        except Exception as e:
            error_context = {
                'operation': 'world_post_generation',
                'world_document_path': world_document_path,
                'story_mode': story_mode,
                'style': style
            }
            
            error_result = error_handler.handle_error(
                error=e,
                context=error_context,
                category=ErrorCategory.RECOVERABLE,
                severity=ErrorSeverity.MEDIUM,
                user_message="World-based post generation encountered an error. Attempting recovery with fallback options."
            )
            
            logger.error(f"World-based post generation failed: {error_result['error_id']}")
            raise
    
    @handle_errors(
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        user_message="Failed to post to Twitter. Please check network connectivity and API credentials."
    )
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
            image_path = post_data.get("image_path")
            
            # Upload the image to Twitter if available
            media_id = None
            if image_path and os.path.exists(image_path):
                try:
                    logger.info(f"Uploading image to Twitter: {image_path}")
                    media_id = self.twitter_client.upload_media(image_path)
                except Exception as media_error:
                    error_context = {
                        'operation': 'twitter_media_upload',
                        'image_path': image_path,
                        'story_length': len(story_text)
                    }
                    
                    error_result = error_handler.handle_error(
                        error=media_error,
                        context=error_context,
                        category=ErrorCategory.NETWORK,
                        severity=ErrorSeverity.MEDIUM,
                        user_message="Image upload to Twitter failed. Posting text only."
                    )
                    
                    logger.warning(f"Media upload failed: {error_result['error_id']}")
                    media_id = None
            
            # Post the tweet
            logger.info("Posting tweet to Twitter")
            tweet_data = self.twitter_client.post_tweet(
                text=story_text,
                media_ids=[media_id] if media_id else None
            )
            
            # Update post data with tweet information
            post_data.update({
                "posted": True,
                "tweet_id": tweet_data.get("id"),
                "tweet_url": f"https://twitter.com/user/status/{tweet_data.get('id')}" if tweet_data.get('id') else None,
                "posted_at": datetime.now().isoformat()
            })
            
            logger.info(f"Successfully posted tweet with ID: {tweet_data.get('id')}")
            
            return {
                "success": True,
                "tweet_data": tweet_data,
                "post_data": post_data
            }
            
        except Exception as e:
            error_context = {
                'operation': 'post_to_twitter',
                'has_image': bool(post_data and post_data.get('image_path')),
                'story_length': len(post_data['story']) if post_data else 0,
                'error_type': type(e).__name__
            }
            
            error_result = error_handler.handle_error(
                error=e,
                context=error_context,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                user_message="Failed to post to Twitter. Please check network connectivity and API credentials."
            )
            
            logger.error(f"Twitter posting failed: {error_result['error_id']}")
            raise
    
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