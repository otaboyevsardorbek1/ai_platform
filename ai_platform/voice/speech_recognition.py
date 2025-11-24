# voice/speech_recognition.py
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.callback = None
        
        # TTS sozlamalari
        self.setup_tts()
        # Mikrofonni sozlash
        self.setup_microphone()
    
    def setup_tts(self):
        """Text-to-Speech sozlamalari"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
    
    def setup_microphone(self):
        """Mikrofonni sozlash"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        logger.info("Microphone setup completed")
    
    def speak(self, text: str):
        """Matnni ovozga aylantirish"""
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def listen(self) -> Optional[str]:
        """Ovozni tinglash va matnga aylantirish"""
        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text.lower()
        
        except sr.WaitTimeoutError:
            logger.info("Listening timeout")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in listening: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable):
        """Doimiy tinglashni boshlash"""
        self.callback = callback
        self.is_listening = True
        
        def _listen_loop():
            while self.is_listening:
                text = self.listen()
                if text and self.callback:
                    self.callback(text)
                time.sleep(0.1)
        
        listener_thread = threading.Thread(target=_listen_loop)
        listener_thread.daemon = True
        listener_thread.start()
        logger.info("Continuous listening started")
    
    def stop_listening(self):
        """Tinglashni to'xtatish"""
        self.is_listening = False
        logger.info("Continuous listening stopped")
    
    def process_voice_command(self, command: str, ai_processor) -> str:
        """Ovozli buyruqni qayta ishlash"""
        # Buyruqlarni aniqlash
        command = command.lower()
        
        if any(word in command for word in ['hello', 'hi', 'hey']):
            response = "Hello! How can I assist you today?"
        elif any(word in command for word in ['time', 'what time']):
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            response = f"The current time is {current_time}"
        elif any(word in command for word in ['stop', 'exit', 'quit']):
            response = "Goodbye! Have a great day!"
            self.stop_listening()
        else:
            # AI ga yo'naltirish
            response, confidence = ai_processor.find_best_answer(command)
        
        # Javobni ovozga aylantirish
        self.speak(response)
        return response