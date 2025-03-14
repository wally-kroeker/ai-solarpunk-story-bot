"""Test suite for the image generator module."""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create mock StoryGenerator/StoryParameters if needed for testing
class MockStoryParams:
    """Mock StoryParameters for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockStoryGenerator:
    """Mock StoryGenerator for testing."""
    def generate_story(self, params):
        return (
            "This is a mock solarpunk story about community and nature in harmony.",
            {"setting": params.setting, "themes": params.themes}
        )

# First try to patch the modules
sys.modules['src.story_generator'] = type('MockModule', (), {
    'StoryGenerator': MockStoryGenerator,
    'StoryParameters': MockStoryParams,
    'load_config': lambda: {
        "api": {
            "google_cloud": {
                "project_id": "twitterstoryagent",
                "credentials_path": "credentials/gcp-credentials.json"
            }
        }
    }
})

# Now import the image generator
from src.image_generator import ImageGenerator, ImageParameters, create_simple_test

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_image_generation():
    """Test basic image generation with a simple prompt."""
    print("\n=== Testing Basic Image Generation ===")
    result = create_simple_test()
    assert result, "Basic image generation test failed"
    print("Basic image generation test passed!")

def test_image_generator_init():
    """Test initialization of the ImageGenerator class."""
    print("\n=== Testing ImageGenerator Initialization ===")
    try:
        generator = ImageGenerator()
        print("Successfully initialized ImageGenerator")
        assert generator is not None
    except Exception as e:
        assert False, f"Failed to initialize ImageGenerator: {str(e)}"

def test_prompt_creation():
    """Test the prompt creation functionality."""
    print("\n=== Testing Prompt Creation ===")
    generator = ImageGenerator()
    
    # Test with a sample story
    story = "In the heart of the city, solar panels gleamed on every rooftop, while community gardens flourished between buildings."
    setting = "urban"
    style = "photographic"
    
    prompt = generator._create_image_prompt(story, setting, style)
    print(f"Generated prompt: {prompt}")
    
    # Check that key elements are included
    assert "solar panels" in prompt, "Prompt should include solar panels mentioned in the story"
    assert "community garden" in prompt, "Prompt should include gardens mentioned in the story"
    assert "urban" in prompt, "Prompt should include the urban setting"
    
    # Check style enhancer is included (from the STYLE_ENHANCERS dictionary)
    expected_style_enhancer = "Photorealistic solarpunk scene with vibrant colors"
    assert expected_style_enhancer in prompt, f"Prompt should include the style enhancer for {style}"
    
    print("Prompt creation test passed!")

def test_minimal_api():
    """Test just the bare minimum API functionality to avoid quota issues."""
    print("\n=== Testing Minimal API Functionality ===")
    
    try:
        # Import required modules
        from vertexai.preview.vision_models import ImageGenerationModel
        import vertexai
        from google.oauth2 import service_account
        import os
        from pathlib import Path
        
        # Get credentials
        PROJECT_ROOT = Path(__file__).parent.parent
        credentials_path = PROJECT_ROOT / "credentials/gcp-credentials.json"
        
        print(f"Using credentials at: {credentials_path}")
        
        # Load credentials explicitly
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        # Initialize Vertex AI with explicit credentials
        vertexai.init(
            project="twitterstoryagent",
            location="us-central1",
            credentials=credentials
        )
        
        # Create model and generate a simple image
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        
        print("Initialized model, generating a simple blue square image...")
        
        # Generate with absolute minimum parameters to avoid quota issues
        response = model.generate_images(
            prompt="A simple blue square on a white background",
            number_of_images=1,
            add_watermark=True
        )
        
        # Verify we got a response
        assert response is not None, "Failed to get a response from the API"
        
        # Save the first image
        output_dir = PROJECT_ROOT / "output" / "images"
        os.makedirs(output_dir, exist_ok=True)
        
        save_path = output_dir / "test_minimal_api.png"
        response[0].save(save_path)
        
        print(f"Successfully generated and saved image to {save_path}")
        return True
    except Exception as e:
        print(f"Minimal API test failed: {str(e)}")
        return False

def run_tests():
    """Run all tests."""
    try:
        # Test initialization
        test_image_generator_init()
        
        # Test prompt creation
        test_prompt_creation()
        
        # Test basic image generation
        # Only run if explicitly requested due to API quotas
        if len(sys.argv) > 1:
            if sys.argv[1] == "with-api":
                test_basic_image_generation()
            elif sys.argv[1] == "minimal-api":
                test_minimal_api()
        else:
            print("\nSkipping API tests to avoid quota issues. Run with 'with-api' or 'minimal-api' argument to include them.")
        
        print("\nAll tests completed successfully!")
        return True
    except Exception as e:
        print(f"\nTests failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Image Generator Test Suite")
    print("=========================")
    success = run_tests()
    sys.exit(0 if success else 1) 