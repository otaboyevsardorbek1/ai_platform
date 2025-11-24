# cli/commands.py
import click
import requests
import json
import sys
from typing import Optional

from ai.nlp_processor import NLPProcessor
from voice.speech_recognition import VoiceAssistant
from config.settings import settings

@click.group()
def cli():
    """AI Platform CLI - Mukammal AI Yordamchi"""
    pass

@cli.command()
@click.option('--question', '-q', help='Savol bering')
@click.option('--domain', '-d', default='general', help='Domain tanlang')
def chat(question, domain):
    """Chat rejimi"""
    ai_processor = NLPProcessor()
    ai_processor.load_domain_knowledge(settings.DOMAIN_KNOWLEDGE)
    
    if question:
        # Bir martalik savol
        answer, confidence = ai_processor.find_best_answer(question, domain)
        click.echo(f"🤖 AI: {answer}")
        click.echo(f"📊 Confidence: {confidence:.2f}")
    else:
        # Interaktiv rejim
        click.echo("💬 AI Assistant ga xush kelibsiz! (Chiqish uchun 'quit' yozing)")
        
        while True:
            try:
                user_input = click.prompt("You", type=str)
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    click.echo("👋 Xayr! Yana kutamiz!")
                    break
                
                answer, confidence = ai_processor.find_best_answer(user_input, domain)
                click.echo(f"🤖 AI: {answer}")
                click.echo(f"📊 Confidence: {confidence:.2f}")
                
            except KeyboardInterrupt:
                click.echo("\n👋 Dastur to'xtatildi!")
                break

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='API URL')
def api_chat(api_url):
    """API orqali chat"""
    click.echo("🌐 API Chat rejimi")
    session_id = None
    
    while True:
        try:
            question = click.prompt("You", type=str)
            
            if question.lower() in ['quit', 'exit']:
                break
            
            response = requests.post(
                f"{api_url}/api/chat",
                json={
                    "question": question,
                    "domain": "general",
                    "session_id": session_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                click.echo(f"🤖 AI: {data['answer']}")
                click.echo(f"⚡ Response Time: {data['response_time']:.2f}s")
                session_id = data['session_id']
            else:
                click.echo("❌ API da xatolik!")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            click.echo(f"❌ Xatolik: {e}")

@cli.command()
def voice_mode():
    """Ovozli rejim"""
    click.echo("🎤 Ovozli rejim ishga tushdi...")
    click.echo("🎧 Mikrofonga gapiring (Chiqish uchun 'stop' deying)")
    
    ai_processor = NLPProcessor()
    ai_processor.load_domain_knowledge(settings.DOMAIN_KNOWLEDGE)
    voice_assistant = VoiceAssistant()
    
    def voice_callback(text):
        if text:
            click.echo(f"🎤 Siz: {text}")
            response = voice_assistant.process_voice_command(text, ai_processor)
            click.echo(f"🤖 AI: {response}")
    
    voice_assistant.start_continuous_listening(voice_callback)
    
    try:
        # Asosiy thread bloklash
        while voice_assistant.is_listening:
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        voice_assistant.stop_listening()
        click.echo("\n👋 Ovozli rejim to'xtatildi!")

@cli.command()
def visual_mode():
    """3D Vizual rejim"""
    click.echo("👁️ 3D Vizual yordamchi ishga tushmoqda...")
    
    try:
        from visual.avatar import Avatar3D
        
        avatar = Avatar3D()
        avatar.start_in_thread()
        
        click.echo("🚀 3D Avatar ishga tushdi! Oynani ko'ring.")
        click.echo("❌ Oynani yopish uchun ESC tugmasini bosing yoki oynani yoping.")
        
        # Asosiy thread ni bloklash
        import time
        while avatar.is_running:
            time.sleep(0.1)
            
    except ImportError as e:
        click.echo(f"❌ 3D kutubxonalar o'rnatilmagan: {e}")
        click.echo("🔧 O'rnatish: pip install pygame PyOpenGL")

@cli.command()
def start_api():
    """API serverni ishga tushirish"""
    click.echo("🚀 FastAPI server ishga tushmoqda...")
    
    from api.server import api_server
    api_server.run()

if __name__ == '__main__':
    cli()