# AI Solarpunk Story Twitter Bot

An automated Twitter bot that generates and posts solarpunk micro-stories with accompanying AI-generated images. The bot creates positive narratives about sustainable futures and visualizes them with beautiful imagery.

## Project Overview

This bot combines several AI technologies to:
1. Generate solarpunk-themed micro-stories using Gemini Pro
2. Create matching imagery using Imagen 2
3. Post the stories and images to Twitter automatically

## Requirements

- Python 3.10 or higher
- Twitter Developer Account with API keys
- Google Cloud Platform account with Vertex AI (Gemini Pro and Imagen) enabled
- Service account credentials for Google Cloud

## Prerequisites
- Twitter Developer Account (Elevated access required)
- Google Cloud account with Gemini Pro and Imagen API access
- Approximately 250 API calls per month (for daily posts)

## Quick Start
1. Clone the repository
2. Run `uv venv && source .venv/bin/activate`
3. Run `uv pip install -e .`
4. Copy `.env.template` to `.env` and add your API keys
5. Run `./run.sh run-unified random` to generate and post your first story

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wally-kroeker/ai-solarpunk-story-bot.git
   cd ai-solarpunk-story-bot
   ```

2. **Set up a virtual environment:**
   ```bash
   # Using uv (recommended)
   uv venv

   # Alternatively, using standard venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install -e .

   # Alternatively, using pip
   pip install -e .
   ```

## API Setup

### Twitter API
1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a new Project and App
3. Generate API keys, API secrets, access token, and access token secret
4. Copy these credentials to a `.env` file (use `.env.template` as a guide)

### Google Cloud / Vertex AI
1. Create a Google Cloud Platform account
2. Create a new project
3. Enable Vertex AI API
4. Create a service account with Vertex AI User role
5. Download the service account JSON key
6. Place the key in the `credentials/` directory
7. Update `config/config.yaml` with the path to your credentials

## Configuration

1. **Environment Variables:**
   Copy `.env.template` to `.env` and fill in your Twitter API credentials:
   ```
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

2. **Configuration File:**
   Update `config/config.yaml` with your specific settings. Here's an example configuration:

   ```yaml
   # Twitter Bot Configuration
   
   # API Configuration
   api:
     google_cloud:
       credentials_path: "credentials/gcp-credentials.json"
       project_id: "your-gcp-project-id"
     twitter:
       api_version: "2"
       rate_limit:
         max_requests: 50
         time_window: 900  # 15 minutes in seconds
   
   # Story Generation
   story:
     max_length: 280  # Twitter character limit
   
   # Image Generation
   image:
     size: "1024x1024"
     style_presets:
       - photographic
       - digital-art
       - watercolor
   
   # Logging
   logging:
     level: "INFO"
     file: "logs/bot.log"
     max_size: 10485760  # 10MB
     backup_count: 5
   ```

## Core Modules

The bot consists of four main Python modules that work together:

### `src/story_generator.py`
The primary story generation module that creates solarpunk micro-stories based on different environmental settings.

**Features:**
- Multiple environment settings with tailored prompts
- Character-focused narrative generation
- X/Twitter character limit compliance (280 characters)
- Comprehensive error handling and retries

### `src/image_generator.py`
Creates AI-generated images that match the story themes using Imagen 2.

**Features:**
- Customizable artistic styles (photographic, digital-art, watercolor)
- Environment-specific visual prompts
- Image validation and metadata tracking
- Image storage and organization

### `src/twitter_client.py`
Manages Twitter API integration for posting stories and images.

**Features:**
- Twitter API v2 integration using Tweepy and OAuth1
- Media upload capabilities
- Rate limit handling
- Tweet posting, deletion, and retrieval
- Error handling and logging

### `src/ai_story_tweet_generator.py`
A unified script that handles the complete generation and posting flow.

**Features:**
- Randomly selects a setting for each story
- Generates a solarpunk micro-story using `story_generator.py`
- Uses AI to extract key visual elements from the story
- Creates an optimized image prompt based on the story content
- Generates a digital art image based on the AI-derived prompt using `image_generator.py`
- Posts both the story and image to Twitter using `twitter_client.py`

## Usage

### Using the Unified Flow (Recommended)

The simplest way to generate and post stories is using the unified flow:

```bash
./run.sh run-unified [setting]
```

This command will:
1. Select a setting (randomly if not specified)
2. Generate a solarpunk micro-story
3. Use AI to analyze the story and create an image prompt
4. Generate a digital art image based on that prompt
5. Post the story and image to Twitter

Example:
```bash
./run.sh run-unified coastal
```

### Generating a Complete Post

To create a new post with both a story and an image, run:

```bash
./run.sh run-unified random
```

This orchestrates the full process:
1. Generates a solarpunk micro-story with a random setting
2. Extracts key visual elements from the story text
3. Creates an image from those elements using digital art style
4. Posts both the story and image to Twitter

You can specify a setting instead of "random":
```bash
./run.sh run-unified urban     # Urban setting
./run.sh run-unified coastal   # Coastal setting 
./run.sh run-unified forest    # Forest setting
```

The process takes around 1-2 minutes to complete, primarily due to image generation time.

### Scheduling Automated Posts

Set up the bot to post automatically:

```bash
./run.sh schedule daily 14:00  # Posts daily at 2:00 PM
```

This will use the unified flow for all scheduled posts.

### Traditional Flow (Individual Components)

You can still use the individual components if needed:

```bash
./run.sh generate-story urban
./run.sh generate-image urban digital-art
./run.sh post story_generation image
```

## Available Settings and Styles

### Settings
- urban
- coastal
- forest
- desert
- rural
- mountain
- arctic
- island

### Image Styles
- photographic (realistic photography style)
- digital-art (digital art illustration style)
- watercolor (watercolor painting style)

## Example Output

![Example Tweet](https://pbs.twimg.com/media/1900570946718625793.jpg)

*Example tweet: "Salt air, tinged with blooming kelp, filled Maya's lungs. The community aquaponics system, usually humming with AI efficiency, had gone quiet. "Power fluctuation," the AI chirped, "rerouting solar now." Lights flickered, then steadied."*

## Troubleshooting

### Twitter API Issues
- Ensure your API keys are correct and have the appropriate permissions
- Check if your Twitter developer account has proper access level
- For 401 errors, regenerate your tokens
- Rate limits: The bot includes retry mechanisms for rate limits

### Google Cloud API Issues
- Verify your service account has the correct permissions
- Check if Vertex AI APIs are enabled in your Google Cloud project
- Ensure your credentials file is correctly referenced in config.yaml

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Gemini Pro by Google for AI story generation
- Imagen 2 by Google for image generation
- Tweepy and requests-oauthlib for Twitter API integration



