from dotenv import load_dotenv
load_dotenv()

import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message()
def message_hello(question, say):
    ans = answer(message=question, history=[])
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ans},
            }
        ],
        text=ans,
    )

from google import genai
from google.genai import types
client = genai.Client()

# Get the file search store
file_search_stores = client.file_search_stores.list()
if not file_search_stores:
    raise ValueError("No file search stores found. Please create one in the Google AI Studio.")
file_search_store = file_search_stores[0]

def answer(message: str, history: list[dict]):
    """Answer questions about MacroMicro internal Standard Operating Procedures (SOP).

    Uses FileSearch to retrieve relevant information from the SOP documentation
    and provides detailed answers to help team members understand workflows and procedures.

    Args:
        message: The current input message from the user.
        history: Chat history in Gradio messages format.

    Yields:
        A stream of strings with the answer.
    """
    # Convert Gradio messages format to Gemini API format
    gemini_contents = []
    for msg in history:
        if msg["role"] == "user":
            gemini_contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            gemini_contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
    gemini_contents.append({"role": "user", "parts": [{"text": message}]})

    # Stream the response for better UX
    response_stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction="你的任務：依據FileSearch工具檢索到的資料，詳細回答MacroMicro團隊內部標準作業流程（SOP）相關問題",
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_search_store.name]
                    )
                )
            ]
        )
    )

    # Stream response chunks as they arrive
    for chunk in response_stream:
        try:
            if chunk.text:
                yield chunk.text
        except ValueError:
            # This error is expected if the chunk contains a function call instead of text.
            # The Gemini API handles the tool call automatically; we just need to ignore this chunk.
            print("Ignoring chunk with function call.")
            continue

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()