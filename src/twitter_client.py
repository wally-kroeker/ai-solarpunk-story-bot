"""Twitter integration module for posting stories and images.

This module provides functionality for interacting with the Twitter (X) API,
including posting tweets with text and media, handling rate limits, and
implementing proper error handling and retry mechanisms.
"""

import os
import time
import logging
import json
import yaml
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

import tweepy
from PIL import Image
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TwitterClient:
    """Client for interacting with the Twitter API."""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the Twitter client with credentials from environment or config.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Load Twitter API credentials
        self._load_credentials()
        
        # Configure Tweepy client
        self._configure_client()
        
        # Track rate limits
        self.rate_limit_info = {
            "remaining_requests": self.config["api"]["twitter"]["rate_limit"]["max_requests"],
            "reset_time": time.time() + self.config["api"]["twitter"]["rate_limit"]["time_window"]
        }
        
        logger.info("Twitter client initialized successfully")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from the specified path or default location.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Dictionary containing configuration values
        """
        if not config_path:
            config_path = PROJECT_ROOT / "config" / "config.yaml"
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {str(e)}")
            logger.info("Using default configuration")
            
            # Default configuration
            return {
                "api": {
                    "twitter": {
                        "api_version": "2",
                        "rate_limit": {
                            "max_requests": 50,
                            "time_window": 900  # 15 minutes in seconds
                        }
                    }
                }
            }
    
    def _load_credentials(self) -> None:
        """Load Twitter API credentials from environment variables."""
        # Load environment variables
        load_dotenv()
        
        # Get API keys and tokens
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Validate credentials
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            error_msg = "Missing Twitter API credentials in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Twitter API credentials loaded successfully")
    
    def _configure_client(self) -> None:
        """Configure Tweepy client with credentials."""
        try:
            # Create authentication handlers
            self.oauth1_user_handler = tweepy.OAuth1UserHandler(
                self.api_key, 
                self.api_secret, 
                self.access_token, 
                self.access_token_secret
            )
            
            # Create v1 API client for media uploads
            self.api_v1 = tweepy.API(self.oauth1_user_handler)
            
            # Create v2 API client for tweets
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            
            logger.info("Twitter API clients configured successfully")
        except Exception as e:
            error_msg = f"Failed to configure Twitter API clients: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within the rate limit.
        
        Returns:
            True if we can proceed, False if we're rate-limited
        """
        current_time = time.time()
        
        # If the reset time has passed, reset the counter
        if current_time > self.rate_limit_info["reset_time"]:
            self.rate_limit_info = {
                "remaining_requests": self.config["api"]["twitter"]["rate_limit"]["max_requests"],
                "reset_time": current_time + self.config["api"]["twitter"]["rate_limit"]["time_window"]
            }
            return True
        
        # If we have remaining requests, decrement and proceed
        if self.rate_limit_info["remaining_requests"] > 0:
            self.rate_limit_info["remaining_requests"] -= 1
            return True
        
        # Otherwise, we're rate-limited
        wait_time = self.rate_limit_info["reset_time"] - current_time
        logger.warning(f"Rate limit reached. Reset in {wait_time:.2f} seconds")
        return False
    
    def _wait_for_rate_limit(self) -> None:
        """Wait for rate limit to reset if needed."""
        if not self._check_rate_limit():
            wait_time = self.rate_limit_info["reset_time"] - time.time()
            if wait_time > 0:
                logger.info(f"Waiting {wait_time:.2f} seconds for rate limit reset")
                time.sleep(wait_time + 1)  # Add 1 second buffer
    
    def upload_media(self, media_path: Union[str, Path]) -> str:
        """Upload media to Twitter.
        
        Args:
            media_path: Path to media file
            
        Returns:
            Media ID string
        """
        self._wait_for_rate_limit()
        
        try:
            # Upload media using v1 API
            media_path = Path(media_path)
            if not media_path.exists():
                raise FileNotFoundError(f"Media file not found: {media_path}")
            
            # Check file size and type
            if media_path.stat().st_size > 5 * 1024 * 1024:  # 5MB limit
                logger.warning("Media file exceeds 5MB, resizing...")
                # Resize image if it's too large
                with Image.open(media_path) as img:
                    img.thumbnail((1200, 1200))
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        tmp_path = tmp.name
                    img.save(tmp_path)
                    media_path = Path(tmp_path)
            
            # Upload the media
            media = self.api_v1.media_upload(filename=str(media_path))
            media_id = media.media_id_string
            
            logger.info(f"Media uploaded successfully with ID: {media_id}")
            
            # Clean up temporary file if created
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
                
            return media_id
        
        except Exception as e:
            error_msg = f"Failed to upload media: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def post_tweet(
        self, 
        text: str, 
        media_ids: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post a tweet with optional media and reply.
        
        Args:
            text: Tweet text
            media_ids: Optional list of media IDs to attach
            reply_to: Optional tweet ID to reply to
            
        Returns:
            Dictionary with tweet data
        """
        self._wait_for_rate_limit()
        
        try:
            # Ensure text is within limits (280 characters)
            if len(text) > 280:
                logger.warning(f"Tweet text exceeds 280 characters, truncating from {len(text)} chars")
                text = text[:277] + "..."
            
            # Prepare payload
            payload = {"text": text}
            
            # Add media IDs if provided
            if media_ids:
                payload["media"] = {"media_ids": media_ids}
                
            # Add reply information if provided
            if reply_to:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to}
            
            # Create OAuth1 session
            oauth = OAuth1Session(
                client_key=self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
            
            # Post tweet using Twitter API v2
            post_url = "https://api.twitter.com/2/tweets"
            response = oauth.post(post_url, json=payload)
            
            # Check for errors
            if response.status_code not in [200, 201]:
                error_msg = f"Failed to post tweet: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            response_data = response.json()
            tweet_id = response_data.get("data", {}).get("id")
            tweet_text = response_data.get("data", {}).get("text")
            
            if not tweet_id:
                raise ValueError("Failed to extract tweet ID from response")
            
            logger.info(f"Tweet posted successfully with ID: {tweet_id}")
            
            # Return tweet data
            return {
                "id": tweet_id,
                "text": tweet_text,
                "created_at": datetime.now().isoformat(),
                "media_ids": media_ids or []
            }
        
        except Exception as e:
            error_msg = f"Failed to post tweet: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID.
        
        Args:
            tweet_id: Tweet ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        self._wait_for_rate_limit()
        
        try:
            # Delete the tweet
            self.client.delete_tweet(id=tweet_id)
            logger.info(f"Tweet {tweet_id} deleted successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete tweet {tweet_id}: {str(e)}")
            return False
    
    def get_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get a tweet by ID.
        
        Args:
            tweet_id: Tweet ID to retrieve
            
        Returns:
            Dictionary with tweet data or None if not found
        """
        self._wait_for_rate_limit()
        
        try:
            # Get the tweet
            response = self.client.get_tweet(
                id=tweet_id,
                expansions=["attachments.media_keys", "author_id"],
                tweet_fields=["created_at", "public_metrics"]
            )
            
            if not response.data:
                logger.warning(f"Tweet {tweet_id} not found")
                return None
            
            # Extract tweet data - handle both dictionary and object responses
            data = response.data
            tweet_data = {}
            
            # Check if data is a dictionary or an object with attributes
            if isinstance(data, dict):
                # It's already a dictionary
                tweet_data = {
                    "id": data.get("id"),
                    "text": data.get("text"),
                    "created_at": data.get("created_at"),
                    "author_id": data.get("author_id"),
                    "metrics": data.get("public_metrics", {}),
                    "media_keys": data.get("attachments", {}).get("media_keys", []) if data.get("attachments") else []
                }
            else:
                # It's an object with attributes
                tweet_data = {
                    "id": getattr(data, "id", None),
                    "text": getattr(data, "text", None),
                    "created_at": getattr(data, "created_at", None),
                    "author_id": getattr(data, "author_id", None),
                    "media_keys": []
                }
                
                # Handle metrics attribute
                if hasattr(data, "public_metrics"):
                    if hasattr(data.public_metrics, "_json"):
                        tweet_data["metrics"] = data.public_metrics._json
                    else:
                        tweet_data["metrics"] = data.public_metrics
                
                # Handle attachments attribute
                if hasattr(data, "attachments") and hasattr(data.attachments, "media_keys"):
                    tweet_data["media_keys"] = data.attachments.media_keys
            
            logger.info(f"Tweet {tweet_id} retrieved successfully")
            return tweet_data
        
        except Exception as e:
            logger.error(f"Failed to get tweet {tweet_id}: {str(e)}")
            return None


class TwitterTestPost:
    """Helper class for creating test posts about the project."""
    
    # Test post templates
    TEMPLATES = [
        "I'm building an #AI Twitter bot that generates solarpunk micro-stories and images! {detail} #MachineLearning #AIArt #CreativeCoding",
        "Just implemented {feature} for my solarpunk #storytelling AI project! {detail} #AIArt #100DaysOfCode",
        "Making progress on my AI storyteller project: {detail} Next up: {next_step}. #AIDev #MachineLearning",
        "Exciting update on my #solarpunk AI storyteller: {detail} This is part of my exploration into #CreativeAI #AIArt",
        "Today's milestone in my AI storyteller project: {detail} Can't wait to share the results! #AIArt #GenerativeAI",
    ]
    
    # Feature details
    FEATURE_DETAILS = {
        "story_generation": {
            "detail": "using Gemini Pro to craft positive micro-stories about sustainable futures",
            "next_step": "adding more thematic diversity to the story prompts"
        },
        "image_generation": {
            "detail": "using Imagen 2 to visualize the stories with beautiful solarpunk aesthetics",
            "next_step": "fine-tuning the visual style to match the story themes"
        },
        "twitter_integration": {
            "detail": "implementing the Twitter API client to share stories and images with the world",
            "next_step": "adding scheduling capabilities for regular posts"
        },
        "error_handling": {
            "detail": "adding robust error handling and retries to ensure reliable operation",
            "next_step": "implementing monitoring to track performance"
        },
        "media_upload": {
            "detail": "successfully implemented media upload for AI-generated images",
            "next_step": "optimizing image quality for Twitter's format"
        },
        "scheduling": {
            "detail": "added a scheduling system to post stories at optimal times",
            "next_step": "analyzing engagement patterns to refine the schedule"
        }
    }
    
    @staticmethod
    def generate_test_post(feature: str) -> Dict[str, str]:
        """Generate a test post about the specified feature.
        
        Args:
            feature: Feature to highlight in the post
            
        Returns:
            Dictionary with post text and metadata
        """
        import random
        
        # Get feature details
        feature_info = TwitterTestPost.FEATURE_DETAILS.get(feature, {
            "detail": f"working on the {feature} module to enhance the user experience",
            "next_step": "continuing to refine the system architecture"
        })
        
        # Select a random template
        template = random.choice(TwitterTestPost.TEMPLATES)
        
        # Fill in the template
        if "{next_step}" in template:
            post_text = template.format(
                feature=feature.replace("_", " "),
                detail=feature_info["detail"],
                next_step=feature_info["next_step"]
            )
        else:
            post_text = template.format(
                feature=feature.replace("_", " "),
                detail=feature_info["detail"]
            )
        
        # Return the post with metadata
        return {
            "text": post_text,
            "feature": feature,
            "detail": feature_info["detail"],
            "timestamp": datetime.now().isoformat(),
            "type": "test_post"
        }


# Testing functions
def test_twitter_connection() -> bool:
    """Test the Twitter API connection.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        client = TwitterClient()
        
        # Get the authenticating user's ID to verify credentials
        user_info = client.client.get_me()
        
        if user_info and hasattr(user_info, "data") and user_info.data:
            logger.info(f"Successfully connected to Twitter as user @{user_info.data.username}")
            return True
        else:
            logger.error("Failed to verify Twitter credentials")
            return False
            
    except Exception as e:
        logger.error(f"Failed to connect to Twitter API: {str(e)}")
        return False


def post_test_update(feature: str, with_image: bool = False) -> Optional[Dict[str, Any]]:
    """Post a test update about the project.
    
    Args:
        feature: Feature to highlight in the post
        with_image: Whether to include a test image
        
    Returns:
        Dictionary with post data or None if failed
    """
    try:
        # Initialize Twitter client
        client = TwitterClient()
        
        # Generate test post
        post_data = TwitterTestPost.generate_test_post(feature)
        
        # Prepare media if requested
        media_ids = None
        if with_image:
            # Try to find a test image
            test_images_dir = PROJECT_ROOT / "output" / "images"
            if test_images_dir.exists():
                # Find the most recent image
                image_files = list(test_images_dir.glob("*.png"))
                if image_files:
                    # Sort by modification time, most recent first
                    image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    test_image = image_files[0]
                    
                    # Upload the image
                    media_id = client.upload_media(test_image)
                    media_ids = [media_id]
                    logger.info(f"Using test image: {test_image}")
        
        # Post the tweet
        tweet_data = client.post_tweet(
            text=post_data["text"],
            media_ids=media_ids
        )
        
        # Add test data
        tweet_data.update({
            "feature": post_data["feature"],
            "test": True,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save test record
        test_record_dir = PROJECT_ROOT / "output" / "twitter_tests"
        test_record_dir.mkdir(parents=True, exist_ok=True)
        
        record_file = test_record_dir / f"test_{tweet_data['id']}.json"
        with open(record_file, 'w') as f:
            json.dump(tweet_data, f, indent=2)
        
        logger.info(f"Test post successful! Tweet ID: {tweet_data['id']}")
        logger.info(f"Test record saved to {record_file}")
        
        return tweet_data
        
    except Exception as e:
        logger.error(f"Failed to post test update: {str(e)}")
        return None


if __name__ == "__main__":
    import sys
    
    print("Twitter Integration Module - Test Tool")
    print("======================================")
    
    # Check for command line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run src/twitter_client.py [test|update] [feature] [with_image]")
        print("  - test: Test the Twitter API connection")
        print("  - update: Post a test update about the project")
        print("  - feature: Feature to highlight (story_generation, image_generation, etc.)")
        print("  - with_image: Add 'image' to include a test image")
        sys.exit(1)
    
    # Parse command line arguments
    command = sys.argv[1]
    
    if command == "test":
        # Test Twitter connection
        if test_twitter_connection():
            print("Twitter connection test successful!")
            sys.exit(0)
        else:
            print("Twitter connection test failed!")
            sys.exit(1)
    
    elif command == "update":
        # Check for feature argument
        if len(sys.argv) < 3:
            print("Please specify a feature to highlight")
            sys.exit(1)
            
        feature = sys.argv[2]
        with_image = "image" in sys.argv or "with_image" in sys.argv
        
        # Post a test update
        result = post_test_update(feature, with_image)
        
        if result:
            print(f"Test post successful! Tweet ID: {result['id']}")
            print(f"Tweet text: {result['text']}")
            sys.exit(0)
        else:
            print("Test post failed!")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 