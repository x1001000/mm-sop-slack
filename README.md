# MacroMicro SOP Slack Bot

Slack bot that answers SOP questions using Google Gemini AI with FileSearch over our internal documentation.

## How It Works

1. A user mentions the bot or DMs it in Slack
2. The bot receives the message via **Socket Mode** (persistent WebSocket, no public URL needed)
3. It fetches the **system instruction** from a remote URL (so you can update bot behavior without redeploying)
4. It calls **Gemini (gemini-3-flash-preview)** with FileSearch to retrieve relevant SOP documents and generate an answer
5. The response is converted from Markdown to Slack mrkdwn and posted back in the thread

Conversations are thread-based — the bot keeps session history so follow-up questions work naturally.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `SLACK_BOT_TOKEN` | Yes | Slack bot token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | Yes | Slack app-level token (`xapp-...`) for Socket Mode |
| `SYSTEM_PROMPT_URL` | Yes | URL to fetch system instruction text from |
| `GOOGLE_SHEET_WEBAPP_URL` | No | Google Apps Script web app URL for Q&A logging |

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the variables above, then:

```bash
python app.py
```

## Deploying to HF Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space) with **Docker** SDK
2. Upload `Dockerfile`, `app.py`, and `requirements.txt` (or connect the GitHub repo)
3. Add the environment variables as Secrets in Space settings
4. The Space builds and deploys automatically — the bot runs 24/7

## Operational Notes

- **Session TTL:** Sessions expire after 1 hour of inactivity
- **History limit:** 20 messages (10 conversation turns) per session, oldest trimmed first
- **FileSearch store:** The bot looks for a Google AI FileSearch store with `mm-sop` in its name — make sure your store is named accordingly
- **System instruction:** Fetched fresh on every request from `SYSTEM_PROMPT_URL`, so edits take effect immediately
- **Response chunking:** Long responses are split into 3000-character blocks to fit Slack's limits
- **Q&A logging:** If `GOOGLE_SHEET_WEBAPP_URL` is set, each question and answer is logged to a Google Sheet
- **Runtime:** Python 3.11 (see Dockerfile)
- **Dependencies:** python-dotenv, slack-bolt, google-genai, requests
