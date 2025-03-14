#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Load credentials from .env file
    load_dotenv()
    
    # Get bearer token
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    
    if not bearer_token:
        logger.error("Missing TWITTER_BEARER_TOKEN in environment variables")
        return False
    
    logger.info("Bearer token loaded successfully")
    
    # Set up headers with bearer token
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    # Use Twitter API v2 to search for Elon Musk's user ID
    logger.info("Looking up Elon Musk's user ID...")
    user_url = "https://api.twitter.com/2/users/by/username/elonmusk"
    
    user_response = requests.get(user_url, headers=headers)
    
    if user_response.status_code != 200:
        logger.error(f"Failed to get user info: {user_response.status_code}")
        logger.error(f"Response: {user_response.text}")
        return False
        
    logger.info(f"Response status code: {user_response.status_code}")
    logger.info(f"Response: {user_response.text}")
    return True

if __name__ == "__main__":
    result = main()
    if result:
        print("\nTwitter API test completed successfully!")
    else:
        print("\nTwitter API test failed!") 