"""Test Twitter API integration.

This module tests the Twitter API client functionality.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from src.utils.credentials import CredentialManager
from src.api.twitter import TwitterClient
from tweepy import Response


def test_twitter_credentials_loading():
    """Test loading Twitter credentials from .env file."""
    # Create credential manager pointing to the .env file in the project root
    cred_manager = CredentialManager(env_file=".env")
    
    # Get Twitter credentials
    try:
        credentials = cred_manager.get_twitter_credentials()
        
        # Check that all required credentials are present
        assert "api_key" in credentials
        assert "api_secret" in credentials
        assert "access_token" in credentials
        assert "access_token_secret" in credentials
        
        # Bearer token is optional but recommended
        if "bearer_token" in credentials:
            assert credentials["bearer_token"] is not None
        
        print("Twitter credentials loaded successfully")
    except Exception as e:
        pytest.fail(f"Failed to load Twitter credentials: {str(e)}")


@pytest.mark.skip(reason="This test posts to Twitter and should only be run manually")
def test_twitter_client_initialization():
    """Test Twitter client initialization with credentials."""
    # Create credential manager
    cred_manager = CredentialManager(env_file=".env")
    
    # Get Twitter credentials
    credentials = cred_manager.get_twitter_credentials()
    
    # Initialize Twitter client
    try:
        client = TwitterClient(
            api_key=credentials["api_key"],
            api_secret=credentials["api_secret"],
            access_token=credentials["access_token"],
            access_token_secret=credentials["access_token_secret"],
            bearer_token=credentials.get("bearer_token")
        )
        
        # If we get here, initialization succeeded
        assert client is not None
        print("Twitter client initialized successfully")
    except Exception as e:
        pytest.fail(f"Failed to initialize Twitter client: {str(e)}")


@pytest.mark.skip(reason="This test posts to Twitter and should only be run manually")
def test_post_tweet():
    """Test posting a tweet.
    
    This test is skipped by default as it posts to the actual Twitter account.
    Run manually only when needed.
    """
    # Create credential manager
    cred_manager = CredentialManager(env_file=".env")
    
    # Get Twitter credentials
    credentials = cred_manager.get_twitter_credentials()
    
    # Initialize Twitter client
    client = TwitterClient(
        api_key=credentials["api_key"],
        api_secret=credentials["api_secret"],
        access_token=credentials["access_token"],
        access_token_secret=credentials["access_token_secret"],
        bearer_token=credentials.get("bearer_token")
    )
    
    # Post a test tweet
    try:
        response = client.post_tweet("This is a test tweet from AI Story Twitter Bot.")
        assert response.data is not None
        assert "id" in response.data
        
        # Clean up - delete the test tweet
        tweet_id = response.data["id"]
        client.delete_tweet(tweet_id)
        print(f"Tweet posted and deleted successfully with ID: {tweet_id}")
    except Exception as e:
        pytest.fail(f"Failed to post tweet: {str(e)}")


@pytest.fixture
def mock_credentials() -> Dict[str, str]:
    """Fixture for mock Twitter credentials.
    
    Returns:
        Dictionary with mock Twitter API credentials
    """
    return {
        "api_key": "mock_api_key",
        "api_secret": "mock_api_secret",
        "access_token": "mock_access_token",
        "access_token_secret": "mock_access_token_secret",
        "bearer_token": "mock_bearer_token",
    }


@pytest.fixture
def twitter_client(mock_credentials: Dict[str, str]) -> TwitterClient:
    """Fixture for TwitterClient with mock credentials.
    
    Args:
        mock_credentials: Mock Twitter API credentials
        
    Returns:
        TwitterClient instance with mock credentials
    """
    return TwitterClient(
        api_key=mock_credentials["api_key"],
        api_secret=mock_credentials["api_secret"],
        access_token=mock_credentials["access_token"],
        access_token_secret=mock_credentials["access_token_secret"],
        bearer_token=mock_credentials["bearer_token"],
    )


@patch("tweepy.Client")
def test_twitter_client_initialization_with_mock(
    mock_tweepy_client: MagicMock, 
    twitter_client: TwitterClient,
    mock_credentials: Dict[str, str],
) -> None:
    """Test that TwitterClient initializes correctly with mocks.
    
    Args:
        mock_tweepy_client: Mock tweepy.Client
        twitter_client: TwitterClient instance
        mock_credentials: Mock Twitter credentials
    """
    # Assert client was initialized with correct credentials
    assert twitter_client.api_key == mock_credentials["api_key"]
    assert twitter_client.api_secret == mock_credentials["api_secret"]
    assert twitter_client.access_token == mock_credentials["access_token"]
    assert twitter_client.access_token_secret == mock_credentials["access_token_secret"]
    assert twitter_client.bearer_token == mock_credentials["bearer_token"]
    
    # Assert tweepy.Client was called with correct parameters
    mock_tweepy_client.assert_called_once_with(
        consumer_key=mock_credentials["api_key"],
        consumer_secret=mock_credentials["api_secret"],
        access_token=mock_credentials["access_token"],
        access_token_secret=mock_credentials["access_token_secret"],
        bearer_token=mock_credentials["bearer_token"],
        wait_on_rate_limit=True,
    )


@patch("tweepy.Client")
def test_post_tweet(
    mock_tweepy_client: MagicMock,
    twitter_client: TwitterClient,
) -> None:
    """Test post_tweet method.
    
    Args:
        mock_tweepy_client: Mock tweepy.Client
        twitter_client: TwitterClient instance
    """
    # Setup mock response
    mock_response = MagicMock(spec=Response)
    mock_response.data = {"id": "12345"}
    mock_instance = mock_tweepy_client.return_value
    mock_instance.create_tweet.return_value = mock_response
    
    # Call the method
    tweet_text = "Test tweet"
    response = twitter_client.post_tweet(tweet_text)
    
    # Assert create_tweet was called with correct parameters
    mock_instance.create_tweet.assert_called_once_with(
        text=tweet_text,
        media_ids=None,
    )
    
    # Assert response was returned correctly
    assert response == mock_response
    assert response.data["id"] == "12345"


@patch("tweepy.OAuth1UserHandler")
@patch("tweepy.API")
def test_upload_media(
    mock_tweepy_api: MagicMock,
    mock_oauth_handler: MagicMock,
    twitter_client: TwitterClient,
) -> None:
    """Test upload_media method.
    
    Args:
        mock_tweepy_api: Mock tweepy.API
        mock_oauth_handler: Mock tweepy.OAuth1UserHandler
        twitter_client: TwitterClient instance
    """
    # Setup mock media response
    mock_media = MagicMock()
    mock_media.media_id = "67890"
    mock_api_instance = mock_tweepy_api.return_value
    mock_api_instance.media_upload.return_value = mock_media
    
    # Call the method
    media_path = "test_image.jpg"
    media_id = twitter_client.upload_media(media_path)
    
    # Assert OAuth handler was created with correct credentials
    mock_oauth_handler.assert_called_once_with(
        twitter_client.api_key,
        twitter_client.api_secret,
        twitter_client.access_token,
        twitter_client.access_token_secret,
    )
    
    # Assert media_upload was called with correct parameters
    mock_api_instance.media_upload.assert_called_once_with(media_path)
    
    # Assert media ID was returned correctly
    assert media_id == "67890"


@patch("tweepy.Client")
def test_delete_tweet(
    mock_tweepy_client: MagicMock,
    twitter_client: TwitterClient,
) -> None:
    """Test delete_tweet method.
    
    Args:
        mock_tweepy_client: Mock tweepy.Client
        twitter_client: TwitterClient instance
    """
    # Setup mock
    mock_instance = mock_tweepy_client.return_value
    
    # Call the method
    tweet_id = "12345"
    twitter_client.delete_tweet(tweet_id)
    
    # Assert delete_tweet was called with correct parameter
    mock_instance.delete_tweet.assert_called_once_with(tweet_id) 