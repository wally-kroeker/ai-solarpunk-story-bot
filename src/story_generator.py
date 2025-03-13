"""Story generation module using Gemini Pro API.

This module provides functionality for generating solarpunk stories
with a positive vision of the future, sized to fit X character limits.
"""

import os
import time
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# X (Twitter) character limits
X_FREE_CHAR_LIMIT = 280

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class StoryParameters:
    """Parameters for story generation."""
    max_chars: int = X_FREE_CHAR_LIMIT
    themes: List[str] = None
    setting: str = "urban"
    ai_role: str = "supportive"
    tone: str = "hopeful"
    
    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.themes is None:
            self.themes = ["sustainability", "community", "technology"]


def load_config() -> Dict[str, Any]:
    """Load the application configuration from YAML.
    
    Returns:
        Dict containing configuration
    """
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


class StoryGenerator:
    """Generator for solarpunk micro-stories using Gemini Pro."""
    
    MODEL_NAME = "gemini-1.5-pro"
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    def __init__(self) -> None:
        """Initialize the story generator with credentials from config."""
        try:
            # Load configuration
            config = load_config()
            
            # Get Google Cloud credentials path and project ID
            gcp_config = config.get("api", {}).get("google_cloud", {})
            project_id = gcp_config.get("project_id")
            credentials_path = gcp_config.get("credentials_path")
            
            # Construct absolute path to credentials file
            credentials_abs_path = PROJECT_ROOT / credentials_path
            
            logger.info(f"Using credentials at: {credentials_abs_path}")
            
            # Load credentials explicitly
            credentials = service_account.Credentials.from_service_account_file(
                credentials_abs_path
            )
            
            # Initialize Vertex AI with explicit credentials
            vertexai.init(
                project=project_id,
                location="us-central1",
                credentials=credentials
            )
            
            # Initialize the generative model
            self.model = GenerativeModel(self.MODEL_NAME)
            logger.info(f"Successfully initialized Gemini Pro model: {self.MODEL_NAME}")
            
        except Exception as e:
            error_msg = f"Failed to initialize story generator: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _create_solarpunk_prompt(self, params: StoryParameters) -> str:
        """Create a detailed prompt for solarpunk micro-story generation."""
        themes_text = ", ".join(params.themes)
        
        prompt = f"""
        Create a very short solarpunk micro-story that fits in exactly {params.max_chars} characters or less.
        
        ABOUT SOLARPUNK:
        Solarpunk envisions a future where humanity has successfully addressed climate change through sustainable
        technology, community-focused solutions, and harmonious integration with nature.
        
        SETTING:
        The story takes place in a {params.setting} environment with green technology and community-focused design.
        
        THEMES:
        Incorporate these themes: {themes_text}
        
        AI ROLE:
        Include AI as a {params.ai_role} element that enhances human life and environmental health.
        
        TONE:
        The story should have a {params.tone} tone while remaining grounded and believable.
        
        STRUCTURE:
        1. Begin with a vivid sensory detail of this solarpunk world
        2. Introduce a small-scale, relatable situation
        3. Show a moment of connection, innovation, or harmony
        4. End with a sense of possibility and hope
        
        CRITICAL REQUIREMENTS:
        - MUST be EXACTLY {params.max_chars} characters or less (this is a strict requirement for X/Twitter)
        - Avoid dystopian elements or climate doom
        - Focus on concrete, specific details rather than abstract concepts
        - Make it feel like a complete moment despite the brevity
        """
        
        return prompt
    
    def generate_story(
        self, 
        params: Optional[StoryParameters] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a solarpunk micro-story based on the provided parameters."""
        if params is None:
            params = StoryParameters()
        
        # Create the prompt
        prompt = self._create_solarpunk_prompt(params)
        
        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.7,
            top_p=0.85,
            top_k=40,
            max_output_tokens=800,
            candidate_count=1,
        )
        
        # Attempt to generate with retries
        attempt = 0
        last_error = None
        
        while attempt < self.MAX_RETRIES:
            try:
                # Generate the story
                response = self.model.generate_content(
                    prompt, 
                    generation_config=generation_config
                )
                
                # Extract and clean the story
                story_text = response.text.strip()
                
                # Ensure it fits within character limit
                if len(story_text) > params.max_chars:
                    # Try to truncate at the last sentence that fits
                    last_period = story_text.rfind('.', 0, params.max_chars)
                    if last_period > 0:
                        story_text = story_text[:last_period + 1]
                    else:
                        # If no suitable truncation point, just cut at the limit
                        story_text = story_text[:params.max_chars]
                
                # Build metadata about the generation
                metadata = {
                    "model": self.MODEL_NAME,
                    "char_count": len(story_text),
                    "themes": params.themes,
                    "setting": params.setting,
                    "ai_role": params.ai_role,
                    "tone": params.tone,
                    "timestamp": time.time(),
                }
                
                logger.info(f"Successfully generated solarpunk story of {len(story_text)} characters")
                return story_text, metadata
            
            except Exception as e:
                attempt += 1
                last_error = e
                logger.warning(f"Story generation attempt {attempt}/{self.MAX_RETRIES} failed: {str(e)}")
                
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)  # Exponential backoff
        
        # If we get here, all retries failed
        error_msg = f"Failed to generate story after {self.MAX_RETRIES} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def generate_test_stories() -> None:
    """Generate sample stories with various settings for testing."""
    # Initialize the generator
    generator = StoryGenerator()
    
    # Create parameters for different types of stories
    settings = ["urban", "coastal", "forest", "desert", "rural"]
    themes_list = [
        ["renewable energy", "community gardens", "localized production"],
        ["ocean conservation", "floating communities", "tidal energy"],
        ["forest stewardship", "ecological monitoring", "natural architecture"],
        ["water conservation", "solar power", "desert greening"],
        ["sustainable agriculture", "community ownership", "appropriate technology"]
    ]
    
    for i, (setting, themes) in enumerate(zip(settings, themes_list)):
        try:
            # Test with a single setting
            if len(sys.argv) > 1 and sys.argv[1] not in ["all", setting]:
                continue
                
            # Generate a story with specific parameters
            params = StoryParameters(
                max_chars=280,
                themes=themes,
                setting=setting,
                ai_role="collaborative",
                tone="hopeful"
            )
            
            logger.info(f"Generating story {i+1}/{len(settings)}: {setting} setting")
            story, metadata = generator.generate_story(params)
            
            # Display the generated story
            print("\n" + "="*80)
            print(f"SOLARPUNK MICRO-STORY - {setting.upper()} SETTING")
            print("="*80)
            print(story)
            print("-"*80)
            print(f"Character count: {len(story)}/280 | Setting: {setting}")
            print(f"Themes: {', '.join(themes)}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error generating story with {setting} setting: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("Solarpunk Story Generator - Testing Tool")
    print("========================================")
    print("Usage: uv run src/story_generator.py [setting|all]")
    print("Available settings: urban, coastal, forest, desert, rural")
    print("If no setting is specified, all settings will be tested.")
    
    generate_test_stories() 