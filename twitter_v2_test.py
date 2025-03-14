#!/usr/bin/env python3
import os
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Test posting a tweet using Twitter API v2 with OAuth 1.0a."""
    try:
        # Load credentials from .env file
        load_dotenv(override=True)
        
        # Get API credentials
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        # Check if credentials are available
        if not all([api_key, api_secret, access_token, access_token_secret]):
            logger.error("Missing Twitter API credentials in environment variables")
            return False
        
        logger.info("Credentials loaded successfully")
        logger.info(f"API Key: {api_key[:5]}... (length: {len(api_key)})")
        logger.info(f"API Secret: {api_secret[:5]}... (length: {len(api_secret)})")
        logger.info(f"Access Token: {access_token[:5]}... (length: {len(access_token)})")
        logger.info(f"Access Token Secret: {access_token_secret[:5]}... (length: {len(access_token_secret)})")
        
        # Create OAuth1 session
        logger.info("Creating OAuth1 session...")
        oauth = OAuth1Session(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        # Prepare tweet text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tweet_text = f"Testing Twitter API v2 with OAuth 1.0a for the Solarpunk Story Bot. This is an automated test post. Timestamp: {timestamp} #AITwitterBot #Test"
        
        # Create payload
        payload = {"text": tweet_text}
        
        # Post tweet using Twitter API v2
        logger.info("Posting tweet...")
        post_url = "https://api.twitter.com/2/tweets"
        
        response = oauth.post(post_url, json=payload)
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        # Check response
        if response.status_code not in [200, 201]:
            logger.error(f"Failed to post tweet: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
        
        # Parse response
        try:
            response_data = response.json()
            tweet_id = response_data.get("data", {}).get("id")
            if tweet_id:
                logger.info(f"Tweet posted successfully with ID: {tweet_id}")
                logger.info(f"Tweet URL: https://twitter.com/user/status/{tweet_id}")
            else:
                logger.warning("Tweet posted but couldn't retrieve tweet ID")
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    result = main()
    if result:
        print("\nTwitter API v2 test completed successfully!")
    else:
        print("\nTwitter API v2 test failed!") 