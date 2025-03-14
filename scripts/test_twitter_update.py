#!/usr/bin/env python
"""Test script for posting project updates to Twitter.

This script provides a simple interface for posting project updates to Twitter
during the development and testing phase of the AI story Twitter bot.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the twitter client
from src.twitter_client import TwitterTestPost, TwitterClient, post_test_update

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project features
FEATURES = [
    "story_generation",
    "image_generation",
    "twitter_integration",
    "error_handling",
    "media_upload",
    "scheduling"
]


def display_templates():
    """Display available post templates."""
    print("\nAvailable Post Templates:")
    print("------------------------")
    for i, template in enumerate(TwitterTestPost.TEMPLATES, 1):
        print(f"{i}. {template}")
    print()


def display_features():
    """Display available features."""
    print("\nAvailable Features:")
    print("-----------------")
    for i, feature in enumerate(FEATURES, 1):
        # Get the feature details
        feature_info = TwitterTestPost.FEATURE_DETAILS.get(feature, {})
        detail = feature_info.get("detail", "No description available")
        print(f"{i}. {feature.replace('_', ' ').title()}: {detail}")
    print()


def display_previous_posts():
    """Display previously posted test updates."""
    # Project root directory
    project_root = Path(__file__).parent.parent
    test_record_dir = project_root / "output" / "twitter_tests"
    
    if not test_record_dir.exists():
        print("\nNo previous test posts found.")
        return
    
    # Find all test records
    test_records = list(test_record_dir.glob("test_*.json"))
    if not test_records:
        print("\nNo previous test posts found.")
        return
    
    print("\nPrevious Test Posts:")
    print("-------------------")
    
    import json
    
    for i, record_file in enumerate(sorted(test_records, key=lambda x: x.stat().st_mtime, reverse=True)[:5], 1):
        try:
            with open(record_file, 'r') as f:
                record = json.load(f)
            
            tweet_id = record.get("id", "Unknown")
            tweet_text = record.get("text", "No text available")
            feature = record.get("feature", "Unknown")
            timestamp = record.get("timestamp", "Unknown")
            
            print(f"{i}. [ID: {tweet_id}] ({feature}) {tweet_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to read test record {record_file}: {str(e)}")
    
    print()


def interactive_menu():
    """Display an interactive menu for posting test updates."""
    while True:
        print("\n" + "="*80)
        print("Twitter Test Update Tool")
        print("=" * 80)
        print("This tool helps you post test updates about the project to Twitter.")
        print("These updates will be informative and interesting for followers.")
        
        display_previous_posts()
        display_features()
        
        print("\nOptions:")
        print("  1. Post an update about a specific feature")
        print("  2. View available tweet templates")
        print("  3. Test Twitter connection (no posting)")
        print("  4. Delete a test tweet")
        print("  0. Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "0":
            print("Exiting.")
            break
            
        elif choice == "1":
            # Post an update
            print("\nSelect a feature to highlight:")
            for i, feature in enumerate(FEATURES, 1):
                print(f"  {i}. {feature.replace('_', ' ').title()}")
                
            feature_choice = input("\nEnter feature number: ")
            try:
                feature_index = int(feature_choice) - 1
                if 0 <= feature_index < len(FEATURES):
                    feature = FEATURES[feature_index]
                    
                    # Ask about including an image
                    include_image = input("Include an AI-generated image? (y/n): ").lower() in ["y", "yes"]
                    
                    # Preview the post
                    post_data = TwitterTestPost.generate_test_post(feature)
                    print("\nPreview:")
                    print(f"Tweet: {post_data['text']}")
                    
                    # Confirm posting
                    confirmation = input("\nPost this to Twitter? (y/n): ")
                    if confirmation.lower() in ["y", "yes"]:
                        result = post_test_update(feature, include_image)
                        if result:
                            print(f"\nPost successful! Tweet ID: {result['id']}")
                            print(f"Tweet text: {result['text']}")
                        else:
                            print("\nPost failed.")
                    else:
                        print("Posting cancelled.")
                else:
                    print("Invalid feature selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == "2":
            # View templates
            display_templates()
            
        elif choice == "3":
            # Test connection
            from src.twitter_client import test_twitter_connection
            
            print("\nTesting Twitter connection...")
            if test_twitter_connection():
                print("Connection successful!")
            else:
                print("Connection failed. Check credentials.")
                
        elif choice == "4":
            # Delete a tweet
            try:
                tweet_id = input("\nEnter the tweet ID to delete: ")
                if tweet_id:
                    client = TwitterClient()
                    if client.delete_tweet(tweet_id):
                        print(f"Tweet {tweet_id} deleted successfully.")
                    else:
                        print(f"Failed to delete tweet {tweet_id}.")
                else:
                    print("No tweet ID provided.")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        else:
            print("Invalid choice.")
        
        # Pause before redisplaying the menu
        input("\nPress Enter to continue...")


def main():
    """Run the Twitter test update tool."""
    print("AI Twitter Bot - Project Update Test Tool")
    print("=======================================")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Non-interactive mode
        command = sys.argv[1]
        
        if command == "post":
            # Post an update
            if len(sys.argv) < 3:
                print("Please specify a feature.")
                print(f"Available features: {', '.join(FEATURES)}")
                return 1
                
            feature = sys.argv[2]
            if feature not in FEATURES:
                print(f"Unknown feature: {feature}")
                print(f"Available features: {', '.join(FEATURES)}")
                return 1
                
            # Check if an image should be included
            with_image = len(sys.argv) > 3 and sys.argv[3].lower() in ["image", "with_image", "true", "yes"]
            
            # Post the update
            result = post_test_update(feature, with_image)
            
            if result:
                print(f"Post successful! Tweet ID: {result['id']}")
                print(f"Tweet text: {result['text']}")
                return 0
            else:
                print("Post failed.")
                return 1
                
        elif command == "list-features":
            # List available features
            print("Available Features:")
            for feature in FEATURES:
                feature_info = TwitterTestPost.FEATURE_DETAILS.get(feature, {})
                detail = feature_info.get("detail", "No description available")
                print(f"- {feature}: {detail}")
            return 0
            
        elif command == "list-templates":
            # List available templates
            print("Available Templates:")
            for i, template in enumerate(TwitterTestPost.TEMPLATES, 1):
                print(f"{i}. {template}")
            return 0
            
        elif command == "test-connection":
            # Test Twitter connection
            from src.twitter_client import test_twitter_connection
            
            print("Testing Twitter connection...")
            if test_twitter_connection():
                print("Connection successful!")
                return 0
            else:
                print("Connection failed. Check credentials.")
                return 1
                
        else:
            print(f"Unknown command: {command}")
            return 1
    
    else:
        # Interactive mode
        try:
            interactive_menu()
            return 0
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 0
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return 1


if __name__ == "__main__":
    sys.exit(main()) 