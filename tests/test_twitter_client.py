"""Test suite for the Twitter client module."""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the twitter client
from src.twitter_client import TwitterClient, TwitterTestPost, test_twitter_connection, post_test_update

# Configure test data
TEST_TWEET_TEXT = "This is a test tweet from the AI story bot test suite."
TEST_TWEET_ID = "1234567890123456789"
TEST_MEDIA_ID = "9876543210987654321"
TEST_USER_ID = "123456789"
TEST_USERNAME = "test_user"

# Mock response objects
class MockResponse:
    """Mock response class for Tweepy API responses."""
    
    def __init__(self, data=None, includes=None, errors=None):
        self.data = data
        self.includes = includes
        self.errors = errors

class MockResponseData:
    """Mock response data class for Tweepy API responses."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # For data that needs to be accessed as properties
        if 'public_metrics' in kwargs:
            self.public_metrics = MagicMock()
            self.public_metrics._json = kwargs['public_metrics']
        
        if 'attachments' in kwargs and 'media_keys' in kwargs['attachments']:
            self.attachments = MagicMock()
            self.attachments.media_keys = kwargs['attachments']['media_keys']


@pytest.fixture
def mock_twitter_client():
    """Create a mock Twitter client with patched methods."""
    with patch('src.twitter_client.TwitterClient._load_credentials'), \
         patch('src.twitter_client.TwitterClient._configure_client'):
        
        client = TwitterClient()
        
        # Mock API clients
        client.client = MagicMock()
        client.api_v1 = MagicMock()
        
        # Set up default responses with proper data structure
        mock_data = {
            "id": TEST_TWEET_ID,
            "text": TEST_TWEET_TEXT
        }
        mock_response = MockResponse(data=mock_data)
        client.client.create_tweet.return_value = mock_response
        
        client.client.delete_tweet.return_value = MockResponse(data=True)
        
        mock_tweet_data = {
            "id": TEST_TWEET_ID,
            "text": TEST_TWEET_TEXT,
            "created_at": datetime.now().isoformat(),
            "author_id": TEST_USER_ID,
            "public_metrics": {'retweet_count': 0, 'like_count': 0},
            "attachments": {'media_keys': [TEST_MEDIA_ID]}
        }
        client.client.get_tweet.return_value = MockResponse(data=mock_tweet_data)
        
        mock_user_data = {
            "id": TEST_USER_ID,
            "username": TEST_USERNAME,
            "name": "Test User"
        }
        client.client.get_me.return_value = MockResponse(data=mock_user_data)
        
        # Mock media upload
        mock_media = MagicMock()
        mock_media.media_id_string = TEST_MEDIA_ID
        client.api_v1.media_upload.return_value = mock_media
        
        yield client


def test_twitter_client_initialization():
    """Test that the Twitter client initializes correctly with mocked credentials."""
    with patch('src.twitter_client.TwitterClient._load_credentials'), \
         patch('src.twitter_client.TwitterClient._configure_client'):
        
        client = TwitterClient()
        assert client is not None
        assert client.config is not None
        assert "api" in client.config
        assert "twitter" in client.config["api"]


def test_post_tweet(mock_twitter_client):
    """Test posting a tweet."""
    result = mock_twitter_client.post_tweet(TEST_TWEET_TEXT)
    
    # Verify the client was called correctly
    mock_twitter_client.client.create_tweet.assert_called_once_with(
        text=TEST_TWEET_TEXT,
        media_ids=None,
        in_reply_to_tweet_id=None
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["id"] == TEST_TWEET_ID
    assert "text" in result
    assert result["text"] == TEST_TWEET_TEXT


def test_post_tweet_with_media(mock_twitter_client):
    """Test posting a tweet with media."""
    result = mock_twitter_client.post_tweet(
        TEST_TWEET_TEXT, 
        media_ids=[TEST_MEDIA_ID]
    )
    
    # Verify the client was called correctly
    mock_twitter_client.client.create_tweet.assert_called_once_with(
        text=TEST_TWEET_TEXT,
        media_ids=[TEST_MEDIA_ID],
        in_reply_to_tweet_id=None
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["id"] == TEST_TWEET_ID
    assert "media_ids" in result
    assert result["media_ids"] == [TEST_MEDIA_ID]


def test_delete_tweet(mock_twitter_client):
    """Test deleting a tweet."""
    result = mock_twitter_client.delete_tweet(TEST_TWEET_ID)
    
    # Verify the client was called correctly
    mock_twitter_client.client.delete_tweet.assert_called_once_with(
        id=TEST_TWEET_ID
    )
    
    # Verify the result
    assert result is True


def test_get_tweet(mock_twitter_client):
    """Test retrieving a tweet."""
    result = mock_twitter_client.get_tweet(TEST_TWEET_ID)
    
    # Verify the client was called correctly
    mock_twitter_client.client.get_tweet.assert_called_once_with(
        id=TEST_TWEET_ID,
        expansions=["attachments.media_keys", "author_id"],
        tweet_fields=["created_at", "public_metrics"]
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["id"] == TEST_TWEET_ID
    assert "text" in result
    assert result["text"] == TEST_TWEET_TEXT
    assert "media_keys" in result
    assert result["media_keys"] == [TEST_MEDIA_ID]


def test_upload_media(mock_twitter_client, tmp_path):
    """Test uploading media."""
    # Create a test image file
    test_image = tmp_path / "test_image.png"
    test_image.write_bytes(b"dummy image data")
    
    # Create a mock stat result with appropriate st_size
    stat_result = MagicMock()
    stat_result.st_size = 1024  # 1KB, well under the 5MB limit
    
    # Test the upload_media method
    with patch('src.twitter_client.Image.open'), \
         patch('src.twitter_client.Path.exists', return_value=True), \
         patch('src.twitter_client.Path.stat', return_value=stat_result):
        
        result = mock_twitter_client.upload_media(test_image)
        
        # Verify the client was called correctly
        mock_twitter_client.api_v1.media_upload.assert_called_once_with(
            filename=str(test_image)
        )
        
        # Verify the result
        assert result == TEST_MEDIA_ID


def test_twitter_test_post_generation():
    """Test the TwitterTestPost class."""
    # Test with a known feature
    test_post = TwitterTestPost.generate_test_post("twitter_integration")
    
    assert test_post is not None
    assert "text" in test_post
    assert "twitter api" in test_post["text"].lower()
    assert "detail" in test_post
    assert "feature" in test_post
    assert test_post["feature"] == "twitter_integration"
    
    # Test with an unknown feature
    test_post = TwitterTestPost.generate_test_post("unknown_feature")
    
    assert test_post is not None
    assert "text" in test_post
    assert "unknown_feature" in test_post["text"].lower()


def test_twitter_api_connection():
    """Test the Twitter API connection directly.
    
    This is a wrapper around the imported test_twitter_connection function
    that uses assertions instead of returning a value.
    """
    with patch('src.twitter_client.TwitterClient', return_value=MagicMock()) as mock_client_class:
        # Set up the mock
        mock_client = mock_client_class.return_value
        mock_client.client.get_me.return_value = MockResponse(
            data=MockResponseData(
                id=TEST_USER_ID,
                username=TEST_USERNAME,
                name="Test User"
            )
        )
        
        # Use assertions instead of returning a value
        assert test_twitter_connection() is True


def test_post_test_update():
    """Test the post_test_update function."""
    with patch('src.twitter_client.TwitterClient', return_value=MagicMock()) as mock_client_class, \
         patch('src.twitter_client.TwitterTestPost.generate_test_post') as mock_generate_post, \
         patch('src.twitter_client.json.dump') as mock_json_dump, \
         patch('src.twitter_client.Path.mkdir') as mock_mkdir, \
         patch('src.twitter_client.Path.exists', return_value=True), \
         patch('src.twitter_client.Path.glob', return_value=[Path("test_image.png")]), \
         patch('src.twitter_client.Path.stat', return_value=MagicMock(st_mtime=123456789)), \
         patch('builtins.open', MagicMock()):
        
        # Set up the mocks
        mock_client = mock_client_class.return_value
        mock_client.post_tweet.return_value = {
            "id": TEST_TWEET_ID,
            "text": TEST_TWEET_TEXT,
            "created_at": datetime.now().isoformat(),
            "media_ids": [TEST_MEDIA_ID]
        }
        
        mock_client.upload_media.return_value = TEST_MEDIA_ID
        
        mock_generate_post.return_value = {
            "text": TEST_TWEET_TEXT,
            "feature": "twitter_integration",
            "timestamp": datetime.now().isoformat(),
            "type": "test_post"
        }
        
        # Test posting with an image
        result = post_test_update("twitter_integration", True)
        
        assert result is not None
        assert "id" in result
        assert result["id"] == TEST_TWEET_ID
        assert "feature" in result
        assert result["feature"] == "twitter_integration"
        
        # Verify the client was called correctly
        mock_client.post_tweet.assert_called_once_with(
            text=TEST_TWEET_TEXT,
            media_ids=[TEST_MEDIA_ID]
        )


def run_tests():
    """Run all tests."""
    pytest.main(["-xvs", __file__])


if __name__ == "__main__":
    print("Twitter Client Test Suite")
    print("=========================")
    run_tests() 