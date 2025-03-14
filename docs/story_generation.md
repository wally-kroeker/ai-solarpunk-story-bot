# Story Generation Module

This module generates solarpunk micro-stories that fit within X (Twitter) character limits.

## Setup

1. Ensure you have uv installed
2. Create a virtual environment:
   ```bash
   uv venv
   ```
3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

## Running the Example

Generate a tweet-sized solarpunk story:

```bash
uv run examples/generate_tweet.py
```

## Testing

Run the tests with pytest:

```bash
uv run pytest tests/test_story_generator.py
```

## Features

- Generates uplifting solarpunk stories within X character limits (280 chars)
- Customizable themes, settings, and tone
- Content validation to ensure appropriate themes
- Automatic character count management 