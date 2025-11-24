# config/settings.py
import os
from pathlib import Path

class Settings:
    # Asosiy sozlamalar
    APP_NAME = "AI Platform"
    VERSION = "1.0.0"
    DEBUG = True
    
    # API sozlamalari
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_DOCS_URL = "/docs"
    
    # Database sozlamalari
    DATABASE_URL = "sqlite:///./ai_platform.db"
    
    # AI Model sozlamalari
    AI_MODELS = {
        "legal": "legal_model.pkl",
        "education": "education_model.pkl", 
        "medical": "medical_model.pkl",
        "general": "general_model.pkl"
    }
    
    # Ovoz sozlamalari
    VOICE_TIMEOUT = 5
    VOICE_LANGUAGE = "en-US"
    
    # 3D Vizual sozlamalari
    AVATAR_MODEL = "avatar.glb"
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    
    # Domain bilimlari
    DOMAIN_KNOWLEDGE = {
        "legal": [
            {
                "question": "What is breach of contract?",
                "answer": "Breach of contract occurs when one party fails to fulfill obligations without legal excuse.",
                "keywords": "contract breach obligation legal"
            }
        ],
        "education": [
            {
                "question": "What is differentiated instruction?",
                "answer": "Teaching approach that tailors instruction to individual student needs.",
                "keywords": "teaching instruction students learning"
            }
        ]
    }

settings = Settings()