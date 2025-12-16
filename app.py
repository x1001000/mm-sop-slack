from dotenv import load_dotenv
load_dotenv()

import os
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Session config
MAX_HISTORY_LENGTH = 20  # Keep last 20 messages (10 conversation turns)
SESSION_TTL_SECONDS = 3600  # Remove sessions inactive for 1 hour

# Session-based history storage: {session_id: {"history": [...], "last_access": timestamp}}
session_histories = {}

def cleanup_old_sessions():
    """Remove sessions that haven't been accessed within SESSION_TTL_SECONDS."""
    current_time = time.time()
    expired_sessions = [
        sid for sid, data in session_histories.items()
        if current_time - data["last_access"] > SESSION_TTL_SECONDS
    ]
    for sid in expired_sessions:
        del session_histories[sid]
    if expired_sessions:
        print(f"[INFO] Cleaned up {len(expired_sessions)} expired sessions")

@app.message()
def message_hello(message, say):
    # Cleanup old sessions on each request (lazy cleanup)
    cleanup_old_sessions()

    # Extract session identifier using thread_ts or create new session with channel+ts
    session_id = message.get("thread_ts") or f"{message['channel']}_{message['ts']}"

    # Get or initialize history for this session
    if session_id not in session_histories:
        print(f"[INFO] Creating new session for {session_id}")
        session_histories[session_id] = {"history": [], "last_access": time.time()}

    session = session_histories[session_id]
    session["last_access"] = time.time()
    history = session["history"]
    user_message = message["text"]

    print(f"[INFO] Session {session_id} has {len(history)} messages in history")

    # Generate answer with session history
    response_text = answer(message=user_message, history=history)

    # Update history with user message and model response
    history.append({"role": "user", "content": user_message})
    history.append({"role": "model", "content": response_text})

    # Trim history to keep only the last MAX_HISTORY_LENGTH messages
    if len(history) > MAX_HISTORY_LENGTH:
        session["history"] = history[-MAX_HISTORY_LENGTH:]
        print(f"[INFO] Trimmed history to {MAX_HISTORY_LENGTH} messages")

    # say() sends a message to the channel where the event was triggered
    # Use the original message's thread_ts if it exists, otherwise use the message's ts to start a new thread
    thread_ts = message.get("thread_ts") or message["ts"]

    # Slack has a 3000 character limit for text in blocks
    # If response is too long, split it into multiple blocks or send as plain text
    MAX_BLOCK_LENGTH = 3000

    if len(response_text) <= MAX_BLOCK_LENGTH:
        # Response fits in a single block
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": response_text},
                }
            ],
            text=response_text,
            thread_ts=thread_ts
        )
    else:
        # Response is too long, split into multiple blocks
        blocks = []
        remaining_text = response_text

        while remaining_text:
            # Take up to MAX_BLOCK_LENGTH characters
            chunk = remaining_text[:MAX_BLOCK_LENGTH]
            remaining_text = remaining_text[MAX_BLOCK_LENGTH:]

            # Add block for this chunk
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": chunk}
            })

        say(
            blocks=blocks,
            text=response_text[:MAX_BLOCK_LENGTH] + "..." if len(response_text) > MAX_BLOCK_LENGTH else response_text,
            thread_ts=thread_ts
        )

from google import genai
from google.genai import types
client = genai.Client()

def answer(message: str, history: list[dict]) -> str:
    """Answer questions about MacroMicro internal Standard Operating Procedures (SOP).

    Uses FileSearch to retrieve relevant information from the SOP documentation
    and provides detailed answers to help team members understand workflows and procedures.

    Args:
        message: The current input message from the user.
        history: Chat history as list of dicts with "role" and "content" keys.

    Returns:
        The answer as a string.
    """
    # Convert history to Gemini API format
    gemini_contents = []
    for msg in history:
        if msg["role"] == "user":
            gemini_contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "model":
            gemini_contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    # Add current message
    gemini_contents.append({"role": "user", "parts": [{"text": message}]})

    print(f"Q: {message[:50]}")

    # Generate the response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction="你的任務：依據FileSearch工具檢索到的資料，詳細回答MacroMicro團隊內部標準作業流程（SOP）相關問題",
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[client.file_search_stores.list()[-1].name]
                    )
                )
            ]
        )
    )

    print(f"A: {response.text[:50] if response.text else response.text}")
    return response.text or ""

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()