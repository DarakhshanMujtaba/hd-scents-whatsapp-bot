"""
whatsapp_sender.py

This module contains the function that sends a text message back to a
customer on WhatsApp, using Meta's Graph API (the "send message" call).

This is the counterpart to the webhook in main.py:
  - Webhook (main.py)       -> messages coming IN from the customer
  - send_whatsapp_message() -> messages going OUT to the customer
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# This is the base URL for Meta's Graph API. We use our specific
# Phone Number ID so Meta knows which number should send the reply.
GRAPH_API_URL = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to_phone_number: str, message_text: str) -> dict:
    """
    Sends a plain text WhatsApp message to a given phone number.

    Args:
        to_phone_number: the customer's phone number (as received from
                          the webhook, e.g. "923261402308")
        message_text: the text to send back to them

    Returns:
        The JSON response from Meta's API (useful for debugging).
    """

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    # This is the exact structure Meta expects for a simple text reply.
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(GRAPH_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Message sent successfully to {to_phone_number}")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

    return response.json()