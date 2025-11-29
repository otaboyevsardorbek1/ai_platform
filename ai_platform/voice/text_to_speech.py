# voice/text_to_speech.py
import pyttsx3
from typing import Dict
import threading
import queue
import time
import logging
from typing import Optional, Callable, List
from enum import Enum

logger = logging.getLogger(__name__)

class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"

class VoiceEmotion(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"

class AdvancedTTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.current_emotion = VoiceEmotion.NEUTRAL
        self.speech_thread = None
        self.on_speech_start = None
        self.on_speech_end = None
        
        # Ovoz sozlamalari
        self.setup_voice()
        
        # Emotion sozlamalari
        self.emotion_settings = self._setup_emotion_settings()
    
    def _setup_emotion_settings(self) -> Dict[VoiceEmotion, Dict]:
        """Emotion sozlamalarini yaratish"""
        return {
            VoiceEmotion.NEUTRAL: {"rate": 150, "volume": 0.8, "pitch": "default"},
            VoiceEmotion.HAPPY: {"rate": 180, "volume": 0.9, "pitch": "high"},
            VoiceEmotion.SAD: {"rate": 120, "volume": 0.7, "pitch": "low"},
            VoiceEmotion.EXCITED: {"rate": 200, "volume": 1.0, "pitch": "high"},
            VoiceEmotion.CALM: {"rate": 130, "volume": 0.8, "pitch": "medium"}
        }
    
    def setup_voice(self):
        """Ovoz sozlamalari"""
        try:
            # Mavjud ovozlarni olish
            voices = self.engine.getProperty('voices')
            
            if voices:
                # Eng yaxshi ovozni tanlash
                for voice in voices:
                    if 'english' in voice.name.lower() or 'us' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Default sozlamalar
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.8)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up TTS: {e}")
    
    def set_voice_gender(self, gender: VoiceGender):
        """Ovoz jinsini o'zgartirish"""
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            voice_name = voice.name.lower()
            if (gender == VoiceGender.MALE and 'male' in voice_name) or \
               (gender == VoiceGender.FEMALE and 'female' in voice_name):
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Voice set to: {voice.name}")
                return
        
        logger.warning(f"Could not find {gender.value} voice")
    
    def set_emotion(self, emotion: VoiceEmotion):
        """Emotion ni o'zgartirish"""
        if emotion in self.emotion_settings:
            settings = self.emotion_settings[emotion]
            self.engine.setProperty('rate', settings["rate"])
            self.engine.setProperty('volume', settings["volume"])
            self.current_emotion = emotion
            logger.info(f"Emotion set to: {emotion.value}")
    
    def speak(self, text: str, emotion: Optional[VoiceEmotion] = None, 
              blocking: bool = False):
        """Matnni ovozga aylantirish"""
        if emotion:
            self.set_emotion(emotion)
        
        if blocking:
            # Bloklovchi rejim
            self._speak_directly(text)
        else:
            # Navbatga qo'shish
            self.speech_queue.put(text)
            self._start_speech_thread()
    
    def _speak_directly(self, text: str):
        """To'g'ridan-to'g'ri ovozga aylantirish"""
        try:
            if self.on_speech_start:
                self.on_speech_start(text)
            
            self.engine.say(text)
            self.engine.runAndWait()
            
            if self.on_speech_end:
                self.on_speech_end(text)
                
        except Exception as e:
            logger.error(f"Error in direct speech: {e}")
    
    def _start_speech_thread(self):
        """Ovoz threadini ishga tushirish"""
        if self.speech_thread is None or not self.speech_thread.is_alive():
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
    
    def _speech_worker(self):
        """Ovoz ishchisi"""
        while not self.speech_queue.empty():
            try:
                text = self.speech_queue.get(timeout=1)
                self._speak_directly(text)
                self.speech_queue.task_done()
                time.sleep(0.1)  # Kichik tanaffus
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error in speech worker: {e}")
                break
    
    def stop_speaking(self):
        """Ovozni to'xtatish"""
        try:
            self.engine.stop()
            # Navbatni tozalash
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def get_available_voices(self) -> List[Dict]:
        """Mavjud ovozlarni olish"""
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for voice in voices:
            voice_list.append({
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages if hasattr(voice, 'languages') else [],
                "gender": "female" if 'female' in voice.name.lower() else "male"
            })
        
        return voice_list
    
    def set_speech_rate(self, rate: int):
        """Nutq tezligini o'zgartirish (50-300)"""
        rate = max(50, min(300, rate))
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Ovoz balandligini o'zgartirish (0.0-1.0)"""
        volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', volume)
    
    def register_callbacks(self, on_start: Callable, on_end: Callable):
        """Callback'larni ro'yxatdan o'tkazish"""
        self.on_speech_start = on_start
        self.on_speech_end = on_end
    
    def speak_ssml(self, ssml_text: str):
        """SSML formatidagi matnni ovozga aylantirish"""
        # Pyttsx3 SSML ni qo'llamaydi, lekin strukturani ko'rsatamiz
        try:
            # SSML ni oddiy matnga aylantirish
            simple_text = self._ssml_to_text(ssml_text)
            self.speak(simple_text)
        except Exception as e:
            logger.error(f"Error speaking SSML: {e}")
    
    def _ssml_to_text(self, ssml_text: str) -> str:
        """SSML ni oddiy matnga aylantirish (soddalashtirilgan)"""
        # SSML teglarini olib tashlash
        import re
        text = re.sub(r'<[^>]+>', '', ssml_text)
        return text.strip()
    
    def get_speech_status(self) -> Dict[str, any]:
        """Nutq holatini olish"""
        return {
            "is_speaking": self.is_speaking,
            "queue_size": self.speech_queue.qsize(),
            "current_emotion": self.current_emotion.value,
            "rate": self.engine.getProperty('rate'),
            "volume": self.engine.getProperty('volume')
        }

class MultiLanguageTTS:
    def __init__(self):
        self.tts_engines = {}
        self.current_language = "en"
        
        # Til kodlari
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "ru": "Russian"
            # O'zbek tili qo'shish uchun maxsus sozlash kerak
        }
    
    def set_language(self, language_code: str):
        """Tilni o'zgartirish"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            # Haqiqiy loyihada har til uchun alohida engine yoki voice
        else:
            logger.warning(f"Language not supported: {language_code}")
    
    def speak(self, text: str, language: Optional[str] = None):
        """Ko'p tilli ovoz"""
        if language:
            self.set_language(language)
        
        # Haqiqiy loyihada tilga mos ovoz ishlatiladi
        # Hozircha asosiy TTS dan foydalanamiz
        tts = AdvancedTTS()
        tts.speak(text)

# Global instance
tts_engine = AdvancedTTS()