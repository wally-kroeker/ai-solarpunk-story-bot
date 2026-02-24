"""
Validation module for AI Solarpunk Story Bot.

This module provides comprehensive validation functions for continuity files,
world data, and other critical components to ensure data integrity and prevent corruption.
"""

import json
import logging
import os
import shutil
import asyncio
import time
import random
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Set up logging
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class LLMAPIError(Exception):
    """Custom exception for LLM API errors."""
    pass

class LLMTimeoutError(LLMAPIError):
    """Custom exception for LLM API timeout errors."""
    pass

class LLMRateLimitError(LLMAPIError):
    """Custom exception for LLM API rate limit errors."""
    pass

class LLMConnectionError(LLMAPIError):
    """Custom exception for LLM API connection errors."""
    pass

class LLMInvalidResponseError(LLMAPIError):
    """Custom exception for invalid LLM API responses."""
    pass

class ContinuityFileValidator:
    """Validator for continuity files."""
    
    # Required top-level keys
    REQUIRED_KEYS = ['last_story_id', 'characters', 'story_log']
    
    # Required character keys
    REQUIRED_CHARACTER_KEYS = [
        'name', 'archetype', 'backstory', 'appearance', 
        'faction', 'traits', 'story_appearances'
    ]
    
    # Required story log keys
    REQUIRED_STORY_KEYS = [
        'id', 'title', 'summary', 'era', 'characters', 'timestamp'
    ]
    
    @staticmethod
    def validate_continuity_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate that the continuity file is in the correct format.
        
        Args:
            file_path: Path to the continuity file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, f"Continuity file not found: {file_path}"
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False, f"Cannot read continuity file: {file_path}"
            
            # Load and parse JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON format: {str(e)}"
            except UnicodeDecodeError as e:
                return False, f"File encoding error: {str(e)}"
            
            # Validate top-level structure
            is_valid, error_msg = ContinuityFileValidator._validate_top_level(data)
            if not is_valid:
                return False, error_msg
            
            # Validate characters
            is_valid, error_msg = ContinuityFileValidator._validate_characters(data['characters'])
            if not is_valid:
                return False, error_msg
            
            # Validate story log
            is_valid, error_msg = ContinuityFileValidator._validate_story_log(data['story_log'])
            if not is_valid:
                return False, error_msg
            
            # Validate data consistency
            is_valid, error_msg = ContinuityFileValidator._validate_consistency(data)
            if not is_valid:
                return False, error_msg
            
            logger.info(f"Continuity file validation successful: {file_path}")
            return True, "Validation successful"
            
        except Exception as e:
            error_msg = f"Unexpected error validating continuity file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def _validate_top_level(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate top-level structure of continuity data."""
        if not isinstance(data, dict):
            return False, "Continuity data must be a JSON object"
        
        # Check required keys
        for key in ContinuityFileValidator.REQUIRED_KEYS:
            if key not in data:
                return False, f"Missing required key: {key}"
        
        # Check data types
        if not isinstance(data['last_story_id'], int):
            return False, "'last_story_id' must be an integer"
        
        if not isinstance(data['characters'], list):
            return False, "'characters' must be a list"
        
        if not isinstance(data['story_log'], list):
            return False, "'story_log' must be a list"
        
        # Validate last_story_id is non-negative
        if data['last_story_id'] < 0:
            return False, "'last_story_id' must be non-negative"
        
        return True, ""
    
    @staticmethod
    def _validate_characters(characters: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate character entries."""
        character_names = set()
        
        for i, char in enumerate(characters):
            if not isinstance(char, dict):
                return False, f"Character at index {i} must be an object"
            
            # Check required keys
            for key in ContinuityFileValidator.REQUIRED_CHARACTER_KEYS:
                if key not in char:
                    return False, f"Character at index {i} missing required key: {key}"
            
            # Validate data types
            if not isinstance(char['name'], str) or not char['name'].strip():
                return False, f"Character at index {i}: 'name' must be a non-empty string"
            
            if not isinstance(char['archetype'], str):
                return False, f"Character at index {i}: 'archetype' must be a string"
            
            if not isinstance(char['backstory'], str):
                return False, f"Character at index {i}: 'backstory' must be a string"
            
            if not isinstance(char['appearance'], str):
                return False, f"Character at index {i}: 'appearance' must be a string"
            
            if char['faction'] is not None and not isinstance(char['faction'], str):
                return False, f"Character at index {i}: 'faction' must be a string or null"
            
            if not isinstance(char['traits'], list):
                return False, f"Character at index {i}: 'traits' must be a list"
            
            if not isinstance(char['story_appearances'], list):
                return False, f"Character at index {i}: 'story_appearances' must be a list"
            
            # Check for duplicate names
            name = char['name'].strip()
            if name in character_names:
                return False, f"Duplicate character name found: {name}"
            character_names.add(name)
            
            # Validate story appearances are integers
            for j, story_id in enumerate(char['story_appearances']):
                if not isinstance(story_id, int) or story_id < 1:
                    return False, f"Character '{name}': story_appearances[{j}] must be a positive integer"
        
        return True, ""
    
    @staticmethod
    def _validate_story_log(story_log: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate story log entries."""
        story_ids = set()
        
        for i, story in enumerate(story_log):
            if not isinstance(story, dict):
                return False, f"Story at index {i} must be an object"
            
            # Check required keys
            for key in ContinuityFileValidator.REQUIRED_STORY_KEYS:
                if key not in story:
                    return False, f"Story at index {i} missing required key: {key}"
            
            # Validate data types
            if not isinstance(story['id'], int) or story['id'] < 1:
                return False, f"Story at index {i}: 'id' must be a positive integer"
            
            if not isinstance(story['title'], str) or not story['title'].strip():
                return False, f"Story at index {i}: 'title' must be a non-empty string"
            
            if not isinstance(story['summary'], str):
                return False, f"Story at index {i}: 'summary' must be a string"
            
            if not isinstance(story['era'], int) or story['era'] < 0:
                return False, f"Story at index {i}: 'era' must be a non-negative integer"
            
            if not isinstance(story['characters'], list):
                return False, f"Story at index {i}: 'characters' must be a list"
            
            if not isinstance(story['timestamp'], str):
                return False, f"Story at index {i}: 'timestamp' must be a string"
            
            # Check for duplicate IDs
            story_id = story['id']
            if story_id in story_ids:
                return False, f"Duplicate story ID found: {story_id}"
            story_ids.add(story_id)
            
            # Validate character names in story
            for j, char_name in enumerate(story['characters']):
                if not isinstance(char_name, str) or not char_name.strip():
                    return False, f"Story {story_id}: characters[{j}] must be a non-empty string"
            
            # Validate timestamp format (basic check)
            try:
                # Try to parse as ISO format datetime
                datetime.fromisoformat(story['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                return False, f"Story {story_id}: invalid timestamp format"
        
        return True, ""
    
    @staticmethod
    def _validate_consistency(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data consistency between characters and story log."""
        # Build character name set
        character_names = {char['name'] for char in data['characters']}
        
        # Build story ID set
        story_ids = {story['id'] for story in data['story_log']}
        
        # Check that characters' story appearances reference valid stories
        for char in data['characters']:
            for story_id in char['story_appearances']:
                if story_id not in story_ids:
                    return False, f"Character '{char['name']}' references non-existent story ID: {story_id}"
        
        # Check that stories reference valid characters
        for story in data['story_log']:
            for char_name in story['characters']:
                if char_name not in character_names:
                    return False, f"Story {story['id']} references non-existent character: {char_name}"
        
        # Check that last_story_id is consistent with story log
        if data['story_log']:
            max_story_id = max(story['id'] for story in data['story_log'])
            if data['last_story_id'] != max_story_id:
                return False, f"last_story_id ({data['last_story_id']}) doesn't match max story ID ({max_story_id})"
        else:
            if data['last_story_id'] != 0:
                return False, f"last_story_id should be 0 when no stories exist"
        
        return True, ""

def create_backup(file_path: str) -> Optional[str]:
    """
    Create a backup of a file with timestamp.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to backup file if successful, None if failed
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Cannot backup non-existent file: {file_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {str(e)}")
        return None

def restore_from_backup(file_path: str, backup_path: Optional[str] = None) -> bool:
    """
    Restore a file from its most recent backup.
    
    Args:
        file_path: Path to the file to restore
        backup_path: Specific backup to restore from (optional)
        
    Returns:
        True if restoration successful, False otherwise
    """
    try:
        if backup_path and os.path.exists(backup_path):
            # Use specified backup
            target_backup = backup_path
        else:
            # Find most recent backup
            backup_pattern = f"{file_path}.backup_*"
            backups = glob.glob(backup_pattern)
            if not backups:
                logger.error(f"No backups found for {file_path}")
                return False
            
            # Sort by timestamp and get most recent
            backups.sort(reverse=True)
            target_backup = backups[0]
        
        shutil.copy2(target_backup, file_path)
        logger.info(f"Restored {file_path} from {target_backup}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to restore {file_path}: {str(e)}")
        return False

def validate_and_load_continuity(file_path: str, create_if_missing: bool = False) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Validate and load continuity file with automatic backup and recovery.
    
    Args:
        file_path: Path to continuity file
        create_if_missing: Whether to create a new file if missing
        
    Returns:
        Tuple of (success, data, message)
    """
    try:
        # If file doesn't exist and we should create it
        if not os.path.exists(file_path) and create_if_missing:
            logger.info(f"Creating new continuity file: {file_path}")
            default_data = {
                "last_story_id": 0,
                "characters": [],
                "story_log": []
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save default data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
            
            return True, default_data, "Created new continuity file"
        
        # Validate existing file
        is_valid, error_msg = ContinuityFileValidator.validate_continuity_file(file_path)
        
        if is_valid:
            # Load the validated data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return True, data, "Continuity file loaded successfully"
        else:
            logger.error(f"Continuity file validation failed: {error_msg}")
            
            # Try to restore from backup
            logger.info("Attempting to restore from backup...")
            if restore_from_backup(file_path):
                # Re-validate after restoration
                is_valid, error_msg = ContinuityFileValidator.validate_continuity_file(file_path)
                if is_valid:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return True, data, "Restored from backup and loaded successfully"
                else:
                    return False, None, f"Backup also invalid: {error_msg}"
            else:
                return False, None, f"Validation failed and no backup available: {error_msg}"
                
    except Exception as e:
        error_msg = f"Unexpected error loading continuity file: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg

class LLMErrorHandler:
    """Handles LLM API errors with retries, backoff, and fallback mechanisms."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ):
        """
        Initialize the LLM error handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            backoff_factor: Factor to multiply delay by after each failure
            max_delay: Maximum delay between retries
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter = jitter
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter (±20%)
            jitter_range = delay * 0.2
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def _classify_error(self, error: Exception) -> str:
        """Classify the type of error for appropriate handling."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network/connection errors
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable']):
            return 'connection'
        
        # Rate limiting
        if any(keyword in error_str for keyword in ['rate limit', 'quota', 'throttle', 'too many requests']):
            return 'rate_limit'
        
        # Authentication errors
        if any(keyword in error_str for keyword in ['auth', 'api key', 'unauthorized', 'forbidden']):
            return 'auth'
        
        # Server errors (5xx)
        if any(keyword in error_str for keyword in ['server error', '500', '502', '503', '504']):
            return 'server'
        
        # Client errors (4xx) - generally not retryable
        if any(keyword in error_str for keyword in ['400', '401', '403', '404', 'bad request']):
            return 'client'
        
        # Model-specific errors
        if any(keyword in error_str for keyword in ['model', 'invalid response', 'malformed']):
            return 'model'
        
        return 'unknown'
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if the error should be retried."""
        if attempt >= self.max_retries:
            return False
        
        error_type = self._classify_error(error)
        
        # Always retry these error types
        if error_type in ['connection', 'server', 'rate_limit']:
            return True
        
        # Sometimes retry these
        if error_type in ['unknown', 'model']:
            return True
        
        # Never retry these
        if error_type in ['auth', 'client']:
            return False
        
        return True
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        fallback_func: Optional[Callable] = None,
        fallback_args: Optional[Tuple] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic and optional fallback.
        
        Args:
            func: The function to execute
            *args: Arguments for the function
            fallback_func: Optional fallback function if all retries fail
            fallback_args: Arguments for the fallback function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from successful execution or fallback
            
        Raises:
            LLMAPIError: If all retries fail and no fallback is provided
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"LLM API call succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)
                
                logger.warning(f"LLM API attempt {attempt + 1} failed ({error_type}): {str(e)}")
                
                if not self._should_retry(e, attempt):
                    logger.error(f"Error not retryable or max attempts reached: {str(e)}")
                    break
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    
                    if asyncio.iscoroutinefunction(func):
                        await asyncio.sleep(delay)
                    else:
                        time.sleep(delay)
        
        # All retries failed, try fallback if available
        if fallback_func:
            logger.info("Attempting fallback mechanism...")
            try:
                fallback_args = fallback_args or ()
                if asyncio.iscoroutinefunction(fallback_func):
                    return await fallback_func(*fallback_args)
                else:
                    return fallback_func(*fallback_args)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                raise LLMAPIError(f"All retries and fallback failed. Last error: {str(last_error)}")
        
        # No fallback available
        if last_error:
            error_type = self._classify_error(last_error)
            if error_type == 'rate_limit':
                raise LLMRateLimitError(f"Rate limit exceeded after {self.max_retries} attempts: {str(last_error)}")
            elif error_type == 'connection':
                raise LLMConnectionError(f"Connection failed after {self.max_retries} attempts: {str(last_error)}")
            elif error_type == 'model':
                raise LLMInvalidResponseError(f"Invalid model response after {self.max_retries} attempts: {str(last_error)}")
            else:
                raise LLMAPIError(f"LLM API failed after {self.max_retries} attempts: {str(last_error)}")
        
        raise LLMAPIError("Unknown error occurred")

def generate_fallback_response(prompt: str, response_type: str = "generic") -> str:
    """
    Generate a fallback response when LLM is unavailable.
    
    Args:
        prompt: The original prompt
        response_type: Type of response needed ('story', 'character', 'summary', etc.)
        
    Returns:
        A fallback response
    """
    logger.info(f"Generating fallback response for type: {response_type}")
    
    fallback_templates = {
        'story': "A solarpunk community works together to build sustainable solutions for their future.",
        'character': "Name: Community Member\nAppearance: A hopeful individual with practical clothing\nTraits: resourceful, collaborative, optimistic\nBackstory: Someone working toward a sustainable future.",
        'summary': "A brief story about community collaboration and sustainable technology.",
        'title': "Community Futures",
        'image_prompt': "A vibrant solarpunk community with green technology and happy people working together",
        'generic': "A positive message about sustainability and community cooperation."
    }
    
    return fallback_templates.get(response_type, fallback_templates['generic'])

# Global error handler instance
default_llm_error_handler = LLMErrorHandler()

class WorldDataValidator:
    """Validator for world data structure and consistency."""
    
    @staticmethod
    def validate_technology(tech: Any, era_id: int) -> Tuple[bool, str]:
        """
        Validate a Technology object.
        
        Args:
            tech: Technology object to validate
            era_id: Expected era ID for this technology
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required attributes
            required_attrs = ['name', 'description', 'era', 'impact']
            for attr in required_attrs:
                if not hasattr(tech, attr):
                    return False, f"Technology missing required attribute: {attr}"
                
                value = getattr(tech, attr)
                # Special handling for era (can be 0) and strings
                if attr == 'era':
                    if value is None or not isinstance(value, int):
                        return False, f"Technology {attr} is invalid (must be integer)"
                elif isinstance(value, str):
                    if not value.strip():
                        return False, f"Technology {attr} is empty"
                else:
                    if value is None:
                        return False, f"Technology {attr} is empty or invalid"
            
            # Validate data types
            if not isinstance(tech.name, str):
                return False, f"Technology name must be string, got {type(tech.name)}"
            if not isinstance(tech.description, str):
                return False, f"Technology description must be string, got {type(tech.description)}"
            if not isinstance(tech.era, int):
                return False, f"Technology era must be int, got {type(tech.era)}"
            if not isinstance(tech.impact, str):
                return False, f"Technology impact must be string, got {type(tech.impact)}"
            
            # Validate era consistency
            if tech.era != era_id:
                return False, f"Technology {tech.name} era mismatch: expected {era_id}, got {tech.era}"
            
            return True, "Technology validation passed"
            
        except Exception as e:
            return False, f"Error validating technology: {str(e)}"
    
    @staticmethod
    def validate_faction(faction: Any) -> Tuple[bool, str]:
        """
        Validate a Faction object.
        
        Args:
            faction: Faction object to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required attributes
            required_attrs = ['name', 'description', 'values', 'technologies']
            for attr in required_attrs:
                if not hasattr(faction, attr):
                    return False, f"Faction missing required attribute: {attr}"
            
            # Validate data types
            if not isinstance(faction.name, str) or not faction.name.strip():
                return False, f"Faction name must be non-empty string, got {type(faction.name)}"
            if not isinstance(faction.description, str) or not faction.description.strip():
                return False, f"Faction description must be non-empty string, got {type(faction.description)}"
            if not isinstance(faction.values, list):
                return False, f"Faction values must be list, got {type(faction.values)}"
            if not isinstance(faction.technologies, list):
                return False, f"Faction technologies must be list, got {type(faction.technologies)}"
            
            # Validate list contents
            for i, value in enumerate(faction.values):
                if not isinstance(value, str) or not value.strip():
                    return False, f"Faction value at index {i} must be non-empty string"
            
            for i, tech in enumerate(faction.technologies):
                if not isinstance(tech, str) or not tech.strip():
                    return False, f"Faction technology at index {i} must be non-empty string"
            
            return True, "Faction validation passed"
            
        except Exception as e:
            return False, f"Error validating faction: {str(e)}"
    
    @staticmethod
    def validate_character_archetype(archetype: Any) -> Tuple[bool, str]:
        """
        Validate a CharacterArchetype object.
        
        Args:
            archetype: CharacterArchetype object to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required attributes
            required_attrs = ['name', 'description', 'typical_traits', 'common_factions']
            for attr in required_attrs:
                if not hasattr(archetype, attr):
                    return False, f"CharacterArchetype missing required attribute: {attr}"
            
            # Validate data types
            if not isinstance(archetype.name, str) or not archetype.name.strip():
                return False, f"CharacterArchetype name must be non-empty string, got {type(archetype.name)}"
            if not isinstance(archetype.description, str) or not archetype.description.strip():
                return False, f"CharacterArchetype description must be non-empty string, got {type(archetype.description)}"
            if not isinstance(archetype.typical_traits, list):
                return False, f"CharacterArchetype typical_traits must be list, got {type(archetype.typical_traits)}"
            if not isinstance(archetype.common_factions, list):
                return False, f"CharacterArchetype common_factions must be list, got {type(archetype.common_factions)}"
            
            # Validate list contents
            for i, trait in enumerate(archetype.typical_traits):
                if not isinstance(trait, str) or not trait.strip():
                    return False, f"CharacterArchetype trait at index {i} must be non-empty string"
            
            for i, faction in enumerate(archetype.common_factions):
                if not isinstance(faction, str) or not faction.strip():
                    return False, f"CharacterArchetype faction at index {i} must be non-empty string"
            
            return True, "CharacterArchetype validation passed"
            
        except Exception as e:
            return False, f"Error validating character archetype: {str(e)}"
    
    @staticmethod
    def validate_plot_seed(plot_seed: Any) -> Tuple[bool, str]:
        """
        Validate a PlotSeed object.
        
        Args:
            plot_seed: PlotSeed object to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required attributes
            required_attrs = ['premise', 'themes', 'potential_conflicts']
            for attr in required_attrs:
                if not hasattr(plot_seed, attr):
                    return False, f"PlotSeed missing required attribute: {attr}"
            
            # Validate data types
            if not isinstance(plot_seed.premise, str) or not plot_seed.premise.strip():
                return False, f"PlotSeed premise must be non-empty string, got {type(plot_seed.premise)}"
            if not isinstance(plot_seed.themes, list):
                return False, f"PlotSeed themes must be list, got {type(plot_seed.themes)}"
            if not isinstance(plot_seed.potential_conflicts, list):
                return False, f"PlotSeed potential_conflicts must be list, got {type(plot_seed.potential_conflicts)}"
            
            # Validate list contents
            for i, theme in enumerate(plot_seed.themes):
                if not isinstance(theme, str) or not theme.strip():
                    return False, f"PlotSeed theme at index {i} must be non-empty string"
            
            for i, conflict in enumerate(plot_seed.potential_conflicts):
                if not isinstance(conflict, str) or not conflict.strip():
                    return False, f"PlotSeed conflict at index {i} must be non-empty string"
            
            return True, "PlotSeed validation passed"
            
        except Exception as e:
            return False, f"Error validating plot seed: {str(e)}"
    
    @staticmethod
    def validate_era(era: Any) -> Tuple[bool, str]:
        """
        Validate an Era object.
        
        Args:
            era: Era object to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required attributes
            required_attrs = ['id', 'name', 'description', 'technologies', 'factions', 'archetypes', 'plot_seeds']
            for attr in required_attrs:
                if not hasattr(era, attr):
                    return False, f"Era missing required attribute: {attr}"
            
            # Validate data types
            if not isinstance(era.id, int):
                return False, f"Era id must be int, got {type(era.id)}"
            if not isinstance(era.name, str) or not era.name.strip():
                return False, f"Era name must be non-empty string, got {type(era.name)}"
            if not isinstance(era.description, str) or not era.description.strip():
                return False, f"Era description must be non-empty string, got {type(era.description)}"
            if not isinstance(era.technologies, list):
                return False, f"Era technologies must be list, got {type(era.technologies)}"
            if not isinstance(era.factions, list):
                return False, f"Era factions must be list, got {type(era.factions)}"
            if not isinstance(era.archetypes, list):
                return False, f"Era archetypes must be list, got {type(era.archetypes)}"
            if not isinstance(era.plot_seeds, list):
                return False, f"Era plot_seeds must be list, got {type(era.plot_seeds)}"
            
            # Check that era has minimum content
            if not era.technologies:
                return False, f"Era {era.id} ({era.name}) has no technologies"
            if not era.plot_seeds:
                return False, f"Era {era.id} ({era.name}) has no plot seeds"
            if not era.archetypes:
                return False, f"Era {era.id} ({era.name}) has no character archetypes"
            
            # Validate each technology
            for i, tech in enumerate(era.technologies):
                is_valid, error_msg = WorldDataValidator.validate_technology(tech, era.id)
                if not is_valid:
                    return False, f"Era {era.id} technology {i}: {error_msg}"
            
            # Validate each faction
            for i, faction in enumerate(era.factions):
                is_valid, error_msg = WorldDataValidator.validate_faction(faction)
                if not is_valid:
                    return False, f"Era {era.id} faction {i}: {error_msg}"
            
            # Validate each archetype
            for i, archetype in enumerate(era.archetypes):
                is_valid, error_msg = WorldDataValidator.validate_character_archetype(archetype)
                if not is_valid:
                    return False, f"Era {era.id} archetype {i}: {error_msg}"
            
            # Validate each plot seed
            for i, plot_seed in enumerate(era.plot_seeds):
                is_valid, error_msg = WorldDataValidator.validate_plot_seed(plot_seed)
                if not is_valid:
                    return False, f"Era {era.id} plot_seed {i}: {error_msg}"
            
            return True, "Era validation passed"
            
        except Exception as e:
            return False, f"Error validating era: {str(e)}"
    
    @staticmethod
    def validate_world_data(world_data: List[Any]) -> Tuple[bool, str]:
        """
        Validate the complete world data structure.
        
        Args:
            world_data: List of Era objects
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not world_data:
                return False, "World data is empty"
            
            if not isinstance(world_data, list):
                return False, f"World data must be a list, got {type(world_data)}"
            
            era_ids = set()
            era_names = set()
            
            # Validate each era
            for i, era in enumerate(world_data):
                is_valid, error_msg = WorldDataValidator.validate_era(era)
                if not is_valid:
                    return False, f"Era {i}: {error_msg}"
                
                # Check for duplicate IDs
                if era.id in era_ids:
                    return False, f"Duplicate era ID: {era.id}"
                era_ids.add(era.id)
                
                # Check for duplicate names
                if era.name in era_names:
                    return False, f"Duplicate era name: {era.name}"
                era_names.add(era.name)
            
            # Validate cross-era consistency
            all_faction_names = set()
            all_tech_names = set()
            
            for era in world_data:
                # Collect all faction and technology names for reference validation
                for faction in era.factions:
                    all_faction_names.add(faction.name)
                for tech in era.technologies:
                    all_tech_names.add(tech.name)
            
            # Validate faction references in archetypes
            for era in world_data:
                for archetype in era.archetypes:
                    for faction_ref in archetype.common_factions:
                        if faction_ref and faction_ref not in all_faction_names:
                            logger.warning(f"Era {era.id} archetype '{archetype.name}' references unknown faction: '{faction_ref}'")
                
                # Validate technology references in factions
                for faction in era.factions:
                    for tech_ref in faction.technologies:
                        if tech_ref and tech_ref not in all_tech_names:
                            logger.warning(f"Era {era.id} faction '{faction.name}' references unknown technology: '{tech_ref}'")
            
            return True, f"World data validation passed ({len(world_data)} eras)"
            
        except Exception as e:
            return False, f"Error validating world data: {str(e)}"

def validate_world_data_with_logging(world_data: List[Any]) -> bool:
    """
    Validate world data with comprehensive logging.
    
    Args:
        world_data: List of Era objects to validate
        
    Returns:
        True if valid, False otherwise
    """
    logger.info("Starting world data validation...")
    
    is_valid, message = WorldDataValidator.validate_world_data(world_data)
    
    if is_valid:
        logger.info(f"World data validation successful: {message}")
    else:
        logger.error(f"World data validation failed: {message}")
    
    return is_valid


# === Safe File Operations ===

import fcntl  # For file locking on Unix systems
import tempfile
import threading
from contextlib import contextmanager

# Thread-local storage for file locks
_file_locks = threading.local()

def _get_file_locks_dict():
    """Get the file locks dictionary for the current thread."""
    if not hasattr(_file_locks, 'locks'):
        _file_locks.locks = {}
    return _file_locks.locks

@contextmanager
def file_lock(file_path: str, timeout: float = 30.0):
    """
    Context manager for file locking to prevent concurrent writes.
    
    Args:
        file_path: Path to the file to lock
        timeout: Maximum time to wait for lock (in seconds)
        
    Yields:
        File lock context
        
    Raises:
        TimeoutError: If lock cannot be acquired within timeout
    """
    lock_path = f"{file_path}.lock"
    locks_dict = _get_file_locks_dict()
    
    # Use a thread lock for the same process
    if lock_path not in locks_dict:
        locks_dict[lock_path] = threading.Lock()
    
    thread_lock = locks_dict[lock_path]
    
    # Acquire thread lock first
    if not thread_lock.acquire(timeout=timeout):
        raise TimeoutError(f"Could not acquire thread lock for {file_path} within {timeout} seconds")
    
    try:
        # Then acquire file system lock
        lock_file = None
        try:
            lock_file = open(lock_path, 'w')
            
            # Try to acquire file lock with timeout
            start_time = time.time()
            while True:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Could not acquire file lock for {file_path} within {timeout} seconds")
                    time.sleep(0.1)
            
            logger.debug(f"Acquired file lock: {lock_path}")
            yield
            
        finally:
            if lock_file:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                    if os.path.exists(lock_path):
                        os.remove(lock_path)
                    logger.debug(f"Released file lock: {lock_path}")
                except Exception as e:
                    logger.warning(f"Error releasing file lock {lock_path}: {e}")
    
    finally:
        thread_lock.release()

def safe_write_json(data: Any, file_path: str, backup_enabled: bool = True, validate_func: Optional[Callable] = None) -> bool:
    """
    Safely write JSON data to a file with backup and atomic operations.
    
    Args:
        data: Data to write (must be JSON serializable)
        file_path: Path to the target file
        backup_enabled: Whether to create a backup before writing
        validate_func: Optional validation function to call before finalizing write
        
    Returns:
        True if write successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with file_lock(file_path):
            # Create backup if requested and file exists
            backup_path = None
            if backup_enabled and os.path.exists(file_path):
                backup_path = create_backup(file_path)
                if not backup_path:
                    logger.warning(f"Failed to create backup for {file_path}, continuing anyway")
            
            # Write to temporary file first (atomic operation)
            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.tmp',
                prefix=os.path.basename(file_path) + '_',
                dir=os.path.dirname(file_path)
            )
            
            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                    json.dump(data, temp_file, indent=2, ensure_ascii=False)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())  # Force write to disk
                
                # Validate the written data if validation function provided
                if validate_func:
                    try:
                        with open(temp_path, 'r', encoding='utf-8') as f:
                            test_data = json.load(f)
                        
                        is_valid, error_msg = validate_func(test_data)
                        if not is_valid:
                            raise ValidationError(f"Validation failed after write: {error_msg}")
                    except Exception as e:
                        logger.error(f"Validation failed for temporary file {temp_path}: {e}")
                        raise
                
                # Atomically replace the original file
                if os.name == 'nt':  # Windows
                    # On Windows, we need to remove the target first
                    if os.path.exists(file_path):
                        os.replace(temp_path, file_path)
                    else:
                        os.rename(temp_path, file_path)
                else:  # Unix/Linux
                    os.replace(temp_path, file_path)
                
                logger.info(f"Successfully wrote {file_path}")
                return True
                
            except Exception as e:
                # Clean up temporary file on error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                
                # Try to restore backup if write failed
                if backup_path and os.path.exists(backup_path):
                    logger.info(f"Write failed, attempting to restore from backup: {backup_path}")
                    if restore_from_backup(file_path, backup_path):
                        logger.info(f"Successfully restored {file_path} from backup")
                    else:
                        logger.error(f"Failed to restore {file_path} from backup")
                
                raise e
    
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {str(e)}")
        return False

def safe_read_json(file_path: str, validate_func: Optional[Callable] = None, auto_recover: bool = True) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Safely read JSON data from a file with validation and auto-recovery.
    
    Args:
        file_path: Path to the file to read
        validate_func: Optional validation function to call after reading
        auto_recover: Whether to automatically try to recover from backup on failure
        
    Returns:
        Tuple of (success, data, message)
    """
    try:
        if not os.path.exists(file_path):
            return False, None, f"File does not exist: {file_path}"
        
        with file_lock(file_path, timeout=10.0):  # Shorter timeout for reads
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate data if validation function provided
                if validate_func:
                    is_valid, error_msg = validate_func(data)
                    if not is_valid:
                        if auto_recover:
                            logger.warning(f"Validation failed for {file_path}: {error_msg}. Attempting recovery...")
                            return _attempt_recovery_read(file_path, validate_func)
                        else:
                            return False, None, f"Validation failed: {error_msg}"
                
                logger.debug(f"Successfully read {file_path}")
                return True, data, "Read successful"
                
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                if auto_recover:
                    logger.warning(f"File corruption detected in {file_path}: {e}. Attempting recovery...")
                    return _attempt_recovery_read(file_path, validate_func)
                else:
                    return False, None, f"File corruption: {str(e)}"
    
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        if auto_recover:
            return _attempt_recovery_read(file_path, validate_func)
        else:
            return False, None, f"Read error: {str(e)}"

def _attempt_recovery_read(file_path: str, validate_func: Optional[Callable] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Attempt to recover a file by restoring from backup.
    
    Args:
        file_path: Path to the corrupted file
        validate_func: Optional validation function
        
    Returns:
        Tuple of (success, data, message)
    """
    try:
        # Try to restore from backup
        if restore_from_backup(file_path):
            logger.info(f"Restored {file_path} from backup, attempting to read again...")
            
            # Try reading again after restoration
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate restored data
                if validate_func:
                    is_valid, error_msg = validate_func(data)
                    if not is_valid:
                        return False, None, f"Backup also invalid: {error_msg}"
                
                return True, data, "Recovered from backup successfully"
                
            except Exception as e:
                return False, None, f"Backup file also corrupted: {str(e)}"
        else:
            return False, None, "No backup available for recovery"
    
    except Exception as e:
        return False, None, f"Recovery failed: {str(e)}"

def safe_write_text(content: str, file_path: str, backup_enabled: bool = True, encoding: str = 'utf-8') -> bool:
    """
    Safely write text content to a file with backup and atomic operations.
    
    Args:
        content: Text content to write
        file_path: Path to the target file
        backup_enabled: Whether to create a backup before writing
        encoding: File encoding to use
        
    Returns:
        True if write successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with file_lock(file_path):
            # Create backup if requested and file exists
            if backup_enabled and os.path.exists(file_path):
                backup_path = create_backup(file_path)
                if not backup_path:
                    logger.warning(f"Failed to create backup for {file_path}, continuing anyway")
            
            # Write to temporary file first (atomic operation)
            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.tmp',
                prefix=os.path.basename(file_path) + '_',
                dir=os.path.dirname(file_path)
            )
            
            try:
                with os.fdopen(temp_fd, 'w', encoding=encoding) as temp_file:
                    temp_file.write(content)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())  # Force write to disk
                
                # Atomically replace the original file
                if os.name == 'nt':  # Windows
                    if os.path.exists(file_path):
                        os.replace(temp_path, file_path)
                    else:
                        os.rename(temp_path, file_path)
                else:  # Unix/Linux
                    os.replace(temp_path, file_path)
                
                logger.info(f"Successfully wrote text file {file_path}")
                return True
                
            except Exception as e:
                # Clean up temporary file on error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                raise e
    
    except Exception as e:
        logger.error(f"Error writing text to {file_path}: {str(e)}")
        return False

def cleanup_old_backups(file_path: str, max_backups: int = 10) -> int:
    """
    Clean up old backup files, keeping only the most recent ones.
    
    Args:
        file_path: Path to the original file
        max_backups: Maximum number of backups to keep
        
    Returns:
        Number of backups removed
    """
    try:
        backup_pattern = f"{file_path}.backup_*"
        backups = glob.glob(backup_pattern)
        
        if len(backups) <= max_backups:
            return 0
        
        # Sort by creation time (oldest first)
        backups.sort(key=lambda x: os.path.getctime(x))
        
        # Remove oldest backups
        to_remove = backups[:-max_backups]
        removed_count = 0
        
        for backup in to_remove:
            try:
                os.remove(backup)
                removed_count += 1
                logger.debug(f"Removed old backup: {backup}")
            except Exception as e:
                logger.warning(f"Failed to remove backup {backup}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old backups for {file_path}")
        
        return removed_count
    
    except Exception as e:
        logger.error(f"Error cleaning up backups for {file_path}: {e}")
        return 0 