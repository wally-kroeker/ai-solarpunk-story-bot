"""
Story-to-Image Prompt Conversion Module

This module provides functionality to convert generated stories into detailed,
thematically consistent image prompts for companion image generation.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VisualElements:
    """Extracted visual elements from a story."""
    characters: List[str]
    setting: str
    objects: List[str]
    actions: List[str]
    mood: str
    time_of_day: Optional[str] = None
    colors: List[str] = None

# Genre-specific visual enhancement templates
GENRE_AESTHETICS = {
    "solarpunk": {
        "style_keywords": ["Studio Ghibli style", "organic architecture", "eco-futurism"],
        "lighting": ["warm sunlight", "golden hour", "bioluminescent glow"],
        "atmosphere": ["hopeful", "peaceful", "harmonious"],
    },
    "fantasy": {
        "style_keywords": ["fantasy art", "magical realism", "ethereal"],
        "lighting": ["ethereal glow", "magical light", "moonlight"],
        "atmosphere": ["mystical", "magical", "otherworldly"],
    },
    "sci-fi": {
        "style_keywords": ["cyberpunk", "concept art", "futuristic"],
        "lighting": ["neon lighting", "artificial light", "holographic"],
        "atmosphere": ["futuristic", "technological", "sleek"],
    },
    "steampunk": {
        "style_keywords": ["steampunk art", "Victorian industrial", "mechanical"],
        "lighting": ["gas lamp", "steam", "warm brass lighting"],
        "atmosphere": ["industrial", "mechanical", "innovative"],
    }
}

class StoryToImageConverter:
    """Converts stories into detailed image prompts with genre-specific enhancements."""
    
    def __init__(self):
        """Initialize the converter."""
        self.genre_aesthetics = GENRE_AESTHETICS
    
    def convert_to_image_prompt(
        self, 
        story_text: str, 
        genre: str = "solarpunk",
        world_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Convert a story into a detailed image prompt."""
        # Extract visual elements
        elements = self._analyze_story_elements(story_text)
        
        # Get genre aesthetics
        aesthetics = self.genre_aesthetics.get(genre.lower(), self.genre_aesthetics["solarpunk"])
        
        # Build prompt components
        prompt_parts = []
        
        # Main subject and action
        if elements.characters and elements.actions:
            main_char = elements.characters[0]
            main_action = elements.actions[0]
            prompt_parts.append(f"{main_char} {main_action}")
        elif elements.characters:
            prompt_parts.append(f"{elements.characters[0]}")
        else:
            prompt_parts.append("figure")
        
        # Setting with time
        setting_desc = elements.setting
        if elements.time_of_day:
            setting_desc = f"{setting_desc} during {elements.time_of_day}"
        prompt_parts.append(f"in a {setting_desc}")
        
        # Objects and technology
        if elements.objects:
            objects_text = ", ".join(elements.objects[:3])
            prompt_parts.append(f"surrounded by {objects_text}")
        
        # Colors and atmosphere
        color_mood_parts = []
        if elements.colors:
            color_mood_parts.append(f"{', '.join(elements.colors[:3])} color palette")
        
        # Mood and lighting
        lighting = aesthetics["lighting"][0]
        mood_text = f"{elements.mood} atmosphere with {lighting}"
        color_mood_parts.append(mood_text)
        
        if color_mood_parts:
            prompt_parts.append(", ".join(color_mood_parts))
        
        # Artistic style
        style = aesthetics["style_keywords"][0]
        prompt_parts.append(f"rendered in {style}")
        
        # Technical quality
        prompt_parts.append("high quality, detailed, professional artwork")
        
        # Join with proper punctuation
        final_prompt = ". ".join(prompt_parts) + "."
        
        # Clean up any double periods or awkward spacing
        final_prompt = re.sub(r'\.\.+', '.', final_prompt)
        final_prompt = re.sub(r'\s+', ' ', final_prompt)
        
        return final_prompt
    
    def _analyze_story_elements(self, story_text: str) -> VisualElements:
        """Extract visual elements from story text."""
        
        # Extract character names (capitalized words that aren't at sentence start)
        sentences = story_text.split('.')
        character_pattern = r'\b[A-Z][a-z]{2,}\b'  # At least 3 letters
        potential_names = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            for i, word in enumerate(words):
                # Skip first word of sentence and common words
                if i > 0 and re.match(character_pattern, word):
                    potential_names.append(word)
        
        # Filter out common non-names and location words
        common_words = {
            'The', 'A', 'An', 'This', 'That', 'Place', 'Night', 'Day', 
            'Minneapolis', 'Chen', 'Resting', 'Each', 'FocusGem', 'KAIROS'
        }
        characters = [name for name in potential_names if name not in common_words][:2]
        
        # Look for character descriptions if no names found
        if not characters:
            desc_patterns = [
                r'apprentice\s+tinker\s+(\w+)',
                r'(\w+)\'s?\s+mentor',
                r'apprentice\s+(\w+)',
                r'tinker\s+(\w+)',
            ]
            
            for pattern in desc_patterns:
                matches = re.findall(pattern, story_text, re.IGNORECASE)
                characters.extend([match for match in matches if match not in common_words])
            
            if not characters:
                # Look for character roles
                if 'apprentice' in story_text.lower():
                    characters = ['apprentice tinker']
                elif 'mentor' in story_text.lower():
                    characters = ['mentor']
                else:
                    characters = ['figure']
        
        # Extract setting
        setting = "urban environment"  # default
        if 'rooftop' in story_text.lower():
            setting = "rooftop garden"
        elif 'market' in story_text.lower():
            setting = "marketplace"
        elif 'sanctuary' in story_text.lower():
            setting = "sanctuary"
        
        # Extract objects with better patterns
        object_patterns = [
            r'(SP-\w+\s+\w+)',  # StillPoint devices with model
            r'(\w+-wind\s+turbines?)',
            r'(micro-wind\s+turbines?)',
            r'(wind\s+turbines?)',
            r'(\w+\s+drones?)',
            r'(\w+\s+devices?)',
            r'(bioluminescent\s+\w+)',
            r'(solar\s+collectors?)',
            r'(vertical\s+farms?)',
        ]
        
        objects = []
        for pattern in object_patterns:
            matches = re.findall(pattern, story_text, re.IGNORECASE)
            objects.extend(matches)
        
        # Remove duplicates and generic matches
        filtered_objects = []
        for obj in objects:
            if obj.lower() not in ['each device', 'other device'] and len(obj) > 3:
                filtered_objects.append(obj)
        objects = list(set(filtered_objects))[:3]
        
        # Extract actions with better patterns
        action_patterns = [
            r'(\w+\s+adjusted)',
            r'(\w+\s+calibrating)',
            r'(\w+\s+worked)',
            r'(\w+\s+tended)',
            r'(standing\s+among)',
            r'(working\s+among)',
            r'(adjusting\s+\w+)',
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, story_text, re.IGNORECASE)
            actions.extend(matches)
        
        # Clean up actions
        cleaned_actions = []
        for action in actions:
            # Remove pronouns and character names, improve readability
            action = re.sub(r'^(she|he|they)\s+', '', action.lower())
            # Remove character names from actions to avoid duplication
            for char in characters:
                action = re.sub(rf'\b{char.lower()}\s+', '', action, flags=re.IGNORECASE)
            if action.strip() and action.strip() not in cleaned_actions:
                cleaned_actions.append(action.strip())
        
        actions = cleaned_actions[:2]
        
        # Extract mood
        mood = "atmospheric"
        if any(word in story_text.lower() for word in ['smiled', 'bright', 'hopeful', 'beautiful']):
            mood = "optimistic"
        elif any(word in story_text.lower() for word in ['calm', 'gentle', 'peaceful', 'meditative']):
            mood = "peaceful"
        elif any(word in story_text.lower() for word in ['sprinted', 'urgent', 'rushed']):
            mood = "dynamic"
        
        # Extract time of day
        time_of_day = None
        if 'morning' in story_text.lower() or 'sunlight' in story_text.lower():
            time_of_day = "morning"
        elif 'evening' in story_text.lower() or 'sunset' in story_text.lower():
            time_of_day = "evening"
        elif 'night' in story_text.lower() or 'darkness' in story_text.lower():
            time_of_day = "night"
        
        # Extract colors
        color_pattern = r'\b(amber|violet|silver|golden|green|blue|red|teal|gray|white|black|honeyed)\b'
        colors = re.findall(color_pattern, story_text, re.IGNORECASE)
        colors = list(set([color.lower() for color in colors]))
        
        return VisualElements(
            characters=characters,
            setting=setting,
            objects=objects,
            actions=actions,
            mood=mood,
            time_of_day=time_of_day,
            colors=colors
        )

# Convenience functions
def convert_story_to_image_prompt(
    story_text: str, 
    genre: str = "solarpunk",
    world_data: Optional[Dict[str, Any]] = None
) -> str:
    """Convert a story to an image prompt."""
    converter = StoryToImageConverter()
    return converter.convert_to_image_prompt(story_text, genre, world_data) 