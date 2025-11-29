# domain_knowledge.py
import json

def load_knowledge(path="data/knowledge_base.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_knowledge(data, path="data/knowledge_base.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
