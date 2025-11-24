# visual/animation.py
import math
import time
import threading
from enum import Enum
from typing import Dict, List, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class AnimationState(Enum):
    IDLE = "idle"
    TALKING = "talking"
    LISTENING = "listening"
    THINKING = "thinking"
    HAPPY = "happy"
    SAD = "sad"
    CONFUSED = "confused"
    WAVING = "waving"

class Animation:
    def __init__(self):
        self.current_state = AnimationState.IDLE
        self.animation_time = 0.0
        self.animation_speed = 1.0
        self.is_looping = True
        self.callbacks = {}
        
        # Animatsiya parametrlari
        self.animation_params = {
            "head_bob": 0.0,
            "body_sway": 0.0,
            "arm_movement": 0.0,
            "eye_blink": 0.0,
            "mouth_open": 0.0
        }
        
        # Animatsiya patternlari
        self.animation_patterns = self._setup_animation_patterns()
    
    def _setup_animation_patterns(self) -> Dict[AnimationState, Dict]:
        """Animatsiya patternlarini sozlash"""
        return {
            AnimationState.IDLE: {
                "head_bob": lambda t: math.sin(t * 0.5) * 0.1,
                "body_sway": lambda t: math.sin(t * 0.3) * 0.05,
                "eye_blink": lambda t: 1.0 if math.sin(t * 0.2) > 0.9 else 0.0,
                "duration": float('inf')
            },
            AnimationState.TALKING: {
                "head_bob": lambda t: math.sin(t * 5) * 0.2,
                "mouth_open": lambda t: (math.sin(t * 10) + 1) * 0.5,
                "body_sway": lambda t: math.sin(t * 2) * 0.1,
                "duration": 2.0
            },
            AnimationState.LISTENING: {
                "head_bob": lambda t: math.sin(t * 2) * 0.15,
                "body_sway": lambda t: math.sin(t * 1) * 0.08,
                "eye_blink": lambda t: 1.0 if math.sin(t * 3) > 0.8 else 0.0,
                "duration": float('inf')
            },
            AnimationState.THINKING: {
                "head_bob": lambda t: math.sin(t * 1.5) * 0.1,
                "body_sway": lambda t: math.sin(t * 0.8) * 0.06,
                "arm_movement": lambda t: math.sin(t * 2) * 0.3,
                "duration": 3.0
            },
            AnimationState.HAPPY: {
                "head_bob": lambda t: math.sin(t * 3) * 0.25,
                "body_sway": lambda t: math.sin(t * 2) * 0.15,
                "arm_movement": lambda t: math.sin(t * 4) * 0.4,
                "duration": 2.5
            },
            AnimationState.WAVING: {
                "arm_movement": lambda t: math.sin(t * 6) * 0.8,
                "head_bob": lambda t: math.sin(t * 2) * 0.1,
                "duration": 1.5
            }
        }
    
    def set_animation_state(self, state: AnimationState):
        """Animatsiya holatini o'zgartirish"""
        if state != self.current_state:
            logger.info(f"Animation state changed: {self.current_state} -> {state}")
            self.current_state = state
            self.animation_time = 0.0
            
            # Callback chaqirish
            if state in self.callbacks:
                self.callbacks[state]()
    
    def update(self, delta_time: float):
        """Animatsiyani yangilash"""
        self.animation_time += delta_time * self.animation_speed
        
        current_pattern = self.animation_patterns.get(self.current_state, {})
        
        # Parametrlarni yangilash
        for param, pattern_func in current_pattern.items():
            if param != "duration":
                self.animation_params[param] = pattern_func(self.animation_time)
        
        # Duration tekshirish
        if (current_pattern.get("duration", float('inf')) < self.animation_time and 
            self.current_state != AnimationState.IDLE):
            self.set_animation_state(AnimationState.IDLE)
    
    def get_animation_parameters(self) -> Dict[str, float]:
        """Animatsiya parametrlarini olish"""
        return self.animation_params.copy()
    
    def trigger_animation(self, state: AnimationState, duration: Optional[float] = None):
        """Animatsiyani ishga tushirish"""
        self.set_animation_state(state)
        if duration:
            # Duration ni o'zgartirish
            if state in self.animation_patterns:
                self.animation_patterns[state]["duration"] = duration
    
    def register_callback(self, state: AnimationState, callback: Callable):
        """Callback qo'shish"""
        self.callbacks[state] = callback
    
    def reset(self):
        """Animatsiyani qayta sozlash"""
        self.current_state = AnimationState.IDLE
        self.animation_time = 0.0
        for param in self.animation_params:
            self.animation_params[param] = 0.0

class LipSync:
    def __init__(self):
        self.phonemes = {
            'A': 0.8, 'E': 0.6, 'I': 0.4, 'O': 0.7, 'U': 0.5,
            'B': 0.9, 'P': 0.9, 'M': 0.8,
            'F': 0.6, 'V': 0.6,
            'L': 0.4, 'R': 0.3,
            'S': 0.2, 'Z': 0.2, 'SH': 0.3, 'CH': 0.5,
            'T': 0.3, 'D': 0.3, 'N': 0.4,
            'K': 0.2, 'G': 0.2,
            'silence': 0.0
        }
        self.current_phoneme = 'silence'
        self.mouth_openness = 0.0
        self.smooth_factor = 0.3
    
    def text_to_phonemes(self, text: str) -> List[str]:
        """Matnni fonemalarga ajratish (soddalashtirilgan)"""
        text = text.upper()
        phonemes = []
        
        for char in text:
            if char in 'AEIOU':
                phonemes.append(char)
            elif char in 'BP':
                phonemes.append('B')
            elif char in 'FV':
                phonemes.append('F')
            elif char in 'LR':
                phonemes.append('L')
            elif char in 'SZ':
                phonemes.append('S')
            elif char in 'TDN':
                phonemes.append('T')
            elif char in 'KG':
                phonemes.append('K')
            elif char == ' ':
                phonemes.append('silence')
            else:
                phonemes.append('silence')
        
        return phonemes
    
    def update_lip_sync(self, text: str, progress: float):
        """Lablar harakatini yangilash"""
        phoneme_list = self.text_to_phonemes(text)
        
        if not phoneme_list:
            target_openness = self.phonemes['silence']
        else:
            # Progress bo'yicha joriy fonemani aniqlash
            index = int(progress * len(phoneme_list))
            index = min(index, len(phoneme_list) - 1)
            current_phoneme = phoneme_list[index]
            target_openness = self.phonemes.get(current_phoneme, 0.0)
        
        # Smootlangan o'tish
        self.mouth_openness = (self.mouth_openness * (1 - self.smooth_factor) + 
                              target_openness * self.smooth_factor)
        
        return self.mouth_openness
    
    def get_mouth_openness(self) -> float:
        """Og'iz ochiqligini olish"""
        return self.mouth_openness