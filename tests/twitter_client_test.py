#!/usr/bin/env python3
"""Test script for the updated TwitterClient."""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the TwitterClient
from twitter_client import TwitterClient, post_test_update

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Test the TwitterClient's post_tweet method."""
    try:
        # Load environment variables from .env file
        load_dotenv(override=True)
        
        # Use the post_test_update function directly (which is an existing function in twitter_client.py)
        feature = "twitter_integration"
        logger.info(f"Posting test update about feature: {feature}")
        
        # This function creates a new TwitterClient internally and posts a test tweet
        result = post_test_update(feature)
        
        if result:
            logger.info(f"Tweet posted successfully with ID: {result['id']}")
            logger.info(f"Tweet URL: https://twitter.com/user/status/{result['id']}")
            return True
        else:
            logger.error("Failed to post test update")
            return False
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    result = main()
    if result:
        print("\nTwitterClient test completed successfully!")
    else:
        print("\nTwitterClient test failed!") 