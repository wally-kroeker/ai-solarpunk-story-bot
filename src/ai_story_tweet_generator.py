#!/usr/bin/env python3
"""
AI Solarpunk Story Bot - Simplified Story Generator
Generates fresh solarpunk micro-stories with new characters and locations each time.
"""

import asyncio
import argparse
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, NamedTuple

# Import story generation clients
from src.ai_solarpunk.clients.openai_story_client import (
    generate_story,
    generate_story_candidates,
    select_best_story,
    select_best_story_with_reasons
)

# Import image generation
from src.image_generator import ImageGenerator, ImageParameters

# Import Twitter functionality
from src.twitter_client import TwitterClient

# Import validation utilities
from src.validation import safe_write_json, safe_write_text

# Import centralized error handling
from src.error_handler import (
    error_handler,
    handle_errors,
    ErrorCategory,
    ErrorSeverity
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
STORY_GENERATION_MODEL = "o3"
STORY_SELECTION_MODEL = "o3"
NUM_STORIES_TO_GENERATE = 3

# File paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
STORIES_DIR = OUTPUT_DIR / "stories"
IMAGES_DIR = OUTPUT_DIR / "images"
PREVIEW_DIR = OUTPUT_DIR / "previews"

# Ensure directories exist
for directory in [OUTPUT_DIR, STORIES_DIR, IMAGES_DIR, PREVIEW_DIR]:
    os.makedirs(directory, exist_ok=True)

# Settings and themes
SETTINGS = [
    "urban", "coastal", "forest", "desert", "rural", "mountain", "arctic", "island",
    "wetland", "grassland", "reef", "reclaimed-industrial", "geothermal", "sky-city",
    "subterranean", "orbital"
]

THEMES = {
    "urban": ["vertical farms", "solar panels", "green rooftops", "urban forests", "bike infrastructure"],
    "coastal": ["wave energy", "kelp farms", "floating gardens", "tidal pools", "salt-resistant crops"],
    "forest": ["tree houses", "mycorrhizal networks", "canopy walkways", "forest restoration", "biomimicry"],
    "desert": ["solar concentrators", "water harvesting", "desert greening", "sand batteries", "oasis creation"],
    "rural": ["permaculture", "wind turbines", "community gardens", "seed banks", "regenerative agriculture"],
    "mountain": ["micro-hydro", "terraced gardens", "alpine greenhouses", "geothermal heating", "avalanche barriers"],
    "arctic": ["ice preservation", "aurora energy", "underground gardens", "thermal mass", "polar research"],
    "island": ["coral restoration", "rainwater collection", "ocean thermal", "floating platforms", "marine permaculture"],
    "wetland": ["bioswales", "floating islands", "water filtration", "amphibious housing", "wetland restoration"],
    "grassland": ["prairie restoration", "carbon sequestration", "rotational grazing", "wildflower corridors", "soil regeneration"],
    "reef": ["coral gardening", "underwater habitats", "marine sanctuaries", "algae cultivation", "ocean cleanup"],
    "reclaimed-industrial": ["brownfield restoration", "industrial symbiosis", "waste-to-energy", "green remediation", "adaptive reuse"],
    "geothermal": ["ground-source heating", "hot springs", "geothermal greenhouses", "mineral extraction", "thermal baths"],
    "sky-city": ["floating platforms", "aerial gardens", "wind harvesting", "cloud seeding", "atmospheric processing"],
    "subterranean": ["underground farms", "earth-sheltered homes", "geothermal systems", "root cellars", "cave ecosystems"],
    "orbital": ["space habitats", "solar collection", "asteroid mining", "zero-gravity gardens", "orbital manufacturing"]
}

# Recent seeds for deduplication
RECENT_SEEDS = []
MAX_RECENT_SEEDS = 50

# Story modes
STORY_MODES = ["micro", "extended"]


class GenerationResult(NamedTuple):
    """Container for generation results."""
    success: bool
    story: Optional[str] = None
    story_metadata: Optional[Dict] = None
    image_path: Optional[str] = None
    image_metadata: Optional[Dict] = None
    tweet_id: Optional[str] = None
    error: Optional[str] = None


def select_random_setting() -> str:
    """Select a random setting from available options."""
    return random.choice(SETTINGS)


def select_random_style() -> str:
    """Select a random art style."""
    styles = ["digital-art", "watercolor", "stylized", "solarpunk-nouveau", "retro-futurism", 
              "isometric", "paper-cut", "low-poly", "ukiyo-e", "stained-glass"]
    return random.choice(styles)


def maybe_secondary_theme() -> Optional[str]:
    """Randomly decide whether to include a secondary theme."""
    if random.random() < 0.3:  # 30% chance
        return random.choice(["community", "resilience", "innovation", "harmony", "regeneration"])
    return None


def build_generation_prompt(setting: str, primary_tech: str, secondary_theme: Optional[str]) -> str:
    """Build a story generation prompt that always creates new characters."""
    base_prompt = f"""You are a solarpunk flash-fiction writer.
Goal: One tweet ≤240 characters.

• Focus on ONE primary eco-tech or practice: {primary_tech}
• Story beats: [Vivid setting + NEW character] → [tech action] → [hopeful effect].
• Keep it plausible within the next 30 years; no magic or hand-waving.
• Tone: sensory, active, present-tense, no hashtags, no quotes.

Create a NEW character in a {setting} setting. Give them a name, brief personality, and show them using {primary_tech} in a meaningful way."""
    
    if secondary_theme:
        base_prompt += f"\n• Weave in themes of {secondary_theme}."
    
    return base_prompt


def build_extended_generation_prompt(setting: str, primary_tech: str, secondary_theme: Optional[str]) -> str:
    """Build an extended story generation prompt for threading."""
    base_prompt = f"""You are a solarpunk flash-fiction writer.
Goal: Extended micro-story (200-250 words) for Twitter threading.

• Focus on ONE primary eco-tech or practice: {primary_tech}
• Story structure: [Setting + NEW character] → [challenge] → [tech solution] → [community impact] → [hopeful conclusion].
• Include meaningful character development and dialogue.
• Build narrative tension and satisfying resolution.
• Keep it plausible within the next 30 years; no magic or hand-waving.
• Tone: sensory, active, present-tense, engaging.

Create a NEW character in a {setting} setting. Give them a name, background, and personality. Show them facing a challenge that requires {primary_tech} and community cooperation to solve."""

    if secondary_theme:
        base_prompt += f"\n• Weave in themes of {secondary_theme}."
    
    return base_prompt


def compress_pass(story: str) -> str:
    """Apply compression to a story that's too long."""
    if len(story) <= 240:
        return story
    # Simple compression: remove extra spaces and some words
    compressed = story.replace("  ", " ").strip()
    if len(compressed) <= 240:
        return compressed
    # More aggressive: truncate to 237 chars and add "..."
    return compressed[:237] + "..."


def extract_image_prompt(story: str, style: str, primary_tech: Optional[str]) -> Dict[str, str]:
    """Extract structured image prompt fields from the story."""
    logger.info(f"Extracting structured image prompt for tech: {primary_tech}")
    
    system_prompt = (
        "You are an AI assistant that extracts visual elements from a solarpunk micro-story to create an image prompt. "
        "Return a JSON object with these fields: subject, environment, mood, palette, style, tech, negatives. "
        "The described scene MUST be plausible within the next 30 years. "
        "If 'negatives' is missing, default to 'no text, no logo, no watermark, unrealistic, fantasy'. "
        "Example: {\"subject\":\"young person with solar device\",\"environment\":\"urban rooftop garden\",\"mood\":\"hopeful\",\"palette\":\"green, gold, blue\",\"style\":\"digital-art\",\"tech\":\"solar panels\",\"negatives\":\"no text, no logo, no watermark, unrealistic, fantasy\"}"
    )
    
    user_prompt = f"Here is a solarpunk micro-story:\n\n{story}\n\nExtract the key visual elements and return a JSON object as described above."
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        response = asyncio.run(generate_story(full_prompt, model="o3"))
        logger.info(f"Raw image prompt LLM output: {response[:200]}")
        
        # Find JSON object in response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            prompt_data = json.loads(json_str)
            
            # Ensure required fields
            if 'tech' not in prompt_data or not prompt_data['tech']:
                prompt_data['tech'] = primary_tech or 'sustainable technology'
            if 'negatives' not in prompt_data:
                prompt_data['negatives'] = 'no text, no logo, no watermark, unrealistic, fantasy'
            if 'style' not in prompt_data:
                prompt_data['style'] = style
                
            return prompt_data
    except Exception as e:
        logger.error(f"Error extracting image prompt: {e}")
    
    # Fallback
    return {
        "subject": "solarpunk scene with new character",
        "environment": "sustainable future setting",
        "mood": "hopeful",
        "palette": "green, gold, blue",
        "style": style,
        "tech": primary_tech or "sustainable technology",
        "negatives": "no text, no logo, no watermark, unrealistic, fantasy"
    }


def generate_image(story: str, setting: str, style: str, image_prompt_data: Optional[Dict[str, str]] = None, 
                  output_dir: Optional[str] = None, base_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Generate a single image from a story."""
    if output_dir is None:
        output_dir = str(IMAGES_DIR)
    
    if base_name is None:
        timestamp = int(time.time())
        base_name = f"image_{setting}_{style}_{timestamp}"
    
    # Generate image using image_generator module
    image_generator = ImageGenerator()
    
    if image_prompt_data is None:
        image_prompt_data = extract_image_prompt(story, style, None)
    
    # Create prompt string from structured data
    prompt_parts = [
        image_prompt_data.get('subject', 'solarpunk scene'),
        f"in {image_prompt_data.get('environment', 'sustainable setting')}",
        f"mood: {image_prompt_data.get('mood', 'hopeful')}",
        f"palette: {image_prompt_data.get('palette', 'green, gold, blue')}",
        f"featuring {image_prompt_data.get('tech', 'sustainable technology')}"
    ]
    prompt = ', '.join(prompt_parts)
    
    # Set up image parameters
    image_params = ImageParameters(
        style=style,
        samples=1,
        add_watermark=True
    )
    
    save_path = os.path.join(output_dir, f"{base_name}.png")
    
    try:
        # Generate image
        image_paths, metadata = image_generator.generate_image(
            prompt=prompt, 
            setting=setting, 
            parameters=image_params, 
            save_path=save_path
        )
        
        if image_paths and len(image_paths) > 0:
            final_image_path = image_paths[0]
            logger.info(f"Successfully generated image: {final_image_path}")
            return final_image_path, metadata
        else:
            raise ValueError("No image paths returned from generator")
            
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise


def post_to_twitter(story: str, image_path: Optional[str]) -> str:
    """Post a story and optional image to Twitter."""
    try:
        twitter_client = TwitterClient()
        
        if image_path and os.path.exists(image_path):
            media_id = twitter_client.upload_media(image_path)
            tweet_data = twitter_client.post_tweet(story, media_ids=[media_id])
        else:
            tweet_data = twitter_client.post_tweet(story)
        
        logger.info(f"Posted to Twitter with tweet ID: {tweet_data['id']}")
        return tweet_data['id']
        
    except Exception as e:
        logger.error(f"Error posting to Twitter: {e}")
        raise


def post_thread_to_twitter(story: str, image_path: Optional[str]) -> List[Dict[str, Any]]:
    """Post a story as a thread to Twitter with an image on the first tweet."""
    try:
        twitter_client = TwitterClient()
        return twitter_client.post_thread(story, image_path)
    except Exception as e:
        logger.error(f"Error posting thread to Twitter: {e}")
        raise


def save_preview(result: GenerationResult) -> str:
    """Save a preview of the generation results."""
    timestamp = int(time.time())
    preview_file = PREVIEW_DIR / f"preview_{timestamp}.json"
    
    preview_data = {
        "timestamp": timestamp,
        "story": result.story,
        "story_metadata": result.story_metadata,
        "image_path": str(result.image_path) if result.image_path else None,
        "image_metadata": result.image_metadata,
        "tweet_id": result.tweet_id,
        "error": result.error
    }
    
    with open(preview_file, 'w') as f:
        json.dump(preview_data, f, indent=2)
    
    return str(preview_file)


@handle_errors(
    category=ErrorCategory.RECOVERABLE,
    severity=ErrorSeverity.HIGH,
    user_message="Story generation failed"
)
def run_generation(
    setting: Optional[str] = None,
    style: Optional[str] = None,
    features: Optional[List[str]] = None,
    preview_only: bool = False,
    output_dir: Optional[str] = None,
    existing_story: Optional[str] = None,
    existing_story_file: Optional[str] = None,
    save_candidates_file: Optional[str] = None,
    story_mode: str = "micro"
) -> GenerationResult:
    """Run the complete generation flow."""
    try:
        # Set defaults
        if not setting or setting == "random":
            setting = select_random_setting()
            logger.info(f"Randomly selected setting: {setting}")
            
        if not style or style == "random":
            style = select_random_style()
            logger.info(f"Randomly selected style: {style}")
            
        if not features:
            features = ["story", "image"]
            
        result = GenerationResult(success=False)
        story = existing_story
        primary_tech = None
        secondary_theme = None
        
        # Generate base name
        timestamp = int(time.time())
        base_name = f"{setting}_{style}_{timestamp}"
        
        # Generate story if requested and not provided
        if "story" in features and not story:
            # Select tech and theme
            primary_tech = random.choice(THEMES.get(setting, ["sustainability"]))
            secondary_theme = maybe_secondary_theme()
            
            logger.info(f"Generating story with setting: {setting}, tech: {primary_tech}, theme: {secondary_theme}")
            
            # Build prompt based on story mode
            if story_mode == "extended":
                prompt = build_extended_generation_prompt(setting, primary_tech, secondary_theme)
            else:
                prompt = build_generation_prompt(setting, primary_tech, secondary_theme)
                
            # Generate candidates
            story_candidates = asyncio.run(generate_story_candidates(
                prompt=prompt,
                num_candidates=NUM_STORIES_TO_GENERATE,
                generation_model=STORY_GENERATION_MODEL
            ))
            
            if not story_candidates:
                raise ValueError("No story candidates generated")
                
            # Select best story with reasons
            selection_data = asyncio.run(select_best_story_with_reasons(
                stories=story_candidates,
                selection_model=STORY_SELECTION_MODEL
            ))
            
            if selection_data and 'selected_story' in selection_data:
                story = selection_data['selected_story']
                selected_index = selection_data.get('selected_index', 0)
                selection_reasons = selection_data.get('reasons', 'No reasons provided')
            else:
                # Fallback to simple selection
                story = asyncio.run(select_best_story(
                    stories=story_candidates,
                    selection_model=STORY_SELECTION_MODEL
                ))
                selected_index = 0
                selection_reasons = "Selection made using simple method"
                
            if not story:
                story = story_candidates[0]  # Fallback
                
            # Save candidates if requested
            if save_candidates_file:
                try:
                    candidates_data = {
                        "stories": story_candidates,
                        "selected_index": selected_index,
                        "selected_story": story,
                        "selection_reasons": selection_reasons,
                        "metadata": {
                            "setting": setting,
                            "style": style,
                            "primary_tech": primary_tech,
                            "secondary_theme": secondary_theme,
                            "timestamp": timestamp,
                            "story_mode": story_mode
                        }
                    }
                    with open(save_candidates_file, 'w') as f:
                        json.dump(candidates_data, f, indent=2)
                    logger.info(f"Candidates saved to {save_candidates_file}")
                except Exception as e:
                    logger.error(f"Failed to save candidates: {e}")
                
            logger.info(f"Selected story: {story[:100]}...")
            
            # Compress if needed (only for micro stories)
            if story_mode == "micro" and len(story) > 240:
                story = compress_pass(story)
                
            # Save story
            if base_name:
                story_file = STORIES_DIR / f"story_{base_name}.txt"
                try:
                    with open(story_file, 'w') as f:
                        f.write(story)
                    logger.info(f"Story saved to {story_file}")
                except Exception as e:
                    logger.error(f"Failed to save story: {e}")
                    
            # Update result
            story_metadata = {
                "setting": setting,
                "style": style,
                "primary_tech": primary_tech,
                "secondary_theme": secondary_theme,
                "char_count": len(story),
                "timestamp": timestamp,
                "story_mode": story_mode
            }
            
            result = result._replace(story=story, story_metadata=story_metadata)
            
        # Generate image if requested
        if "image" in features and result.story:
            try:
                logger.info("Generating image...")
                image_prompt_data = extract_image_prompt(result.story, style, primary_tech)
                image_path, image_metadata = generate_image(
                    result.story,
                    setting,
                    style,
                    image_prompt_data=image_prompt_data,
                    output_dir=output_dir,
                    base_name=base_name
                )
                result = result._replace(image_path=image_path, image_metadata=image_metadata)
                
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                # Continue without image
                
        # Post to Twitter if requested
        if "post" in features and not preview_only and result.story:
            try:
                if "thread" in features and story_mode == "extended":
                    # Post as thread
                    thread_data = post_thread_to_twitter(result.story, result.image_path)
                    if thread_data and len(thread_data) > 0:
                        tweet_id = thread_data[0].get('id')
                        result = result._replace(tweet_id=tweet_id)
                else:
                    # Post as single tweet
                    tweet_id = post_to_twitter(result.story, result.image_path)
                    result = result._replace(tweet_id=tweet_id)
                    
            except Exception as e:
                logger.error(f"Twitter posting failed: {e}")
                # Continue without posting
                
        return result._replace(success=True)
        
    except Exception as e:
        logger.exception(f"Generation pipeline error: {e}")
        return GenerationResult(success=False, error=str(e))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Solarpunk Story Generator")
    parser.add_argument('--setting', choices=SETTINGS + ['random'], default='random',
                      help='Story setting')
    parser.add_argument('--style', default='random',
                      help='Art style for image generation')
    parser.add_argument('--features', default='story,image',
                      help='Comma-separated list of features to run')
    parser.add_argument('--preview', action='store_true',
                      help='Generate preview without posting')
    parser.add_argument('--output-dir', type=str,
                      help='Output directory for generated content')
    parser.add_argument('--story-file', type=str,
                      help='Use existing story file')
    parser.add_argument('--save-candidates', type=str,
                      help='Save story candidates to file')
    parser.add_argument('--story-mode', choices=STORY_MODES, default='micro',
                      help='Story generation mode')
    
    args = parser.parse_args()
    features = [f.strip() for f in args.features.split(',')]
    
    # Load existing story if provided
    existing_story = None
    if args.story_file and os.path.exists(args.story_file):
        with open(args.story_file, 'r') as f:
            existing_story = f.read().strip()
    
    # Run generation
    result = run_generation(
        setting=args.setting,
        style=args.style,
        features=features,
        preview_only=args.preview,
        output_dir=args.output_dir,
        existing_story=existing_story,
        existing_story_file=args.story_file,
        save_candidates_file=args.save_candidates,
        story_mode=args.story_mode
    )
    
    if result.success:
        logger.info("Generation completed successfully")
        if args.preview:
            preview_file = save_preview(result)
            logger.info(f"Preview saved to: {preview_file}")
    else:
        logger.error(f"Generation failed: {result.error}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main()) 