import os
import json
import argparse
import numpy as np
import faiss
import config
from ai.nlp_processor import NLPProcessor
from ai.model_trainer import generate_embeddings, build_faiss_index

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

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

# --- QA functions ---
def ask_question(query):
    kb = load_json(config.KNOWLEDGE_FILE)
    verified_items = [item for item in kb if item.get("verified", False)]
    if not verified_items:
        print("Knowledge base bo'sh yoki verified ma'lumot yo'q.")
        return

    embeddings = np.array([item["embedding"] for item in verified_items]).astype('float32')
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    query_emb = nlp.get_embedding(query).astype('float32')
    D, I = index.search(np.array([query_emb]), config.MAX_RESULTS)

    if D[0][0] >= config.SIMILARITY_THRESHOLD:
        for rank, idx in enumerate(I[0]):
            print(f"{rank+1}. Domain: {verified_items[idx]['domain']}, Language: {verified_items[idx]['language']}")
            print(f"   Question: {verified_items[idx]['question']}")
            print(f"   Answer: {verified_items[idx]['answer']}")
            print(f"   Similarity: {D[0][rank]:.3f}\n")
    else:
        print("Mos javob topilmadi. Iltimos, savolni qayta tekshiring yoki yangi ma'lumot qo'shing.")

def add_user_submission(domain, question, answer, language="uz", added_by="user"):
    submission = {
        "domain": domain,
        "question": question,
        "answer": answer,
        "keywords": question.lower().split(),
        "language": language,
        "added_by": added_by,
        "verified": False
    }
    submissions = load_json(config.USER_SUBMISSIONS_FILE)
    submissions.append(submission)
    save_json(submissions, config.USER_SUBMISSIONS_FILE)
    print("Ma'lumot qo'shildi. Admin tekshiruvini kuting.")

def list_submissions():
    submissions = load_json(config.USER_SUBMISSIONS_FILE)
    for i, item in enumerate(submissions):
        print(f"{i}. [{item['domain']}] {item['question']} ({item['language']}) Verified={item['verified']}")

def verify_submission(index):
    submissions = load_json(config.USER_SUBMISSIONS_FILE)
    if index < 0 or index >= len(submissions):
        print("Noto'g'ri indeks")
        return
    submission = submissions.pop(index)
    submission["verified"] = True

    # Generate embedding for new verified item
    submission["embedding"] = nlp.get_embedding(submission["question"]).tolist()

    # Add to knowledge base
    kb = load_json(config.KNOWLEDGE_FILE)
    kb.append(submission)
    save_json(kb, config.KNOWLEDGE_FILE)
    save_json(submissions, config.USER_SUBMISSIONS_FILE)
    print(f"Ma'lumot tasdiqlandi va knowledge bazaga qo'shildi.")

    # Auto-retraining: rebuild FAISS index
    print("FAISS index yangilanmoqda...")
    build_faiss_index(kb)
    print("FAISS index yangilandi.")

# --- CLI ---
def main():
    parser = argparse.ArgumentParser(description="AI-FinHub Multilingual FAISS CLI (Auto-Retraining)")
    parser.add_argument('--ask', type=str, help="Savol kiriting")
    parser.add_argument('--add', nargs=3, metavar=('DOMAIN','QUESTION','ANSWER'), help="Foydalanuvchi ma'lumot qo'shadi")
    parser.add_argument('--list', action='store_true', help="Foydalanuvchi submissions ro'yxati")
    parser.add_argument('--verify', type=int, help="Admin submission tasdiqlaydi (index)")

    args = parser.parse_args()

    if args.ask:
        ask_question(args.ask)
    elif args.add:
        domain, question, answer = args.add
        add_user_submission(domain, question, answer)
    elif args.list:
        list_submissions()
    elif args.verify is not None:
        verify_submission(args.verify)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
