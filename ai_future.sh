#!/bin/bash
# AI Solarpunk Story Bot - Enhanced Management Interface

# Set environment variables for UV
export UV_HTTP_TIMEOUT=300  # 5 minutes timeout for downloads

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display the script header
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
    echo -e "${YELLOW}============== Solarpunk Story Generator and Publisher ==============${NC}"
    echo -e "${GREEN}Using UV package manager${NC}"
}

# Function to run the original run.sh with parameters
run_original_script() {
    ./run.sh "$@"
}

# Function to generate and post content
generate_and_post() {
    echo -e "\n${GREEN}Story Generation and Posting${NC}"
    echo -e "${YELLOW}1)${NC} Quick post (random setting, digital-art)"
    echo -e "${YELLOW}2)${NC} Choose setting"
    echo -e "${YELLOW}3)${NC} Advanced options"
    echo -e "${YELLOW}4)${NC} Preview without posting"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " gen_choice

    case $gen_choice in
        1)
            run_original_script run-unified random
            ;;
        2)
            echo -e "\n${BLUE}Available settings:${NC}"
            echo -e "${CYAN}1)${NC} Urban    - City-focused sustainable technology"
            echo -e "${CYAN}2)${NC} Coastal  - Ocean and waterfront communities"
            echo -e "${CYAN}3)${NC} Forest   - Woodland and natural integration"
            echo -e "${CYAN}4)${NC} Desert   - Arid climate adaptation"
            echo -e "${CYAN}5)${NC} Rural    - Sustainable agriculture"
            read -p "Enter setting number: " setting_num
            
            case $setting_num in
                1) setting="urban" ;;
                2) setting="coastal" ;;
                3) setting="forest" ;;
                4) setting="desert" ;;
                5) setting="rural" ;;
                *) 
                    echo -e "${RED}Invalid setting, using random${NC}"
                    setting="random"
                    ;;
            esac
            run_original_script run-unified "$setting"
            ;;
        3)
            advanced_generation
            ;;
        4)
            preview_generation
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
}

# Function for advanced generation options
advanced_generation() {
    echo -e "\n${GREEN}Advanced Generation Options${NC}"
    
    # Setting selection
    echo -e "\n${BLUE}Select setting:${NC}"
    echo -e "${CYAN}1)${NC} Urban    - City-focused sustainable technology"
    echo -e "${CYAN}2)${NC} Coastal  - Ocean and waterfront communities"
    echo -e "${CYAN}3)${NC} Forest   - Woodland and natural integration"
    echo -e "${CYAN}4)${NC} Desert   - Arid climate adaptation"
    echo -e "${CYAN}5)${NC} Rural    - Sustainable agriculture"
    echo -e "${CYAN}6)${NC} Random   - Let the AI choose"
    read -p "Enter setting number [6]: " setting_num
    case $setting_num in
        1) setting="urban" ;;
        2) setting="coastal" ;;
        3) setting="forest" ;;
        4) setting="desert" ;;
        5) setting="rural" ;;
        *) setting="random" ;;
    esac

    # Style selection
    echo -e "\n${BLUE}Select style:${NC}"
    echo -e "${CYAN}1)${NC} Photographic - Realistic photography style"
    echo -e "${CYAN}2)${NC} Digital-art  - Digital illustration style"
    echo -e "${CYAN}3)${NC} Watercolor   - Artistic watercolor style"
    read -p "Enter style number [2]: " style_num
    case $style_num in
        1) style="photographic" ;;
        3) style="watercolor" ;;
        *) style="digital-art" ;;
    esac

    run_original_script generate-and-post "$setting" "$style"
}

# Function to preview generation without posting
preview_generation() {
    echo -e "\n${BLUE}Generating preview (will not post to Twitter)...${NC}"
    # TODO: Implement preview functionality
    echo -e "${YELLOW}Preview functionality coming soon!${NC}"
}

# Function to manage scheduling
manage_scheduling() {
    echo -e "\n${GREEN}Scheduling Management${NC}"
    echo -e "${YELLOW}1)${NC} Set up daily schedule"
    echo -e "${YELLOW}2)${NC} Set up weekly schedule"
    echo -e "${YELLOW}3)${NC} View current schedule"
    echo -e "${YELLOW}4)${NC} Remove all schedules"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " schedule_choice

    case $schedule_choice in
        1)
            read -p "Enter time (HH:MM): " time
            run_original_script schedule daily "$time"
            ;;
        2)
            read -p "Enter time (HH:MM): " time
            run_original_script schedule weekly "$time"
            ;;
        3)
            echo -e "${BLUE}Current schedule:${NC}"
            crontab -l
            ;;
        4)
            echo -e "${RED}WARNING: This will remove all scheduled tasks!${NC}"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                crontab -r
                echo -e "${GREEN}All schedules removed${NC}"
            fi
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
}

# Function to view recent activity
view_recent_activity() {
    echo -e "\n${GREEN}Recent Activity${NC}"
    echo -e "${YELLOW}1)${NC} View recent posts"
    echo -e "${YELLOW}2)${NC} View recent images"
    echo -e "${YELLOW}3)${NC} View logs"
    echo -e "${YELLOW}4)${NC} View statistics"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " activity_choice

    case $activity_choice in
        1)
            echo -e "${BLUE}Recent posts:${NC}"
            ls -lt output/twitter_tests/ | head -n 5
            ;;
        2)
            echo -e "${BLUE}Recent images:${NC}"
            ls -lt output/images/ | head -n 5
            ;;
        3)
            echo -e "${BLUE}Recent logs:${NC}"
            ls -lt logs/ | head -n 5
            ;;
        4)
            show_statistics
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
}

# Function to show statistics
show_statistics() {
    echo -e "\n${BLUE}System Statistics${NC}"
    echo -e "${CYAN}Total posts:${NC} $(ls -1 output/twitter_tests/ | wc -l)"
    echo -e "${CYAN}Total images:${NC} $(ls -1 output/images/ | wc -l)"
    echo -e "${CYAN}Disk usage:${NC} $(du -sh output/)"
}

# Main menu function
show_menu() {
    echo -e "\n${GREEN}Select an action:${NC}"
    echo -e "${YELLOW}1)${NC} Generate and post story"
    echo -e "${YELLOW}2)${NC} Manage scheduling"
    echo -e "${YELLOW}3)${NC} View recent activity"
    echo -e "${YELLOW}4)${NC} Check system status"
    echo -e "${YELLOW}h)${NC} Show help"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " choice

    case $choice in
        1)
            generate_and_post
            ;;
        2)
            manage_scheduling
            ;;
        3)
            view_recent_activity
            ;;
        4)
            check_system_status
            ;;
        h|H)
            show_help
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
}

# Function to check system status
check_system_status() {
    echo -e "\n${BLUE}System Status${NC}"
    
    # Check if credentials exist
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓${NC} Credentials file found"
    else
        echo -e "${RED}✗${NC} Credentials file missing"
    fi

    # Check output directories
    if [ -d "output/stories" ] && [ -d "output/images" ]; then
        echo -e "${GREEN}✓${NC} Output directories exist"
    else
        echo -e "${RED}✗${NC} Output directories missing"
    fi

    # Check scheduled tasks
    if crontab -l 2>/dev/null | grep -q "run.sh"; then
        echo -e "${GREEN}✓${NC} Scheduled tasks found"
        echo -e "${BLUE}Current schedule:${NC}"
        crontab -l | grep "run.sh"
    else
        echo -e "${YELLOW}!${NC} No scheduled tasks"
    fi

    # Show disk usage
    echo -e "\n${BLUE}Disk Usage:${NC}"
    du -sh output/* 2>/dev/null || echo "No output files yet"
}

# Main function
main() {
    show_header

    # If command-line arguments were provided
    if [ $# -gt 0 ]; then
        case "$1" in
            "generate"|"post")
                run_original_script run-unified "${2:-random}"
                ;;
            "schedule")
                run_original_script schedule "$2" "$3"
                ;;
            "status")
                check_system_status
                ;;
            *)
                echo -e "${RED}Unknown command: $1${NC}"
                show_help
                exit 1
                ;;
        esac
        exit 0
    fi

    # Interactive mode
    while true; do
        show_menu
        echo
        read -p "Press Enter to continue..."
        clear
        show_header
    done
}

# Make the script executable
chmod +x ai_future.sh

# Run the script
main "$@" 