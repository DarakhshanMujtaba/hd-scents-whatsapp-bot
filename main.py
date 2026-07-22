"""
main.py

This is the FastAPI server that acts as the "letterbox" for WhatsApp.
It has two endpoints:
  - GET /webhook  -> handles Meta's one-time verification handshake
  - POST /webhook -> receives actual incoming WhatsApp messages

The POST endpoint runs the message through our RAG function and sends
the generated answer back to the customer via the WhatsApp Cloud API.

Run this server with: uvicorn main:app --reload --port 8080
"""

import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from rag_query import get_answer
from whatsapp_sender import send_whatsapp_message

load_dotenv()

app = FastAPI()

# This is a secret string YOU choose yourself (set in .env as
# WHATSAPP_VERIFY_TOKEN). Meta will send it back to us during
# verification, and we check it matches to confirm the request
# really came from Meta's setup process, not someone else.
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@app.get("/webhook")
def verify_webhook(request: Request):
    """
    Meta calls this once, when you first set up the webhook in the
    Meta for Developers dashboard, to confirm you own this server.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        # Correct token -> confirm by echoing back the challenge value
        return int(challenge)

    # Wrong token -> reject
    return {"error": "Verification failed"}, 403


@app.post("/webhook")
async def receive_message(request: Request):
    """
    Meta calls this every time a customer sends a WhatsApp message
    to our business number. We extract the message text and phone
    number, generate an answer using our RAG pipeline, and send it
    back to the customer on WhatsApp.
    """
    body = await request.json()

    try:
        # This is the structure Meta uses to wrap incoming messages.
        # We're digging into the JSON to find the actual message text
        # and the sender's phone number.
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # If there's no "messages" key, this webhook call is something
        # else (like a delivery/read status update) - we just ignore it.
        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        sender_phone = message["from"]
        user_text = message["text"]["body"]

        print(f"Message from {sender_phone}: {user_text}")

        # Run the message through our RAG pipeline from Step 3
        answer = get_answer(user_text)

        print(f"Generated answer: {answer}")

        # Send the generated answer back to the customer on WhatsApp
        send_whatsapp_message(sender_phone, answer)

        return {"status": "received"}

    except (KeyError, IndexError) as e:
        print(f"Could not parse incoming webhook payload: {e}")
        return {"status": "error"}