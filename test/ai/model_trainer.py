#!/usr/bin/env python3
"""
Model Trainer for AI-FinHub
- Generates embeddings for verified knowledge items
- Saves embeddings to knowledge_base.json
- Builds FAISS index for fast similarity search
"""

import os
import json
import numpy as np
import faiss
import config
from .nlp_processor import NLPProcessor

nlp = NLPProcessor()

# --- Helpers ---
def load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Embedding generation ---
def generate_embeddings():
    kb = load_json(config.KNOWLEDGE_FILE)
    updated = False
    for item in kb:
        if item.get("verified", False) and "embedding" not in item:
            item["embedding"] = nlp.get_embedding(item["question"]).tolist()
            updated = True
    if updated:
        save_json(kb, config.KNOWLEDGE_FILE)
        print("Embeddings generated and saved for verified knowledge items.")
    else:
        print("All verified items already have embeddings.")
    return kb

# --- FAISS Index creation ---
def build_faiss_index(kb):
    verified_items = [item for item in kb if item.get("verified", False)]
    if not verified_items:
        print("No verified items to build FAISS index.")
        return None

    embeddings = np.array([item["embedding"] for item in verified_items]).astype('float32')
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, config.FAISS_INDEX_FILE)
    print(f"FAISS index created with {len(verified_items)} items and saved to {config.FAISS_INDEX_FILE}")
    return index

# --- Main ---
if __name__ == "__main__":
    print("=== Generating embeddings and building FAISS index ===")
    kb = generate_embeddings()
    build_faiss_index(kb)
    print("=== Model training / preparation completed ===")
