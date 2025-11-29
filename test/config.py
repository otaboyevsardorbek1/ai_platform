import os
import platform

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(DATA_DIR, "model")
LOG_DIR = os.path.join(BASE_DIR, "logs")

KNOWLEDGE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
USER_SUBMISSIONS_FILE = os.path.join(DATA_DIR, "user_submissions.json")
FAISS_INDEX_FILE = os.path.join(MODEL_DIR, "faiss_index.idx")
LOG_FILE = os.path.join(LOG_DIR, "ai_platform.log")

SUPPORTED_LANGUAGES = ["uz", "en", "ru", "tr"]

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

SIMILARITY_THRESHOLD = 0.5
MAX_RESULTS = 5

AUTO_CREATE_DIRS = True
if AUTO_CREATE_DIRS:
    for d in [DATA_DIR, MODEL_DIR, LOG_DIR]:
        os.makedirs(d, exist_ok=True)
