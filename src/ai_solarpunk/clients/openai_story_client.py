import os
import logging
import asyncio
from typing import Optional, List, Tuple
from pathlib import Path
import re
import json

import openai

logger = logging.getLogger(__name__)

# --- Constants ---
GENERATION_MODEL = "gpt-4o"  # More reliable model for story generation
SELECTION_MODEL = "gpt-4o"   # Same model for consistency and reliability
NUM_CANDIDATES = 10

async def generate_story(
    prompt: str,
    model: str = GENERATION_MODEL,
    api_key: Optional[str] = None,
    timeout: int = 60
) -> str:
    """Generate a single story using a specified OpenAI model.

    Args:
        prompt: The prompt to send to the model.
        model: The OpenAI model to use (default: gpt-4o-mini).
        api_key: Optional API key (uses env if not provided).
        timeout: Timeout in seconds for the request.

    Returns:
        The generated story as a string.

    Raises:
        ValueError: If the API key is not found.
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
                logger.info(f"[OpenAI Story Gen] Sending prompt to model '{model}': {prompt[:100]}...")
                response = await openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=timeout
                )
                if response and response.choices and response.choices[0].message:
                    story = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
                    logger.info(f"[OpenAI Story Gen] Received story ({len(story)} chars) from model '{model}'")
                    return story
                else:
                    logger.warning(f"[OpenAI Story Gen] Invalid response structure received from model '{model}'.")
                    raise ValueError(f"Invalid response structure from model '{model}'.")
            except openai.APIConnectionError as e:
                logger.error(f"[OpenAI Story Gen] Connection error on attempt {attempt}: {e}")
            except openai.RateLimitError as e:
                logger.warning(f"[OpenAI Story Gen] Rate limit exceeded on attempt {attempt}: {e}")
            except openai.APIStatusError as e:
                logger.error(f"[OpenAI Story Gen] API status error on attempt {attempt}: {e.status_code} - {e.response}")
            except Exception as e:
                logger.warning(f"[OpenAI Story Gen] Attempt {attempt} failed with model '{model}': {e}")
            if attempt == max_retries:
                logger.error(f"[OpenAI Story Gen] All {max_retries} attempts failed with model '{model}'.")
                raise Exception(f"Failed to generate story with {model} after {max_retries} attempts.")
            await asyncio.sleep(2 ** attempt)
        return ""
    finally:
        await openai_client.close()

async def generate_story_candidates(
    prompt: str,
    num_candidates: int = NUM_CANDIDATES,
    generation_model: str = GENERATION_MODEL,
    api_key: Optional[str] = None,
    timeout: int = 60
) -> List[str]:
    """Generate multiple story candidates concurrently using the specified generation model.

    Args:
        prompt: The base prompt for story generation.
        num_candidates: The number of stories to generate.
        generation_model: The OpenAI model to use for generating candidates.
        api_key: Optional API key.
        timeout: Timeout for each individual generation request.

    Returns:
        A list of generated story strings. Returns fewer stories if some generations fail.
    """
    logger.info(f"Generating {num_candidates} story candidates using model '{generation_model}'...")
    tasks = [
        generate_story(prompt, model=generation_model, api_key=api_key, timeout=timeout)
        for _ in range(num_candidates)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_stories: List[str] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Candidate generation task {i+1} failed: {result}")
        elif isinstance(result, str):
            successful_stories.append(result)
        else:
            logger.warning(f"Candidate generation task {i+1} returned unexpected type: {type(result)}")

    logger.info(f"Successfully generated {len(successful_stories)} out of {num_candidates} candidates.")
    return successful_stories

async def select_best_story(
    stories: List[str],
    selection_model: str = SELECTION_MODEL,
    api_key: Optional[str] = None,
    timeout: int = 90
) -> Optional[str]:
    """Select the best story from a list of candidates using the specified selection model.

    Args:
        stories: A list of story candidate strings.
        selection_model: The OpenAI model to use for selection (e.g., gpt-4o).
        api_key: Optional API key.
        timeout: Timeout for the selection request.

    Returns:
        The selected story string, or None if selection fails or no valid stories provided.
    """
    if not stories:
        logger.warning("No stories provided for selection.")
        return None

    formatted_stories = "\n\n".join([f"--- STORY {i+1} ---\n{story}" for i, story in enumerate(stories)])

    selection_prompt = (
        "You are an expert editor selecting the best solarpunk micro-story for a Twitter bot. "
        "Review the following story candidates. Select the *single* best story that meets these criteria:\n"
        "1. Genre: Clearly solarpunk - positive, hopeful vision of a sustainable future.\n"
        "2. Plausibility: Technologically and socially plausible within the next ~30 years.\n"
        "3. Engagement: Interesting, evocative, and well-written.\n"
        "4. Conciseness: Fits well within Twitter's character limits (ideally < 280 chars).\n"
        "5. Adherence: Matches the original prompt's setting and primary technology focus (if discernible).\n\n"
        f"Candidates:\n{formatted_stories}\n\n"
        "Based on these criteria, which story is the absolute best? Respond with ONLY the full text of the chosen story, exactly as it appeared in the list above. Do not add any explanation, commentary, or formatting like 'STORY X:' just the raw story text."
    )

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")

    openai_client = openai.AsyncOpenAI(api_key=api_key)
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[OpenAI Story Select] Sending {len(stories)} candidates to model '{selection_model}' for review...")
                response = await openai_client.chat.completions.create(
                    model=selection_model,
                    messages=[{"role": "user", "content": selection_prompt}],
                    timeout=timeout
                )

                if response and response.choices and response.choices[0].message:
                    selected_story = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    if selected_story in stories:
                        logger.info(f"[OpenAI Story Select] Model '{selection_model}' selected story: {selected_story[:100]}...")
                        return selected_story
                    else:
                        logger.warning(f"[OpenAI Story Select] Model '{selection_model}' returned text not matching any candidate. Trying to find closest match...")
                        raise ValueError("Selection response did not match any candidate story.")
                else:
                    logger.warning(f"[OpenAI Story Select] Invalid response structure received from model '{selection_model}'.")
                    raise ValueError(f"Invalid response structure from model '{selection_model}'.")

            except openai.APIConnectionError as e:
                logger.error(f"[OpenAI Story Select] Connection error on attempt {attempt}: {e}")
            except openai.RateLimitError as e:
                logger.warning(f"[OpenAI Story Select] Rate limit exceeded on attempt {attempt}: {e}")
            except openai.APIStatusError as e:
                logger.error(f"[OpenAI Story Select] API status error on attempt {attempt}: {e.status_code} - {e.response}")
            except Exception as e:
                logger.warning(f"[OpenAI Story Select] Attempt {attempt} failed with model '{selection_model}': {e}")

            if attempt == max_retries:
                logger.error(f"[OpenAI Story Select] All {max_retries} attempts failed with model '{selection_model}'.")
                return None
            await asyncio.sleep(2 ** attempt)

        return None
    finally:
        await openai_client.close()

async def select_best_story_with_reasons(
    stories: List[str],
    selection_model: str = SELECTION_MODEL,
    api_key: Optional[str] = None,
    timeout: int = 90
) -> Optional[Tuple[str, str, int]]:
    """Select the best story from a list of candidates using the specified model, returning story, reasons and index.

    Args:
        stories: A list of story candidate strings.
        selection_model: The OpenAI model to use for selection (e.g., o3).
        api_key: Optional API key.
        timeout: Timeout for the selection request.

    Returns:
        A tuple containing (selected story, selection reasons, selected index),
        or None if selection fails or no valid stories provided.
    """
    if not stories:
        logger.warning("No stories provided for selection.")
        return None

    # Format stories for the prompt
    formatted_stories = "\n\n".join([f"--- STORY {i+1} ---\n{story}" for i, story in enumerate(stories)])

    selection_prompt = (
        "You are an expert editor selecting the best solarpunk micro-story for a Twitter bot. "
        "Review the following story candidates. Select the *single* best story that meets these criteria:\n"
        "1. Genre: Clearly solarpunk - positive, hopeful vision of a sustainable future.\n"
        "2. Plausibility: Technologically and socially plausible within the next ~30 years.\n"
        "3. Engagement: Interesting, evocative, and well-written.\n"
        "4. Conciseness: Fits well within Twitter's character limits (ideally < 280 chars).\n"
        "5. Adherence: Matches the original prompt's setting and primary technology focus (if discernible).\n\n"
        f"Candidates:\n{formatted_stories}\n\n"
        "Your response must be formatted as JSON with these fields:\n"
        "1. 'selected_story_number': The number of the story you selected (e.g., 1 for STORY 1)\n"
        "2. 'reasons': A detailed explanation of why you selected this story and how it meets the criteria\n\n"
        "Respond with VALID JSON only, no other text."
    )

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")

    openai_client = openai.AsyncOpenAI(api_key=api_key)
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[OpenAI Story Select] Sending {len(stories)} candidates to model '{selection_model}' for review with reasons...")
                response = await openai_client.chat.completions.create(
                    model=selection_model,
                    messages=[{"role": "user", "content": selection_prompt}],
                    timeout=timeout,
                    response_format={"type": "json_object"}  # Ensure we get a valid JSON response
                )

                if response and response.choices and response.choices[0].message:
                    response_content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    # Try to parse the JSON response
                    try:
                        result = json.loads(response_content)
                        selected_story_number = result.get("selected_story_number", 0)
                        reasons = result.get("reasons", "No reasons provided")
                        
                        # Convert to 0-based index and validate
                        selected_index = selected_story_number - 1
                        if 0 <= selected_index < len(stories):
                            selected_story = stories[selected_index]
                            logger.info(f"[OpenAI Story Select] Model '{selection_model}' selected story #{selected_story_number}")
                            return selected_story, reasons, selected_index
                        else:
                            logger.warning(f"[OpenAI Story Select] Invalid story number: {selected_story_number}")
                            raise ValueError(f"Invalid story number: {selected_story_number}")
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(f"[OpenAI Story Select] Error parsing response: {e}")
                        logger.debug(f"Response content: {response_content}")
                        raise ValueError(f"Invalid JSON response: {e}")
                else:
                    logger.warning(f"[OpenAI Story Select] Invalid response structure received from model '{selection_model}'.")
                    raise ValueError(f"Invalid response structure from model '{selection_model}'.")

            except openai.APIConnectionError as e:
                logger.error(f"[OpenAI Story Select] Connection error on attempt {attempt}: {e}")
            except openai.RateLimitError as e:
                logger.warning(f"[OpenAI Story Select] Rate limit exceeded on attempt {attempt}: {e}")
            except openai.APIStatusError as e:
                logger.error(f"[OpenAI Story Select] API status error on attempt {attempt}: {e.status_code} - {e.response}")
            except Exception as e:
                logger.warning(f"[OpenAI Story Select] Attempt {attempt} failed with model '{selection_model}': {e}")

            if attempt == max_retries:
                logger.error(f"[OpenAI Story Select] All {max_retries} attempts failed with model '{selection_model}'.")
                return None
            await asyncio.sleep(2 ** attempt)

        return None
    finally:
        await openai_client.close()

# Remove the old rating function
# async def openai_rate_story(prompt: str, model: str = "o3") -> int:
#     ... (rest of the old function) ... 