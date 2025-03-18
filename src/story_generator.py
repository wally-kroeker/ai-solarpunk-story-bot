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
    """Parameters for story generation.
    
    Attributes:
        max_chars: Maximum characters allowed in the story (default: X_FREE_CHAR_LIMIT)
        themes: List of themes to incorporate (default: ["sustainability", "community", "technology"])
        setting: Environmental setting for the story (default: "urban")
        ai_role: How AI should be portrayed in the story (default: "supportive")
        tone: Overall tone of the story (default: "hopeful")
        community_focus: Type of community element to highlight (default: "shared resources")
        character_diversity: Type of character diversity to emphasize (default: "age")
    """
    max_chars: int = X_FREE_CHAR_LIMIT
    themes: List[str] = None
    setting: str = "urban"
    ai_role: str = "supportive"
    tone: str = "hopeful"
    community_focus: str = "shared resources"
    character_diversity: str = "age"
    
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
        
        # Calculate a safety margin to ensure complete sentences
        char_limit = params.max_chars - 15  # Reserve 15 chars for completion
        
        prompt = f"""
        Write a complete solarpunk micro-story under {char_limit} characters (maximum {params.max_chars}).
        
        MICROFICTION TECHNIQUES:
        - Focus on a single powerful moment or image
        - Use 1-2 characters maximum (not 3)
        - Employ precise, evocative language where each word does multiple jobs
        - Imply a larger world through specific details
        - Create a complete arc in minimal space
        
        SOLARPUNK ELEMENTS:
        - Set in a {params.setting} environment
        - Subtly incorporate theme(s): {themes_text}
        - Include technology that serves community needs
        - Suggest harmony between nature and human design
        - Integrate {params.ai_role} AI naturally into the backdrop
        
        STYLE GUIDANCE:
        - Use concrete sensory details rather than abstract concepts
        - Show character connection through small gestures
        - Let the setting imply the larger solarpunk world
        - Trust the reader to infer themes from specific details
        - Use a {params.tone} tone that feels authentic
        
        EXAMPLES OF SUCCESSFUL MICROFICTION STRUCTURE:
        1. Sensory detail → character reaction → implied meaning
        2. Character action → environmental response → character realization
        3. Environmental setting → character interaction → revealing detail
        
        REMEMBER:
        - Every word must earn its place
        - Names should be short (1-2 syllables)
        - Dialogue must be minimal and natural
        - The story must have a complete ending
        - Current character count is critical - stay under {char_limit}
        
        After drafting your story, count the characters and ensure it's complete and under the limit.
        """
        
        return prompt
    
    def generate_story(self, params: StoryParameters) -> Tuple[str, Dict[str, Any]]:
        """Generate a solarpunk micro-story based on the provided parameters."""
        # Create the prompt
        prompt = self._create_solarpunk_prompt(params)
        
        # Generate the story using the model
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7, 
                "max_output_tokens": 512,
                "top_k": 40,
                "top_p": 0.95
            }
        )
        
        story = response.text.strip()
        
        # Ensure the story meets the character limit and ends with a complete sentence
        if len(story) > params.max_chars:
            # Find the last complete sentence that fits within the limit
            last_period_index = story[:params.max_chars].rfind('.')
            if last_period_index > 0:
                story = story[:last_period_index + 1]
            else:
                # Try other sentence-ending punctuation
                for punct in ['!', '?']:
                    last_punct_index = story[:params.max_chars].rfind(punct)
                    if last_punct_index > 0:
                        story = story[:last_punct_index + 1]
                        break
                else:
                    # If no sentence-ending punctuation found, just truncate
                    story = story[:params.max_chars]
        
        # Create metadata
        metadata = {
            "setting": params.setting,
            "themes": params.themes,
            "ai_role": params.ai_role,
            "tone": params.tone,
            "community_focus": params.community_focus,
            "character_diversity": params.character_diversity,
            "char_count": len(story),
            "timestamp": int(time.time())
        }
        
        return story, metadata


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