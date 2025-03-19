# AI Solarpunk Story Bot

An AI-powered Twitter bot that generates and posts solarpunk micro-stories with AI-generated images. The bot uses Gemini Pro for story generation and Imagen for creating visually stunning artwork that matches each story's theme.

## Features

- 🤖 AI-powered story generation using Gemini Pro
- 🎨 AI image generation using Imagen
- 🐦 Automated Twitter posting
- ⏰ Systemd-based scheduling with timezone support
- 🎯 Multiple settings and art styles
- 📊 Comprehensive logging and monitoring
- 🔄 Interactive management interface

## Prerequisites

- Python 3.10 or higher
- UV package manager
- Systemd (for service management)
- Google Cloud Platform account with Vertex AI access
- Twitter Developer account with API v2 access

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-solarpunk-story-bot.git
   cd ai-solarpunk-story-bot
   ```

2. Create and activate a virtual environment using UV:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Set up configuration:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and settings
   ```

5. Install the systemd service:
   ```bash
   sudo cp systemd/ai-solarpunk-story.service /etc/systemd/system/
   sudo cp systemd/ai-solarpunk-story.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

## Usage

### Bot Manager Interface

The easiest way to manage the bot is through the interactive bot-manager script:

```bash
./bot-manager.sh
```

This provides a comprehensive interface for:
- Generating test posts
- Managing the posting schedule
- Monitoring service status
- Viewing logs
- Running manual tests

### Service Management

The bot runs as a systemd service for reliable scheduling:

1. Enable the service:
   ```bash
   sudo systemctl enable ai-solarpunk-story.timer
   ```

2. Start the service:
   ```bash
   sudo systemctl start ai-solarpunk-story.timer
   ```

3. Check status:
   ```bash
   sudo systemctl status ai-solarpunk-story.service
   ```

### Available Settings

#### Story Settings
- urban: Modern city environments
- coastal: Seaside and ocean themes
- forest: Woodland and forest settings
- desert: Arid and desert landscapes
- rural: Countryside and farming
- mountain: Mountain and alpine settings
- arctic: Polar and ice regions
- island: Island and tropical settings

#### Art Styles
- digital-art: Modern digital illustration
- watercolor: Watercolor painting style
- stylized: Stylized artistic rendering
- solarpunk-nouveau: Art nouveau inspired
- retro-futurism: Retro-futuristic aesthetic
- isometric: Isometric illustration style

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Optional Settings
UV_HTTP_TIMEOUT=300
```

### Timezone Configuration

The bot supports timezone-aware scheduling:
1. Set your timezone through the bot manager
2. Schedule posts in your local time
3. The system automatically handles DST adjustments

## Known Issues

1. Preview generation in the bot manager needs improvement
2. Image display functionality may not work in all environments
3. Some UI/UX elements need refinement

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Cloud Platform for AI services
- Twitter for API access
- The solarpunk community for inspiration

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

4. **Set up the systemd service:**
   ```bash
   # Copy service files
   sudo cp systemd/ai-solarpunk-story.service /etc/systemd/system/
   sudo cp systemd/ai-solarpunk-story.timer /etc/systemd/system/

   # Reload systemd
   sudo systemctl daemon-reload

   # Enable and start the timer
   sudo systemctl enable --now ai-solarpunk-story.timer
   ```

## Service Management

The bot now uses systemd for reliable scheduling and service management. A comprehensive management interface is provided through the `bot-manager.sh` script.

### Using bot-manager.sh

The bot-manager.sh script provides a user-friendly interface for managing all aspects of the bot:

```bash
./bot-manager.sh
```

This launches an interactive menu with the following options:

1. **Generate Preview**
   - Test story and image generation without posting
   - Choose from different settings and styles
   - Preview how posts will look

2. **Check Service Status**
   - View current service state
   - Check if timer is active
   - See when next post is scheduled
   - View recent service logs

3. **Manage Schedule**
   - View current schedule
   - Change posting time (with timezone support)
   - Enable/disable service
   - Change timezone settings

4. **Test Service**
   - Run the service manually
   - Watch live log output
   - Verify functionality

5. **View Logs**
   - View recent log entries
   - Check today's activity
   - Follow logs in real-time
   - Access detailed script output

6. **Run Service Now**
   - Trigger an immediate post
   - Choose custom settings
   - Test full functionality

### Timezone Support

The scheduling system includes comprehensive timezone support:
- Automatic detection of local timezone
- Support for Daylight Saving Time
- Clear display of both local and UTC times
- Easy timezone selection interface

### Scheduling Posts

To schedule posts, use the bot-manager.sh script:

1. Launch the script:
   ```bash
   ./bot-manager.sh
   ```

2. Select "Manage Schedule" (Option 3)

3. Choose your timezone if not already set

4. Select "Change posting time" and enter your desired local time

The service will automatically:
- Convert times to UTC for consistent scheduling
- Handle Daylight Saving Time transitions
- Maintain the schedule across system restarts

### Monitoring and Maintenance

To monitor the bot's operation:

1. Check current status:
   ```bash
   ./bot-manager.sh
   # Select Option 2 (Check Service Status)
   ```

2. View logs:
   ```bash
   ./bot-manager.sh
   # Select Option 5 (View Logs)
   ```

3. Test functionality:
   ```bash
   ./bot-manager.sh
   # Select Option 4 (Test Service)
   ```

### Service Configuration

The systemd service is configured for:
- Automatic startup on system boot
- Proper dependency handling
- Logging to both systemd journal and dedicated log files
- Automatic restart on failure
- Environment variable management

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

### Using the Bot Manager (Recommended)

The easiest way to manage the bot is through the interactive bot-manager script:

```bash
./bot-manager.sh
```

This provides a comprehensive interface for:
- Generating test posts
- Managing the posting schedule
- Monitoring service status
- Viewing logs
- Running manual tests

### Generating Test Posts

To create a test post without publishing:

1. Launch bot-manager:
   ```bash
   ./bot-manager.sh
   ```

2. Select "Generate Preview" (Option 1)

3. Choose your desired setting and style

The preview will show you exactly how the post would look on Twitter.

### Manual Post Generation

To trigger an immediate post:

1. Launch bot-manager:
   ```bash
   ./bot-manager.sh
   ```

2. Select "Run Service Now" (Option 6)

3. Choose between:
   - Default settings (random selection)
   - Custom settings (choose specific setting/style)

### Available Settings and Styles

#### Settings
- urban
- coastal
- forest
- desert
- rural
- mountain
- arctic
- island

#### Image Styles
- digital-art (digital art illustration style)
- watercolor (watercolor painting style)
- stylized (stylized art)
- solarpunk-nouveau (art nouveau inspired)
- retro-futurism (retro-futuristic style)
- isometric (isometric illustration style)

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



