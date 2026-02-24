#!/usr/bin/env python
"""
Application-Level Error Handler for AI Solarpunk Story Bot

This module provides application-wide error handling, recovery mechanisms,
and graceful degradation for the entire story generation system.
"""

import os
import sys
import signal
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from contextlib import contextmanager

from src.error_handler import (
    CentralizedErrorHandler,
    ErrorCategory,
    ErrorSeverity,
    handle_errors,
    with_error_reporting,
    create_error_context,
    get_user_friendly_message,
    graceful_shutdown,
    get_application_health,
    set_debug_mode
)

# Setup logging
logger = logging.getLogger(__name__)


class ApplicationErrorManager:
    """Manages application-level error handling and recovery."""
    
    def __init__(self, debug_mode: Optional[bool] = None):
        """Initialize the application error manager."""
        # Check for debug mode from environment
        if debug_mode is None:
            debug_mode = os.getenv('AI_SOLARPUNK_DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        self.debug_mode = debug_mode
        set_debug_mode(debug_mode)
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Initialize health monitoring
        self.startup_health = get_application_health()
        
        logger.info(f"Application Error Manager initialized (debug_mode={debug_mode})")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            graceful_shutdown(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    @contextmanager
    def application_context(self, operation_name: str = "application_operation"):
        """Context manager for application-level error handling."""
        start_context = create_error_context(
            operation=operation_name,
            startup_health=self.startup_health
        )
        
        try:
            logger.info(f"Starting {operation_name}")
            yield
            logger.info(f"Completed {operation_name} successfully")
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            graceful_shutdown(0)
            
        except SystemExit as e:
            logger.info(f"System exit called with code {e.code}")
            graceful_shutdown(e.code if e.code is not None else 0)
            
        except Exception as e:
            # Create comprehensive error context
            error_context = create_error_context(
                operation=operation_name,
                startup_health=self.startup_health,
                final_health=get_application_health(),
                error_details=str(e)
            )
            
            # Log the error with full context
            logger.error(f"Critical error in {operation_name}: {e}", exc_info=True)
            
            # Provide user-friendly message
            user_message = get_user_friendly_message(e, operation_name)
            logger.error(f"User message: {user_message}")
            
            # Attempt recovery or graceful degradation
            recovery_successful = self._attempt_application_recovery(e, error_context)
            
            if recovery_successful:
                logger.info("Application recovery successful, continuing operation")
            else:
                logger.error("Application recovery failed, shutting down gracefully")
                graceful_shutdown(1)
    
    def _attempt_application_recovery(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from application-level errors."""
        error_type = type(error).__name__
        
        recovery_strategies = {
            'FileNotFoundError': self._recover_missing_files,
            'PermissionError': self._recover_permission_issues,
            'ConnectionError': self._recover_network_issues,
            'JSONDecodeError': self._recover_corrupted_data,
            'ImportError': self._recover_missing_dependencies,
            'MemoryError': self._recover_memory_issues,
        }
        
        recovery_func = recovery_strategies.get(error_type)
        if recovery_func:
            try:
                logger.info(f"Attempting recovery for {error_type}")
                return recovery_func(error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery attempt failed: {recovery_error}")
                return False
        
        logger.warning(f"No recovery strategy available for {error_type}")
        return False
    
    def _recover_missing_files(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from missing files."""
        logger.info("Attempting to recover from missing files")
        
        # Create essential directories
        essential_dirs = [
            "output",
            "output/images", 
            "output/stories",
            "output/previews",
            "logs",
            "config"
        ]
        
        for dir_path in essential_dirs:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {e}")
                return False
        
        # Initialize empty continuity file if missing
        continuity_path = Path("output/continuity.json")
        if not continuity_path.exists():
            try:
                empty_continuity = {
                    "last_story_id": 0,
                    "characters": [],
                    "story_log": []
                }
                with open(continuity_path, 'w') as f:
                    import json
                    json.dump(empty_continuity, f, indent=2)
                logger.info("Created empty continuity file")
            except Exception as e:
                logger.error(f"Failed to create continuity file: {e}")
                return False
        
        return True
    
    def _recover_permission_issues(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from permission issues."""
        logger.info("Attempting to recover from permission issues")
        
        # Log detailed permission information
        import stat
        current_dir = Path.cwd()
        
        try:
            # Check permissions on key directories
            for dir_name in ["output", "logs", "config"]:
                dir_path = current_dir / dir_name
                if dir_path.exists():
                    perms = stat.filemode(dir_path.stat().st_mode)
                    logger.info(f"Directory {dir_name} permissions: {perms}")
                else:
                    logger.warning(f"Directory {dir_name} does not exist")
        except Exception as e:
            logger.error(f"Failed to check permissions: {e}")
        
        # Can't automatically fix permissions, but provide helpful info
        logger.error("Permission issues detected. Please ensure the application has")
        logger.error("read/write access to the output, logs, and config directories.")
        
        return False
    
    def _recover_network_issues(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from network issues."""
        logger.info("Attempting to recover from network issues")
        
        # For network issues, we can suggest offline mode or retry
        logger.warning("Network connectivity issues detected.")
        logger.info("The application can continue with limited functionality:")
        logger.info("- Story generation may use cached data")
        logger.info("- Image generation may be disabled")
        logger.info("- Social media posting will be disabled")
        
        # Return True to indicate graceful degradation is possible
        return True
    
    def _recover_corrupted_data(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from corrupted data files."""
        logger.info("Attempting to recover from corrupted data")
        
        # Try to restore from backups
        from src.validation import restore_from_backup
        
        critical_files = [
            "output/continuity.json",
            "config/error_handler.json"
        ]
        
        recovery_success = True
        for file_path in critical_files:
            if Path(file_path).exists():
                try:
                    backup_restored = restore_from_backup(file_path)
                    if backup_restored:
                        logger.info(f"Restored {file_path} from backup")
                    else:
                        logger.warning(f"No backup available for {file_path}")
                        recovery_success = False
                except Exception as e:
                    logger.error(f"Failed to restore {file_path}: {e}")
                    recovery_success = False
        
        return recovery_success
    
    def _recover_missing_dependencies(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from missing dependencies."""
        logger.info("Attempting to recover from missing dependencies")
        
        # Log the specific import that failed
        logger.error(f"Missing dependency: {error}")
        logger.error("Please ensure all required packages are installed:")
        logger.error("Run: uv pip install -r requirements.txt")
        
        return False
    
    def _recover_memory_issues(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from memory issues."""
        logger.info("Attempting to recover from memory issues")
        
        # Log memory usage information
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.warning(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
            logger.warning("System is running low on memory.")
            logger.error("Consider closing other applications or upgrading system memory.")
        except ImportError:
            logger.warning("Cannot check memory usage - psutil not available")
        
        return False

    def get_health_report(self) -> Dict[str, Any]:
        """Get a comprehensive health report for the application."""
        current_health = get_application_health()
        
        return {
            'startup_health': self.startup_health,
            'current_health': current_health,
            'debug_mode': self.debug_mode,
            'process_id': os.getpid(),
            'working_directory': str(Path.cwd()),
        }


# Global application error manager instance
app_error_manager = ApplicationErrorManager()

# Convenience functions for application-level error handling
def with_application_error_handling(operation_name: str = "operation"):
    """Decorator for application-level error handling."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with app_error_manager.application_context(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def application_context(operation_name: str = "operation"):
    """Context manager for application-level error handling."""
    return app_error_manager.application_context(operation_name)

def get_app_health_report() -> Dict[str, Any]:
    """Get application health report."""
    return app_error_manager.get_health_report()

def enable_application_debug_mode(enabled: bool = True) -> None:
    """Enable application debug mode."""
    app_error_manager.debug_mode = enabled
    set_debug_mode(enabled)
    logger.info(f"Application debug mode {'enabled' if enabled else 'disabled'}") 