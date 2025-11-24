# visual/avatar.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import threading
import time
from typing import List, Tuple

class Avatar3D:
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_running = False
        self.avatar_position = [0, -1, -5]
        self.avatar_rotation = 0
        self.animation_state = "idle"
        self.animation_time = 0
        
        # Avatar qismlari
        self.body_parts = {
            "head": {"position": [0, 0.8, 0], "size": 0.3},
            "body": {"position": [0, 0, 0], "size": [0.4, 0.8, 0.2]},
            "left_arm": {"position": [-0.5, 0.3, 0], "size": [0.15, 0.6, 0.15]},
            "right_arm": {"position": [0.5, 0.3, 0], "size": [0.15, 0.6, 0.15]},
            "left_leg": {"position": [-0.2, -0.8, 0], "size": [0.15, 0.7, 0.15]},
            "right_leg": {"position": [0.2, -0.8, 0], "size": [0.15, 0.7, 0.15]}
        }
    
    def init_pygame(self):
        """PyGame va OpenGL ni ishga tushirish"""
        pygame.init()
        pygame.display.set_mode((self.screen_width, self.screen_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("AI Assistant - 3D Avatar")
        
        # OpenGL sozlamalari
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Nur sozlamalari
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        
        # Projektoriya
        gluPerspective(45, (self.screen_width / self.screen_height), 0.1, 50.0)
        
        print("3D Avatar initialized successfully")
    
    def draw_cube(self, position, size, color=None):
        """Kub chizish"""
        if color:
            glColor3f(*color)
        
        x, y, z = position
        if isinstance(size, (int, float)):
            s = size / 2
            vertices = [
                [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y+s, z-s], [x-s, y+s, z-s],
                [x-s, y-s, z+s], [x+s, y-s, z+s], [x+s, y+s, z+s], [x-s, y+s, z+s]
            ]
        else:
            sx, sy, sz = size
            vertices = [
                [x-sx, y-sy, z-sz], [x+sx, y-sy, z-sz], [x+sx, y+sy, z-sz], [x-sx, y+sy, z-sz],
                [x-sx, y-sy, z+sz], [x+sx, y-sy, z+sz], [x+sx, y+sy, z+sz], [x-sx, y+sy, z+sz]
            ]
        
        faces = [
            [0,1,2,3], [3,2,6,7], [7,6,5,4],
            [4,5,1,0], [1,5,6,2], [4,0,3,7]
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
    
    def draw_sphere(self, position, radius, color=None):
        """Sfera chizish"""
        if color:
            glColor3f(*color)
        
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(*position)
        gluSphere(quadric, radius, 32, 32)
        glPopMatrix()
        gluDeleteQuadric(quadric)
    
    def draw_avatar(self):
        """Avatar ni chizish"""
        glPushMatrix()
        glTranslatef(*self.avatar_position)
        glRotatef(self.avatar_rotation, 0, 1, 0)
        
        # Animatsiya
        self.apply_animation()
        
        # Bosh
        self.draw_sphere(
            self.body_parts["head"]["position"],
            self.body_parts["head"]["size"],
            (0.8, 0.6, 0.4)  # Ter rang
        )
        
        # Tana
        self.draw_cube(
            self.body_parts["body"]["position"],
            self.body_parts["body"]["size"],
            (0.2, 0.4, 0.8)  # Ko'k rang
        )
        
        # Qo'llar va oyoqlar
        self.draw_cube(self.body_parts["left_arm"]["position"], self.body_parts["left_arm"]["size"], (0.8, 0.6, 0.4))
        self.draw_cube(self.body_parts["right_arm"]["position"], self.body_parts["right_arm"]["size"], (0.8, 0.6, 0.4))
        self.draw_cube(self.body_parts["left_leg"]["position"], self.body_parts["left_leg"]["size"], (0.3, 0.3, 0.3))
        self.draw_cube(self.body_parts["right_leg"]["position"], self.body_parts["right_leg"]["size"], (0.3, 0.3, 0.3))
        
        glPopMatrix()
    
    def apply_animation(self):
        """Animatsiya qo'llash"""
        self.animation_time += 0.1
        
        if self.animation_state == "idle":
            # Sekin harakat
            sway = math.sin(self.animation_time) * 0.1
            self.body_parts["head"]["position"][1] = 0.8 + sway * 0.1
            
        elif self.animation_state == "talking":
            # Gapirish animatsiyasi
            jaw_move = math.sin(self.animation_time * 5) * 0.05
            self.body_parts["head"]["position"][1] = 0.8 + jaw_move
            
        elif self.animation_state == "listening":
            # Tinglash animatsiyasi
            head_tilt = math.sin(self.animation_time * 2) * 5
            glRotatef(head_tilt, 0, 0, 1)
    
    def set_animation_state(self, state: str):
        """Animatsiya holatini o'zgartirish"""
        self.animation_state = state
    
    def render_text(self, text: str):
        """Matnni ekranda ko'rsatish"""
        # Soddalashtirilgan matn ko'rsatish
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glWindowPos2d(10, self.screen_height - 40)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    def run(self):
        """Asosiy render loop"""
        self.init_pygame()
        self.is_running = True
        
        clock = pygame.time.Clock()
        current_text = "AI Assistant is ready!"
        
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
            
            # Tozalash
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Kamerani sozlash
            gluLookAt(0, 0, 0, 0, 0, -1, 0, 1, 0)
            
            # Avatar ni chizish
            self.draw_avatar()
            
            # Matnni ko'rsatish
            self.render_text(current_text)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
    
    def update_dialogue(self, text: str):
        """Dialog yangilash"""
        # Bu metod tashqi tomondan chaqiriladi
        self.set_animation_state("talking")
        # Matn yangilanishi
    
    def start_in_thread(self):
        """Avatar ni threadda ishga tushirish"""
        def _run():
            self.run()
        
        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()
        return thread