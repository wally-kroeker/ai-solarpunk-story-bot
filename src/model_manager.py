#!/usr/bin/env python
"""
Model Manager for AI Solarpunk Story Bot

This module handles discovering available models from Vertex AI
and managing model selection for story and image generation.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Import Vertex AI libraries
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview.generative_models import ModelGardenModel
from vertexai.preview.vision_models import ImageGenerationModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path for storing model configuration
CONFIG_DIR = Path(__file__).parent.parent / "config"
MODEL_CONFIG_PATH = CONFIG_DIR / "models.json"

class ModelManager:
    """Manager for Vertex AI model discovery and selection."""
    
    def __init__(self):
        """Initialize the model manager."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.load_config()
    
    def load_config(self) -> None:
        """Load saved model configuration."""
        try:
            if MODEL_CONFIG_PATH.exists():
                with open(MODEL_CONFIG_PATH, 'r') as f:
                    self.config = json.load(f)
            else:
                # Default configuration
                self.config = {
                    "text_model": "gemini-1.5-pro-preview",
                    "image_model": "imagen-3.0-generate-001",
                    "available_text_models": [],
                    "available_image_models": []
                }
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading model configuration: {e}")
            # Fall back to defaults
            self.config = {
                "text_model": "gemini-1.5-pro-preview",
                "image_model": "imagen-3.0-generate-001",
                "available_text_models": [],
                "available_image_models": []
            }
    
    def save_config(self) -> None:
        """Save current model configuration."""
        try:
            with open(MODEL_CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving model configuration: {e}")
    
    def get_text_model(self) -> str:
        """Get the currently selected text model."""
        return self.config.get("text_model", "gemini-1.5-pro-preview")
    
    def get_image_model(self) -> str:
        """Get the currently selected image model."""
        return self.config.get("image_model", "imagen-3.0-generate-001")
    
    def set_text_model(self, model_name: str) -> None:
        """Set the text model to use for generation."""
        self.config["text_model"] = model_name
        self.save_config()
    
    def set_image_model(self, model_name: str) -> None:
        """Set the image model to use for generation."""
        self.config["image_model"] = model_name
        self.save_config()
    
    def discover_available_models(self) -> Tuple[List[str], List[str]]:
        """Discover available models from Vertex AI."""
        try:
            # Get text generation models
            text_models = self._discover_text_models()
            # Get image generation models
            image_models = self._discover_image_models()
            
            # Update config
            self.config["available_text_models"] = text_models
            self.config["available_image_models"] = image_models
            self.save_config()
            
            return text_models, image_models
        
        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            return [], []
    
    def _discover_text_models(self) -> List[str]:
        """Discover available text generation models."""
        # List of known text models - will be replaced with API call
        models = [
            "gemini-1.0-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-pro-preview",
            "gemini-2.0-flash-001",
            "gemini-2.0-flash-002",
            "gemini-2.0-flash-thinking-exp-01-21",
            "gemini-2.0-pro-001",
            "gemini-2.0-pro-002"
        ]
        
        try:
            # In a real implementation, we would use the Vertex AI API
            # to discover available models dynamically
            # For example:
            # client = aiplatform.gapic.ModelServiceClient()
            # models = client.list_models(...)
            
            return models
        except Exception as e:
            logger.error(f"Error discovering text models: {e}")
            return models  # Return hardcoded list as fallback
    
    def _discover_image_models(self) -> List[str]:
        """Discover available image generation models."""
        # List of known image models - will be replaced with API call
        models = [
            "imagen-3.0-generate-001",
            "imagen-3.0-fast-generate-001"
        ]
        
        try:
            # In a real implementation, we would use the Vertex AI API
            # to discover available models dynamically
            
            return models
        except Exception as e:
            logger.error(f"Error discovering image models: {e}")
            return models  # Return hardcoded list as fallback
    
    def get_available_text_models(self) -> List[str]:
        """Get list of available text models."""
        models = self.config.get("available_text_models", [])
        if not models:
            text_models, _ = self.discover_available_models()
            models = text_models
        return models
    
    def get_available_image_models(self) -> List[str]:
        """Get list of available image models."""
        models = self.config.get("available_image_models", [])
        if not models:
            _, image_models = self.discover_available_models()
            models = image_models
        return models

def main():
    """Command line interface for model management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.model_manager [command]")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = ModelManager()
    
    if command == "list":
        # List all models and currently selected ones
        text_models = manager.get_available_text_models()
        image_models = manager.get_available_image_models()
        
        for model in text_models:
            print(f"TEXT: {model}")
        
        for model in image_models:
            print(f"IMAGE: {model}")
        
        print(f"SELECTED: Text Model: {manager.get_text_model()}")
        print(f"SELECTED: Image Model: {manager.get_image_model()}")
    
    elif command == "text-models":
        # List available text models
        for model in manager.get_available_text_models():
            print(model)
    
    elif command == "image-models":
        # List available image models
        for model in manager.get_available_image_models():
            print(model)
    
    elif command == "set-text-model" and len(sys.argv) > 2:
        # Set text model
        model_name = sys.argv[2]
        manager.set_text_model(model_name)
        print(f"Text model set to: {model_name}")
    
    elif command == "set-image-model" and len(sys.argv) > 2:
        # Set image model
        model_name = sys.argv[2]
        manager.set_image_model(model_name)
        print(f"Image model set to: {model_name}")
    
    elif command == "refresh":
        # Refresh model list
        text_models, image_models = manager.discover_available_models()
        print(f"Discovered {len(text_models)} text models and {len(image_models)} image models")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 