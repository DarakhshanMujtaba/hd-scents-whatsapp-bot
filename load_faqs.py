"""
load_faqs.py

This script reads all .txt files inside the data/ folder
and stores them in ChromaDB (vector database).

Run this once (or whenever you update the FAQs).
Usage: python load_faqs.py
"""

import os
import chromadb

# Step 1: Create a ChromaDB client. The path tells ChromaDB where
# to persist data on disk, so we don't need to reload everything
# every time the server restarts.
client = chromadb.PersistentClient(path="./chroma_db")

# Step 2: Create a collection — think of this as a table that will
# hold all the FAQ entries. get_or_create_collection avoids errors
# if the collection already exists from a previous run.
collection = client.get_or_create_collection(name="hd_scents_faqs")

# Step 3: Get the list of all .txt files inside the data/ folder
data_folder = "./data"
faq_files = [f for f in os.listdir(data_folder) if f.endswith(".txt")]

print(f"Found {len(faq_files)} FAQ files. Loading into ChromaDB...")

# Step 4: Read each file and prepare it for insertion
documents = []
ids = []

for filename in faq_files:
    filepath = os.path.join(data_folder, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    documents.append(content)
    # Each document needs a unique ID — we use the filename itself
    ids.append(filename.replace(".txt", ""))

# Step 5: Add all documents to the collection in one call.
# ChromaDB automatically converts each document into an embedding
# (a vector of numbers representing its meaning) behind the scenes.
collection.add(
    documents=documents,
    ids=ids
)

print("Done! All FAQs have been loaded into ChromaDB.")
print(f"Total entries: {collection.count()}")