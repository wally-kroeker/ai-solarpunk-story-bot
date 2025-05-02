import os
import logging
import asyncio
from typing import Optional
from pathlib import Path
import re

import openai

logger = logging.getLogger(__name__)

async def generate_story(
    prompt: str,
    model: str = "o3",
    api_key: Optional[str] = None,
    timeout: int = 60
) -> str:
    """Generate a story using OpenAI's o3 model.

    Args:
        prompt: The prompt to send to the model.
        model: The OpenAI model to use (default: 'o3').
        api_key: Optional API key (uses env if not provided).
        timeout: Timeout in seconds for the request.

    Returns:
        The generated story as a string.

    Raises:
        Exception: If the API call fails after retries.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")
    openai_client = openai.AsyncOpenAI(api_key=api_key)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[OpenAI] Sending prompt to model '{model}': {prompt[:100]}...")
            response = await openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout
            )
            story = response.choices[0].message.content.strip()
            logger.info(f"[OpenAI] Received story ({len(story)} chars)")
            return story
        except Exception as e:
            logger.warning(f"[OpenAI] Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error(f"[OpenAI] All attempts failed.")
                raise
            await asyncio.sleep(2 ** attempt) 

async def openai_rate_story(prompt: str, model: str = "o3") -> int:
    """Get a numeric rating from OpenAI based on a prompt."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set.")
    openai_client = openai.AsyncOpenAI(api_key=api_key)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[OpenAI Rating] Sending prompt to model '{model}': {prompt[:100]}...")
            response = await openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=30
            )
            content = response.choices[0].message.content.strip()
            # Extract the first integer found
            match = re.search(r'\d+', content)
            if match:
                rating = int(match.group(0))
                logger.info(f"[OpenAI Rating] Received rating: {rating}")
                return rating
            else:
                logger.warning(f"[OpenAI Rating] Could not extract integer from response: {content}")
                raise ValueError("No integer rating found in LLM response")
        except Exception as e:
            logger.warning(f"[OpenAI Rating] Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error(f"[OpenAI Rating] All rating attempts failed.")
                raise
            await asyncio.sleep(2 ** attempt)
    return 1 # Default to lowest score if all retries fail 