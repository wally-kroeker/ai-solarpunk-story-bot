#!/usr/bin/env python
"""
Error Handler Management CLI

This script provides a command-line interface for managing the centralized error 
handling system, including debug mode configuration, health monitoring, and error statistics.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.error_handler import (
    error_handler,
    get_system_health,
    enable_debug_mode,
    ErrorCategory,
    ErrorSeverity
)


def show_health_status() -> None:
    """Display the current system health status."""
    print("=== System Health Status ===")
    
    try:
        health_data = get_system_health()
        
        # Overall health
        system_health = health_data.get('system_health', {})
        status = system_health.get('status', 'unknown')
        uptime_hours = system_health.get('uptime_hours', 0)
        errors_last_hour = system_health.get('errors_last_hour', 0)
        
        print(f"Overall Status: {status.upper()}")
        print(f"Uptime: {uptime_hours:.1f} hours")
        print(f"Errors in last hour: {errors_last_hour}")
        
        # Error statistics
        print(f"\nTotal Errors: {health_data.get('total_errors', 0)}")
        print(f"Debug Mode: {'ON' if health_data.get('debug_mode', False) else 'OFF'}")
        
        # Most common error
        most_common = health_data.get('most_common_error')
        if most_common:
            error_count = health_data.get('error_by_type', {}).get(most_common, 0)
            print(f"Most common error: {most_common} ({error_count} occurrences)")
        
        # Performance metrics
        performance = system_health.get('performance_metrics', {})
        if performance:
            print(f"\nPerformance Metrics (avg duration in seconds):")
            for operation, avg_time in performance.items():
                print(f"  {operation}: {avg_time:.3f}s")
        
        # Recovery statistics
        recovery_stats = health_data.get('recovery_stats', {})
        total_attempts = recovery_stats.get('total_attempts', 0)
        active_types = recovery_stats.get('active_recovery_types', 0)
        print(f"\nRecovery Statistics:")
        print(f"  Total recovery attempts: {total_attempts}")
        print(f"  Active recovery types: {active_types}")
        
    except Exception as e:
        print(f"Error retrieving health status: {e}")


def show_error_details() -> None:
    """Display detailed error statistics."""
    print("=== Detailed Error Statistics ===")
    
    try:
        health_data = get_system_health()
        error_by_type = health_data.get('error_by_type', {})
        
        if not error_by_type:
            print("No errors recorded yet.")
            return
        
        print(f"Total error types: {len(error_by_type)}")
        print("\nError breakdown:")
        
        # Sort errors by count (descending)
        sorted_errors = sorted(error_by_type.items(), key=lambda x: x[1], reverse=True)
        
        for error_type, count in sorted_errors:
            print(f"  {error_type}: {count} occurrences")
        
        # Show hourly error trend if available
        system_health = health_data.get('system_health', {})
        errors_last_hour = system_health.get('errors_last_hour', 0)
        total_errors = health_data.get('total_errors', 0)
        
        if total_errors > 0:
            recent_percentage = (errors_last_hour / total_errors) * 100
            print(f"\nRecent activity: {recent_percentage:.1f}% of all errors occurred in the last hour")
        
    except Exception as e:
        print(f"Error retrieving error details: {e}")


def toggle_debug_mode(enabled: bool) -> None:
    """Enable or disable debug mode."""
    try:
        enable_debug_mode(enabled)
        status = "enabled" if enabled else "disabled"
        print(f"Debug mode {status} successfully.")
        
        # Save the configuration
        error_handler.save_config()
        print("Configuration saved.")
        
    except Exception as e:
        print(f"Error toggling debug mode: {e}")


def test_error_handling() -> None:
    """Test the error handling system with sample errors."""
    print("=== Testing Error Handling System ===")
    
    try:
        # Test different error categories
        test_cases = [
            {
                'category': ErrorCategory.RECOVERABLE,
                'severity': ErrorSeverity.LOW,
                'error': ValueError("Test recoverable error"),
                'context': {'operation': 'test_recoverable', 'test_case': 1}
            },
            {
                'category': ErrorCategory.FILE_IO,
                'severity': ErrorSeverity.MEDIUM,
                'error': FileNotFoundError("Test file not found"),
                'context': {'operation': 'test_file_io', 'file_path': '/tmp/test.txt'}
            },
            {
                'category': ErrorCategory.NETWORK,
                'severity': ErrorSeverity.HIGH,
                'error': ConnectionError("Test network error"),
                'context': {'operation': 'test_network', 'endpoint': 'test.example.com'}
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['category'].value} error")
            
            result = error_handler.handle_error(
                error=test_case['error'],
                context=test_case['context'],
                category=test_case['category'],
                severity=test_case['severity'],
                user_message=f"Test error {i} for validation"
            )
            
            print(f"  Error ID: {result['error_id']}")
            print(f"  User message: {result['user_message']}")
            print(f"  Recovery attempted: {result.get('recovery_attempted', False)}")
            print(f"  Recovery successful: {result.get('recovery_successful', False)}")
        
        print(f"\nCompleted {len(test_cases)} test cases.")
        
    except Exception as e:
        print(f"Error during testing: {e}")


def reset_statistics() -> None:
    """Reset error statistics (with confirmation)."""
    print("=== Reset Error Statistics ===")
    
    try:
        # Get current stats before reset
        health_data = get_system_health()
        total_errors = health_data.get('total_errors', 0)
        error_types = len(health_data.get('error_by_type', {}))
        
        print(f"Current statistics:")
        print(f"  Total errors: {total_errors}")
        print(f"  Error types: {error_types}")
        
        # Confirm reset
        response = input("\nAre you sure you want to reset all statistics? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Reset cancelled.")
            return
        
        # Reset error counts
        error_handler.error_counts.clear()
        error_handler.health_monitor.error_counts_by_hour.clear()
        error_handler.recovery_manager.recovery_attempts.clear()
        error_handler.recovery_manager.last_recovery_time.clear()
        
        print("Error statistics reset successfully.")
        
    except Exception as e:
        print(f"Error resetting statistics: {e}")


def export_logs(output_file: str) -> None:
    """Export current error statistics to a JSON file."""
    print(f"=== Exporting Error Statistics to {output_file} ===")
    
    try:
        health_data = get_system_health()
        
        # Add additional metadata
        export_data = {
            'export_timestamp': health_data.get('timestamp'),
            'error_handler_version': '1.0.0',
            'statistics': health_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Statistics exported successfully to {output_file}")
        print(f"Total errors exported: {health_data.get('total_errors', 0)}")
        
    except Exception as e:
        print(f"Error exporting logs: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="AI Solarpunk Error Handler Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health status command
    subparsers.add_parser('status', help='Show system health status')
    
    # Error details command
    subparsers.add_parser('errors', help='Show detailed error statistics')
    
    # Debug mode commands
    debug_parser = subparsers.add_parser('debug', help='Manage debug mode')
    debug_group = debug_parser.add_mutually_exclusive_group(required=True)
    debug_group.add_argument('--enable', action='store_true', help='Enable debug mode')
    debug_group.add_argument('--disable', action='store_true', help='Disable debug mode')
    
    # Test command
    subparsers.add_parser('test', help='Test the error handling system')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset error statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export error statistics to file')
    export_parser.add_argument('--output', '-o', default='error_stats.json',
                              help='Output file path (default: error_stats.json)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'status':
        show_health_status()
    elif args.command == 'errors':
        show_error_details()
    elif args.command == 'debug':
        if args.enable:
            toggle_debug_mode(True)
        elif args.disable:
            toggle_debug_mode(False)
    elif args.command == 'test':
        test_error_handling()
    elif args.command == 'reset':
        reset_statistics()
    elif args.command == 'export':
        export_logs(args.output)


if __name__ == '__main__':
    main() 