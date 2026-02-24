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

# Available settings and styles
SETTINGS=("urban" "coastal" "forest" "desert" "rural" "mountain" "arctic" "island")
STYLES=("digital-art" "watercolor" "stylized" "solarpunk-nouveau" "retro-futurism" "isometric")

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

# Function to run the generator with specified options
run_generator() {
    local setting=$1
    local style=$2
    local features=$3
    local preview=$4
    local extra_arg=$5
    local extra_value=$6

    local cmd="uv run src/ai_story_tweet_generator.py"
    
    # Add arguments if provided
    [[ -n $setting ]] && cmd="$cmd --setting $setting"
    [[ -n $style ]] && cmd="$cmd --style $style"
    [[ -n $features ]] && cmd="$cmd --features $features"
    [[ $preview == true ]] && cmd="$cmd --preview"
    [[ -n $extra_arg ]] && cmd="$cmd $extra_arg $extra_value"

    echo -e "${BLUE}Running command: $cmd${NC}"
    eval $cmd
}

# Function to display available eras for world-building stories
show_eras() {
    echo -e "\n${CYAN}===== Available Eras =====${NC}"
    echo -e "${YELLOW}0)${NC} ${GREEN}Tipping Point${NC}"
    echo -e "   ${CYAN}Compounded AI disruption, severe climate events, social polarisation.${NC}"
    echo -e "   ${CYAN}Grassroots mindfulness labs experiment with early Pods.${NC}\n"
    
    echo -e "${YELLOW}1)${NC} ${GREEN}Extinction Burst${NC}"
    echo -e "   ${CYAN}Old patriarchal institutions tighten control; \"scarcity wars\" over data & water.${NC}"
    echo -e "   ${CYAN}Prototype Pods prove transformative, spreading via open-source blueprints.${NC}\n"
    
    # Note for future eras
    echo -e "${BLUE}More eras will be added as the world-building system expands${NC}"
}

# Function to list existing characters from the continuity file
list_characters() {
    echo -e "\n${CYAN}===== Available Characters =====${NC}"
    
    # Check if continuity file exists
    if [ ! -f "output/continuity.json" ]; then
        echo -e "${YELLOW}No continuity file found. No characters available yet.${NC}"
        echo -e "${BLUE}Generate some stories first to create characters!${NC}"
        return
    fi
    
    # Check if the file is readable and has content
    if [ ! -s "output/continuity.json" ]; then
        echo -e "${YELLOW}Continuity file is empty. No characters available yet.${NC}"
        echo -e "${BLUE}Generate some stories first to create characters!${NC}"
        return
    fi
    
    # Try to read characters using Python with error handling
    local char_output
    char_output=$(uv run python3 -c "
import json
import sys

try:
    with open('output/continuity.json', 'r') as f:
        data = json.load(f)
    
    characters = data.get('characters', [])
    
    if not characters:
        print('EMPTY')
    else:
        for i, char in enumerate(characters):
            name = char.get('name', 'Unknown')
            archetype = char.get('archetype', 'Unknown')
            backstory = char.get('backstory', 'No backstory available')
            appearances = len(char.get('story_appearances', []))
            
            print(f'{i+1}|{name}|{archetype}|{backstory}|{appearances}')
            
except json.JSONDecodeError:
    print('ERROR_JSON')
except Exception as e:
    print('ERROR_OTHER')
" 2>/dev/null)
    
    # Handle different outcomes
    case "$char_output" in
        "EMPTY")
            echo -e "${YELLOW}No characters found in continuity file.${NC}"
            echo -e "${BLUE}Generate some stories first to create characters!${NC}"
            ;;
        "ERROR_JSON")
            echo -e "${RED}Error: Continuity file contains invalid JSON.${NC}"
            echo -e "${BLUE}You may need to regenerate the continuity file.${NC}"
            ;;
        "ERROR_OTHER")
            echo -e "${RED}Error: Could not read continuity file.${NC}"
            echo -e "${BLUE}Please check file permissions and try again.${NC}"
            ;;
        "")
            echo -e "${RED}Error: Failed to read character data.${NC}"
            ;;
        *)
            # Success - display characters
            local char_count=0
            while IFS='|' read -r num name archetype backstory appearances; do
                if [[ -n "$num" ]]; then
                    echo -e "${YELLOW}$num)${NC} ${GREEN}$name${NC} ${CYAN}($archetype)${NC}"
                    echo -e "   ${BLUE}Backstory:${NC} $backstory"
                    echo -e "   ${BLUE}Appeared in:${NC} $appearances stories\n"
                    ((char_count++))
                fi
            done <<< "$char_output"
            
            if [ $char_count -eq 0 ]; then
                echo -e "${YELLOW}No characters found.${NC}"
            else
                echo -e "${BLUE}Total characters available: $char_count${NC}"
            fi
            ;;
    esac
}

# Function for era selection and story generation with a new character
era_selection() {
    clear
    echo -e "${GREEN}===== New Story Generation =====${NC}"
    echo -e "${BLUE}Select an era for your new story:${NC}\n"
    
    show_eras
    
    echo -e "\n${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"
    
    read -p "Enter your choice (0-1, b, q): " era_choice
    
    case $era_choice in
        0|1)
            # Validate era choice
            if [[ $era_choice =~ ^[0-1]$ ]]; then
                echo -e "\n${BLUE}Generating new story in era $era_choice...${NC}"
                
                # Use the run_generator function with new era parameters
                local cmd="uv run src/ai_story_tweet_generator.py --era-id $era_choice --features story,image"
                echo -e "${BLUE}Running command: $cmd${NC}"
                eval $cmd
                
                echo -e "\n${GREEN}Story generation completed!${NC}"
                read -p "Press Enter to continue..." 
            else
                echo -e "${RED}Invalid era selection. Please try again.${NC}"
                sleep 2
                era_selection
                return
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
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            era_selection
            ;;
    esac
}

# Function for character selection and story generation with existing character
character_selection() {
    clear
    echo -e "${GREEN}===== Story with Existing Character =====${NC}"
    echo -e "${BLUE}Select an existing character for your story:${NC}\n"
    
    # Display available characters
    list_characters
    
    # Check if we actually have characters to choose from
    if [ ! -f "output/continuity.json" ] || [ ! -s "output/continuity.json" ]; then
        echo -e "\n${YELLOW}No characters available. Generate some stories first!${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Get character count for validation
    local char_count
    char_count=$(uv run python3 -c "
import json
try:
    with open('output/continuity.json', 'r') as f:
        data = json.load(f)
    print(len(data.get('characters', [])))
except:
    print('0')
" 2>/dev/null)
    
    if [ "$char_count" -eq "0" ]; then
        echo -e "\n${YELLOW}No characters found. Generate some stories first!${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    echo -e "\n${YELLOW}0)${NC} Back to main menu"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"
    
    read -p "Enter character number (1-$char_count, 0/b, q): " char_choice
    
    case $char_choice in
        0|b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        [1-9]*)
            # Validate character choice
            if [[ $char_choice =~ ^[0-9]+$ ]] && [[ $char_choice -ge 1 ]] && [[ $char_choice -le $char_count ]]; then
                # Get the character name
                local char_name
                char_name=$(uv run python3 -c "
import json
try:
    with open('output/continuity.json', 'r') as f:
        data = json.load(f)
    characters = data.get('characters', [])
    if $((char_choice-1)) < len(characters):
        print(characters[$((char_choice-1))]['name'])
    else:
        print('ERROR')
except:
    print('ERROR')
" 2>/dev/null)
                
                if [ "$char_name" = "ERROR" ] || [ -z "$char_name" ]; then
                    echo -e "${RED}Error getting character information. Please try again.${NC}"
                    sleep 2
                    character_selection
                    return
                fi
                
                # Now select era for this character's story
                clear
                echo -e "${GREEN}===== Era Selection for $char_name =====${NC}"
                echo -e "${BLUE}Select an era for ${GREEN}$char_name${BLUE}'s story:${NC}\n"
                
                show_eras
                
                echo -e "\n${YELLOW}b)${NC} Back to character selection"
                echo -e "${YELLOW}q)${NC} Quit"
                
                read -p "Enter era choice (0-1, b, q): " era_choice
                
                case $era_choice in
                    0|1)
                        if [[ $era_choice =~ ^[0-1]$ ]]; then
                            echo -e "\n${BLUE}Generating story for ${GREEN}$char_name${BLUE} in era $era_choice...${NC}"
                            
                            # Generate story with selected character and era
                            local cmd="uv run src/ai_story_tweet_generator.py --era-id $era_choice --use-existing-character --character-name \"$char_name\" --features story,image"
                            echo -e "${BLUE}Running command: $cmd${NC}"
                            eval $cmd
                            
                            echo -e "\n${GREEN}Story generation completed!${NC}"
                            read -p "Press Enter to continue..."
                        else
                            echo -e "${RED}Invalid era selection.${NC}"
                            sleep 2
                            character_selection
                        fi
                        ;;
                    b|B)
                        character_selection
                        return
                        ;;
                    q|Q)
                        echo -e "${GREEN}Exiting.${NC}"
                        exit 0
                        ;;
                    *)
                        echo -e "${RED}Invalid choice. Please try again.${NC}"
                        sleep 2
                        character_selection
                        ;;
                esac
            else
                echo -e "${RED}Invalid character selection. Please enter a number between 1 and $char_count.${NC}"
                sleep 2
                character_selection
            fi
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            character_selection
            ;;
         esac
}

# Function to view continuity information main menu
view_continuity() {
    clear
    echo -e "${GREEN}===== Continuity Information =====${NC}"
    echo -e "${BLUE}View the story universe and character development:${NC}\n"
    
    echo -e "${YELLOW}1)${NC} View all characters"
    echo -e "${YELLOW}2)${NC} View story log"
    echo -e "${YELLOW}3)${NC} View era information"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"
    
    read -p "Enter your choice (1-3, b, q): " continuity_choice
    
    case $continuity_choice in
        1)
            view_characters
            ;;
        2)
            view_story_log
            ;;
        3)
            view_era_info
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            view_continuity
            ;;
    esac
}

# Function to view detailed character information
view_characters() {
    clear
    echo -e "${GREEN}===== Character Details =====${NC}"
    
    # Check if continuity file exists
    if [ ! -f "output/continuity.json" ] || [ ! -s "output/continuity.json" ]; then
        echo -e "${YELLOW}No continuity file found. Generate some stories first!${NC}"
        read -p "Press Enter to continue..."
        view_continuity
        return
    fi
    
    # Display detailed character information
    local char_output
    char_output=$(uv run python3 -c "
import json
try:
    with open('output/continuity.json', 'r') as f:
        data = json.load(f)
    
    characters = data.get('characters', [])
    
    if not characters:
        print('EMPTY')
    else:
        for char in characters:
            name = char.get('name', 'Unknown')
            archetype = char.get('archetype', 'Unknown')
            appearance = char.get('appearance', 'No description available')
            backstory = char.get('backstory', 'No backstory available')
            faction = char.get('faction', 'Unknown')
            traits = char.get('traits', [])
            appearances = len(char.get('story_appearances', []))
            
            print(f'NAME:{name}')
            print(f'ARCHETYPE:{archetype}')
            print(f'APPEARANCE:{appearance}')
            print(f'BACKSTORY:{backstory}')
            print(f'FACTION:{faction}')
            print(f'TRAITS:{\"|\".join(traits) if traits else \"None\"}')
            print(f'APPEARANCES:{appearances}')
            print('---SEPARATOR---')
            
except Exception as e:
    print('ERROR')
" 2>/dev/null)
    
    case "$char_output" in
        "EMPTY")
            echo -e "${YELLOW}No characters found. Generate some stories first!${NC}"
            ;;
        "ERROR")
            echo -e "${RED}Error reading character data.${NC}"
            ;;
        *)
            # Parse and display character data
            echo "$char_output" | while IFS= read -r line; do
                if [[ $line == NAME:* ]]; then
                    name="${line#NAME:}"
                    echo -e "\n${GREEN}━━━ $name ━━━${NC}"
                elif [[ $line == ARCHETYPE:* ]]; then
                    archetype="${line#ARCHETYPE:}"
                    echo -e "${CYAN}Archetype:${NC} $archetype"
                elif [[ $line == APPEARANCE:* ]]; then
                    appearance="${line#APPEARANCE:}"
                    echo -e "${CYAN}Appearance:${NC} $appearance"
                elif [[ $line == BACKSTORY:* ]]; then
                    backstory="${line#BACKSTORY:}"
                    echo -e "${CYAN}Backstory:${NC} $backstory"
                elif [[ $line == FACTION:* ]]; then
                    faction="${line#FACTION:}"
                    echo -e "${CYAN}Faction:${NC} $faction"
                elif [[ $line == TRAITS:* ]]; then
                    traits="${line#TRAITS:}"
                    if [[ "$traits" != "None" ]]; then
                        traits_formatted=$(echo "$traits" | sed 's/|/, /g')
                        echo -e "${CYAN}Traits:${NC} $traits_formatted"
                    else
                        echo -e "${CYAN}Traits:${NC} None specified"
                    fi
                elif [[ $line == APPEARANCES:* ]]; then
                    appearances="${line#APPEARANCES:}"
                    echo -e "${CYAN}Story Appearances:${NC} $appearances"
                elif [[ $line == "---SEPARATOR---" ]]; then
                    echo ""
                fi
            done
            ;;
    esac
    
    echo -e "\n${BLUE}Press Enter to return to continuity menu...${NC}"
    read
    view_continuity
}

# Function to view story log
view_story_log() {
    clear
    echo -e "${GREEN}===== Story Log =====${NC}"
    
    # Check if continuity file exists
    if [ ! -f "output/continuity.json" ] || [ ! -s "output/continuity.json" ]; then
        echo -e "${YELLOW}No continuity file found. Generate some stories first!${NC}"
        read -p "Press Enter to continue..."
        view_continuity
        return
    fi
    
    # Display story log
    local story_output
    story_output=$(uv run python3 -c "
import json
from datetime import datetime
try:
    with open('output/continuity.json', 'r') as f:
        data = json.load(f)
    
    story_log = data.get('story_log', [])
    
    if not story_log:
        print('EMPTY')
    else:
        for event in story_log:
            event_id = event.get('id', 'Unknown')
            title = event.get('title', 'Untitled')
            summary = event.get('summary', 'No summary available')
            era = event.get('era', 'Unknown')
            characters = event.get('characters', [])
            timestamp = event.get('timestamp', '')
            
            print(f'ID:{event_id}')
            print(f'TITLE:{title}')
            print(f'SUMMARY:{summary}')
            print(f'ERA:{era}')
            print(f'CHARACTERS:{\"||\".join(characters) if characters else \"None\"}')
            print(f'TIMESTAMP:{timestamp}')
            print('---SEPARATOR---')
            
except Exception as e:
    print('ERROR')
" 2>/dev/null)
    
    case "$story_output" in
        "EMPTY")
            echo -e "${YELLOW}No stories found. Generate some stories first!${NC}"
            ;;
        "ERROR")
            echo -e "${RED}Error reading story log data.${NC}"
            ;;
        *)
            # Parse and display story data
            echo "$story_output" | while IFS= read -r line; do
                if [[ $line == ID:* ]]; then
                    story_id="${line#ID:}"
                    echo -e "\n${GREEN}━━━ Story #$story_id ━━━${NC}"
                elif [[ $line == TITLE:* ]]; then
                    title="${line#TITLE:}"
                    echo -e "${CYAN}Title:${NC} $title"
                elif [[ $line == SUMMARY:* ]]; then
                    summary="${line#SUMMARY:}"
                    echo -e "${CYAN}Summary:${NC} $summary"
                elif [[ $line == ERA:* ]]; then
                    era="${line#ERA:}"
                    era_name="Unknown"
                    case $era in
                        0) era_name="Tipping Point" ;;
                        1) era_name="Extinction Burst" ;;
                    esac
                    echo -e "${CYAN}Era:${NC} $era ($era_name)"
                elif [[ $line == CHARACTERS:* ]]; then
                    characters="${line#CHARACTERS:}"
                    if [[ "$characters" != "None" ]]; then
                        characters_formatted=$(echo "$characters" | sed 's/||/, /g')
                        echo -e "${CYAN}Characters:${NC} $characters_formatted"
                    else
                        echo -e "${CYAN}Characters:${NC} None"
                    fi
                elif [[ $line == TIMESTAMP:* ]]; then
                    timestamp="${line#TIMESTAMP:}"
                    echo -e "${CYAN}Created:${NC} $timestamp"
                elif [[ $line == "---SEPARATOR---" ]]; then
                    echo ""
                fi
            done
            ;;
    esac
    
    echo -e "\n${BLUE}Press Enter to return to continuity menu...${NC}"
    read
    view_continuity
}

# Function to view era information
view_era_info() {
    clear
    echo -e "${GREEN}===== Era Information =====${NC}"
    echo -e "${BLUE}Detailed information about the story world eras:${NC}\n"
    
    show_eras
    
    echo -e "\n${BLUE}These eras form the backbone of the Solarpunk story universe.${NC}"
    echo -e "${BLUE}Characters and stories are set within these historical periods,${NC}"
    echo -e "${BLUE}each with distinct technological, social, and environmental contexts.${NC}"
    
    echo -e "\n${BLUE}Press Enter to return to continuity menu...${NC}"
    read
    view_continuity
}

# Function to generate and post content
generate_and_post() {
    echo -e "\n${GREEN}Story Generation and Posting${NC}"
    echo -e "${YELLOW}1)${NC} Quick post (random everything)"
    echo -e "${YELLOW}2)${NC} Choose setting and style"
    echo -e "${YELLOW}3)${NC} Advanced options"
    echo -e "${YELLOW}4)${NC} Preview mode"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " gen_choice

    case $gen_choice in
        1)
            run_generator "random" "random" "story,image,post" false
            ;;
        2)
            # Setting selection
            echo -e "\n${BLUE}Choose Setting:${NC}"
            for i in "${!SETTINGS[@]}"; do
                echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
            done
            echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
            
            read -p "Select setting (1-$((${#SETTINGS[@]}+1))): " setting_num
            
            if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
                setting="${SETTINGS[$((setting_num-1))]}"
            else
                setting="random"
            fi
            
            # Style selection
            echo -e "\n${BLUE}Choose Style:${NC}"
            for i in "${!STYLES[@]}"; do
                echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
            done
            echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
            
            read -p "Select style (1-$((${#STYLES[@]}+1))): " style_num
            
            if [[ $style_num -le ${#STYLES[@]} ]]; then
                style="${STYLES[$((style_num-1))]}"
            else
                style="random"
            fi
            
            run_generator "$setting" "$style" "story,image,post" false
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
    for i in "${!SETTINGS[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
    done
    echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
    
    read -p "Enter setting number [$((${#SETTINGS[@]}+1))]: " setting_num
    if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
        setting="${SETTINGS[$((setting_num-1))]}"
    else
        setting="random"
    fi

    # Style selection
    echo -e "\n${BLUE}Select style:${NC}"
    for i in "${!STYLES[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
    done
    echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
    
    read -p "Enter style number [$((${#STYLES[@]}+1))]: " style_num
    if [[ $style_num -le ${#STYLES[@]} ]]; then
        style="${STYLES[$((style_num-1))]}"
    else
        style="random"
    fi

    # Feature selection
    echo -e "\n${BLUE}Select features:${NC}"
    echo -e "${CYAN}1)${NC} Story only"
    echo -e "${CYAN}2)${NC} Story + Image"
    echo -e "${CYAN}3)${NC} Complete (Story + Image + Post)"
    
    read -p "Enter feature set [3]: " feature_num
    case $feature_num in
        1) features="story" ;;
        2) features="story,image" ;;
        *) features="story,image,post" ;;
    esac

    # Preview option
    echo -e "\n${BLUE}Preview mode?${NC}"
    read -p "Generate preview only (no posting) [y/N]: " preview_choice
    preview=false
    [[ $preview_choice =~ ^[Yy]$ ]] && preview=true

    run_generator "$setting" "$style" "$features" "$preview"
}

# Function to preview story and image side by side
preview_story_and_image() {
    local story_file="$1"
    local image_file="$2"

    # Validate inputs
    if [ ! -f "$story_file" ]; then
        echo -e "${RED}Error: Story file not found: $story_file${NC}"
        return 1
    fi

    if [ ! -f "$image_file" ]; then
        echo -e "${RED}Error: Image file not found: $image_file${NC}"
        return 1
    fi

    # Get terminal width and height with fallbacks
    local term_width=$(tput cols || echo 80)
    local term_height=$(tput lines || echo 24)
    
    # Ensure minimum dimensions
    if [ "$term_width" -lt 80 ]; then
        term_width=80
    fi
    
    if [ "$term_height" -lt 24 ]; then
        term_height=24
    fi
    
    # Calculate image width (use ~40% of terminal width)
    local img_width=$((term_width * 4 / 10))
    local text_width=$((term_width / 2 - 5))  # Reduced width for text to ensure padding
    
    # Clear screen for better presentation
    clear
    
    # Print header
    echo -e "${CYAN}======= Solarpunk Story Preview =======${NC}\n"
    
    # Create a temporary file for the story with proper formatting
    local temp_story=$(mktemp)
    fold -s -w "$text_width" "$story_file" > "$temp_story"
    
    # Add padding after story
    local story_lines=$(wc -l < "$temp_story")
    local padding_needed=$((term_height - story_lines - 10))  # 10 lines for header and footer
    
    # Use a more reliable approach for side-by-side display
    # First display story with some right padding
    echo -e "${YELLOW}Story:${NC}\n"
    cat "$temp_story"
    
    # Add some vertical space
    echo -e "\n"
    
    # Display image centered below story
    echo -e "${YELLOW}Image:${NC}\n"
    # Use the best timg settings - high quality, auto adjust
    timg -g "${img_width}x$((term_height/2))" -U -F -C -p h "$image_file"
    
    # Clean up
    rm "$temp_story"
    
    # Add a visual separator
    echo -e "\n${CYAN}=========================================${NC}"
    echo -e "${YELLOW}Would you like to post this story and image? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Posting story and image...${NC}"
        
        # Move files to permanent locations
        local timestamp=$(date +%s)
        local setting=$(basename "$story_file" | sed -n 's/story_\([^_]*\)_.*/\1/p')
        local style=$(basename "$image_file" | sed -n 's/image_[^_]*_\([^_]*\)_.*/\1/p')
        
        # Create permanent filenames
        local perm_story="output/stories/story_${setting}_${timestamp}.txt"
        local perm_image="output/images/image_${setting}_${style}_${timestamp}.png"
        
        # Move files
        cp "$story_file" "$perm_story"
        cp "$image_file" "$perm_image"
        
        # Post using the regular command
        run_generator "" "" "" false "--post-files" "$perm_story:$perm_image"
        
        echo -e "${GREEN}Story and image have been posted and saved to permanent storage${NC}"
    else
        echo -e "${YELLOW}Preview closed without posting.${NC}"
    fi
}

# Function to preview generation without posting
preview_generation() {
    echo -e "\n${BLUE}Preview Generation${NC}"
    
    # Create/ensure the preview directory exists and is empty
    local preview_dir="output/preview_files"
    mkdir -p "$preview_dir"
    rm -f "$preview_dir"/*
    
    # Setting selection
    echo -e "\n${BLUE}Select setting (or 'random'):${NC}"
    for i in "${!SETTINGS[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${SETTINGS[$i]}"
    done
    echo -e "${CYAN}$((${#SETTINGS[@]}+1)))${NC} random"
    
    read -p "Enter setting number [$((${#SETTINGS[@]}+1))]: " setting_num
    if [[ $setting_num -le ${#SETTINGS[@]} ]]; then
        setting="${SETTINGS[$((setting_num-1))]}"
    else
        setting="random"
    fi

    # Style selection
    echo -e "\n${BLUE}Select style (or 'random'):${NC}"
    for i in "${!STYLES[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${STYLES[$i]}"
    done
    echo -e "${CYAN}$((${#STYLES[@]}+1)))${NC} random"
    
    read -p "Enter style number [$((${#STYLES[@]}+1))]: " style_num
    if [[ $style_num -le ${#STYLES[@]} ]]; then
        style="${STYLES[$((style_num-1))]}"
    else
        style="random"
    fi

    # Generate content with output to preview directory
    echo -e "${BLUE}Generating new story and image...${NC}"
    run_generator "$setting" "$style" "story,image" true "--output-dir" "$preview_dir"
    
    # Find the story and image files in the preview directory
    local story_file=$(find "$preview_dir" -name "story_*.txt" | head -n 1)
    local image_file=$(find "$preview_dir" -name "image_*.png" | head -n 1)
    
    if [[ -n "$story_file" && -n "$image_file" && -f "$story_file" && -f "$image_file" ]]; then
        echo -e "${GREEN}Found story: $(basename "$story_file")${NC}"
        echo -e "${GREEN}Found image: $(basename "$image_file")${NC}"
        
        preview_story_and_image "$story_file" "$image_file"
    else
        echo -e "${RED}Error: Could not find generated files in preview directory${NC}"
        echo -e "${YELLOW}Preview directory contents:${NC}"
        ls -la "$preview_dir"
    fi
}

# Function to display timezone information with user timezone
display_timezone_info() {
    local utc_time=$(TZ=UTC date +"%H:%M")
    local server_time=$(date +"%H:%M")
    local server_tz_name=$(date +"%Z")
    local server_tz_offset=$(date +"%z")
    
    echo -e "${BLUE}Timezone Information:${NC}"
    echo -e "  • Server time: ${server_time} ${server_tz_name} (${server_tz_offset})"
    echo -e "  • UTC time:    ${utc_time} UTC"
    
    # If user timezone is set, show it
    if [ -n "$USER_TZ" ]; then
        local user_time=$(TZ="$USER_TZ" date +"%H:%M")
        echo -e "  • Your time:   ${user_time} $USER_TZ_NAME ($USER_TZ_OFFSET)"
    fi
    echo ""
}

# Function to convert between user local time and UTC
convert_user_to_utc() {
    local local_hour=$1
    local local_minute=$2
    
    # Use specified offset instead of system offset
    local tz_offset="$USER_TZ_OFFSET"
    local sign=${tz_offset:0:1}
    local tz_hours=${tz_offset:1:2}
    local tz_mins=${tz_offset:3:2}
    
    # Calculate total minutes offset
    local total_offset_mins=$((tz_hours * 60 + tz_mins))
    if [ "$sign" = "+" ]; then
        total_offset_mins=$((0 - total_offset_mins))
    fi
    
    # Convert local time to minutes since midnight
    local local_mins=$((local_hour * 60 + local_minute))
    
    # Apply offset to get UTC minutes
    local utc_mins=$((local_mins + total_offset_mins))
    
    # Handle day boundaries
    while [ $utc_mins -lt 0 ]; do
        utc_mins=$((utc_mins + 1440))  # Add 24 hours in minutes
    done
    while [ $utc_mins -ge 1440 ]; do
        utc_mins=$((utc_mins - 1440))  # Subtract 24 hours in minutes
    done
    
    # Convert back to hours and minutes
    local utc_hour=$((utc_mins / 60))
    local utc_minute=$((utc_mins % 60))
    
    echo "$utc_hour $utc_minute"
}

# Function to convert UTC time to user local time
convert_utc_to_user() {
    local utc_hour=$1
    local utc_minute=$2
    
    # Use specified offset instead of system offset
    local tz_offset="$USER_TZ_OFFSET"
    local sign=${tz_offset:0:1}
    local tz_hours=${tz_offset:1:2}
    local tz_mins=${tz_offset:3:2}
    
    # Calculate total minutes offset
    local total_offset_mins=$((tz_hours * 60 + tz_mins))
    if [ "$sign" = "-" ]; then
        total_offset_mins=$((0 - total_offset_mins))
    fi
    
    # Convert UTC time to minutes since midnight
    local utc_mins=$((utc_hour * 60 + utc_minute))
    
    # Apply offset to get local minutes
    local local_mins=$((utc_mins + total_offset_mins))
    
    # Handle day boundaries
    local day_shift="same day"
    if [ $local_mins -lt 0 ]; then
        local_mins=$((local_mins + 1440))  # Add 24 hours in minutes
        day_shift="previous day"
    elif [ $local_mins -ge 1440 ]; then
        local_mins=$((local_mins - 1440))  # Subtract 24 hours in minutes
        day_shift="next day"
    fi
    
    # Convert back to hours and minutes
    local local_hour=$((local_mins / 60))
    local local_minute=$((local_mins % 60))
    
    echo "$local_hour $local_minute $day_shift"
}

# Function to prompt for timezone selection
select_timezone() {
    echo -e "\n${CYAN}Timezone Selection${NC}"
    echo -e "${YELLOW}Please select your timezone:${NC}"
    
    # Common US timezones
    echo -e "${BLUE}US Timezones:${NC}"
    echo -e "1) Eastern (UTC-05:00/UTC-04:00 DST)"
    echo -e "2) Central (UTC-06:00/UTC-05:00 DST)"
    echo -e "3) Mountain (UTC-07:00/UTC-06:00 DST)"
    echo -e "4) Pacific (UTC-08:00/UTC-07:00 DST)"
    echo -e "5) Alaska (UTC-09:00/UTC-08:00 DST)"
    echo -e "6) Hawaii (UTC-10:00)"
    
    # European/Other timezones
    echo -e "\n${BLUE}European/Other Timezones:${NC}"
    echo -e "7) UK/Ireland (UTC+00:00/UTC+01:00 DST)"
    echo -e "8) Central Europe (UTC+01:00/UTC+02:00 DST)"
    echo -e "9) Eastern Europe (UTC+02:00/UTC+03:00 DST)"
    echo -e "10) India (UTC+05:30)"
    echo -e "11) Japan/Korea (UTC+09:00)"
    echo -e "12) Australia Eastern (UTC+10:00/UTC+11:00 DST)"
    
    # Custom option
    echo -e "\n13) Enter custom UTC offset"
    echo -e "14) Use server timezone (UTC)"
    
    read -p "Enter your choice (1-14): " tz_choice
    
    case $tz_choice in
        1)  USER_TZ="America/New_York"; USER_TZ_NAME="Eastern Time"; USER_TZ_OFFSET="-0500" ;;
        2)  USER_TZ="America/Chicago"; USER_TZ_NAME="Central Time"; USER_TZ_OFFSET="-0600" ;;
        3)  USER_TZ="America/Denver"; USER_TZ_NAME="Mountain Time"; USER_TZ_OFFSET="-0700" ;;
        4)  USER_TZ="America/Los_Angeles"; USER_TZ_NAME="Pacific Time"; USER_TZ_OFFSET="-0800" ;;
        5)  USER_TZ="America/Anchorage"; USER_TZ_NAME="Alaska Time"; USER_TZ_OFFSET="-0900" ;;
        6)  USER_TZ="Pacific/Honolulu"; USER_TZ_NAME="Hawaii Time"; USER_TZ_OFFSET="-1000" ;;
        7)  USER_TZ="Europe/London"; USER_TZ_NAME="UK Time"; USER_TZ_OFFSET="+0000" ;;
        8)  USER_TZ="Europe/Paris"; USER_TZ_NAME="Central European"; USER_TZ_OFFSET="+0100" ;;
        9)  USER_TZ="Europe/Helsinki"; USER_TZ_NAME="Eastern European"; USER_TZ_OFFSET="+0200" ;;
        10) USER_TZ="Asia/Kolkata"; USER_TZ_NAME="India Time"; USER_TZ_OFFSET="+0530" ;;
        11) USER_TZ="Asia/Tokyo"; USER_TZ_NAME="Japan Time"; USER_TZ_OFFSET="+0900" ;;
        12) USER_TZ="Australia/Sydney"; USER_TZ_NAME="Australia Eastern"; USER_TZ_OFFSET="+1000" ;;
        13) 
            echo -e "\n${YELLOW}Enter your UTC offset in ±HHMM format${NC}"
            echo -e "Examples: -0500 (EST), +0100 (CET), +0530 (IST)"
            read -p "UTC offset: " custom_offset
            
            # Validate format
            if [[ "$custom_offset" =~ ^[+-][0-1][0-9][0-5][0-9]$ ]]; then
                USER_TZ="Etc/GMT$(echo "$custom_offset" | sed 's/+/-/' | sed 's/-/+/' | sed 's/[0-9][0-9]$//')"
                USER_TZ_NAME="UTC$custom_offset"
                USER_TZ_OFFSET="$custom_offset"
            else
                echo -e "${RED}Invalid format. Using UTC.${NC}"
                USER_TZ="UTC"
                USER_TZ_NAME="UTC"
                USER_TZ_OFFSET="+0000"
            fi
            ;;
        14)
            USER_TZ="UTC"
            USER_TZ_NAME="UTC"
            USER_TZ_OFFSET="+0000"
            ;;
        *)
            echo -e "${RED}Invalid choice. Using UTC.${NC}"
            USER_TZ="UTC"
            USER_TZ_NAME="UTC" 
            USER_TZ_OFFSET="+0000"
            ;;
    esac
    
    # Check current time in the selected timezone
    local user_time=$(TZ="$USER_TZ" date +"%H:%M")
    echo -e "\n${GREEN}Timezone set to $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
    echo -e "${BLUE}Your current time: $user_time${NC}"
    
    # Save to configuration if possible
    if [ -d "config" ] || mkdir -p "config" 2>/dev/null; then
        echo "USER_TZ=$USER_TZ" > "config/timezone.conf"
        echo "USER_TZ_NAME=$USER_TZ_NAME" >> "config/timezone.conf"
        echo "USER_TZ_OFFSET=$USER_TZ_OFFSET" >> "config/timezone.conf"
        echo -e "${GREEN}Timezone preference saved${NC}"
    fi
}

# Function to load timezone configuration
load_timezone_config() {
    if [ -f "config/timezone.conf" ]; then
        source "config/timezone.conf"
        local user_time=$(TZ="$USER_TZ" date +"%H:%M")
        echo -e "${BLUE}Loaded timezone: $USER_TZ_NAME ($USER_TZ_OFFSET)${NC}"
        echo -e "${BLUE}Your current time: $user_time${NC}"
        return 0
    else
        # No saved timezone
        return 1
    fi
}

# Function to check cron status and debug issues
check_cron_status() {
    echo -e "\n${BLUE}Checking cron service status...${NC}"
    
    # Check if cron service is running
    if systemctl is-active --quiet cron 2>/dev/null || service cron status >/dev/null 2>&1 || pgrep -x crond >/dev/null; then
        echo -e "${GREEN}✓ Cron service is running${NC}"
    else
        echo -e "${RED}✗ Cron service appears to be inactive${NC}"
        echo -e "${YELLOW}Try running: sudo service cron start${NC}"
        return 1
    fi
    
    # Check if the user has cron permissions
    if command -v getfacl >/dev/null && getfacl /usr/bin/crontab 2>/dev/null | grep -q "$(whoami)"; then
        echo -e "${GREEN}✓ User has crontab permissions${NC}"
    elif groups | grep -qE 'crontab|sudo|root|admin'; then
        echo -e "${GREEN}✓ User is in a group with crontab permissions${NC}"
    else
        echo -e "${YELLOW}⚠ Cannot verify crontab permissions${NC}"
    fi
    
    # Verify crontab entries
    if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
        echo -e "${GREEN}✓ AI Future crontab entries exist${NC}"
        
        # Show the actual crontab entry for verification
        echo -e "${BLUE}Current crontab entry:${NC}"
        crontab -l | grep "AI_FUTURE" | sed 's/^/    /'
    else
        echo -e "${RED}✗ No AI Future entries in crontab${NC}"
        return 1
    fi
    
    # Check scheduler script permissions
    local scheduler_scripts=$(find scheduler -name "*.sh" 2>/dev/null)
    if [ -n "$scheduler_scripts" ]; then
        for script in $scheduler_scripts; do
            if [ -x "$script" ]; then
                echo -e "${GREEN}✓ Scheduler script is executable: $script${NC}"
            else
                echo -e "${RED}✗ Scheduler script is NOT executable: $script${NC}"
                echo -e "${YELLOW}  Fix with: chmod +x $script${NC}"
            fi
        done
    else
        echo -e "${RED}✗ No scheduler scripts found${NC}"
        return 1
    fi
    
    # Check for cron logs
    local cron_log=""
    for log_file in /var/log/syslog /var/log/cron /var/log/cron.log /var/log/messages; do
        if [ -f "$log_file" ] && grep -q "CRON" "$log_file" 2>/dev/null; then
            cron_log="$log_file"
            break
        fi
    done
    
    if [ -n "$cron_log" ]; then
        echo -e "${GREEN}✓ Found cron logs in $cron_log${NC}"
        echo -e "${YELLOW}  You can check cron activity with: sudo grep CRON $cron_log | tail${NC}"
    else
        echo -e "${YELLOW}⚠ Could not locate cron logs${NC}"
    fi
    
    # Add a test cron job to run in 2 minutes
    echo -e "\n${BLUE}Would you like to add a test cron job to run in 2 minutes?${NC}"
    echo -e "${YELLOW}This will help verify if cron is working correctly${NC}"
    read -p "Add test job? (y/n): " add_test
    
    if [[ "$add_test" =~ ^[Yy]$ ]]; then
        # Create a test script
        mkdir -p debug
        local test_script="debug/cron_test_$(date +%s).sh"
        
        cat > "$test_script" << 'EOF'
#!/bin/bash
echo "Cron test executed at $(date)" > "debug/cron_test_result.txt"
# Try to write to the logs directory if it exists
if [ -d "logs" ]; then
    echo "Cron test executed at $(date)" > "logs/cron_test_result.txt"
fi
# Try to create a flag file with more debug info
{
    echo "=== CRON TEST RESULTS ==="
    echo "Date: $(date)"
    echo "User: $(whoami)"
    echo "Working Directory: $(pwd)"
    echo "PATH: $PATH"
    echo "Environment Variables:"
    env | sort
    echo "========================="
} > "debug/cron_debug_$(date +%s).txt"
EOF
        
        chmod +x "$test_script"
        
        # Calculate a time 2 minutes from now
        local current_min=$(date +%M)
        local current_hour=$(date +%H)
        local test_min=$((current_min + 2))
        local test_hour=$current_hour
        
        if [ $test_min -ge 60 ]; then
            test_min=$((test_min - 60))
            test_hour=$((test_hour + 1))
            if [ $test_hour -ge 24 ]; then
                test_hour=0
            fi
        fi
        
        # Add to crontab
        local cron_cmd="$test_min $test_hour * * * $(pwd)/$test_script # AI_FUTURE_TEST"
        (crontab -l 2>/dev/null | grep -v "AI_FUTURE_TEST"; echo "$cron_cmd") | crontab -
        
        echo -e "${GREEN}Test job scheduled for $(date -d "$test_hour:$test_min" +"%H:%M")${NC}"
        echo -e "${YELLOW}Check debug/cron_test_result.txt in 2-3 minutes${NC}"
        echo -e "${YELLOW}If the file doesn't appear, cron is not running correctly${NC}"
    fi
    
    echo -e "\n${BLUE}Scheduler Troubleshooting Tips:${NC}"
    echo -e "1. ${YELLOW}Make sure all scheduler scripts are executable (chmod +x)${NC}"
    echo -e "2. ${YELLOW}Use absolute paths in crontab entries${NC}"
    echo -e "3. ${YELLOW}Check if cron service is running${NC}"
    echo -e "4. ${YELLOW}Look for errors in system logs${NC}"
    echo -e "5. ${YELLOW}Verify that the script can run manually${NC}"
    echo -e "6. ${YELLOW}Try running: sudo service cron restart${NC}"
}

# Add a crontab debugging function
diagnose_scheduler() {
    echo -e "\n${CYAN}Scheduler Diagnostics${NC}"
    echo -e "${BLUE}This will help diagnose issues with scheduled tasks${NC}"
    
    # Create a diagnostic output directory
    local diag_dir="diagnostics"
    mkdir -p "$diag_dir"
    local diag_file="$diag_dir/scheduler_diagnostics_$(date +%s).txt"
    
    # Start collecting diagnostic info
    {
        echo "=== AI FUTURE SCHEDULER DIAGNOSTICS ==="
        echo "Date: $(date)"
        echo "User: $(whoami)"
        echo "Working Directory: $(pwd)"
        echo ""
        
        echo "=== CRONTAB ENTRIES ==="
        if crontab -l 2>/dev/null; then
            crontab -l 2>/dev/null | grep -v "^#" | grep .
        else
            echo "No crontab entries or cannot access crontab"
        fi
        echo ""
        
        echo "=== SCHEDULER SCRIPTS ==="
        find . -path "*/scheduler/*.sh" -type f -ls 2>/dev/null || echo "No scheduler scripts found"
        echo ""
        
        echo "=== SCRIPT PERMISSIONS ==="
        for script in $(find . -path "*/scheduler/*.sh" -type f 2>/dev/null); do
            ls -la "$script"
            echo "File is executable: $([ -x "$script" ] && echo "Yes" || echo "No")"
            echo "File contents (first 10 lines):"
            head -10 "$script"
            echo "..."
        done
        echo ""
        
        echo "=== ENVIRONMENT ==="
        echo "PATH=$PATH"
        echo "SHELL=$SHELL"
        echo "HOME=$HOME"
        which uv || echo "uv command not found"
        echo ""
        
        echo "=== CRON SERVICE STATUS ==="
        systemctl status cron 2>/dev/null || service cron status 2>/dev/null || echo "Could not check cron service status"
        echo ""
        
        echo "=== RECENT LOGS ==="
        find logs -name "scheduler_*.log" -type f -mtime -1 2>/dev/null | sort -r | head -3 | while read -r log; do
            echo "=== $log ==="
            cat "$log" 2>/dev/null || echo "Could not read log file"
            echo ""
        done
        
        echo "=== SYSTEM CRON LOGS ==="
        for log in /var/log/syslog /var/log/cron /var/log/cron.log /var/log/messages; do
            if [ -f "$log" ] && grep -q "CRON" "$log" 2>/dev/null; then
                echo "=== Recent entries from $log ==="
                sudo grep CRON "$log" 2>/dev/null | tail -20 || echo "Could not access log (try running as root)"
                break
            fi
        done
        
        echo "=== END OF DIAGNOSTICS ==="
    } > "$diag_file"
    
    echo -e "${GREEN}Diagnostic information saved to: $diag_file${NC}"
    echo -e "${YELLOW}Please check this file for insights into scheduler issues${NC}"
    
    # Offer to run the most recent scheduler script manually
    local latest_script=$(find scheduler -name "*.sh" -type f -exec ls -t {} \; 2>/dev/null | head -1)
    if [ -n "$latest_script" ]; then
        echo -e "\n${BLUE}Would you like to run the latest scheduler script manually?${NC}"
        echo -e "${YELLOW}This will help determine if the script itself works correctly${NC}"
        read -p "Run script? (y/n): " run_script
        
        if [[ "$run_script" =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}Running: $latest_script${NC}"
            "$latest_script"
            echo -e "${YELLOW}Check the logs directory for results${NC}"
        fi
    fi
    
    # Run the cron status check
    check_cron_status
}

# Function to manage scheduling with improved reliability and timezone awareness
manage_scheduling() {
    # First check if we have saved timezone settings
    if ! load_timezone_config; then
        echo -e "${YELLOW}No timezone configuration found${NC}"
        select_timezone
    fi
    
    while true; do
    echo -e "\n${GREEN}Scheduling Management${NC}"
        
        # Display timezone information
        display_timezone_info
        echo -e "${BLUE}Scheduled posts will be published automatically at the specified times${NC}"
    echo -e "${YELLOW}1)${NC} Set up daily schedule"
        echo -e "${YELLOW}2)${NC} Set up weekly schedule (specific day)"
    echo -e "${YELLOW}3)${NC} View current schedule"
    echo -e "${YELLOW}4)${NC} Remove all schedules"
        echo -e "${YELLOW}5)${NC} Test scheduler now (for debugging)"
        echo -e "${YELLOW}6)${NC} Change your timezone"
        echo -e "${YELLOW}7)${NC} Diagnose scheduler issues"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " schedule_choice

    case $schedule_choice in
            1|2)
                # Common code for daily (1) or weekly (2) schedule
                if [ "$schedule_choice" -eq 1 ]; then
                    echo -e "\n${CYAN}Daily Post Schedule${NC}"
                    schedule_type="daily"
                else
                    echo -e "\n${CYAN}Weekly Post Schedule${NC}"
                    echo -e "${BLUE}Select day of week:${NC}"
                    echo -e "${YELLOW}0)${NC} Sunday"
                    echo -e "${YELLOW}1)${NC} Monday"
                    echo -e "${YELLOW}2)${NC} Tuesday"
                    echo -e "${YELLOW}3)${NC} Wednesday"
                    echo -e "${YELLOW}4)${NC} Thursday"
                    echo -e "${YELLOW}5)${NC} Friday"
                    echo -e "${YELLOW}6)${NC} Saturday"
                    read -p "Enter day (0-6): " weekday
                    
                    if ! [[ "$weekday" =~ ^[0-6]$ ]]; then
                        echo -e "${RED}Invalid day. Please enter a number between 0-6.${NC}"
                        continue
                    fi
                    schedule_type="weekly"
                    day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                fi
                
                # Time entry in user's local timezone
                echo -e "\n${BLUE}Enter time in YOUR timezone ($USER_TZ_NAME)${NC}"
                echo -e "${BLUE}Your current time: $(TZ="$USER_TZ" date +"%H:%M")${NC}"
                read -p "Enter hour (0-23): " local_hour
                read -p "Enter minute (0-59): " local_minute
                
                # Validate input
                if ! [[ "$local_hour" =~ ^[0-9]+$ ]] || [ "$local_hour" -lt 0 ] || [ "$local_hour" -gt 23 ]; then
                    echo -e "${RED}Invalid hour. Please enter a number between 0-23.${NC}"
                    continue
                fi
                
                if ! [[ "$local_minute" =~ ^[0-9]+$ ]] || [ "$local_minute" -lt 0 ] || [ "$local_minute" -gt 59 ]; then
                    echo -e "${RED}Invalid minute. Please enter a number between 0-59.${NC}"
                    continue
                fi
                
                # Convert to UTC
                IFS=' ' read -r hour minute <<< "$(convert_user_to_utc "$local_hour" "$local_minute")"
                echo -e "${GREEN}Converting your local time ${local_hour}:$(printf "%02d" $local_minute) to UTC ${hour}:$(printf "%02d" $minute)${NC}"
                
                # Get absolute paths
                script_path="$(readlink -f "$0")"
                script_dir="$(dirname "$script_path")"
                
                # Create crontab entry using the direct command approach
                if [ "$schedule_type" = "daily" ]; then
                    cron_comment="# AI_FUTURE_DAILY"
                    cron_cmd="$minute $hour * * * cd $script_dir && ./$(basename "$script_path") generate random random $cron_comment"
                else  # weekly
                    cron_comment="# AI_FUTURE_WEEKLY_${weekday}"
                    cron_cmd="$minute $hour * * $weekday cd $script_dir && ./$(basename "$script_path") generate random random $cron_comment"
                fi

                # Remove any existing entries with the same comment
                (crontab -l 2>/dev/null | grep -v "$cron_comment"; echo "$cron_cmd") | crontab -
                
                # Confirm settings
                if [ "$schedule_type" = "daily" ]; then
                    echo -e "${GREEN}Daily post scheduled for ${hour}:$(printf "%02d" $minute) UTC${NC}"
                    echo -e "${GREEN}(${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone)${NC}"
                else
                    echo -e "${GREEN}Weekly post scheduled for ${hour}:$(printf "%02d" $minute) UTC every ${day_names[$weekday]}${NC}"
                    echo -e "${GREEN}(${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone)${NC}"
                fi
                
                echo -e "${BLUE}Schedule details:${NC}"
                echo -e "  • Scheduler script: $script_path"
                echo -e "  • Log files will be created in: $script_dir/logs"
                echo -e "  • The script will automatically use reliable environment setup"
                echo -e "${YELLOW}You can test the scheduler immediately with option 5${NC}"
                ;;
                
            3)
                echo -e "\n${BLUE}Current Schedule:${NC}"
                if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
                    echo -e "${CYAN}Found the following scheduled tasks:${NC}"
                    crontab -l | grep "AI_FUTURE" | while read -r line; do
                        # Parse the crontab entry for better display
                        min=$(echo "$line" | awk '{print $1}')
                        hour=$(echo "$line" | awk '{print $2}')
                        dow=$(echo "$line" | awk '{print $5}')
                        
                        # Get local time equivalent
                        IFS=' ' read -r local_hour local_minute day_shift <<< "$(convert_utc_to_user "$hour" "$min")"
                        
                        # Format display based on schedule type
                        if [[ "$line" == *"AI_FUTURE_DAILY"* ]]; then
                            echo -e "${CYAN}• Daily at ${hour}:$(printf "%02d" $min) UTC${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        elif [[ "$line" == *"AI_FUTURE_WEEKLY"* ]]; then
                            day_num=$(echo "$line" | sed -n 's/.*AI_FUTURE_WEEKLY_\([0-6]\).*/\1/p')
                            if [ -z "$day_num" ]; then day_num="$dow"; fi
                            day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                            day_name="${day_names[$day_num]}"
                            echo -e "${CYAN}• Weekly on $day_name at ${hour}:$(printf "%02d" $min) UTC${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        else
                            echo -e "${CYAN}• Custom: $min $hour * * $dow${NC}"
                            echo -e "${CYAN}  (${local_hour}:$(printf "%02d" $local_minute) in your $USER_TZ_NAME timezone, ${day_shift})${NC}"
                        fi
                    done
                    
                    # Check logs directory for recent runs
                    if [ -d "logs" ]; then
                        recent_logs=$(find "logs" -name "scheduler_*" -type f -mtime -1 | sort -r | head -3)
                        if [ -n "$recent_logs" ]; then
                            echo -e "\n${BLUE}Recent scheduler logs:${NC}"
                            for log in $recent_logs; do
                                log_time=$(echo "$log" | sed -n 's/.*scheduler_\([0-9]\{8\}_[0-9]\{6\}\).log/\1/p')
                                log_time_fmt=$(date -d "${log_time:0:8} ${log_time:9:2}:${log_time:11:2}:${log_time:13:2}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                                
                                if [ -n "$log_time_fmt" ]; then
                                    echo -e "${YELLOW}• $log_time_fmt${NC}"
                                else
                                    echo -e "${YELLOW}• $log${NC}"
                                fi
                                
                                # Check if log contains errors
                                if grep -q "ERROR" "$log"; then
                                    echo -e "${RED}  Contains errors! Check $log${NC}"
                                else
                                    echo -e "${GREEN}  No errors detected${NC}"
                                fi
                            done
                        else
                            echo -e "\n${YELLOW}No recent scheduler logs found${NC}"
                        fi
                    fi
                else
                    echo -e "${YELLOW}No schedules found${NC}"
                fi
                ;;
                
            4)
                echo -e "\n${RED}WARNING: This will remove all scheduled AI Future tasks!${NC}"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                    crontab -l 2>/dev/null | grep -v "AI_FUTURE" | crontab -
                    echo -e "${GREEN}All AI Future schedules removed${NC}"
                else
                    echo -e "${YELLOW}Operation cancelled${NC}"
                fi
                ;;
                
            5)
                echo -e "\n${BLUE}Testing scheduler...${NC}"
                
                # Find the most recent scheduler script
                script_dir="scheduler"
                if [ ! -d "$script_dir" ]; then
                    echo -e "${RED}No scheduler scripts found. Please set up a schedule first.${NC}"
                    continue
                fi
                
                latest_script=$(find "$script_dir" -name "*.sh" -type f -exec ls -t {} \; | head -1)
                
                if [ -z "$latest_script" ]; then
                    echo -e "${RED}No scheduler scripts found. Please set up a schedule first.${NC}"
                    continue
                fi
                
                echo -e "${YELLOW}Running scheduler script: $latest_script${NC}"
                echo -e "${BLUE}This will generate and post content immediately${NC}"
                read -p "Continue? (y/n): " test_confirm
                
                if [[ "$test_confirm" =~ ^[Yy]$ ]]; then
                    echo -e "${GREEN}Executing scheduler - check logs folder for results${NC}"
                    "$latest_script" &
                    echo -e "${YELLOW}Scheduler is running in background.${NC}"
                    echo -e "${YELLOW}Check logs directory in a few moments for results.${NC}"
                else
                    echo -e "${YELLOW}Test cancelled${NC}"
                fi
                ;;
                
            6)
                select_timezone
                ;;
                
            7)
                # Run the scheduler diagnostics
                diagnose_scheduler
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
        
        # Pause after each action
        read -p "Press Enter to continue..."
    done
}

# Function to post a preview
post_preview() {
    local preview_file=$1
    
    if [ ! -f "$preview_file" ]; then
        echo -e "${RED}Preview file not found: $preview_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Preview content:${NC}"
    cat "$preview_file"
    
    echo -e "\n${YELLOW}Would you like to post this content to Twitter? [y/N]:${NC}"
    read -p "" post_choice
    
    if [[ $post_choice =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Posting preview content...${NC}"
        run_generator "" "" "" false "--post-preview" "$preview_file"
    else
        echo -e "${YELLOW}Posting cancelled${NC}"
    fi
}

# Function to view recent activity
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
            read -p "View a preview? (enter number or 'n'): " preview_num
            if [[ $preview_num =~ ^[0-9]+$ ]]; then
                preview_file=$(ls -t output/previews/ | sed -n "${preview_num}p")
                if [ -n "$preview_file" ]; then
                    preview_path="output/previews/$preview_file"
                    cat "$preview_path"
                    
                    # Check if already posted
                    if grep -q '"posted": true' "$preview_path"; then
                        echo -e "\n${YELLOW}This preview has already been posted${NC}"
                    else
                        echo -e "\n${BLUE}Would you like to post this preview? [y/N]:${NC}"
                        read -p "" post_choice
                        if [[ $post_choice =~ ^[Yy]$ ]]; then
                            post_preview "$preview_path"
                        fi
                    fi
                fi
            fi
            ;;
        4)
            echo -e "${BLUE}Recent logs:${NC}"
            ls -lt logs/ | head -n 5
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

# Updated check_system_status function to properly detect schedules
check_system_status() {
    echo -e "\n${BLUE}System Status${NC}"
    
    # Check if credentials exist
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓${NC} Credentials file found"
    else
        echo -e "${RED}✗${NC} Credentials file missing"
    fi

    # Check output directories
    for dir in "output/stories" "output/images" "output/previews"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓${NC} $dir exists"
            echo -e "   Files: $(ls -1 "$dir" | wc -l)"
        else
            echo -e "${RED}✗${NC} $dir missing"
        fi
    done

    # Check scheduled tasks using the AI_FUTURE marker
    if crontab -l 2>/dev/null | grep -q "AI_FUTURE"; then
        echo -e "${GREEN}✓${NC} Scheduled tasks found"
        echo -e "${BLUE}Current schedule:${NC}"
        crontab -l | grep "AI_FUTURE" | while read -r line; do
            # Parse the crontab entry for better display
            min=$(echo "$line" | awk '{print $1}')
            hour=$(echo "$line" | awk '{print $2}')
            
            # Format display based on schedule type
            if [[ "$line" == *"AI_FUTURE_DAILY"* ]]; then
                echo -e "  • Daily at ${hour}:$(printf "%02d" $min)"
            elif [[ "$line" == *"AI_FUTURE_WEEKLY"* ]]; then
                dow=$(echo "$line" | awk '{print $5}')
                day_names=("Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")
                day_name="${day_names[$dow]}"
                echo -e "  • Weekly on $day_name at ${hour}:$(printf "%02d" $min)"
            else
                echo -e "  • Custom schedule"
            fi
        done
    else
        echo -e "${YELLOW}!${NC} No scheduled tasks"
    fi

    # Show disk usage
    echo -e "\n${BLUE}Disk Usage:${NC}"
    du -sh output/* 2>/dev/null || echo "No output files yet"
}

# Function to show help
show_help() {
    echo -e "\n${BLUE}AI Solarpunk Story Bot - Help${NC}"
    echo -e "Available commands:"
    echo -e "  ${YELLOW}./ai_future.sh${NC} - Interactive mode"
    echo -e "  ${YELLOW}./ai_future.sh generate [setting] [style]${NC} - Generate and post content"
    echo -e "  ${YELLOW}./ai_future.sh preview [setting] [style]${NC} - Generate preview without posting"
    echo -e "  ${YELLOW}./ai_future.sh status${NC} - Check system status"
    echo
    echo -e "Settings: ${CYAN}${SETTINGS[*]}${NC}"
    echo -e "Styles: ${CYAN}${STYLES[*]}${NC}"
}

# Function to handle custom world document input
custom_world_generation() {
    clear
    echo -e "${GREEN}===== Custom World Document Story Generation =====${NC}"
    echo -e "${BLUE}Create stories from your own world-building documents!${NC}\n"
    
    echo -e "${CYAN}This feature allows you to:${NC}"
    echo -e "• Paste world-building text from your clipboard"
    echo -e "• Use any format (narrative, bullet points, JSON, etc.)"
    echo -e "• Generate stories set in your custom world"
    echo -e "• Build continuity within your custom setting\n"
    
    echo -e "${YELLOW}Options:${NC}"
    echo -e "${YELLOW}1)${NC} Paste world document from clipboard"
    echo -e "${YELLOW}2)${NC} Load world document from file"
    echo -e "${YELLOW}3)${NC} View example world documents"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"
    
    read -p "Enter your choice (1-3, b, q): " world_choice
    
    case $world_choice in
        1)
            paste_world_document
            ;;
        2)
            load_world_document_file
            ;;
        3)
            view_example_worlds
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            custom_world_generation
            ;;
    esac
}

# Function to paste world document from clipboard
paste_world_document() {
    clear
    echo -e "${GREEN}===== Paste World Document =====${NC}"
    echo -e "${BLUE}Paste your world-building document below.${NC}\n"
    
    echo -e "${CYAN}Instructions:${NC}"
    echo -e "• Paste or type your world-building content"
    echo -e "• Include details about technology, culture, conflicts, etc."
    echo -e "• Any format is fine (narrative, bullet points, etc.)"
    echo -e "• Type ${YELLOW}END_DOCUMENT${NC} on a new line when finished"
    echo -e "• Type ${YELLOW}CANCEL${NC} to abort\n"
    
    echo -e "${YELLOW}Start pasting/typing your world document:${NC}"
    
    # Create temporary file for world document
    local temp_world_file=$(mktemp)
    local line
    
    while IFS= read -r line; do
        if [[ "$line" == "END_DOCUMENT" ]]; then
            break
        elif [[ "$line" == "CANCEL" ]]; then
            echo -e "\n${YELLOW}Operation cancelled.${NC}"
            rm -f "$temp_world_file"
            read -p "Press Enter to continue..."
            custom_world_generation
            return
        else
            echo "$line" >> "$temp_world_file"
        fi
    done
    
    # Check if we got any content
    if [ ! -s "$temp_world_file" ]; then
        echo -e "\n${YELLOW}No content received. Operation cancelled.${NC}"
        rm -f "$temp_world_file"
        read -p "Press Enter to continue..."
        custom_world_generation
        return
    fi
    
    # Show preview of what was pasted
    local char_count=$(wc -c < "$temp_world_file")
    local line_count=$(wc -l < "$temp_world_file")
    
    echo -e "\n${GREEN}Document received!${NC}"
    echo -e "${BLUE}Stats: $line_count lines, $char_count characters${NC}\n"
    
    echo -e "${CYAN}Preview (first 10 lines):${NC}"
    head -n 10 "$temp_world_file" | sed 's/^/  /'
    if [ "$line_count" -gt 10 ]; then
        echo -e "  ${BLUE}... (and $((line_count-10)) more lines)${NC}"
    fi
    
    echo -e "\n${YELLOW}Options:${NC}"
    echo -e "${YELLOW}1)${NC} Generate story from this world"
    echo -e "${YELLOW}2)${NC} Save document and generate story"
    echo -e "${YELLOW}3)${NC} Edit document"
    echo -e "${YELLOW}4)${NC} Cancel"
    
    read -p "Enter your choice (1-4): " doc_choice
    
    case $doc_choice in
        1)
            generate_story_from_world_doc "$temp_world_file" false
            ;;
        2)
            # Save to a permanent location
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local saved_file="examples/worlds/custom_world_${timestamp}.txt"
            cp "$temp_world_file" "$saved_file"
            echo -e "\n${GREEN}World document saved to: $saved_file${NC}"
            generate_story_from_world_doc "$temp_world_file" true
            ;;
        3)
            echo -e "\n${BLUE}Re-edit your document:${NC}"
            echo -e "${CYAN}Current content will be shown. Add/modify as needed.${NC}"
            echo -e "${CYAN}Type ${YELLOW}END_DOCUMENT${NC} when finished.${NC}\n"
            
            # Show current content for editing
            cat "$temp_world_file"
            
            # Clear the file and start fresh
            > "$temp_world_file"
            
            # Read new content
            while IFS= read -r line; do
                if [[ "$line" == "END_DOCUMENT" ]]; then
                    break
                else
                    echo "$line" >> "$temp_world_file"
                fi
            done
            
            paste_world_document  # Recursively call to show options again
            ;;
        4)
            echo -e "\n${YELLOW}Operation cancelled.${NC}"
            rm -f "$temp_world_file"
            read -p "Press Enter to continue..."
            custom_world_generation
            ;;
        *)
            echo -e "\n${RED}Invalid choice.${NC}"
            sleep 2
            paste_world_document
            ;;
    esac
}

# Function to load world document from file
load_world_document_file() {
    clear
    echo -e "${GREEN}===== Load World Document from File =====${NC}"
    echo -e "${BLUE}Specify a file path to load your world document.${NC}\n"
    
    echo -e "${CYAN}Supported formats:${NC}"
    echo -e "• Plain text (.txt)"
    echo -e "• Markdown (.md)"
    echo -e "• JSON (.json)"
    echo -e "• YAML (.yaml, .yml)\n"
    
    echo -e "${YELLOW}Available example files:${NC}"
    if [ -d "examples/worlds" ]; then
        ls -la examples/worlds/ | grep -E '\.(txt|md|json|yaml|yml)$' | awk '{print "  " $9}' | head -10
        echo ""
    fi
    
    read -p "Enter file path (or 'b' to go back): " file_path
    
    if [[ "$file_path" == "b" || "$file_path" == "B" ]]; then
        custom_world_generation
        return
    fi
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "\n${RED}Error: File not found: $file_path${NC}"
        read -p "Press Enter to try again..."
        load_world_document_file
        return
    fi
    
    # Show file info
    local file_size=$(stat -c%s "$file_path" 2>/dev/null || echo "unknown")
    local line_count=$(wc -l < "$file_path")
    
    echo -e "\n${GREEN}File found!${NC}"
    echo -e "${BLUE}File: $file_path${NC}"
    echo -e "${BLUE}Size: $file_size bytes, $line_count lines${NC}\n"
    
    echo -e "${CYAN}Preview (first 10 lines):${NC}"
    head -n 10 "$file_path" | sed 's/^/  /'
    if [ "$line_count" -gt 10 ]; then
        echo -e "  ${BLUE}... (and $((line_count-10)) more lines)${NC}"
    fi
    
    echo -e "\n${YELLOW}Generate story from this world document? (y/n):${NC}"
    read -p "" use_file
    
    if [[ "$use_file" =~ ^[Yy]$ ]]; then
        generate_story_from_world_doc "$file_path" true
    else
        echo -e "${YELLOW}Operation cancelled.${NC}"
        read -p "Press Enter to continue..."
        custom_world_generation
    fi
}

# Function to generate story from world document
generate_story_from_world_doc() {
    local world_file="$1"
    local is_permanent="${2:-false}"
    
    clear
    echo -e "${GREEN}===== Generate Story from Custom World =====${NC}"
    echo -e "${BLUE}Using world document: $(basename "$world_file")${NC}\n"
    
    echo -e "${CYAN}Story Generation Options:${NC}"
    echo -e "${YELLOW}1)${NC} Preview only (no posting)"
    echo -e "${YELLOW}2)${NC} Generate and post to Twitter"
    echo -e "${YELLOW}3)${NC} Generate with specific era (0 or 1)"
    echo -e "${YELLOW}b)${NC} Back to world document menu"
    
    read -p "Enter your choice (1-3, b): " gen_choice
    
    case $gen_choice in
        1|2)
            local features="story,image"
            local preview_mode=true
            
            if [ "$gen_choice" == "2" ]; then
                features="story,image,post"
                preview_mode=false
                
                echo -e "\n${YELLOW}⚠ WARNING: This will post to Twitter!${NC}"
                read -p "Are you sure? (y/N): " confirm_post
                if [[ ! "$confirm_post" =~ ^[Yy]$ ]]; then
                    echo -e "${YELLOW}Switching to preview mode instead.${NC}"
                    features="story,image"
                    preview_mode=true
                fi
            fi
            
            echo -e "\n${BLUE}Generating story from your custom world...${NC}"
            echo -e "${CYAN}This may take a moment while the AI analyzes your world document.${NC}"
            
            # Run the generator with the custom world document
            local cmd="uv run src/ai_story_tweet_generator.py --world-doc \"$world_file\" --features $features --era-id 0"
            if [ "$preview_mode" == true ]; then
                cmd="$cmd --preview"
            fi
            
            echo -e "${BLUE}Running command: $cmd${NC}"
            eval $cmd
            
            local exit_code=$?
            if [ $exit_code -eq 0 ]; then
                echo -e "\n${GREEN}✓ Story generation completed successfully!${NC}"
            else
                echo -e "\n${RED}✗ Story generation failed.${NC}"
                echo -e "${YELLOW}This might be due to:${NC}"
                echo -e "• Invalid world document format"
                echo -e "• Missing API keys"
                echo -e "• Network connectivity issues"
                echo -e "• AI service availability"
            fi
            ;;
        3)
            echo -e "\n${BLUE}Select era for the story:${NC}"
            show_eras
            
            read -p "Enter era ID (0-1): " era_choice
            
            if [[ "$era_choice" =~ ^[0-1]$ ]]; then
                echo -e "\n${BLUE}Generating story in era $era_choice from your custom world...${NC}"
                
                local cmd="uv run src/ai_story_tweet_generator.py --world-doc \"$world_file\" --era-id $era_choice --features story,image --preview"
                echo -e "${BLUE}Running command: $cmd${NC}"
                eval $cmd
                
                local exit_code=$?
                if [ $exit_code -eq 0 ]; then
                    echo -e "\n${GREEN}✓ Story generation completed successfully!${NC}"
                else
                    echo -e "\n${RED}✗ Story generation failed.${NC}"
                fi
            else
                echo -e "${RED}Invalid era selection.${NC}"
            fi
            ;;
        b|B)
            custom_world_generation
            return
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            sleep 2
            generate_story_from_world_doc "$world_file" "$is_permanent"
            return
            ;;
    esac
    
    # Cleanup temporary file if it was temporary
    if [ "$is_permanent" == false ]; then
        rm -f "$world_file"
    fi
    
    echo -e "\n${BLUE}Would you like to generate another story? (y/N):${NC}"
    read -p "" another
    
    if [[ "$another" =~ ^[Yy]$ ]]; then
        custom_world_generation
    else
        read -p "Press Enter to return to main menu..."
    fi
}

# Function to view example world documents
view_example_worlds() {
    clear
    echo -e "${GREEN}===== Example World Documents =====${NC}"
    echo -e "${BLUE}Here are some example world documents you can use as templates:${NC}\n"
    
    if [ -d "examples/worlds" ]; then
        echo -e "${CYAN}Available examples:${NC}"
        local i=1
        local files=()
        
        for file in examples/worlds/*; do
            if [ -f "$file" ]; then
                files+=("$file")
                echo -e "${YELLOW}$i)${NC} $(basename "$file")"
                ((i++))
            fi
        done
        
        if [ ${#files[@]} -eq 0 ]; then
            echo -e "${YELLOW}No example files found.${NC}"
        else
            echo -e "\n${YELLOW}v)${NC} View an example file"
            echo -e "${YELLOW}c)${NC} Copy example to clipboard (requires xclip)"
            echo -e "${YELLOW}b)${NC} Back to world document menu"
            
            read -p "Enter your choice: " example_choice
            
            case $example_choice in
                v|V)
                    read -p "Enter example number to view (1-${#files[@]}): " file_num
                    if [[ "$file_num" =~ ^[0-9]+$ ]] && [ "$file_num" -ge 1 ] && [ "$file_num" -le ${#files[@]} ]; then
                        local selected_file="${files[$((file_num-1))]}"
                        clear
                        echo -e "${GREEN}===== $(basename "$selected_file") =====${NC}\n"
                        cat "$selected_file"
                        echo -e "\n${BLUE}Press Enter to continue...${NC}"
                        read
                        view_example_worlds
                    else
                        echo -e "${RED}Invalid file number.${NC}"
                        sleep 2
                        view_example_worlds
                    fi
                    ;;
                c|C)
                    # Check if xclip is available
                    if command -v xclip >/dev/null 2>&1; then
                        read -p "Enter example number to copy (1-${#files[@]}): " file_num
                        if [[ "$file_num" =~ ^[0-9]+$ ]] && [ "$file_num" -ge 1 ] && [ "$file_num" -le ${#files[@]} ]; then
                            local selected_file="${files[$((file_num-1))]}"
                            cat "$selected_file" | xclip -selection clipboard
                            echo -e "${GREEN}✓ $(basename "$selected_file") copied to clipboard!${NC}"
                            echo -e "${BLUE}You can now paste it when using the 'Paste world document' option.${NC}"
                            read -p "Press Enter to continue..."
                            view_example_worlds
                        else
                            echo -e "${RED}Invalid file number.${NC}"
                            sleep 2
                            view_example_worlds
                        fi
                    else
                        echo -e "${RED}xclip not found. Install it with: sudo apt install xclip${NC}"
                        read -p "Press Enter to continue..."
                        view_example_worlds
                    fi
                    ;;
                b|B)
                    custom_world_generation
                    ;;
                *)
                    echo -e "${RED}Invalid choice.${NC}"
                    sleep 2
                    view_example_worlds
                    ;;
            esac
        fi
    else
        echo -e "${YELLOW}Examples directory not found.${NC}"
        echo -e "${BLUE}Creating examples directory and sample files...${NC}"
        
        mkdir -p examples/worlds
        
        # Create a simple example
        cat > examples/worlds/simple_example.txt << 'EOF'
# Neo-Tokyo 2087

A cyberpunk city where nature has been reintroduced through advanced biotechnology.

## Technology
- Bioluminescent trees that provide street lighting
- Air-purifying moss walls on buildings
- Neural-linked urban gardens
- Symbiotic human-plant interfaces

## Society
- Tech-druid collectives manage city ecosystems
- Corporate bio-hackers compete with open-source mycologists
- Underground seed libraries preserve genetic diversity

## Conflicts
- Patent wars over living architecture
- Resistance against commodified nature
- Generation gap between cyborgs and bio-enhanced humans

## Environment
The city glows with living light, where skyscrapers are overgrown with engineered vines and the streets are soft with bio-concrete that photosynthesizes.
EOF
        
        echo -e "${GREEN}✓ Created simple_example.txt${NC}"
        echo -e "${BLUE}You can now view and use this example.${NC}"
        read -p "Press Enter to continue..."
        view_example_worlds
    fi
}

# Main menu function
show_menu() {
    echo -e "\n${GREEN}Select an action:${NC}"
    echo -e "${CYAN}== World-Building Stories ==${NC}"
    echo -e "${YELLOW}1)${NC} Generate new story (new character)"
    echo -e "${YELLOW}2)${NC} Generate story with existing character"
    echo -e "${YELLOW}3)${NC} Custom world document stories"
    echo -e "${YELLOW}4)${NC} View continuity information"
    echo -e "${CYAN}== Classic Mode ==${NC}"
    echo -e "${YELLOW}5)${NC} Generate content (original mode)"
    echo -e "${YELLOW}6)${NC} Preview generation"
    echo -e "${CYAN}== Management ==${NC}"
    echo -e "${YELLOW}7)${NC} Manage scheduling"
    echo -e "${YELLOW}8)${NC} View recent activity"
    echo -e "${YELLOW}9)${NC} Check system status"
    echo -e "${YELLOW}a)${NC} Check error handler health"
    echo -e "${YELLOW}b)${NC} Cleanup and archive outputs"
    echo -e "${YELLOW}0)${NC} Clear preview files only"
    echo -e "${YELLOW}h)${NC} Show help"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " choice

    case $choice in
        1)
            era_selection
            ;;
        2)
            character_selection
            ;;
        3)
            custom_world_generation
            ;;
        4)
            view_continuity
            ;;
        5)
            generate_and_post
            ;;
        6)
            preview_generation
            ;;
        7)
            manage_scheduling
            ;;
        8)
            view_recent_activity
            ;;
        9)
            check_system_status
            ;;
        a|A)
            check_error_handler_health
            ;;
        b|B)
            cleanup_outputs
            ;;
        0)
            clear_preview_files
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

# Function to clear only preview files
clear_preview_files() {
    echo -e "\n${BLUE}Clearing Preview Files${NC}"
    
    # Check if the preview directory exists
    local preview_dir="output/preview_files"
    if [ ! -d "$preview_dir" ]; then
        mkdir -p "$preview_dir"
        echo -e "${YELLOW}Preview directory created.${NC}"
        return
    fi
    
    # Count files before clearing
    local file_count=$(find "$preview_dir" -type f | wc -l)
    
    if [ $file_count -eq 0 ]; then
        echo -e "${YELLOW}No preview files to clear.${NC}"
        return
    fi
    
    echo -e "${YELLOW}Found $file_count preview files. What would you like to do?${NC}"
    echo -e "${CYAN}1)${NC} Delete all preview files"
    echo -e "${CYAN}2)${NC} Archive preview files before deleting"
    echo -e "${CYAN}b)${NC} Cancel operation"
    
    read -p "Enter your choice: " clear_choice
    
    case $clear_choice in
        1)
            # Delete files directly
            rm -f "$preview_dir"/*
            echo -e "${GREEN}✓${NC} Deleted $file_count preview files"
            ;;
        2)
            # Archive before deleting
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local archive_dir="archive/preview_files_${timestamp}"
            mkdir -p "$archive_dir"
            
            # Move files to archive
            mv "$preview_dir"/* "$archive_dir/" 2>/dev/null
            
            echo -e "${GREEN}✓${NC} Archived $file_count preview files to $archive_dir"
            ;;
        b|B)
            echo -e "${YELLOW}Operation cancelled.${NC}"
            return
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            return
            ;;
    esac
}

# Updated function to clean up and archive output folders
cleanup_outputs() {
    echo -e "\n${GREEN}Output Folder Cleanup and Archiving${NC}"
    
    # Create archive directory with timestamp
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local archive_dir="archive/${timestamp}"
    mkdir -p "$archive_dir/stories" "$archive_dir/images" "$archive_dir/previews" "$archive_dir/preview_files"
    
    echo -e "${BLUE}Select cleanup option:${NC}"
    echo -e "${YELLOW}1)${NC} Archive everything"
    echo -e "${YELLOW}2)${NC} Keep files from last 7 days, archive the rest"
    echo -e "${YELLOW}3)${NC} Keep files from last 30 days, archive the rest"
    echo -e "${YELLOW}4)${NC} Custom (select what to archive)"
    echo -e "${YELLOW}5)${NC} Clear preview files only"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    
    read -p "Enter your choice: " cleanup_choice
    
    case $cleanup_choice in
        1)
            # Archive everything
            echo -e "${BLUE}Archiving all output files...${NC}"
            
            # Count files before moving
            local stories_count=$(find output/stories -type f | wc -l)
            local images_count=$(find output/images -type f | wc -l)
            local previews_count=$(find output/previews -type f | wc -l)
            local preview_files_count=$(find output/preview_files -type f 2>/dev/null | wc -l)
            
            # Move all files to archive
            mv output/stories/* "$archive_dir/stories/" 2>/dev/null
            mv output/images/* "$archive_dir/images/" 2>/dev/null
            mv output/previews/* "$archive_dir/previews/" 2>/dev/null
            mv output/preview_files/* "$archive_dir/preview_files/" 2>/dev/null
            
            echo -e "${GREEN}✓${NC} Archived $stories_count stories, $images_count images, $previews_count previews, and $preview_files_count preview files"
            echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            ;;
            
        2|3)
            # Keep recent files, archive older ones
            local days=7
            [[ $cleanup_choice -eq 3 ]] && days=30
            
            echo -e "${BLUE}Keeping files from last $days days, archiving older files...${NC}"
            
            # Find files older than specified days
            find output/stories -type f -mtime +$days -exec mv {} "$archive_dir/stories/" \;
            find output/images -type f -mtime +$days -exec mv {} "$archive_dir/images/" \;
            find output/previews -type f -mtime +$days -exec mv {} "$archive_dir/previews/" \;
            find output/preview_files -type f -mtime +$days -exec mv {} "$archive_dir/preview_files/" \; 2>/dev/null
            
            # Count files in archive
            local archive_count=$(find "$archive_dir" -type f | wc -l)
            
            if [ $archive_count -eq 0 ]; then
                echo -e "${YELLOW}No files older than $days days were found.${NC}"
                rmdir -p "$archive_dir/stories" "$archive_dir/images" "$archive_dir/previews" "$archive_dir/preview_files" 2>/dev/null
            else
                echo -e "${GREEN}✓${NC} Archived $archive_count files older than $days days"
                echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            fi
            ;;
            
        4)
            # Custom archiving
            echo -e "\n${BLUE}Custom Archiving${NC}"
            echo -e "${YELLOW}a)${NC} Archive stories"
            echo -e "${YELLOW}b)${NC} Archive images"
            echo -e "${YELLOW}c)${NC} Archive previews"
            echo -e "${YELLOW}d)${NC} Archive preview_files"
            echo -e "${YELLOW}q)${NC} Cancel archiving"
            
            read -p "Select folders to archive (e.g., abc for stories, images, and previews): " archive_selection
            
            if [[ $archive_selection =~ [aA] ]]; then
                mv output/stories/* "$archive_dir/stories/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived stories"
            fi
            
            if [[ $archive_selection =~ [bB] ]]; then
                mv output/images/* "$archive_dir/images/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived images"
            fi
            
            if [[ $archive_selection =~ [cC] ]]; then
                mv output/previews/* "$archive_dir/previews/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived previews"
            fi
            
            if [[ $archive_selection =~ [dD] ]]; then
                mv output/preview_files/* "$archive_dir/preview_files/" 2>/dev/null
                echo -e "${GREEN}✓${NC} Archived preview_files"
            fi
            
            # Check if any files were archived
            local archive_count=$(find "$archive_dir" -type f | wc -l)
            
            if [ $archive_count -eq 0 ]; then
                echo -e "${YELLOW}No files were archived.${NC}"
                rmdir -p "$archive_dir" 2>/dev/null
            else
                echo -e "${GREEN}✓${NC} Archive location: $archive_dir"
            fi
            ;;
            
        5)
            # Just clear preview files
            clear_preview_files
            ;;
            
        b|B)
            return
            ;;
            
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    
    # Ensure output directories exist after cleanup
    mkdir -p output/stories output/images output/previews output/preview_files
}

# Function to check error handler and application health
check_error_handler_health() {
    echo -e "\n${GREEN}===== Error Handler Health Check =====${NC}"
    
    echo -e "${BLUE}Checking application health and error handling status...${NC}\n"
    
    # Run the health check command
    local health_output
    health_output=$(uv run python3 -c "
import sys
import json
try:
    from src.application_error_handler import get_app_health_report
    from src.error_handler import get_application_health
    
    # Get comprehensive health report
    app_health = get_app_health_report()
    system_health = get_application_health()
    
    print('=== Application Health Report ===')
    print(f'Debug Mode: {app_health.get(\"debug_mode\", \"Unknown\")}')
    print(f'Process ID: {app_health.get(\"process_id\", \"Unknown\")}')
    print(f'Working Directory: {app_health.get(\"working_directory\", \"Unknown\")}')
    
    print('\n=== System Health ===')
    system_status = system_health.get('system_health', {})
    print(f'Status: {system_status.get(\"status\", \"Unknown\")}')
    print(f'Uptime Hours: {system_status.get(\"uptime_hours\", 0):.2f}')
    print(f'Errors (Last Hour): {system_status.get(\"errors_last_hour\", 0)}')
    print(f'Total Error Types: {system_status.get(\"total_error_types\", 0)}')
    
    print('\n=== Performance Metrics ===')
    perf_metrics = system_status.get('performance_metrics', {})
    if perf_metrics:
        for operation, avg_time in perf_metrics.items():
            print(f'{operation}: {avg_time:.2f}s average')
    else:
        print('No performance metrics available yet')
    
    print('\n=== Error Statistics ===')
    error_stats = system_health.get('error_statistics', {})
    if error_stats:
        print(f'Total Error Count: {error_stats.get(\"total_errors\", 0)}')
        print(f'Unique Error Types: {error_stats.get(\"unique_error_types\", 0)}')
        error_counts = error_stats.get('error_counts_by_type', {})
        if error_counts:
            print('Error Breakdown:')
            for error_type, count in error_counts.items():
                print(f'  {error_type}: {count}')
    else:
        print('No error statistics available yet')
    
    print('\n=== Health Check Complete ===')
    
except ImportError as e:
    print(f'Error: Could not import health monitoring modules: {e}')
    print('The error handler system may not be properly installed.')
    sys.exit(1)
except Exception as e:
    print(f'Error during health check: {e}')
    sys.exit(1)
" 2>&1)
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "$health_output"
        echo -e "\n${GREEN}✓ Health check completed successfully${NC}"
    else
        echo -e "${RED}✗ Health check failed:${NC}"
        echo "$health_output"
        echo -e "\n${YELLOW}This may indicate issues with the error handling system.${NC}"
    fi
    
    # Also check for critical files
    echo -e "\n${BLUE}Checking critical files...${NC}"
    
    local files_ok=true
    
    # Check continuity file
    if [ -f "output/continuity.json" ]; then
        echo -e "${GREEN}✓${NC} Continuity file exists"
        
        # Validate JSON
        if uv run python3 -c "import json; json.load(open('output/continuity.json'))" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Continuity file is valid JSON"
        else
            echo -e "${RED}✗${NC} Continuity file has invalid JSON"
            files_ok=false
        fi
    else
        echo -e "${YELLOW}⚠${NC} Continuity file does not exist (will be created on first story generation)"
    fi
    
    # Check essential directories
    for dir in "output" "output/images" "output/stories" "output/previews" "logs"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓${NC} Directory $dir exists"
        else
            echo -e "${YELLOW}⚠${NC} Directory $dir does not exist (will be created as needed)"
        fi
    done
    
    # Check log files
    local log_count=$(find logs -name "*.log" 2>/dev/null | wc -l)
    if [ "$log_count" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $log_count log files"
    else
        echo -e "${YELLOW}⚠${NC} No log files found"
    fi
    
    if [ "$files_ok" = true ]; then
        echo -e "\n${GREEN}✓ All critical files and directories are healthy${NC}"
    else
        echo -e "\n${RED}✗ Some issues found with critical files${NC}"
        echo -e "${BLUE}Consider running a story generation to reinitialize missing files${NC}"
    fi
    
    read -p "Press Enter to continue..."
}

# Main function
main() {
    show_header

    # If command-line arguments were provided
    if [ $# -gt 0 ]; then
        case "$1" in
            "generate")
                setting=${2:-"random"}
                style=${3:-"random"}
                run_generator "$setting" "$style" "story,image,post" false
                ;;
            "preview")
                setting=${2:-"random"}
                style=${3:-"random"}
                run_generator "$setting" "$style" "story,image" true
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

# Run the script
main "$@" 