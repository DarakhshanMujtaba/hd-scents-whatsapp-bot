"""
rag_query.py

This module contains the core RAG logic:
1. Take a customer's question.
2. Retrieve the most relevant FAQ entry from ChromaDB.
3. Pass that FAQ as context to Groq's Llama 3.3 model to generate
   a natural-sounding answer.

This will later be called from the FastAPI webhook (Step 4) whenever
a new WhatsApp message comes in.
"""

import os
import chromadb
from groq import Groq
from dotenv import load_dotenv
# Load environment variables from the .env file (e.g. GROQ_API_KEY)
load_dotenv()
# Connect to the same ChromaDB we created in load_faqs.py
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="hd_scents_faqs")
# Set up the Groq client using the API key from .env
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_answer(user_question: str) -> str:
    """
    Given a customer's question, retrieve the most relevant FAQ
    and generate a natural-language answer using Groq's Llama 3.3.
    """

    # Step 1: Retrieve the top matching FAQ entry from ChromaDB.
    # n_results=2 means we grab the top 2 most relevant entries,
    # in case the answer needs info from more than one FAQ.
    results = collection.query(
        query_texts=[user_question],
        n_results=2
    )

    retrieved_docs = results["documents"][0]
    context = "\n\n".join(retrieved_docs)

    # Step 2: Build the prompt for the LLM. We give it the retrieved
    # FAQ context and tell it to answer ONLY based on that context,
    # so it doesn't make up information that isn't in our FAQs.
    system_prompt = (
        "You are a friendly customer support assistant for H&D Scents, "
        "a perfume business based in Karachi, Pakistan. "
        "Answer the customer's question using ONLY the context provided below. "
        "Keep answers short, warm, and conversational, like a WhatsApp reply. "
        "If the context does not contain the answer, say you don't have that "
        "information and suggest the customer wait for a human team member.\n\n"
        f"Context:\n{context}"
    )

    # Step 3: Call Groq's Llama 3.3 70B model to generate the final answer
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content

# Quick manual test - only runs if you execute this file directly
if __name__ == "__main__":
    test_question = "Do you deliver outside Karachi?"
    print(f"Question: {test_question}")
    print(f"Answer: {get_answer(test_question)}")