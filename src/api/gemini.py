"""Gemini Pro API client module.

This module provides a client for interacting with Google's Gemini Pro
large language model via the Vertex AI API.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, cast

import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GeminiProClient:
    """Client for Google's Gemini Pro API.
    
    This client handles authentication and provides methods for generating
    text content with the Gemini Pro language model.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        credentials_path: Optional[str] = None,
        model_name: str = "gemini-pro",
    ) -> None:
        """Initialize the Gemini Pro client.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            credentials_path: Path to Google Cloud credentials JSON file
            model_name: Name of the Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.credentials_path = credentials_path
        self.model_name = model_name
        
        # Initialize Vertex AI
        self._initialize_vertex_ai()
        
        # Initialize the model
        self.model = GenerativeModel(model_name)
        logger.info(f"Gemini Pro client initialized with model: {model_name}")
    
    def _initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI with appropriate credentials.
        
        Raises:
            FileNotFoundError: If credentials file not found
            Exception: If initialization fails
        """
        try:
            # Use explicit credentials if provided
            if self.credentials_path:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=credentials
                )
            else:
                # Use default credentials
                vertexai.init(
                    project=self.project_id,
                    location=self.location
                )
                
            logger.info(f"Vertex AI initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {e}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 300,
        top_p: float = 0.95,
        top_k: int = 40,
    ) -> str:
        """Generate text using the Gemini Pro model.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Controls randomness (0.0 to 1.0)
            max_output_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated text content
            
        Raises:
            Exception: If the API request fails
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_output_tokens,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini Pro")
                return ""
                
            logger.info("Successfully generated text with Gemini Pro")
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini Pro: {e}")
            raise
    
    def retry_with_backoff(
        self,
        prompt: str,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        temperature: float = 0.7,
        max_output_tokens: int = 300,
        top_p: float = 0.95,
        top_k: int = 40,
    ) -> str:
        """Generate text with exponential backoff retry logic.
        
        Args:
            prompt: The prompt to send to the model
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            backoff_factor: Factor to increase delay with each retry
            temperature: Controls randomness (0.0 to 1.0)
            max_output_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated text content
            
        Raises:
            Exception: If all retry attempts fail
        """
        import time
        
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.generate_text(
                    prompt=prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    top_p=top_p,
                    top_k=top_k
                )
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor
        
        logger.error(f"All {max_retries} attempts failed")
        if last_exception:
            raise last_exception
        
        # This should never happen, but satisfies type checking
        return "" 