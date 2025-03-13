import os
import pytest
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.oauth2 import service_account


def test_gemini_pro():
    """Test Gemini Pro API access with a simple prompt."""
    try:
        # Get the absolute path to the credentials file
        credentials_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "credentials/gcp-credentials.json"
        ))
        
        # Load the credentials explicitly
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        
        # Initialize Vertex AI with explicit credentials
        vertexai.init(
            project="twitterstoryagent", 
            location="us-central1",
            credentials=credentials
        )
        
        # Import here to avoid circular imports
        from vertexai.preview.generative_models import GenerativeModel
        
        # Create model and generate content
        model = GenerativeModel("gemini-pro")
        response = model.generate_content("Write a one-sentence story about a robot.")
        
        # Simple verification
        assert response.text
        print(f"Gemini Pro response: {response.text}")
    except Exception as e:
        pytest.fail(f"Gemini Pro test failed: {str(e)}")


def test_imagen():
    """Test Imagen API access."""
    try:
        # Get the absolute path to the credentials file
        credentials_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "credentials/gcp-credentials.json"
        ))
        
        # Load the credentials explicitly
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        
        # Initialize Vertex AI with explicit credentials
        vertexai.init(
            project="twitterstoryagent", 
            location="us-central1",
            credentials=credentials
        )
        
        # Create model using the correct model name from the Studio
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        
        # Generate an image with minimal parameters
        response = model.generate_images(
            prompt="A blue square",
            number_of_images=1,
            add_watermark=True
        )
        
        # Simple verification
        assert response is not None
        print("Imagen test successful!")
        
    except Exception as e:
        pytest.fail(f"Imagen test failed: {str(e)}") 