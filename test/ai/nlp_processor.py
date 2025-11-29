from sentence_transformers import SentenceTransformer
from langdetect import detect, DetectorFactory
import re
import string
import config

DetectorFactory.seed = 0

class NLPProcessor:
    def __init__(self):
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        text = re.sub("\s+", " ", text).strip()
        return text

    def detect_language(self, text):
        try:
            return detect(text)
        except:
            return "unknown"

    def get_embedding(self, text):
        text = self.clean_text(text)
        embedding = self.embedder.encode([text], normalize_embeddings=True)
        return embedding[0]

    def process_text(self, text):
        cleaned = self.clean_text(text)
        lang = self.detect_language(cleaned)
        embedding = self.get_embedding(cleaned)
        return {"text": cleaned, "language": lang, "embedding": embedding}
