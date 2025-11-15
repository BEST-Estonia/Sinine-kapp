# src/app/ui_pygame.py
import pygame
import sys
import time
from pathlib import Path

SCREEN_W, SCREEN_H = 800, 480  # typical 7" touchscreen resolution
BUTTON_COLOR = (200, 200, 200)
TEXT_COLOR = (20, 20, 20)
FPS = 30

class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action

    def draw(self, surf, font):
        pygame.draw.rect(surf, BUTTON_COLOR, self.rect, border_radius=10)
        txt = font.render(self.text, True, TEXT_COLOR)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

class TouchUI:
    def __init__(self, rfid, qr, camera, scale_top, scale_bottom):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Smart Cupboard (mock)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)

        # hardware
        self.rfid = rfid
        self.qr = qr
        self.camera = camera
        self.scale_top = scale_top
        self.scale_bottom = scale_bottom

        # character placeholder (text fallback)
        self.character_text = "Cupby"

        # Buttons layout
        padding = 20
        btn_w = (SCREEN_W - padding * 3) // 2
        btn_h = 120
        self.buttons = [
            Button((padding, 160, btn_w, btn_h), "Open cupboard", self.open_cupboard),
            Button((padding*2+btn_w, 160, btn_w, btn_h), "Return drink", self.register_return),
            Button((padding, 300, btn_w, btn_h), "Register user", self.register_user),
            Button((padding*2+btn_w, 300, btn_w, btn_h), "Admin", self.admin_panel),
        ]

        # Status area
        self.status = "Ready"

    def run(self):
        while True:
            self.clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = ev.pos
                    for b in self.buttons:
                        if b.contains(pos):
                            b.action()
                elif ev.type == pygame.KEYDOWN:
                    # keyboard shortcuts for testing
                    if ev.key == pygame.K_1:
                        self.open_cupboard()
                    elif ev.key == pygame.K_2:
                        self.register_return()
                    elif ev.key == pygame.K_3:
                        self.register_user()
                    elif ev.key == pygame.K_4:
                        self.admin_panel()

            self.draw()

    def draw(self):
        self.screen.fill((255,255,255))
        # draw character on left side
        char_rect = pygame.Rect(20, 20, 220, 110)
        pygame.draw.rect(self.screen, (240,240,255), char_rect, border_radius=12)
        name = self.large_font.render(self.character_text, True, TEXT_COLOR)
        self.screen.blit(name, (char_rect.x + 10, char_rect.y + 10))
        msg = self.font.render("Hi! I'm Cupby :) Tap a button to start.", True, TEXT_COLOR)
        self.screen.blit(msg, (char_rect.x + 10, char_rect.y + 60))

        # draw buttons
        for b in self.buttons:
            b.draw(self.screen, self.font)

        # draw status bar
        status_surf = self.font.render(f"Status: {self.status}", True, TEXT_COLOR)
        self.screen.blit(status_surf, (20, SCREEN_H - 40))

        pygame.display.flip()

    # --- actions ---
    def open_cupboard(self):
        self.status = "Waiting for RFID..."
        pygame.display.flip()
        uid = self.rfid.read()
        if not uid:
            self.status = "RFID read cancelled or empty"
            return
        self.status = f"User {uid} — unlocking..."
        # mock unlock (in real: GPIO trigger)
        time.sleep(0.6)
        self.status = "Cupboard unlocked. Close to finish."
        # mock weight read
        wt_top = self.scale_top.read_weight()
        wt_bottom = self.scale_bottom.read_weight()
        self.status = f"Opened by {uid} | top:{wt_top}kg bottom:{wt_bottom}kg"

    def register_return(self):
        self.status = "Scan QR to register return..."
        code = self.qr.scan()
        if not code:
            self.status = "QR cancelled"
            return
        self.status = f"Return registered: {code}"

    def register_user(self):
        self.status = "Registering user: tap card..."
        uid = self.rfid.read()
        if not uid:
            self.status = "Registration cancelled"
            return
        # here we would create user entry in users.json
        self.status = f"Registered user: {uid}"

    def admin_panel(self):
        self.status = "Admin mode (mock)"
