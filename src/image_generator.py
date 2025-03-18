"""Image generation module using Imagen 2 API.

This module provides functionality for generating solarpunk images
that visualize the stories created with the story generation module.
"""

import os
import time
import logging
import yaml
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.oauth2 import service_account

# Import the story generator to use its functionality
try:
    # When imported as a module
    from src.story_generator import StoryGenerator, StoryParameters, load_config
except ImportError:
    # When run directly
    try:
        from story_generator import StoryGenerator, StoryParameters, load_config
    except ImportError:
        # Allow running without story generator for testing
        StoryGenerator = None
        StoryParameters = None
        
        def load_config():
            """Load configuration from the config file."""
            config_path = Path(__file__).parent.parent / "config.yaml"
            try:
                with open(config_path, 'r') as file:
                    return yaml.safe_load(file)
            except Exception as e:
                logging.error(f"Failed to load config: {str(e)}")
                return {
                    "api": {
                        "google_cloud": {
                            "project_id": "twitterstoryagent",
                            "credentials_path": "credentials/gcp-credentials.json"
                        }
                    }
                }

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Create output directory if it doesn't exist
OUTPUT_DIR = PROJECT_ROOT / "output" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ImageParameters:
    """Parameters for image generation."""
    model_name: str = "imagen-3.0-generate-002"
    samples: int = 1
    style: str = "digital-art"
    add_watermark: bool = True
    
    def __post_init__(self) -> None:
        """Ensure parameters are valid."""
        # Validate model name
        valid_models = ["imagen-3.0-generate-002"]
        if self.model_name not in valid_models:
            self.model_name = valid_models[0]
        
        # Validate samples
        if self.samples < 1 or self.samples > 4:
            self.samples = 1
        
        # Validate style
        valid_styles = ["digital-art", "watercolor", "stylized", "solarpunk-nouveau", "retro-futurism", "isometric"]
        if self.style not in valid_styles:
            self.style = "digital-art"


class ImageGenerator:
    """Generator for solarpunk images using Imagen 2 API."""
    
    # Maximum retries for API calls
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    # Solarpunk style descriptors to enhance prompts
    STYLE_ENHANCERS = {
        "digital-art": "digital art, vibrant colors, detailed illustration, concept art style",
        "watercolor": "watercolor painting style, soft edges, artistic, traditional media",
        "stylized": "stylized animation, bold colors, clean lines, distinctive shapes",
        "solarpunk-nouveau": "art nouveau inspired, organic flowing lines, botanical motifs, stained glass elements",
        "retro-futurism": "retro-futuristic style, vibrant optimistic palette, vintage poster aesthetic, hopeful utopian",
        "isometric": "isometric illustration, clean technical lines, geometric patterns, architectural precision"
    }
    
    def __init__(self) -> None:
        """Initialize the image generator with credentials from config."""
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
            
            logger.info("Initialized Vertex AI successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize image generator: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _create_image_prompt(self, story: str, setting: str, style: str) -> str:
        """Create a detailed prompt for image generation based on the story.
        
        Args:
            story: The story text to visualize
            setting: The setting of the story (urban, coastal, etc.)
            style: The visual style to use
            
        Returns:
            Detailed prompt for image generation
        """
        # Extract key elements from the story
        story_lowercase = story.lower()
        
        # Common solarpunk elements to highlight if they appear in the story
        elements = {
            "solar panels": "solar panels",
            "garden": "community garden",
            "plants": "lush greenery",
            "water": "water systems",
            "community": "people gathering",
            "technology": "eco-friendly technology",
            "wind": "wind turbines",
            "forest": "integrated forest",
            "wood": "sustainable wooden structures",
            "bamboo": "bamboo structures",
            "glass": "glass and sunlight",
            "ai": "subtle AI interfaces",
            "robot": "helpful robots",
            "farm": "vertical farming"
        }
        
        # Identify elements present in the story
        present_elements = []
        for key, element in elements.items():
            if key in story_lowercase:
                present_elements.append(element)
        
        # Setting-specific descriptors
        setting_descriptors = {
            "urban": "vibrant urban solarpunk cityscape with vertical gardens, green rooftops, solar panels, and community spaces",
            "coastal": "coastal solarpunk community with floating gardens, wave energy collectors, sustainable houseboats, and ocean-plastic recycling systems",
            "forest": "forest solarpunk village with tree-integrated architecture, canopy walkways, forest gardens, and natural observatories",
            "desert": "desert solarpunk oasis with shade structures, solar arrays, water harvesting systems, and drought-resistant gardens",
            "rural": "rural solarpunk farm community with regenerative agriculture, communal spaces, energy-positive buildings, and natural materials"
        }
        
        # Default to urban if setting not recognized
        setting_descriptor = setting_descriptors.get(setting, setting_descriptors["urban"])
        
        # Style enhancer from our predefined list
        style_enhancer = self.STYLE_ENHANCERS.get(style, self.STYLE_ENHANCERS["digital-art"])
        
        # Combine elements into a detailed prompt
        elements_text = ", ".join(present_elements) if present_elements else "harmonious integration of nature and technology"
        
        prompt = (
            f"{style_enhancer}, {setting_descriptor}, "
            f"featuring {elements_text}. "
            f"Scene inspired by this story: {story}"
        )
        
        logger.debug(f"Generated image prompt: {prompt[:100]}...")
        return prompt
    
    def generate_image(
        self,
        story: str,
        setting: str,
        params: Optional[ImageParameters] = None,
        save_path: Optional[str] = None
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """Generate images based on a story.
        
        Args:
            story: The story text to visualize
            setting: The setting of the story (urban, coastal, etc.)
            params: Parameters for image generation
            save_path: Optional path to save the image(s)
            
        Returns:
            Tuple of (list of PIL Image objects, metadata)
        """
        if params is None:
            params = ImageParameters()
        
        # Create the image generation model
        model = ImageGenerationModel.from_pretrained(params.model_name)
        logger.info(f"Initialized image generation model: {params.model_name}")
        
        # Create a detailed prompt
        prompt = self._create_image_prompt(story, setting, params.style)
        
        # Attempt to generate with retries
        attempt = 0
        last_error = None
        
        while attempt < self.MAX_RETRIES:
            try:
                # Generate the image with correct parameters according to the API
                # Using only the parameters proven to work in test_google_apis.py
                response = model.generate_images(
                    prompt=prompt,
                    number_of_images=params.samples,
                    add_watermark=params.add_watermark
                )
                
                # Process the images - response is already an iterable of PIL Images
                images = []
                for i, image in enumerate(response):
                    images.append(image)
                    
                    # Save the image if a path is provided
                    if save_path:
                        self._save_pil_image(image, save_path, i)
                
                # Build metadata
                metadata = {
                    "model": params.model_name,
                    "style": params.style,
                    "prompt": prompt,
                    "setting": setting,
                    "timestamp": time.time(),
                }
                
                logger.info(f"Successfully generated {params.samples} image(s)")
                return images, metadata
            
            except Exception as e:
                attempt += 1
                last_error = e
                logger.warning(f"Image generation attempt {attempt}/{self.MAX_RETRIES} failed: {str(e)}")
                
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)  # Exponential backoff
        
        # If we get here, all retries failed
        error_msg = f"Failed to generate image after {self.MAX_RETRIES} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _save_pil_image(self, pil_image: Any, base_path: str, index: int = 0) -> str:
        """Save PIL Image to file.
        
        Args:
            pil_image: PIL Image object
            base_path: Base path for saving
            index: Index for multiple images
            
        Returns:
            Path where image was saved
        """
        # Create timestamp-based filename
        timestamp = int(time.time())
        
        # If base_path includes a specific filename structure, use it
        if base_path.endswith('.png'):
            # Replace trailing .png with _index.png
            base_without_ext = base_path[:-4]
            if index > 0:
                full_path = f"{base_without_ext}_{index}.png"
            else:
                full_path = base_path
        else:
            # Otherwise, create a filename
            filename = f"{timestamp}_{index}.png"
            # If base_path is a directory, append filename
            if os.path.isdir(base_path):
                full_path = os.path.join(base_path, filename)
            else:
                # Ensure path ends with / before adding filename
                full_path = os.path.join(base_path, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
        
        # Save the image (without specifying format)
        pil_image.save(full_path)
        
        logger.info(f"Saved image to {full_path}")
        return full_path


def create_simple_test(style: str = "digital-art") -> None:
    """Create a simple test to verify the image generation functionality.
    
    This test mirrors the test_google_apis.py implementation to ensure 
    baseline functionality works.
    """
    try:
        logger.info("Running simple test with basic prompt...")
        
        # Initialize the image generator
        image_generator = ImageGenerator()
        
        # Create a very simple prompt
        test_prompt = "A solarpunk city with vertical gardens and solar panels"
        
        # Create the model directly following test_google_apis.py approach
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        
        # Generate with minimal parameters
        logger.info(f"Generating test image with prompt: '{test_prompt}'")
        response = model.generate_images(
            prompt=test_prompt,
            number_of_images=1,
            add_watermark=True
        )
        
        # Verify response
        if response is not None:
            # The response is already an iterable of images
            # Save the first image (there should be only one)
            timestamp = int(time.time())
            save_path = str(OUTPUT_DIR / f"test_basic_{timestamp}.png")
            response[0].save(save_path)
            
            logger.info(f"Simple test successful! Image saved to {save_path}")
            print(f"\nTest image saved to: {save_path}")
            return True
        else:
            logger.error("Simple test failed: No image generated")
            return False
            
    except Exception as e:
        logger.error(f"Simple test failed with error: {str(e)}")
        return False


def generate_test_images() -> None:
    """Generate sample images from solarpunk stories for testing."""
    # First run a simple test to verify the API works
    if not create_simple_test():
        print("Basic image generation test failed. Cannot proceed with story-based images.")
        return
        
    print("\nBasic image generation test succeeded. Proceeding with story-based images...")
    
    # Initialize the generators
    story_generator = StoryGenerator()
    image_generator = ImageGenerator()
    
    # Create parameters for different types of stories and images
    settings = ["urban", "coastal", "forest", "desert", "rural"]
    themes_list = [
        ["renewable energy", "community gardens", "localized production"],
        ["ocean conservation", "floating communities", "tidal energy"],
        ["forest stewardship", "ecological monitoring", "natural architecture"],
        ["water conservation", "solar power", "desert greening"],
        ["sustainable agriculture", "community ownership", "appropriate technology"]
    ]
    
    # Image styles to test
    styles = ["digital-art", "watercolor", "stylized"]
    
    # Check if a specific setting and style was requested
    setting_input = sys.argv[1] if len(sys.argv) > 1 else "all"
    style_input = sys.argv[2] if len(sys.argv) > 2 else "digital-art"
    
    # Filter settings if specific one requested
    if setting_input != "all":
        if setting_input in settings:
            selected_indices = [settings.index(setting_input)]
        else:
            logger.error(f"Unknown setting: {setting_input}")
            return
    else:
        selected_indices = range(len(settings))
    
    # Filter styles if specific one requested
    if style_input not in styles:
        style_input = "digital-art"
    
    # Process each selected setting
    for i in selected_indices:
        setting = settings[i]
        themes = themes_list[i]
        
        try:
            # Generate a story
            logger.info(f"Generating story for {setting} setting...")
            story_params = StoryParameters(
                max_chars=280,
                themes=themes,
                setting=setting,
                ai_role="collaborative",
                tone="hopeful"
            )
            
            story, story_metadata = story_generator.generate_story(story_params)
            
            # Display the generated story
            print("\n" + "="*80)
            print(f"SOLARPUNK STORY - {setting.upper()} SETTING")
            print("="*80)
            print(story)
            print("-"*80)
            
            # Generate an image based on the story
            logger.info(f"Generating {style_input} image for {setting} setting...")
            image_params = ImageParameters(
                style=style_input,
                samples=1,
                add_watermark=True
            )
            
            # Create a timestamp-based filename
            timestamp = int(time.time())
            save_path = str(OUTPUT_DIR / f"{setting}_{style_input}_{timestamp}.png")
            
            # Generate and save the image
            images, image_metadata = image_generator.generate_image(
                story=story,
                setting=setting,
                params=image_params,
                save_path=save_path
            )
            
            print(f"Image generated and saved to: {save_path}")
            print(f"Image style: {image_metadata['style']}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error processing {setting} setting: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("Solarpunk Image Generator - Testing Tool")
    print("========================================")
    print("Usage: uv run src/image_generator.py [setting] [style]")
    print("Available settings: urban, coastal, forest, desert, rural, all")
    print("Available styles: digital-art, watercolor, stylized, solarpunk-nouveau, retro-futurism, isometric")
    print("Default: all settings with digital-art style")
    
    generate_test_images() 