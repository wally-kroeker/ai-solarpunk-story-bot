#!/bin/bash
# AI Solarpunk Story Bot - Minimal Management Interface (Lite)

# Set environment variables for UV
export UV_HTTP_TIMEOUT=300

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SERVICE_NAME="ai-solarpunk-story"
SYSTEMD_DIR="/etc/systemd/system"

show_header() {
    clear
    echo -e "${CYAN}"
    echo "    █████╗ ██╗    ███████╗██╗   ██╗████████╗██╗   ██╗██████╗ ███████╗"
    echo "   ██╔══██╗██║    ██╔════╝██║   ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝"
    echo "   ███████║██║    █████╗  ██║   ██║   ██║   ██║   ██║██████╔╝█████╗  "
    echo "   ██╔══██║██║    ██╔══╝  ██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  "
    echo "   ██║  ██║██║    ██║     ╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗"
    echo "   ╚═╝  ╚═╝╚═╝    ╚═╝      ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝"
    echo -e "${NC}"
    echo -e "${YELLOW}========= Solarpunk Story Bot - Management (Lite) =========${NC}"
}

display_timezone_info() {
    if [ -f "config/timezone.conf" ]; then
        USER_TZ_NAME=$(grep "^USER_TZ_NAME=" config/timezone.conf | cut -d= -f2)
        USER_TZ_OFFSET=$(grep "^USER_TZ_OFFSET=" config/timezone.conf | cut -d= -f2)
        echo -e "${BLUE}Current Timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
        local current_time=$(TZ=$USER_TZ_NAME date +"%H:%M")
        local utc_time=$(TZ=UTC date +"%H:%M")
        echo -e "${GREEN}Current time: $current_time ($USER_TZ_NAME) / $utc_time (UTC)${NC}"
    else
        echo -e "${YELLOW}No timezone set - using UTC${NC}"
    fi
}

check_service_status() {
    echo -e "${YELLOW}Checking AI Solarpunk Story Bot Service Status${NC}"
    echo -e "\n${BLUE}Service Status:${NC}"
    systemctl status "$SERVICE_NAME.service" | head -n 5
    echo -e "\n${BLUE}Timer Status:${NC}"
    systemctl status "$SERVICE_NAME.timer" | head -n 5
    echo -e "\n${BLUE}Next Scheduled Run:${NC}"
    systemctl list-timers "$SERVICE_NAME.timer" | grep "$SERVICE_NAME"
    echo -e "\n${BLUE}Recent Logs:${NC}"
    journalctl -u "$SERVICE_NAME.service" -n 5
    read -p "Press Enter to continue..."
}

view_logs() {
    echo -e "${YELLOW}Viewing AI Solarpunk Story Bot Logs${NC}"
    echo -e "${BLUE}Log viewing options:${NC}"
    echo "1) View recent logs (last 50 lines)"
    echo "2) View today's logs"
    echo "3) View logs with follow mode (live updates)"
    echo "4) View service log file (detailed script output)"
    echo "5) Back to main menu"
    read -p "Enter your choice: " choice
    case $choice in
        1)
            echo -e "${YELLOW}Last 50 log entries:${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service -n 50 --no-pager"
            ;;
        2)
            echo -e "${YELLOW}Today's logs:${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service --since today --no-pager"
            ;;
        3)
            echo -e "${YELLOW}Following logs (press Ctrl+C to exit):${NC}"
            echo -e "${GREEN}Please run this command:${NC}"
            echo -e "sudo journalctl -u $SERVICE_NAME.service -f"
            ;;
        4)
            echo -e "${YELLOW}Service log file (actual script output):${NC}"
            if [ ! -d "logs" ]; then
                mkdir -p logs
                touch logs/service.log
                echo "Log file created. No entries yet." > logs/service.log
            fi
            if [ ! -f "logs/service.log" ]; then
                touch logs/service.log
                echo "Log file created. No entries yet." > logs/service.log
            fi
            echo -e "${GREEN}Contents of service log file (last 50 lines):${NC}"
            tail -n 50 logs/service.log
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
    read -p "Press Enter to continue..."
}

manage_schedule() {
    echo -e "${YELLOW}Schedule management is available via timer file and timezone logic.${NC}"
    echo -e "${GREEN}Please use the main bot-manager.sh for advanced schedule editing.${NC}"
    read -p "Press Enter to continue..."
}

cleanup_outputs() {
    echo -e "\n${GREEN}Output Folder Cleanup and Archiving${NC}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local archive_dir="archive/${timestamp}"
    mkdir -p "$archive_dir/stories" "$archive_dir/images" "$archive_dir/previews" "$archive_dir/preview_files"
    echo -e "${BLUE}Archiving all output files...${NC}"
    mv output/stories/* "$archive_dir/stories/" 2>/dev/null
    mv output/images/* "$archive_dir/images/" 2>/dev/null
    mv output/previews/* "$archive_dir/previews/" 2>/dev/null
    mv output/preview_files/* "$archive_dir/preview_files/" 2>/dev/null
    echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
    mkdir -p output/stories output/images output/previews output/preview_files
    read -p "Press Enter to continue..."
}

view_recent_activity() {
    echo -e "\n${GREEN}Recent Activity${NC}"
    echo -e "${YELLOW}1)${NC} View recent posts"
    echo -e "${YELLOW}2)${NC} View recent images"
    echo -e "${YELLOW}3)${NC} View recent previews"
    echo -e "${YELLOW}4)${NC} View logs"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"
    read -p "Enter your choice: " activity_choice
    case $activity_choice in
        1)
            echo -e "${BLUE}Recent posts:${NC}"
            ls -lt output/stories/ | head -n 5
            ;;
        2)
            echo -e "${BLUE}Recent images:${NC}"
            ls -lt output/images/ | head -n 5
            ;;
        3)
            echo -e "${BLUE}Recent previews:${NC}"
            ls -lt output/previews/ | head -n 5
            ;;
        4)
            view_logs
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    read -p "Press Enter to continue..."
}

main_menu() {
    local choice
    while true; do
        show_header
        display_timezone_info
        echo -e "\n${YELLOW}Main Menu${NC}"
        echo "1) Check Service Status"
        echo "2) View Logs"
        echo "3) Manage Schedule (info only)"
        echo "4) Cleanup and Archive Outputs"
        echo "5) View Recent Activity"
        echo "6) Exit"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                check_service_status
                ;;
            2)
                view_logs
                ;;
            3)
                manage_schedule
                ;;
            4)
                cleanup_outputs
                ;;
            5)
                view_recent_activity
                ;;
            6)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
    done
}

main_menu 