"""Secure credential management module.

This module provides utilities for loading and managing API credentials
from environment variables or .env files.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, cast

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manager for securely handling API credentials.
    
    This class handles loading credentials from environment variables
    or .env files, with support for configuration from YAML files.
    """
    
    def __init__(
        self, 
        env_file: Optional[str] = None,
        config_file: Optional[str] = None
    ) -> None:
        """Initialize the credential manager.
        
        Args:
            env_file: Optional path to .env file
            config_file: Optional path to configuration YAML file
        """
        self.env_file = env_file
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        # Load environment variables from .env file if provided
        if env_file:
            self._load_env_file(env_file)
        
        # Load configuration from YAML file if provided
        if config_file:
            self._load_config_file(config_file)
            
        logger.info("Credential manager initialized")
    
    def _load_env_file(self, env_file: str) -> None:
        """Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file
        """
        env_path = Path(env_file)
        if not env_path.exists():
            logger.warning(f"Env file not found: {env_file}")
            return
            
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_file}")
    
    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration YAML file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_file}")
            return
            
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_file}")
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get value from environment variables.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Value from environment variable or default
        """
        value = os.environ.get(key, default)
        if value is None:
            logger.warning(f"Environment variable not found: {key}")
        return value
    
    def get_required_env(self, key: str) -> str:
        """Get required value from environment variables.
        
        Args:
            key: Environment variable key
            
        Returns:
            Value from environment variable
            
        Raises:
            ValueError: If the environment variable is not set
        """
        value = self.get_env(key)
        if value is None:
            logger.error(f"Required environment variable not found: {key}")
            raise ValueError(f"Required environment variable not set: {key}")
        return value
    
    def get_twitter_credentials(self) -> Dict[str, str]:
        """Get Twitter API credentials.
        
        Returns:
            Dictionary containing Twitter API credentials
            
        Raises:
            ValueError: If required credentials are missing
        """
        return {
            "api_key": self.get_required_env("TWITTER_API_KEY"),
            "api_secret": self.get_required_env("TWITTER_API_SECRET"),
            "access_token": self.get_required_env("TWITTER_ACCESS_TOKEN"),
            "access_token_secret": self.get_required_env("TWITTER_ACCESS_TOKEN_SECRET"),
            "bearer_token": self.get_env("TWITTER_BEARER_TOKEN"),
        }
    
    def get_google_cloud_credentials(self) -> Dict[str, str]:
        """Get Google Cloud credentials.
        
        Returns:
            Dictionary containing Google Cloud credentials
            
        Raises:
            ValueError: If required credentials are missing
        """
        credentials_path = self.get_env(
            "GOOGLE_APPLICATION_CREDENTIALS", 
            self.config.get("api", {}).get("google_cloud", {}).get("credentials_path")
        )
        
        if not credentials_path:
            logger.error("Google Cloud credentials path not found")
            raise ValueError("Google Cloud credentials path not set")
        
        return {"credentials_path": cast(str, credentials_path)} 