# main.py
#!/usr/bin/env python3
"""
Mukammal AI Platformasi - Asosiy Dastur
"""

import click
import sys
import os

# Path ni sozlash
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli.commands import cli
from api.server import AIPlatformAPI
from visual.avatar import Avatar3D
from voice.speech_recognition import VoiceAssistant
from ai.nlp_processor import NLPProcessor
from config.settings import settings

def main():
    """Asosiy dastur"""
    print(f"""
    🚀 {settings.APP_NAME} v{settings.VERSION}
    📚 Domain-Specific AI Platformasi
    ✨ Mukammal Yechim: FastAPI + CLI + Ovoz + 3D Vizual
    
    👉 Foydalanish: python main.py [OPTIONS] COMMAND [ARGS]
    👉 Yordam: python main.py --help
    """)
    
    # CLI ni ishga tushirish
    cli()

if __name__ == "__main__":
    main()