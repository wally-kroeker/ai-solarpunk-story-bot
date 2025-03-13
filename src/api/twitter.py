"""Twitter API client using tweepy."""

import logging
import os
from typing import Dict, List, Optional, Union, Any

import tweepy
from tweepy import Response

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter API client for interacting with Twitter API v2.
    
    This client handles authentication and provides methods for posting
    tweets with text and media.
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: Optional[str] = None,
    ) -> None:
        """Initialize the Twitter API client.
        
        Args:
            api_key: The Twitter API key
            api_secret: The Twitter API secret
            access_token: The Twitter access token
            access_token_secret: The Twitter access token secret
            bearer_token: Optional bearer token for app-only authentication
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token
        
        # Initialize the API client
        self._client = self._initialize_client()
        logger.info("Twitter API client initialized")
    
    def _initialize_client(self) -> tweepy.Client:
        """Initialize the Twitter API client.
        
        Returns:
            The initialized tweepy Client
        """
        return tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            bearer_token=self.bearer_token,
            wait_on_rate_limit=True,
        )
    
    def upload_media(self, media_path: str) -> str:
        """Upload media to Twitter.
        
        Args:
            media_path: Path to the media file to upload
            
        Returns:
            The media ID for the uploaded file
            
        Raises:
            Exception: If media upload fails
        """
        # For v2 API with media, we need to use v1.1 endpoint for media upload
        auth = tweepy.OAuth1UserHandler(
            self.api_key, 
            self.api_secret,
            self.access_token, 
            self.access_token_secret
        )
        api = tweepy.API(auth)
        
        try:
            media = api.media_upload(media_path)
            logger.info(f"Media uploaded successfully with ID: {media.media_id}")
            return str(media.media_id)
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise
    
    def post_tweet(
        self, 
        text: str, 
        media_ids: Optional[List[str]] = None
    ) -> Response:
        """Post a tweet with optional media.
        
        Args:
            text: The text content of the tweet
            media_ids: Optional list of media IDs to attach to the tweet
            
        Returns:
            The tweepy Response object
            
        Raises:
            Exception: If tweet posting fails
        """
        try:
            response = self._client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            tweet_id = response.data["id"]
            logger.info(f"Tweet posted successfully with ID: {tweet_id}")
            return response
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            raise
    
    def delete_tweet(self, tweet_id: str) -> None:
        """Delete a tweet by ID.
        
        Args:
            tweet_id: The ID of the tweet to delete
            
        Raises:
            Exception: If tweet deletion fails
        """
        try:
            self._client.delete_tweet(tweet_id)
            logger.info(f"Tweet with ID {tweet_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting tweet: {e}")
            raise 