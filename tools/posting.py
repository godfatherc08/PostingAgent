import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

@tool
def post_to_discord(tweet_text: str, image_url: str):
    """
    Post a message with an embedded image to a Discord channel via webhook.

    Args:
        tweet_text: The text content to display in the Discord message.
        image_url: The URL of the image to embed in the message.
    """
    payload = {
        "content": tweet_text,
        "embeds": [
            {
                "image": {
                    "url": image_url
                }
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    response.raise_for_status()
    print(f"[DISCORD] Posted successfully. Status: {response.status_code}")