#!/usr/bin/env python
"""
AI Solarpunk Story Tweet Generator

This script implements the complete flow for the AI Solarpunk Story Twitter Bot:
1. Randomly selects a setting and style (or uses provided ones)
2. Generates a solarpunk micro-story with that setting
3. Optionally extracts key elements from the story to create an image prompt
4. Generates an image using that prompt with the specified style
5. Optionally posts both the story and image to Twitter
"""

import os
import random
import logging
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, NamedTuple
import asyncio
import json as _json
import collections

# Import our modules
from src.story_generator import StoryGenerator, StoryParameters
from src.image_generator import ImageGenerator, ImageParameters
from src.twitter_client import TwitterClient
from src.ai_solarpunk.clients.openai_story_client import generate_story as openai_generate_story, openai_rate_story

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- SETTINGS ------------------------------------
SETTINGS = [
    "urban","coastal","forest","desert","rural","mountain",
    "arctic","island",
    # NEW
    "wetland","grassland","reef","reclaimed-industrial",
    "geothermal","sky-city","subterranean","orbital"
]

# --- THEME MAP (primary) -------------------------
THEMES = {
    "urban": ["renewable energy","community gardens","local production"],
    "coastal": ["ocean conservation","floating communities","tidal energy"],
    "forest": ["forest stewardship","ecological monitoring","natural architecture"],
    "desert": ["water conservation","solar power","desert greening"],
    "rural": ["sustainable agriculture","community ownership","regenerative practices"],
    "mountain": ["sustainability"],
    "arctic": ["sustainability"],
    "island": ["sustainability"],
    # NEW
    "wetland": ["flood-resilience","mangrove restoration","floating hydroponics"],
    "grassland": ["wind-harvest","regenerative grazing","soil-carbon"],
    "reef": ["coral 3-D printing","kelp bio-fuel","tidal-kite turbines"],
    "reclaimed-industrial": ["phytoremediation","vertical forests","circular workshops"],
    "geothermal": ["magma greenhouses","district heat","lava-steam grids"],
    "sky-city": ["airborne algae","cloud farms","wind-shear turbines"],
    "subterranean": ["mycelium farms","kinetic-floor lighting","earth-cooling"],
    "orbital": ["closed-loop life support","solar-sail agri","asteroid gardens"]
}

# --- CROSS-CUT THEMES (secondary tag) ------------
X_THEMES = [
  "indigenous stewardship","biodiversity corridors","open-source tech",
  "inclusive design","eco-mobility","citizen-science","festival culture"
]

# --- ART STYLES & MODIFIERS ----------------------
ART_STYLES = {
  "digital-art": "ultra-detailed digital painting",
  "watercolor": "loose watercolor illustration",
  "stylized": "Studio Ghibli vibe",
  "solarpunk-nouveau": "Art-Nouveau lines, stained-glass light",
  "retro-futurism": "1960s sci-fi poster, halftone shading",
  "isometric": "isometric cutaway, crisp lines",
  # NEW
  "paper-cut": "layered paper-cut collage",
  "low-poly": "low-poly diorama, toy-like",
  "ukiyo-e": "ukiyo-e woodblock print",
  "stained-glass": "luminous stained-glass mosaic",
  "claymation": "hand-crafted claymation still",
  "pixel-art": "16-bit pixel art",
  "flat-vector": "clean flat-vector poster",
  "impressionist": "loose impressionist brush",
  "holo-neon": "holographic neon glow"
}

# Available options
STYLES = list(ART_STYLES.keys())
FEATURES = ["story", "image", "post"]  # Can be combined

# Project root directory for saving files
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
STORIES_DIR = OUTPUT_DIR / "stories"
PREVIEW_DIR = OUTPUT_DIR / "previews"

# Ensure output directories exist
for directory in [IMAGES_DIR, STORIES_DIR, PREVIEW_DIR]:
    os.makedirs(directory, exist_ok=True)

# At module level:
RECENT_SEEDS = collections.deque(maxlen=10)

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
    """Randomly select a setting, with 20% chance for new settings."""
    legacy = [s for s in SETTINGS if s not in {"wetland","grassland","reef","reclaimed-industrial","geothermal","sky-city","subterranean","orbital"}]
    new = [s for s in SETTINGS if s not in legacy]
    if random.random() < 0.20 and new:
        return random.choice(new)
    return random.choice(legacy)

def select_random_style() -> str:
    """Randomly select an art style, with 20% chance for new styles."""
    legacy = [k for k in ART_STYLES.keys() if k in {"digital-art","watercolor","stylized","solarpunk-nouveau","retro-futurism","isometric"}]
    new = [k for k in ART_STYLES.keys() if k not in legacy]
    if random.random() < 0.20 and new:
        return random.choice(new)
    return random.choice(legacy)

def maybe_secondary_theme() -> Optional[str]:
    """25% chance to select a secondary theme from X_THEMES."""
    if random.random() < 0.25:
        return random.choice(X_THEMES)
    return None

class StoryParameters:
    """Parameters for story generation (local wrapper)."""
    def __init__(self, setting: str, primary_tech: str, secondary_theme: Optional[str] = None):
        self.setting = setting
        self.primary_tech = primary_tech
        self.secondary_theme = secondary_theme
        self.max_chars = 280 # Upper limit, prompt uses 240

def compress_pass(story: str) -> str:
    """Compress a story to <=240 characters using the LLM, preserving meaning and solarpunk tone."""
    logger.info(f"Compressing story (original length: {len(story)})")
    compress_prompt = (
        "You are a solarpunk flash-fiction writer.\n"
        "Goal: One tweet ≤240 characters.\n\n"
        "• Focus on ONE primary eco-tech or practice.\n"
        "• Story beats: [Vivid setting + character] → [tech action] → [hopeful effect].\n"
        "• Keep it plausible within the next 30 years; no magic or hand-waving.\n"
        "• Tone: sensory, active, present-tense, no hashtags, no quotes.\n\n"
        "COMPRESS the following micro-story to 240 characters or fewer, preserving its core meaning, hopefulness, and solarpunk tone. Do not simply truncate.\n\n"
        f"ORIGINAL:\n{story}\n\nCOMPRESSED:"
    )
    try:
        compressed = asyncio.run(openai_generate_story(compress_prompt, model="o3"))
        compressed = compressed.strip()
        logger.info(f"Compressed story length: {len(compressed)}")
        return compressed
    except Exception as e:
        logger.error(f"Error compressing story: {e}")
        return story

def generate_story(setting: str, style: str, primary_tech: str, secondary_theme: Optional[str], output_dir: Optional[str] = None, base_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Generate a solarpunk micro-story focusing on a primary tech."""
    logger.info(f"Generating story with setting: {setting}, primary_tech: {primary_tech}, style: {style}")
    try:
        # Initialize the story generator
        story_generator = StoryGenerator()
        # Create story parameters with the specified setting and tech
        params = StoryParameters(setting=setting, primary_tech=primary_tech, secondary_theme=secondary_theme)
        # Build the prompt
        prompt = (
            "You are a solarpunk flash-fiction writer.\n"
            "Goal: One tweet ≤240 characters.\n\n"
            "• Focus on ONE primary eco-tech or practice.\n"
            "• Story beats: [Vivid setting + character] → [tech action] → [hopeful effect].\n"
            "• Keep it plausible within the next 30 years; no magic or hand-waving.\n"
            "• Tone: sensory, active, present-tense, no hashtags, no quotes.\n\n"
            f"Write a solarpunk micro-story set in a {params.setting} environment. "
            f"Primary Eco-Tech: {params.primary_tech}. " # Use primary_tech here
        )
        if params.secondary_theme:
            prompt += f"Secondary theme: {params.secondary_theme}. "
        prompt += (
            f"The story must be positive, hopeful, and fit within 240 characters. "
            f"It should be suitable for a Twitter post."
        )
        logger.info(f"Story prompt: {prompt}")
        # Generate the story
        story, metadata = story_generator.generate_story(params)
        # If len(story) > 240, call compress_pass and use the result
        if len(story) > 240:
            story = compress_pass(story)
        # Save the story to a file (using provided base_name)
        if base_name: # Ensure base_name is provided
            if output_dir:
                story_file = Path(output_dir) / f"story_{base_name}.txt"
            else:
                story_file = STORIES_DIR / f"story_{base_name}.txt"
            with open(story_file, 'w') as f:
                f.write(story)
            logger.info(f"Story generated successfully ({len(story)} characters)")
            logger.info(f"Story saved to {story_file}")
            return story, metadata
        else:
            logger.error("Base name not provided to generate_story")
            raise ValueError("Base name is required for saving the story file")
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise

def send_error_email(subject: str, message: str) -> None:
    """Stub for sending an error notification email to the maintainer."""
    logger.warning(f"[EMAIL STUB] Would send email: {subject} - {message}")

def extract_image_prompt(story: str, style: str, primary_tech: str) -> Dict[str, str]:
    """Extract structured image prompt fields from the story using OpenAI o3 LLM.
    Ensures the primary_tech is included in the output.
    Returns a dict with keys: subject, environment, mood, palette, style, tech, negatives.
    """
    logger.info(f"Extracting structured image prompt for tech: {primary_tech}")
    system_prompt = (
        "You are an AI assistant that extracts visual elements from a solarpunk micro-story to create an image prompt. "
        "Return a JSON object with these fields: subject, environment, mood, palette, style, tech, negatives. "
        "Crucially, the described scene MUST be plausible within the next 30 years. Avoid fantasy elements like floating islands unless explicitly and plausibly described in the story. "
        "The 'tech' field MUST accurately represent the main technology mentioned. "
        "If a field other than 'tech' is not present, make a creative guess consistent with near-future plausibility. "
        "If 'negatives' is missing, default to 'no text, no logo, no watermark, unrealistic, fantasy'. "
        "Example output: {\"subject\":\"...\",\"environment\":\"...\",\"mood\":\"...\",\"palette\":\"...\",\"style\":\"digital-art\",\"tech\":\"vertical farms\",\"negatives\":\"no text, no logo, no watermark, unrealistic, fantasy\"}"
    )
    user_prompt = (
        f"Here is a solarpunk micro-story featuring {primary_tech}:\n\n{story}\n\n"
        "Extract the key visual elements and return a JSON object as described above, ensuring the 'tech' field is accurate."
    )
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        # Use OpenAI o3 model to generate the image prompt JSON
        response = asyncio.run(openai_generate_story(full_prompt, model="o3"))
        logger.info(f"Raw image prompt LLM output: {response[:200]}")
        # Find the first JSON object in the response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in LLM response")
        json_str = response[start:end]
        prompt_data = _json.loads(json_str)
        # Ensure all required fields are present and tech is correct
        prompt_data['tech'] = primary_tech # Force correct tech
        if 'negatives' not in prompt_data or not prompt_data['negatives']:
            prompt_data['negatives'] = 'no text, no logo, no watermark, unrealistic, fantasy'
        if 'style' not in prompt_data or not prompt_data['style']:
            prompt_data['style'] = style
        return prompt_data
    except Exception as e:
        logger.error(f"Error extracting structured image prompt: {e}")
        send_error_email(
            subject="AI Solarpunk Bot: Image Prompt Extraction Failure",
            message=f"Failed to extract image prompt for story: {story[:200]}\nError: {e}"
        )
        raise

def generate_image(story: str, setting: str, style: str, image_prompt_data: Optional[Dict[str, str]] = None, output_dir: Optional[str] = None, base_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Generate an image based on the story and structured image prompt, using the provided base name for file naming."""
    logger.info(f"Generating image with setting: {setting}, style: {style}")
    try:
        # Initialize the image generator
        image_generator = ImageGenerator()
        # Create image parameters with specified style
        params = ImageParameters(style=style)
        # Use the provided base name
        if not base_name:
            logger.error("Base name not provided to generate_image")
            raise ValueError("Base name is required for saving the image file")
        if output_dir:
            image_file = Path(output_dir) / f"image_{base_name}.png"
        else:
            image_file = IMAGES_DIR / f"image_{base_name}.png"
        # Build the final image prompt from the structured fields
        if image_prompt_data:
            art_style_modifier = ART_STYLES.get(image_prompt_data.get('style', style), ART_STYLES[style])
            prompt = (
                f"{image_prompt_data.get('subject','')}, {image_prompt_data.get('environment','')}, featuring {image_prompt_data.get('tech','')}, "
                f"{image_prompt_data.get('mood','')}, palette {image_prompt_data.get('palette','')}, {art_style_modifier}, near-future realism, plausible technology, "
                f"negative prompt: {image_prompt_data.get('negatives','no text, no logo, no watermark, unrealistic, fantasy, floating islands, magic')}"
            )
        else:
            prompt = f"{story}, near-future realism, plausible technology, negative prompt: no text, no logo, no watermark, unrealistic, fantasy, floating islands, magic"
        logger.info(f"Final image prompt: {prompt}")
        # Generate the image
        images, metadata = image_generator.generate_image(
            prompt,
            setting,
            params,
            save_path=str(image_file)
        )
        logger.info(f"Image generated and saved to {image_file}")
        return str(image_file), metadata
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise

def post_to_twitter(story: str, image_path: str) -> str:
    """Post the story and image to Twitter."""
    logger.info("Posting story and image to Twitter")
    
    try:
        # Initialize the Twitter client
        twitter_client = TwitterClient()
        
        # Upload the image
        media_id = twitter_client.upload_media(image_path)
        
        # Post the tweet with the story and image
        tweet_id = twitter_client.post_tweet(story, media_ids=[media_id])
        
        logger.info(f"Successfully posted tweet with ID: {tweet_id}")
        return tweet_id
    except Exception as e:
        logger.error(f"Error posting to Twitter: {e}")
        raise

def save_preview(result: GenerationResult) -> str:
    """Save a preview of the generation results."""
    timestamp = int(time.time())
    preview_file = PREVIEW_DIR / f"preview_{timestamp}.json"
    
    preview_data = {
        "timestamp": timestamp,
        "story": result.story,
        "story_metadata": result.story_metadata,
        "image_path": result.image_path,
        "image_metadata": result.image_metadata,
        "tweet_id": result.tweet_id,
        "error": result.error
    }
    
    with open(preview_file, 'w') as f:
        json.dump(preview_data, f, indent=2)
    
    return str(preview_file)

def believability_check(story: str) -> bool:
    """Check story plausibility using an LLM rating (1-9). Returns True if score >= 7."""
    prompt = (
        "Rate the following solarpunk micro-story on realism (plausibility within the next 30 years). "
        "Use a scale of 1-9, where 9 = fully plausible near-future, 1 = speculative fantasy. "
        "Return ONLY the integer rating.\n\n"
        f"STORY:\n{story}\n\nRATING:"
    )
    try:
        score = asyncio.run(openai_rate_story(prompt))
        logger.info(f"Believability score: {score}")
        return score >= 7
    except Exception as e:
        logger.error(f"Error during believability check: {e}")
        return False # Default to not believable on error

def run_generation(
    setting: Optional[str] = None,
    style: Optional[str] = None,
    features: Optional[List[str]] = None,
    preview_only: bool = False,
    output_dir: Optional[str] = None,
    existing_story: Optional[str] = None,
    existing_story_file: Optional[str] = None
) -> GenerationResult:
    """Run the complete or partial generation flow based on specified features."""
    try:
        # 1. Set defaults and validate inputs
        if not setting or setting == "random":
            setting = select_random_setting()
            logger.info(f"Randomly selected setting: {setting}")
        if not style or style == "random":
            style = select_random_style()
            logger.info(f"Randomly selected style: {style}")
        if not features:
            features = ["story", "image", "post"]
        result = GenerationResult(success=False)
        story = existing_story
        story_metadata = {"source": "provided"} if existing_story else None
        primary_tech = None
        secondary_theme = None
        # ---> Generate base_name ONCE here <-----
        timestamp = int(time.time())
        # Determine base_name early, before the loop
        # If existing_story_file is provided, try to extract from it
        if existing_story_file and story:
            filename = os.path.basename(existing_story_file)
            if filename.startswith("story_") and filename.endswith(".txt"):
                base_name = filename[len("story_"):-len(".txt")]
            else:
                # Fallback if filename pattern doesn't match
                base_name = f"{setting}_{style}_{timestamp}"
        elif not existing_story: # Only generate new name if not using existing story
             base_name = f"{setting}_{style}_{timestamp}"
        else:
            base_name = None # Should not happen if logic is correct, but safer
        # 1.5 Seed deduplication for random generations
        if not existing_story:
            # Try up to 10 times to get a unique seed
            for _ in range(10):
                primary_tech = random.choice(THEMES.get(setting, ["sustainability"]))
                secondary_theme = maybe_secondary_theme()
                seed = (setting, primary_tech, secondary_theme, style) # Updated seed
                if seed not in RECENT_SEEDS:
                    RECENT_SEEDS.append(seed)
                    break
                # If duplicate, re-randomize setting/style
                setting = select_random_setting()
                style = select_random_style()
            else:
                logger.warning("Could not find a unique seed after 10 attempts; proceeding anyway.")
                RECENT_SEEDS.append(seed)
        # 2. Generate story if requested and no existing story is provided
        if "story" in features and not story:
            # Ensure primary_tech is selected if we didn't go through the deduplication loop (e.g., fixed setting/style)
            if primary_tech is None:
                primary_tech = random.choice(THEMES.get(setting, ["sustainability"]))
            if secondary_theme is None:
                 secondary_theme = maybe_secondary_theme()
            # Loop for regeneration based on believability
            story = None
            story_metadata = None
            for attempt in range(3):
                logger.info(f"Story generation attempt {attempt + 1}/3")
                current_story, current_metadata = generate_story(
                    setting,
                    style,
                    primary_tech,
                    secondary_theme,
                    output_dir,
                    base_name=base_name
                )
                if believability_check(current_story):
                    story = current_story
                    story_metadata = current_metadata
                    logger.info("Story passed believability check.")
                    break
                else:
                    story = current_story # Keep last attempt if all fail
                    story_metadata = current_metadata
                    logger.warning("Story failed believability check, will retry if possible...")
            else: # If loop finishes without break
                logger.warning("Story failed believability check after 3 attempts, using last generated story.")

            # Ensure story is not None before proceeding
            if story is None:
                raise ValueError("Story generation failed after retries.")

            result = result._replace(
                story=story,
                story_metadata=story_metadata
            )
        elif story:
            result = result._replace(
                story=story,
                story_metadata=story_metadata
            )
        # 3. Generate image if requested
        if "image" in features and result.story:
            image_prompt_data = extract_image_prompt(result.story, style, primary_tech)
            image_path, image_metadata = generate_image(
                result.story,
                setting,
                style,
                image_prompt_data=image_prompt_data,
                output_dir=output_dir,
                base_name=base_name
            )
            result = result._replace(
                image_path=image_path,
                image_metadata=image_metadata
            )
        # 4. Post to Twitter if requested and not in preview mode
        if "post" in features and not preview_only and result.story and result.image_path:
            tweet_id = post_to_twitter(result.story, result.image_path)
            result = result._replace(tweet_id=tweet_id)
        result = result._replace(success=True)
        return result
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        return GenerationResult(success=False, error=str(e))

def post_from_preview(preview_file: str) -> bool:
    """Post content from a previously generated preview file."""
    logger.info(f"Posting from preview file: {preview_file}")
    
    try:
        # Load the preview data
        with open(preview_file, 'r') as f:
            preview_data = json.load(f)
        
        # Verify we have the required data
        if not preview_data.get('story') or not preview_data.get('image_path'):
            raise ValueError("Preview file missing required story or image data")
            
        # Check if image file exists
        if not os.path.exists(preview_data['image_path']):
            raise FileNotFoundError(f"Image file not found: {preview_data['image_path']}")
        
        # Post to Twitter
        tweet_id = post_to_twitter(preview_data['story'], preview_data['image_path'])
        
        # Update the preview file with the tweet ID
        preview_data['tweet_id'] = tweet_id
        preview_data['posted'] = True
        preview_data['post_timestamp'] = int(time.time())
        
        with open(preview_file, 'w') as f:
            json.dump(preview_data, f, indent=2)
        
        logger.info(f"Successfully posted preview content, tweet ID: {tweet_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error posting from preview: {e}")
        return False

def main():
    """Parse command line arguments and run the generator."""
    parser = argparse.ArgumentParser(description='AI Solarpunk Story Tweet Generator')
    
    # Input options
    parser.add_argument('--setting', type=str, choices=SETTINGS + ['random'],
                      help='Setting for the story (or "random")')
    parser.add_argument('--style', type=str, choices=STYLES + ['random'],
                      help='Style for the image (or "random")')
    parser.add_argument('--features', type=str, default="story,image,post",
                      help='Comma-separated list of features to generate (story,image,post)')
    parser.add_argument('--preview', action='store_true',
                      help='Generate for preview only (no posting)')
    parser.add_argument('--output-dir', type=str,
                      help='Directory to save output files')
    
    # Add story-file option for using an existing story
    parser.add_argument('--story-file', type=str,
                      help='Use an existing story file instead of generating a new one')
    
    # Direct posting options
    parser.add_argument('--post-files', type=str,
                      help='Post existing files (format: "story_path:image_path")')
    parser.add_argument('--post-preview', type=str,
                      help='Post from a preview file')
    
    args = parser.parse_args()
    
    try:
        # Handle the post-files option (direct posting of existing files)
        if args.post_files:
            story_path, image_path = args.post_files.split(':')
            
            # Read the story content
            with open(story_path, 'r') as f:
                story = f.read()
                
            # Post directly
            tweet_id = post_to_twitter(story, image_path)
            logger.info(f"Posted existing files successfully. Tweet ID: {tweet_id}")
            return 0
            
        # Handle the post-preview option
        if args.post_preview:
            with open(args.post_preview, 'r') as f:
                preview_data = json.load(f)
                
            # Post the story and image from the preview
            tweet_id = post_to_twitter(preview_data['story'], preview_data['image_path'])
            
            # Update the preview file to mark as posted
            preview_data['posted'] = True
            preview_data['tweet_id'] = tweet_id
            
            with open(args.post_preview, 'w') as f:
                json.dump(preview_data, f, indent=2)
                
            logger.info(f"Posted from preview successfully. Tweet ID: {tweet_id}")
            return 0
        
        # Parse features
        features = [f.strip() for f in args.features.split(',')]
        
        # If we're generating just an image but using an existing story file,
        # make sure "story" is not in features to avoid regenerating it
        if args.story_file and "image" in features and "story" in features:
            features.remove("story")
        
        # Handle story-file option
        existing_story = None
        
        if args.story_file:
            with open(args.story_file, 'r') as f:
                existing_story = f.read()
            
            # Extract setting from the filename if possible
            filename = os.path.basename(args.story_file)
            if filename.startswith("story_"):
                parts = filename.split("_")
                if len(parts) > 1 and not args.setting:
                    args.setting = parts[1]
            
            logger.info(f"Using existing story from {args.story_file}")
        
        # Run the generator
        result = run_generation(
            setting=args.setting,
            style=args.style,
            features=features,
            preview_only=args.preview,
            output_dir=args.output_dir,
            existing_story=existing_story,
            existing_story_file=args.story_file
        )
        
        # Save preview if requested
        if args.preview:
            preview_file = save_preview(result)
            logger.info(f"Preview saved to {preview_file}")
            
        # Show summary if successful
        if result.success:
            logger.info("Generation completed successfully")
            if result.story:
                logger.info(f"Story length: {len(result.story)} characters")
            if result.image_path:
                logger.info(f"Image saved to: {result.image_path}")
            if result.tweet_id:
                logger.info(f"Posted to Twitter with ID: {result.tweet_id}")
                
            return 0
        else:
            logger.error(f"Generation failed: {result.error}")
            return 1
            
    except Exception as e:
        logger.exception(f"Error running generator: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 