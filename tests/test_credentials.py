"""Tests for credential management.

This test module verifies the functionality of the credential management system.
"""

import os
import tempfile
from typing import Dict, Generator, cast
from pathlib import Path

import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch

from src.utils.credentials import CredentialManager


@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    """Fixture to set up mock environment variables.
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setenv("TWITTER_API_KEY", "test_api_key")
    monkeypatch.setenv("TWITTER_API_SECRET", "test_api_secret")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "test_access_token")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET", "test_access_token_secret")
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "test_bearer_token")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "test_credentials_path.json")


@pytest.fixture
def temp_env_file() -> Generator[str, None, None]:
    """Fixture to create a temporary .env file.
    
    Yields:
        Path to temporary .env file
    """
    with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as temp_file:
        temp_file.write(b"""
TWITTER_API_KEY=env_file_api_key
TWITTER_API_SECRET=env_file_api_secret
TWITTER_ACCESS_TOKEN=env_file_access_token
TWITTER_ACCESS_TOKEN_SECRET=env_file_access_token_secret
TWITTER_BEARER_TOKEN=env_file_bearer_token
GOOGLE_APPLICATION_CREDENTIALS=env_file_credentials_path.json
""")
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up
    os.unlink(temp_path)


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """Fixture to create a temporary config YAML file.
    
    Yields:
        Path to temporary config file
    """
    config_data = {
        "api": {
            "google_cloud": {
                "credentials_path": "config_file_credentials_path.json",
                "project_id": "test-project"
            },
            "twitter": {
                "api_version": "2"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
        yaml.dump(config_data, temp_file)
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up
    os.unlink(temp_path)


def test_credential_manager_init() -> None:
    """Test basic initialization of CredentialManager."""
    manager = CredentialManager()
    assert manager.env_file is None
    assert manager.config_file is None
    assert manager.config == {}


def test_credential_manager_with_env_file(temp_env_file: str) -> None:
    """Test CredentialManager with .env file.
    
    Args:
        temp_env_file: Path to temporary .env file
    """
    manager = CredentialManager(env_file=temp_env_file)
    assert manager.env_file == temp_env_file
    
    # Check that values from .env file were loaded
    assert os.environ.get("TWITTER_API_KEY") == "env_file_api_key"
    assert os.environ.get("TWITTER_API_SECRET") == "env_file_api_secret"


def test_credential_manager_with_config_file(temp_config_file: str) -> None:
    """Test CredentialManager with config file.
    
    Args:
        temp_config_file: Path to temporary config file
    """
    manager = CredentialManager(config_file=temp_config_file)
    assert manager.config_file == temp_config_file
    
    # Check that config was loaded
    assert manager.config["api"]["google_cloud"]["credentials_path"] == "config_file_credentials_path.json"
    assert manager.config["api"]["google_cloud"]["project_id"] == "test-project"


def test_get_env(mock_env_vars: None) -> None:
    """Test get_env method.
    
    Args:
        mock_env_vars: Mock environment variables fixture
    """
    manager = CredentialManager()
    
    # Test getting existing variable
    assert manager.get_env("TWITTER_API_KEY") == "test_api_key"
    
    # Test getting non-existent variable
    assert manager.get_env("NON_EXISTENT_VAR") is None
    
    # Test getting non-existent variable with default
    assert manager.get_env("NON_EXISTENT_VAR", "default_value") == "default_value"


def test_get_required_env(mock_env_vars: None) -> None:
    """Test get_required_env method.
    
    Args:
        mock_env_vars: Mock environment variables fixture
    """
    manager = CredentialManager()
    
    # Test getting existing variable
    assert manager.get_required_env("TWITTER_API_KEY") == "test_api_key"
    
    # Test getting non-existent variable (should raise ValueError)
    with pytest.raises(ValueError):
        manager.get_required_env("NON_EXISTENT_VAR")


def test_get_twitter_credentials(mock_env_vars: None) -> None:
    """Test get_twitter_credentials method.
    
    Args:
        mock_env_vars: Mock environment variables fixture
    """
    manager = CredentialManager()
    credentials = manager.get_twitter_credentials()
    
    assert credentials["api_key"] == "test_api_key"
    assert credentials["api_secret"] == "test_api_secret"
    assert credentials["access_token"] == "test_access_token"
    assert credentials["access_token_secret"] == "test_access_token_secret"
    assert credentials["bearer_token"] == "test_bearer_token"


def test_get_google_cloud_credentials(mock_env_vars: None) -> None:
    """Test get_google_cloud_credentials method.
    
    Args:
        mock_env_vars: Mock environment variables fixture
    """
    manager = CredentialManager()
    credentials = manager.get_google_cloud_credentials()
    
    assert credentials["credentials_path"] == "test_credentials_path.json"


def test_get_google_cloud_credentials_from_config(temp_config_file: str) -> None:
    """Test get_google_cloud_credentials method using config file.
    
    Args:
        temp_config_file: Path to temporary config file
    """
    # Create manager with config file but no env var
    manager = CredentialManager(config_file=temp_config_file)
    
    # Should use config file value as fallback
    credentials = manager.get_google_cloud_credentials()
    assert credentials["credentials_path"] == "config_file_credentials_path.json" 