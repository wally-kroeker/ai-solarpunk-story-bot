#!/usr/bin/env python
"""
Centralized Error Handling and Logging System for AI Solarpunk Story Bot
"""

import logging
import sys
import traceback
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from functools import wraps


class ErrorCategory(Enum):
    """Categories of errors for different handling strategies."""
    CRITICAL = "critical"
    RECOVERABLE = "recoverable" 
    WARNING = "warning"
    VALIDATION = "validation"
    NETWORK = "network"
    FILE_IO = "file_io"
    USER_INPUT = "user_input"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SystemHealthMonitor:
    """Monitors system health and performance metrics."""
    
    def __init__(self):
        """Initialize the health monitor."""
        self.start_time = datetime.now()
        self.error_counts_by_hour: Dict[str, int] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.last_health_check = datetime.now()
        
    def record_performance_metric(self, operation: str, duration: float) -> None:
        """Record a performance metric for an operation."""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = duration
        else:
            # Use exponential moving average
            self.performance_metrics[operation] = (
                0.7 * self.performance_metrics[operation] + 
                0.3 * duration
            )
    
    def increment_hourly_errors(self, error_type: str) -> None:
        """Increment error count for the current hour."""
        current_hour = datetime.now().strftime('%Y-%m-%d_%H')
        key = f"{current_hour}_{error_type}"
        self.error_counts_by_hour[key] = self.error_counts_by_hour.get(key, 0) + 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""
        uptime = datetime.now() - self.start_time
        current_hour = datetime.now().strftime('%Y-%m-%d_%H')
        
        # Count errors in current hour
        current_hour_errors = sum(
            count for key, count in self.error_counts_by_hour.items()
            if key.startswith(current_hour)
        )
        
        # Determine health status
        if current_hour_errors > 50:
            health_status = "critical"
        elif current_hour_errors > 20:
            health_status = "degraded"
        elif current_hour_errors > 5:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "uptime_hours": uptime.total_seconds() / 3600,
            "errors_last_hour": current_hour_errors,
            "performance_metrics": self.performance_metrics.copy(),
            "last_check": self.last_health_check.isoformat(),
            "total_error_types": len(set(
                key.split('_', 2)[-1] for key in self.error_counts_by_hour.keys()
            ))
        }


class RecoveryManager:
    """Manages automatic recovery mechanisms."""
    
    def __init__(self):
        """Initialize the recovery manager."""
        self.recovery_attempts: Dict[str, int] = {}
        self.last_recovery_time: Dict[str, datetime] = {}
        
    def should_attempt_recovery(self, error_type: str, max_attempts: int = 3, 
                              cooldown_minutes: int = 10) -> bool:
        """Determine if automatic recovery should be attempted."""
        current_time = datetime.now()
        
        # Check if we're in cooldown period
        if error_type in self.last_recovery_time:
            last_attempt = self.last_recovery_time[error_type]
            if current_time - last_attempt < timedelta(minutes=cooldown_minutes):
                return False
        
        # Check attempt count
        attempts = self.recovery_attempts.get(error_type, 0)
        return attempts < max_attempts
    
    def record_recovery_attempt(self, error_type: str, success: bool) -> None:
        """Record a recovery attempt."""
        current_time = datetime.now()
        self.last_recovery_time[error_type] = current_time
        
        if success:
            # Reset attempt count on success
            self.recovery_attempts[error_type] = 0
        else:
            # Increment attempt count on failure
            self.recovery_attempts[error_type] = self.recovery_attempts.get(error_type, 0) + 1


class CentralizedErrorHandler:
    """Centralized error handling system with logging, recovery, and reporting."""
    
    def __init__(self, 
                 log_file: Optional[str] = None,
                 debug_mode: Optional[bool] = None,
                 enable_email_alerts: bool = False):
        """Initialize the centralized error handler."""
        # Load debug mode from environment if not explicitly set
        if debug_mode is None:
            debug_mode = os.getenv('AI_SOLARPUNK_DEBUG', 'false').lower() in ('true', '1', 'yes')
            
        self.debug_mode = debug_mode
        self.enable_email_alerts = enable_email_alerts
        self.error_counts: Dict[str, int] = {}
        
        # Initialize health monitoring and recovery
        self.health_monitor = SystemHealthMonitor()
        self.recovery_manager = RecoveryManager()
        
        # Initialize logging
        self._setup_logging(log_file)
        
        # Load configuration if available
        self._load_config()
        
        self.logger.info(f"Centralized Error Handler initialized (debug_mode={self.debug_mode})")
    
    def _load_config(self) -> None:
        """Load error handler configuration from file."""
        config_path = Path("config/error_handler.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                # Update settings from config
                self.debug_mode = config.get('debug_mode', self.debug_mode)
                self.enable_email_alerts = config.get('enable_email_alerts', self.enable_email_alerts)
                
                self.logger.info("Error handler configuration loaded from file")
            except Exception as e:
                self.logger.warning(f"Failed to load error handler config: {e}")
    
    def _setup_logging(self, log_file: Optional[str]) -> None:
        """Setup comprehensive logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Use provided log file or create default
        if log_file is None:
            log_file = log_dir / f"ai_solarpunk_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure root logger
        log_level = logging.DEBUG if self.debug_mode else logging.INFO
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Clear existing handlers to avoid duplication
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Create specialized loggers
        self.logger = logging.getLogger(__name__)
        self.error_logger = logging.getLogger('error_handler')
        self.recovery_logger = logging.getLogger('recovery')
    
    def handle_error(self,
                    error: Exception,
                    context: Dict[str, Any],
                    category: ErrorCategory = ErrorCategory.RECOVERABLE,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    user_message: Optional[str] = None,
                    enable_recovery: bool = True) -> Dict[str, Any]:
        """Handle an error with comprehensive logging and optional recovery."""
        error_id = self._generate_error_id()
        error_type = type(error).__name__
        
        # Update error statistics
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.health_monitor.increment_hourly_errors(error_type)
        
        # Log the error
        self._log_error(error, context, category, severity, error_id)
        
        # Attempt recovery if enabled and appropriate
        recovery_attempted = False
        recovery_successful = False
        
        if (enable_recovery and 
            category in [ErrorCategory.RECOVERABLE, ErrorCategory.NETWORK, ErrorCategory.FILE_IO] and
            self.recovery_manager.should_attempt_recovery(error_type)):
            
            recovery_attempted = True
            try:
                recovery_successful = self._attempt_recovery(error, context, category)
                self.recovery_manager.record_recovery_attempt(error_type, recovery_successful)
                
                if recovery_successful:
                    self.recovery_logger.info(f"Automatic recovery successful for error {error_id}")
                else:
                    self.recovery_logger.warning(f"Automatic recovery failed for error {error_id}")
                    
            except Exception as recovery_error:
                self.recovery_logger.error(f"Recovery attempt failed for error {error_id}: {recovery_error}")
                self.recovery_manager.record_recovery_attempt(error_type, False)
        
        # Generate user-friendly message
        friendly_message = user_message or self._generate_user_message(error, category)
        
        return {
            'error_id': error_id,
            'error_type': error_type,
            'category': category.value,
            'severity': severity.value,
            'user_message': friendly_message,
            'technical_details': str(error) if self.debug_mode else None,
            'timestamp': datetime.now().isoformat(),
            'context': context if self.debug_mode else {},
            'recovery_attempted': recovery_attempted,
            'recovery_successful': recovery_successful
        }
    
    def _attempt_recovery(self, error: Exception, context: Dict[str, Any], 
                         category: ErrorCategory) -> bool:
        """Attempt automatic recovery based on error category."""
        operation = context.get('operation', 'unknown')
        
        if category == ErrorCategory.FILE_IO:
            return self._recover_file_operation(context)
        elif category == ErrorCategory.NETWORK:
            return self._recover_network_operation(context)
        elif category == ErrorCategory.VALIDATION:
            return self._recover_validation_error(context)
        
        return False
    
    def _recover_file_operation(self, context: Dict[str, Any]) -> bool:
        """Attempt to recover from file operation errors."""
        try:
            operation = context.get('operation')
            file_path = context.get('file_path')
            
            if operation == 'story_file_save' or operation == 'post_data_save':
                # Check if directory exists and create if needed
                if file_path:
                    dir_path = Path(file_path).parent
                    dir_path.mkdir(parents=True, exist_ok=True)
                    return True
                    
            return False
        except Exception:
            return False
    
    def _recover_network_operation(self, context: Dict[str, Any]) -> bool:
        """Attempt to recover from network operation errors."""
        try:
            # For network errors, we typically can't auto-recover
            # but we can log the attempt and suggest retry
            operation = context.get('operation')
            
            if operation in ['image_generation', 'twitter_media_upload', 'post_to_twitter']:
                # Log that a retry might be successful
                self.recovery_logger.info(f"Network operation {operation} failed, retry may succeed")
                return False  # Can't actually recover, but logged for user info
                
            return False
        except Exception:
            return False
    
    def _recover_validation_error(self, context: Dict[str, Any]) -> bool:
        """Attempt to recover from validation errors."""
        try:
            # For validation errors, attempt to use backup or defaults
            file_path = context.get('file_path')
            
            if file_path and 'continuity' in file_path:
                # For continuity file validation errors, restoration is handled elsewhere
                return False
                
            return False
        except Exception:
            return False
    
    def _log_error(self, error: Exception, context: Dict[str, Any], 
                   category: ErrorCategory, severity: ErrorSeverity, error_id: str) -> None:
        """Log error with comprehensive details."""
        error_details = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'context': context,
            'traceback': traceback.format_exc() if self.debug_mode else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if severity == ErrorSeverity.CRITICAL:
            self.error_logger.critical(f"CRITICAL ERROR [{error_id}]: {error_details}")
        elif severity == ErrorSeverity.HIGH:
            self.error_logger.error(f"HIGH SEVERITY ERROR [{error_id}]: {error_details}")
        elif severity == ErrorSeverity.MEDIUM:
            self.error_logger.warning(f"MEDIUM SEVERITY ERROR [{error_id}]: {error_details}")
        else:
            self.error_logger.info(f"LOW SEVERITY ERROR [{error_id}]: {error_details}")
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory) -> str:
        """Generate user-friendly error messages."""
        base_messages = {
            ErrorCategory.CRITICAL: "A critical system error occurred. Please contact support.",
            ErrorCategory.NETWORK: "Network connectivity issue detected. Retrying with backup systems.",
            ErrorCategory.FILE_IO: "File operation failed. Attempting to recover from backup.",
            ErrorCategory.VALIDATION: "Data validation error. Using default values where possible.",
            ErrorCategory.USER_INPUT: "Invalid input provided. Please check your parameters.",
            ErrorCategory.RECOVERABLE: "A recoverable error occurred. Attempting automatic recovery.",
            ErrorCategory.WARNING: "Minor issue detected. Operation may continue with limited functionality."
        }
        
        return base_messages.get(category, "An unexpected error occurred.")
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"ERR_{timestamp}_{id(self) % 10000:04d}"
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and system health information."""
        total_errors = sum(self.error_counts.values())
        health_status = self.health_monitor.get_health_status()
        
        return {
            'total_errors': total_errors,
            'error_by_type': self.error_counts.copy(),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None,
            'debug_mode': self.debug_mode,
            'system_health': health_status,
            'recovery_stats': {
                'total_attempts': sum(self.recovery_manager.recovery_attempts.values()),
                'active_recovery_types': len(self.recovery_manager.recovery_attempts)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def enable_debug_mode(self, enabled: bool = True) -> None:
        """Enable or disable debug mode."""
        self.debug_mode = enabled
        
        # Update log level
        log_level = logging.DEBUG if enabled else logging.INFO
        logging.getLogger().setLevel(log_level)
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)
        
        self.logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config = {
            'debug_mode': self.debug_mode,
            'enable_email_alerts': self.enable_email_alerts,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(config_dir / "error_handler.json", 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info("Error handler configuration saved")
        except Exception as e:
            self.logger.warning(f"Failed to save error handler config: {e}")


# Create global error handler instance
error_handler = CentralizedErrorHandler()

# Convenience function to get logger
logger = error_handler.logger

# Convenience function for direct error reporting
def report_error(error: Exception, 
                context: Dict[str, Any] = None,
                category: ErrorCategory = ErrorCategory.RECOVERABLE,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                user_message: Optional[str] = None) -> Dict[str, Any]:
    """Report an error through the centralized error handling system."""
    if context is None:
        context = {}
    return error_handler.handle_error(error, context, category, severity, user_message)

# Error reporting decorator for application-level functions
def with_error_reporting(category: ErrorCategory = ErrorCategory.RECOVERABLE,
                        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                        user_message: Optional[str] = None):
    """Decorator that adds comprehensive error reporting to any function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # Record successful performance metric
                duration = time.time() - start_time
                error_handler.health_monitor.record_performance_metric(
                    func.__name__, duration
                )
                
                return result
                
            except Exception as e:
                # Add function context
                context = {
                    'function_name': func.__name__,
                    'args': str(args) if args else None,
                    'kwargs': str(kwargs) if kwargs else None,
                    'duration': time.time() - start_time
                }
                
                # Report the error
                error_info = error_handler.handle_error(
                    e, context, category, severity, user_message
                )
                
                # Re-raise for higher-level handling if needed
                raise
                
        return wrapper
    return decorator

# Function to create application-wide error context
def create_error_context(operation: str, **additional_context) -> Dict[str, Any]:
    """Create a standardized error context for the application."""
    import psutil
    import os
    
    base_context = {
        'operation': operation,
        'timestamp': datetime.now().isoformat(),
        'process_id': os.getpid(),
        'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
        'system_load': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None,
        'working_directory': os.getcwd(),
    }
    
    # Add additional context
    base_context.update(additional_context)
    
    return base_context

# Function to get user-friendly error messages
def get_user_friendly_message(error: Exception, operation: str = "operation") -> str:
    """Generate user-friendly error messages for different error types."""
    error_type = type(error).__name__
    
    friendly_messages = {
        'FileNotFoundError': f"Could not find required file during {operation}. Please check that all necessary files exist.",
        'PermissionError': f"Permission denied while performing {operation}. Please check file/directory permissions.",
        'ConnectionError': f"Network connection failed during {operation}. Please check your internet connection.",
        'TimeoutError': f"Operation timed out during {operation}. Please try again or check network connectivity.",
        'JSONDecodeError': f"Invalid data format encountered during {operation}. The data file may be corrupted.",
        'ValidationError': f"Data validation failed during {operation}. Please check your input data.",
        'KeyError': f"Missing required information during {operation}. Please check configuration settings.",
        'ValueError': f"Invalid value provided during {operation}. Please check your input parameters.",
        'ImportError': f"Required component not available for {operation}. Please check software installation.",
        'OSError': f"System error occurred during {operation}. Please check system resources and permissions.",
    }
    
    return friendly_messages.get(error_type, 
        f"An unexpected error occurred during {operation}. Please try again or contact support.")

# Health check function for monitoring
def get_application_health() -> Dict[str, Any]:
    """Get comprehensive application health information."""
    health_data = error_handler.health_monitor.get_health_status()
    error_stats = error_handler.get_error_statistics()
    
    return {
        'system_health': health_data,
        'error_statistics': error_stats,
        'debug_mode': error_handler.debug_mode,
        'handlers_active': True,
        'timestamp': datetime.now().isoformat()
    }

# Debug mode management
def set_debug_mode(enabled: bool = True) -> None:
    """Enable or disable debug mode for detailed error information."""
    error_handler.enable_debug_mode(enabled)
    logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")

# Recovery management
def attempt_system_recovery(error_type: str, context: Dict[str, Any]) -> bool:
    """Attempt to recover from system-level errors."""
    return error_handler.recovery_manager.should_attempt_recovery(error_type)

# Configuration management
def save_error_handler_config() -> None:
    """Save current error handler configuration."""
    error_handler.save_config()

# Graceful shutdown handling
def graceful_shutdown(exit_code: int = 0) -> None:
    """Perform graceful shutdown with error reporting."""
    try:
        # Save final statistics
        error_handler.save_config()
        
        # Log shutdown
        logger.info("Application shutting down gracefully")
        
        # Cleanup handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
    except Exception as e:
        # Last resort error handling
        print(f"Error during shutdown: {e}")
    finally:
        sys.exit(exit_code)


def handle_errors(category: ErrorCategory = ErrorCategory.RECOVERABLE,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: Optional[str] = None,
                 enable_recovery: bool = True):
    """Decorator for automatic error handling of functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # Record performance metric
                duration = time.time() - start_time
                error_handler.health_monitor.record_performance_metric(func.__name__, duration)
                
                return result
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200] if args else None,
                    'kwargs': str(kwargs)[:200] if kwargs else None,
                    'execution_time': time.time() - start_time
                }
                
                error_result = error_handler.handle_error(
                    error=e,
                    context=context,
                    category=category,
                    severity=severity,
                    user_message=user_message,
                    enable_recovery=enable_recovery
                )
                
                # Re-raise if critical
                if severity == ErrorSeverity.CRITICAL:
                    raise
                
                return None
        
        return wrapper
    return decorator


def get_system_health() -> Dict[str, Any]:
    """Get current system health status."""
    return error_handler.get_error_statistics()


def enable_debug_mode(enabled: bool = True) -> None:
    """Enable or disable debug mode globally."""
    error_handler.enable_debug_mode(enabled) 