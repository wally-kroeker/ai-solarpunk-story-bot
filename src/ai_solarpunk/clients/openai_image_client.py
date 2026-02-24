import os
import logging
import asyncio
from typing import Optional
from pathlib import Path

import openai
import base64

logger = logging.getLogger(__name__)

async def generate_image(
    prompt: str,
    model: str = "gpt-image-1",
    api_key: Optional[str] = None,
    timeout: int = 60,
    output_dir: Optional[Path] = None,
    save_path: Optional[Path] = None
) -> Path:
    """Generate an image using OpenAI's GPT Image 1 (DALL-E 3) model and save to disk.

    Args:
        prompt: The prompt to send to the model.
        model: The OpenAI model to use (default: 'dall-e-3').
        api_key: Optional API key (uses env if not provided).
        timeout: Timeout in seconds for the request.
        output_dir: Optional directory to save the image (default: ./output/images)
        save_path: Optional full path to save the image file (overrides output_dir)

    Returns:
        The path to the saved image file.

    Raises:
        Exception: If the API call fails after retries.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")
    openai_client = openai.AsyncOpenAI(api_key=api_key)
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[OpenAI] Sending image prompt to model '{model}': {prompt[:100]}...")
                response = await openai_client.images.generate(
                    model=model,
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    timeout=timeout
                )
                image_b64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_b64)
                if save_path is not None:
                    image_path = Path(save_path)
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_dir = output_dir or Path("output/images")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    image_path = output_dir / f"openai_image_{model}_{os.getpid()}_{int(asyncio.get_event_loop().time())}.png"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                logger.info(f"[OpenAI] Image saved to {image_path}")
                return image_path
            except Exception as e:
                logger.warning(f"[OpenAI] Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    logger.error(f"[OpenAI] All attempts failed.")
                    raise
                await asyncio.sleep(2 ** attempt)
    finally:
        await openai_client.close() 