#!/usr/bin/env python3
"""CLI script to generate stories using the story generation module.

This script demonstrates the use of the StoryGenerator class
to generate and display creative one-sentence stories.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add the parent directory to the path to allow importing from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.gemini import GeminiProClient
from src.story_generation import StoryGenerator
from src.utils.credentials import CredentialManager


def setup_logging(level: int = logging.INFO) -> None:
    """Set up basic logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


def main() -> None:
    """Main function for the story generation CLI script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate creative one-sentence stories.")
    parser.add_argument("--genre", type=str, help="Genre for the story (if not specified, a random genre will be used)")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config file")
    parser.add_argument("--env-file", type=str, default=".env", help="Path to .env file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of stories to generate")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature for generation (0.0 to 1.0)")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)
    
    # Make sure the config file exists
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Get credentials
        cred_manager = CredentialManager(
            env_file=args.env_file,
            config_file=config_path
        )
        
        # Get Google Cloud credentials
        gcp_creds = cred_manager.get_google_cloud_credentials()
        
        # Create Gemini Pro client
        gemini_client = GeminiProClient(
            project_id=cred_manager.config.get("api", {}).get("google_cloud", {}).get("project_id", ""),
            credentials_path=gcp_creds.get("credentials_path")
        )
        
        # Create story generator
        story_generator = StoryGenerator(
            gemini_client=gemini_client,
            config_path=config_path
        )
        
        # Generate stories
        print(f"\nGenerating {args.count} story/stories...\n")
        
        for i in range(args.count):
            try:
                story, genre = story_generator.generate_story(
                    genre=args.genre,
                    temperature=args.temperature
                )
                
                print(f"Story {i+1} ({genre}):")
                print(f"\"{story}\"")
                print()
                
            except Exception as e:
                print(f"Error generating story {i+1}: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 