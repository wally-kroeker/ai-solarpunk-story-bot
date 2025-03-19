#!/bin/bash

# AI Solarpunk Story Bot - Service Management Script

SERVICE_NAME="ai-solarpunk-story"
SYSTEMD_DIR="/etc/systemd/system"
PROJECT_DIR="/home/wally/ai-solarpunk-story-bot"

# Ensure we're running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Function to install the service
install_service() {
    echo "Installing AI Solarpunk Story Bot service..."
    
    # Copy service files
    cp "${PROJECT_DIR}/systemd/${SERVICE_NAME}.service" "${SYSTEMD_DIR}/"
    cp "${PROJECT_DIR}/systemd/${SERVICE_NAME}.timer" "${SYSTEMD_DIR}/"
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "Service files installed. Use 'sudo systemctl enable --now ${SERVICE_NAME}.timer' to start scheduling."
}

# Function to remove the service
remove_service() {
    echo "Removing AI Solarpunk Story Bot service..."
    
    # Stop and disable the service
    systemctl stop "${SERVICE_NAME}.timer"
    systemctl disable "${SERVICE_NAME}.timer"
    systemctl stop "${SERVICE_NAME}.service"
    systemctl disable "${SERVICE_NAME}.service"
    
    # Remove service files
    rm -f "${SYSTEMD_DIR}/${SERVICE_NAME}.service"
    rm -f "${SYSTEMD_DIR}/${SERVICE_NAME}.timer"
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "Service removed successfully."
}

# Function to show service status
show_status() {
    echo "=== AI Solarpunk Story Bot Service Status ==="
    echo ""
    echo "Service Status:"
    systemctl status "${SERVICE_NAME}.service"
    echo ""
    echo "Timer Status:"
    systemctl status "${SERVICE_NAME}.timer"
    echo ""
    echo "Recent Logs:"
    journalctl -u "${SERVICE_NAME}.service" -n 20
}

# Function to show help
show_help() {
    echo "AI Solarpunk Story Bot - Service Management"
    echo ""
    echo "Usage: sudo $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install    Install and configure the service"
    echo "  remove     Remove the service"
    echo "  status     Show service status and recent logs"
    echo "  help       Show this help message"
}

# Main command handling
case "$1" in
    install)
        install_service
        ;;
    remove)
        remove_service
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac 