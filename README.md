---
title: Mm Sop Slack
emoji: 👁
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# MacroMicro SOP Slack Bot

A Slack bot that answers questions about MacroMicro internal Standard Operating Procedures using Google Gemini AI with FileSearch.

## Features

- Session-based conversation history
- Thread-based Slack conversations
- Real-time streaming responses
- Google Gemini AI with FileSearch integration

## Deployment on Hugging Face Spaces

### Prerequisites

1. A Hugging Face account
2. Your Slack bot tokens (Bot Token and App Token)
3. Your Google Gemini API key
4. A Google AI FileSearch store with your SOP documents

### Deployment Steps

1. **Create a new Space on Hugging Face:**
   - Go to https://huggingface.co/new-space
   - Choose a name for your Space
   - Select "Docker" as the SDK
   - Set visibility (Private recommended for internal bots)

2. **Upload your files:**
   - Upload `Dockerfile`, `app.py`, and `requirements.txt`
   - Or connect your GitHub repository

3. **Configure Environment Variables:**
   - Go to your Space's Settings
   - Add the following secrets:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `SLACK_APP_TOKEN`: Your Slack App Token (starts with `xapp-`)
     - `SLACK_BOT_TOKEN`: Your Slack Bot Token (starts with `xoxb-`)

4. **Build and Deploy:**
   - The Space will automatically build and deploy
   - Check the logs to ensure the bot starts successfully
   - Your bot will run 24/7 on HF Spaces

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
# GEMINI_API_KEY=your_key_here
# SLACK_APP_TOKEN=xapp-...
# SLACK_BOT_TOKEN=xoxb-...

# Run the bot
python app.py
```

## Important Notes

- This bot uses Socket Mode, which maintains a persistent WebSocket connection to Slack
- The FileSearch store must be pre-configured in Google AI Studio
- Session histories are stored in memory and will reset on restart
- For production use, consider adding persistent storage for conversation history
