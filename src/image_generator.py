"""Image generation module using OpenAI DALL-E for companion image generation.

This module provides functionality for generating solarpunk images
that visualize the stories created with the story generation module.
Enhanced with genre-specific aesthetics and threading support.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from src.ai_solarpunk.clients import openai_image_client
import asyncio
from dotenv import load_dotenv

# Import centralized error handling
from src.error_handler import (
    CentralizedErrorHandler, 
    handle_errors, 
    ErrorCategory
)

# Load environment variables from .env file
load_dotenv()

# Initialize centralized error handler
error_handler = CentralizedErrorHandler()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Create output directory if it doesn't exist
OUTPUT_DIR = PROJECT_ROOT / "output" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Genre-specific image enhancement templates
GENRE_IMAGE_ENHANCEMENTS = {
    "solarpunk": {
        "style_suffix": "Studio Ghibli style, organic architecture, eco-futurism aesthetic",
        "lighting": "warm natural sunlight, golden hour lighting, bioluminescent accents",
        "quality": "high quality, detailed, professional illustration, cinematic composition",
        "negative": "dark, polluted, industrial waste, concrete dominance, grey sky"
    },
    "fantasy": {
        "style_suffix": "fantasy art style, magical realism, ethereal atmosphere",
        "lighting": "ethereal glow, magical light sources, moonbeams, enchanted lighting",
        "quality": "high quality, detailed, professional fantasy illustration, mystical composition",
        "negative": "modern technology, urban elements, cars, concrete buildings"
    },
    "sci-fi": {
        "style_suffix": "cyberpunk aesthetic, futuristic concept art, sleek design",
        "lighting": "neon lighting, holographic displays, artificial illumination, chrome reflections",
        "quality": "high quality, detailed, professional sci-fi illustration, cinematic composition",
        "negative": "medieval elements, fantasy creatures, organic textures, pastoral scenes"
    },
    "steampunk": {
        "style_suffix": "steampunk art style, Victorian industrial aesthetic, brass and copper",
        "lighting": "gas lamp lighting, steam effects, warm brass illumination, mechanical gleam",
        "quality": "high quality, detailed, professional steampunk illustration, industrial composition",
        "negative": "digital technology, plastic materials, modern electronics, clean minimalism"
    }
}

@dataclass
class ImageParameters:
    """Parameters for companion image generation."""
    style: str = "digital-art"
    samples: int = 1
    add_watermark: bool = True
    genre: str = "solarpunk"
    enhance_prompt: bool = True
    include_negative_prompt: bool = True
    # model_name is kept for compatibility but not used in OpenAI-only mode
    model_name: str = "dall-e-3"

    def __post_init__(self) -> None:
        """Ensure parameters are valid."""
        # Validate samples
        if self.samples < 1 or self.samples > 4:
            self.samples = 1
        # Validate style
        valid_styles = ["digital-art", "watercolor", "stylized", "solarpunk-nouveau", "retro-futurism", "isometric", "photographic"]
        if self.style not in valid_styles:
            self.style = "digital-art"
        # Validate genre
        valid_genres = ["solarpunk", "fantasy", "sci-fi", "steampunk"]
        if self.genre not in valid_genres:
            self.genre = "solarpunk"

class CompanionImageGenerator:
    """Enhanced generator for companion images with genre-specific aesthetics."""
    
    def __init__(self):
        """Initialize the companion image generator."""
        self.genre_enhancements = GENRE_IMAGE_ENHANCEMENTS
    
    def enhance_prompt_for_genre(
        self, 
        base_prompt: str, 
        genre: str = "solarpunk",
        style: str = "digital-art",
        include_negative: bool = True
    ) -> Tuple[str, Optional[str]]:
        """Enhance an image prompt with genre-specific aesthetics.
        
        Args:
            base_prompt: The base image prompt
            genre: The genre for aesthetic enhancement
            style: The artistic style
            include_negative: Whether to include negative prompts
            
        Returns:
            Tuple of (enhanced_prompt, negative_prompt)
        """
        genre_data = self.genre_enhancements.get(genre, self.genre_enhancements["solarpunk"])
        
        # Build enhanced prompt
        enhanced_parts = [
            base_prompt.strip(),
            f"artistic style: {style}, {genre_data['style_suffix']}",
            f"lighting: {genre_data['lighting']}",
            genre_data['quality']
        ]
        
        enhanced_prompt = ". ".join(enhanced_parts) + "."
        
        # Generate negative prompt if requested
        negative_prompt = None
        if include_negative:
            base_negative = "text overlays, watermarks, signatures, blurry, low quality, distorted, malformed"
            negative_prompt = f"{base_negative}, {genre_data['negative']}"
        
        return enhanced_prompt, negative_prompt
    
    def create_threading_structure(
        self,
        story_text: str,
        threading_blocks: List[str],
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a structured format for Twitter thread posting.
        
        Args:
            story_text: The full story text
            threading_blocks: Pre-generated threading blocks
            image_path: Path to the companion image
            
        Returns:
            Dictionary with threading structure and metadata
        """
        # Validate threading blocks
        validated_blocks = []
        for i, block in enumerate(threading_blocks):
            if len(block) <= 250:  # Twitter thread limit
                validated_blocks.append(block)
            else:
                # Truncate if too long
                truncated = block[:247] + "..."
                validated_blocks.append(truncated)
                logger.warning(f"Block {i+1} truncated from {len(block)} to 250 characters")
        
        threading_structure = {
            "story_text": story_text,
            "blocks": validated_blocks,
            "total_blocks": len(validated_blocks),
            "image_path": image_path,
            "has_image": bool(image_path),
            "story_length": len(story_text),
            "word_count": len(story_text.split()),
            "ready_for_posting": len(validated_blocks) > 0,
            "estimated_thread_length": len(validated_blocks)
        }
        
        return threading_structure

class ImageGenerator:
    """Generator for solarpunk images using OpenAI only, enhanced for companion image generation."""
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def __init__(self) -> None:
        """Initialize the image generator (OpenAI only)."""
        self.companion_generator = CompanionImageGenerator()
        logger.info("ImageGenerator configured to use OpenAI provider only.")

    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def generate_image(
        self,
        story: Optional[str] = None,  # Accept story parameter for backward compatibility
        prompt: Optional[str] = None,  # Accept prompt parameter for direct prompts
        setting: Optional[str] = None,
        parameters: Optional[ImageParameters] = None,
        params: Optional[ImageParameters] = None,  # Alternative parameter name
        save_path: Optional[str] = None
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """Generate companion images based on a story or prompt using OpenAI.
        
        Args:
            story: The story text (for backward compatibility) or image prompt
            prompt: Direct image prompt (alternative to story)
            setting: The setting of the story (urban, coastal, etc.)
            parameters: Parameters for image generation (alternative name)
            params: Parameters for image generation  
            save_path: Optional path to save the image(s)
            
        Returns:
            Tuple of (list of image paths, metadata)
        """
        try:
            # Handle parameter alternatives
            if parameters is None:
                parameters = params or ImageParameters()
            
            # Determine the actual prompt to use
            actual_prompt = prompt or story
            if not actual_prompt or not isinstance(actual_prompt, str):
                raise ValueError("Either 'story' or 'prompt' parameter must be provided")
            
            if len(actual_prompt.strip()) < 10:
                raise ValueError("Image prompt too short for meaningful generation")
            
            # Enhance prompt with genre-specific aesthetics
            if parameters.enhance_prompt:
                enhanced_prompt, negative_prompt = self.companion_generator.enhance_prompt_for_genre(
                    base_prompt=actual_prompt,
                    genre=parameters.genre,
                    style=parameters.style,
                    include_negative=parameters.include_negative_prompt
                )
                logger.info(f"Enhanced prompt with {parameters.genre} aesthetics")
            else:
                enhanced_prompt = actual_prompt
                negative_prompt = None
            
            logger.info("Using OpenAI DALL-E 3 for companion image generation.")
            
            # Generate image with AI using enhanced prompt
            image_path = asyncio.run(openai_image_client.generate_image(
                enhanced_prompt,
                output_dir=Path(save_path).parent if save_path else None,
                save_path=Path(save_path) if save_path else None
            ))
            
            # Validate image was generated
            if not image_path:
                raise ValueError("Image generation failed - no image path returned")
            
            metadata = {
                "model": "dall-e-3",
                "style": parameters.style,
                "genre": parameters.genre,
                "original_prompt": actual_prompt,
                "enhanced_prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "setting": setting,
                "timestamp": time.time(),
                "provider": "openai-dall-e-3",
                "enhancement_applied": parameters.enhance_prompt
            }
            
            logger.info(f"Successfully generated companion image: {image_path}")
            return [image_path], metadata
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "operation": "companion_image_generation",
                    "prompt": (actual_prompt[:100] if 'actual_prompt' in locals() and actual_prompt else ""),
                    "setting": setting,
                    "parameters": parameters.__dict__ if parameters and hasattr(parameters, '__dict__') else {},
                    "save_path": save_path
                },
                category=ErrorCategory.RECOVERABLE
            )
            # Re-raise to let decorator handle recovery
            raise
    
    @handle_errors(
        category=ErrorCategory.RECOVERABLE
    )
    def generate_companion_image_with_threading(
        self,
        story_text: str,
        threading_blocks: List[str],
        image_prompt: str,
        genre: str = "solarpunk",
        style: str = "digital-art",
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a companion image and create threading structure for Twitter posting.
        
        Args:
            story_text: The full story text
            threading_blocks: Pre-generated threading blocks
            image_prompt: The image prompt extracted from the story
            genre: The genre for aesthetic enhancement
            style: The artistic style
            save_path: Optional path to save the image
            
        Returns:
            Dictionary with image, threading structure, and metadata
        """
        try:
            # Create image parameters with genre enhancement
            image_params = ImageParameters(
                style=style,
                genre=genre,
                enhance_prompt=True,
                include_negative_prompt=True
            )
            
            # Generate the companion image
            images, image_metadata = self.generate_image(
                prompt=image_prompt,
                parameters=image_params,
                save_path=save_path
            )
            
            # Create threading structure
            threading_structure = self.companion_generator.create_threading_structure(
                story_text=story_text,
                threading_blocks=threading_blocks,
                image_path=images[0] if images else None
            )
            
            # Combine all data
            result = {
                "image_path": images[0] if images else None,
                "image_metadata": image_metadata,
                "threading_structure": threading_structure,
                "genre": genre,
                "style": style,
                "ready_for_twitter": threading_structure["ready_for_posting"]
            }
            
            logger.info("Successfully generated companion image with threading structure")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "operation": "companion_image_with_threading",
                    "story_length": len(story_text),
                    "thread_blocks": len(threading_blocks),
                    "genre": genre,
                    "style": style
                },
                category=ErrorCategory.RECOVERABLE
            )
            raise


@handle_errors(
    category=ErrorCategory.WARNING
)
def create_simple_test(style: str = "digital-art") -> None:
    """Create a simple test to verify the image generation functionality.
    
    This test mirrors the test_google_apis.py implementation to ensure 
    baseline functionality works.
    """
    import os
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    try:
        logger.info("Running simple test with basic prompt...")
        test_prompt = "A solarpunk city with vertical gardens and solar panels"
        if use_openai:
            logger.info("[Test] Using OpenAI DALL-E 3 for simple test.")
            from src.ai_solarpunk.clients import openai_image_client
            import asyncio
            image_path = asyncio.run(openai_image_client.generate_image(test_prompt))
            logger.info(f"[Test] OpenAI image saved to: {image_path}")
            print(f"\nTest image saved to: {image_path}")
            return True
        else:
            # Initialize the image generator
            image_generator = ImageGenerator()
            # Create a visual prompt from the test prompt
            logger.info(f"Generating test image with prompt: '{test_prompt}'")
            
            # Create timestamp-based filename
            timestamp = int(time.time())
            save_path = str(OUTPUT_DIR / f"test_basic_{timestamp}.png")
            
            # Generate image using our centralized error handling
            images, metadata = image_generator.generate_image(
                prompt=test_prompt,
                setting="urban",
                save_path=save_path
            )
            
            logger.info(f"Simple test successful! Image saved to {save_path}")
            print(f"\nTest image saved to: {save_path}")
            return True
            
    except Exception as e:
        error_handler.handle_error(
            e,
            context={
                "operation": "simple_image_test",
                "test_prompt": test_prompt if 'test_prompt' in locals() else ""
            },
            category=ErrorCategory.WARNING
        )
        logger.error(f"Simple test failed with error: {str(e)}")
        return False


@handle_errors(
    category=ErrorCategory.RECOVERABLE
)
def generate_test_images() -> None:
    """Generate test images with various settings and styles."""
    try:
        # Initialize the image generator
        image_generator = ImageGenerator()
        
        # Test settings and styles
        test_configs = [
            {"setting": "urban", "style": "digital-art", "genre": "solarpunk"},
            {"setting": "coastal", "style": "watercolor", "genre": "fantasy"},
            {"setting": "forest", "style": "retro-futurism", "genre": "sci-fi"},
            {"setting": "mountain", "style": "stylized", "genre": "steampunk"}
        ]
        
        for i, config in enumerate(test_configs):
            logger.info(f"Generating test image {i+1}/4: {config}")
            
            # Create a test prompt based on the setting and genre
            test_prompts = {
                "urban": "A futuristic urban landscape with green architecture",
                "coastal": "A mystical coastal scene with magical elements",
                "forest": "A cyberpunk forest with holographic trees",
                "mountain": "A steampunk mountain settlement with brass machinery"
            }
            
            test_prompt = test_prompts[config["setting"]]
            
            # Create timestamp-based filename
            timestamp = int(time.time())
            filename = f"test_{config['setting']}_{config['style']}_{config['genre']}_{timestamp}.png"
            save_path = str(OUTPUT_DIR / filename)
            
            # Create parameters with the test config
            params = ImageParameters(
                style=config["style"],
                genre=config["genre"],
                enhance_prompt=True,
                include_negative_prompt=True
            )
            
            # Generate the image
            images, metadata = image_generator.generate_image(
                prompt=test_prompt,
                setting=config["setting"],
                parameters=params,
                save_path=save_path
            )
            
            logger.info(f"Test image {i+1} saved to: {save_path}")
            print(f"Test image {i+1} ({config['genre']}/{config['style']}) saved to: {save_path}")
            
            # Brief pause between generations
            time.sleep(2)
        
        logger.info("All test images generated successfully!")
        
    except Exception as e:
        error_handler.handle_error(
            e,
            context={
                "operation": "generate_test_images",
                "test_count": len(test_configs) if 'test_configs' in locals() else 0
            },
            category=ErrorCategory.RECOVERABLE
        )
        logger.error(f"Test generation failed: {str(e)}")
        raise


@handle_errors(
    category=ErrorCategory.RECOVERABLE
)
def test_companion_image_generation() -> bool:
    """Test the companion image generation with threading functionality."""
    try:
        logger.info("Testing companion image generation with threading...")
        
        # Sample story and threading blocks
        story_text = """In the heart of Neo-Singapore's vertical gardens, Maya tended to the bioluminescent algae pools that powered her district. The morning mist carried the sweet scent of engineered jasmine, while solar collectors hummed softly on every rooftop. Children played in the canopy walkways above, their laughter echoing through the living architecture. This was the world they had built together—a symphony of nature and technology, where every breath of air was clean and every drop of water was precious. Maya smiled as she watched the city breathe, knowing that today, like every day, they were writing the future with hope."""
        
        threading_blocks = [
            "In the heart of Neo-Singapore's vertical gardens, Maya tended to the bioluminescent algae pools that powered her district. ✨🌱",
            "The morning mist carried the sweet scent of engineered jasmine, while solar collectors hummed softly on every rooftop. 🌸☀️",
            "Children played in the canopy walkways above, their laughter echoing through the living architecture. 👶🌳",
            "This was the world they had built together—a symphony of nature and technology, where every breath of air was clean... 🎵💨",
            "...and every drop of water was precious. Maya smiled as she watched the city breathe, knowing that today... 💧😊",
            "...like every day, they were writing the future with hope. 🌟✍️"
        ]
        
        image_prompt = "Maya tending to bioluminescent algae pools in vertical gardens with solar collectors and living architecture"
        
        # Initialize the image generator
        image_generator = ImageGenerator()
        
        # Create save path
        timestamp = int(time.time())
        save_path = str(OUTPUT_DIR / f"test_companion_{timestamp}.png")
        
        # Test the companion image generation
        result = image_generator.generate_companion_image_with_threading(
            story_text=story_text,
            threading_blocks=threading_blocks,
            image_prompt=image_prompt,
            genre="solarpunk",
            style="digital-art",
            save_path=save_path
        )
        
        # Validate results
        if result["ready_for_twitter"] and result["image_path"]:
            logger.info("✅ Companion image generation test PASSED")
            logger.info(f"  - Image saved: {result['image_path']}")
            logger.info(f"  - Thread blocks: {result['threading_structure']['total_blocks']}")
            logger.info(f"  - Ready for Twitter: {result['ready_for_twitter']}")
            return True
        else:
            logger.error("❌ Companion image generation test FAILED")
            return False
            
    except Exception as e:
        error_handler.handle_error(
            e,
            context={
                "operation": "test_companion_image_generation",
                "story_length": len(story_text) if 'story_text' in locals() else 0
            },
            category=ErrorCategory.RECOVERABLE
        )
        logger.error(f"Companion test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run tests when executed directly
    logger.info("Running image generation tests...")
    
    # Test basic functionality
    logger.info("1. Testing basic image generation...")
    basic_test_result = create_simple_test()
    
    # Test companion image generation
    logger.info("2. Testing companion image generation...")
    companion_test_result = test_companion_image_generation()
    
    # Test multiple configurations
    logger.info("3. Testing multiple genre/style configurations...")
    try:
        generate_test_images()
        multi_test_result = True
    except Exception:
        multi_test_result = False
    
    # Summary
    logger.info("\n=== TEST RESULTS ===")
    logger.info(f"Basic test: {'✅ PASSED' if basic_test_result else '❌ FAILED'}")
    logger.info(f"Companion test: {'✅ PASSED' if companion_test_result else '❌ FAILED'}")
    logger.info(f"Multi-config test: {'✅ PASSED' if multi_test_result else '❌ FAILED'}")
    
    if all([basic_test_result, companion_test_result, multi_test_result]):
        logger.info("🎉 All tests PASSED! Image generation is working correctly.")
    else:
        logger.error("⚠️  Some tests FAILED. Check the logs for details.") 