
# -*- coding: utf-8 -*-
import pygame
import math
import random
import time


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, w=40, h=28, color=(220, 60, 60), flight_pattern=None, screen_width=1000, screen_height=700, pattern_config=None):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        self.flight_pattern = flight_pattern or "linear_down"
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 3
        self.base_x = x
        self.base_y = y
        self.angle = 0
        self.time = 0
        self.player_target = None
        self.pattern_config = pattern_config or {}
        self.pattern_params = self._get_pattern_params()
        # Shooting parameters (can be configured by the caller)
        self.last_shot_time = 0.0
        self.shot_interval = 3.0  # seconds between shots by default
        self.shooter_callback = None
        self.bullet_speed = 6  # default enemy bullet speed (positive = downwards)
        self.bullet_tipo = "normal"

    def _get_pattern_params(self):
        """Extract pattern parameters from config"""
        if self.flight_pattern in self.pattern_config:
            return self.pattern_config[self.flight_pattern].copy()
        return {}

    def set_flight_pattern(self, pattern_name, **kwargs):
        """Set the flight pattern for this enemy"""
        self.flight_pattern = pattern_name
        self.pattern_params = self._get_pattern_params()
        if 'speed' in kwargs:
            self.speed = kwargs['speed']
        if 'player_target' in kwargs:
            self.player_target = kwargs['player_target']
        if 'pattern_config' in kwargs:
            self.pattern_config = kwargs['pattern_config']
            self.pattern_params = self._get_pattern_params()

    def set_shooter(self, callback, interval=3.0, bullet_speed=6, bullet_tipo="normal"):
        """Register a callback to spawn bullets.

        callback: function accepting (x, y, speed, tipo) and should add the bullet to the game's group.
        interval: seconds between shots.
        bullet_speed: positive value to move bullet downwards.
        bullet_tipo: optional type string passed to Bala/Bullet constructor.
        """
        self.shooter_callback = callback
        self.shot_interval = float(interval)
        self.bullet_speed = bullet_speed
        self.bullet_tipo = bullet_tipo

    def _try_shoot(self):
        """Attempt to shoot based on interval and registered callback."""
        if not self.shooter_callback:
            return
        now = time.time()
        if now - self.last_shot_time >= self.shot_interval:
            # Spawn bullet slightly below the enemy
            bx = int(self.rect.centerx)
            by = int(self.rect.bottom + 6)
            try:
                self.shooter_callback(bx, by, self.bullet_speed, self.bullet_tipo)
            except Exception:
                pass
            self.last_shot_time = now

    def update(self, dt=1.0):
        """Update enemy position based on flight pattern and configuration"""
        self.time += dt
        pattern_type = self.pattern_params.get("type", self.flight_pattern)

        if pattern_type == "linear":
            direction = self.pattern_params.get("direction", "down")
            speed_mult = self.pattern_params.get("speed_multiplier", 1.0)
            effective_speed = self.speed * speed_mult
            
            if direction == "down":
                self.rect.y += effective_speed
            elif direction == "up":
                self.rect.y -= effective_speed
            elif direction == "left":
                self.rect.x -= effective_speed
            elif direction == "right":
                self.rect.x += effective_speed

        elif pattern_type == "linear_diagonal":
            direction = self.pattern_params.get("direction", "down_left")
            speed_mult = self.pattern_params.get("speed_multiplier", 1.0)
            effective_speed = self.speed * speed_mult
            
            if direction == "down_left":
                self.rect.y += effective_speed
                self.rect.x -= effective_speed * 0.5
            elif direction == "down_right":
                self.rect.y += effective_speed
                self.rect.x += effective_speed * 0.5

        elif pattern_type == "sinusoidal":
            amplitude = self.pattern_params.get("amplitude", 150)
            frequency = self.pattern_params.get("frequency", 0.1)
            v_speed_mult = self.pattern_params.get("vertical_speed_multiplier", 1.0)
            
            self.rect.x = self.base_x + math.sin(self.time * frequency) * amplitude
            self.rect.y += self.speed * v_speed_mult

        elif pattern_type == "zigzag":
            amplitude = self.pattern_params.get("amplitude", 120)
            frequency = self.pattern_params.get("frequency", 0.3)
            v_speed_mult = self.pattern_params.get("vertical_speed_multiplier", 1.0)
            
            self.rect.x = self.base_x + math.sin(self.time * frequency) * amplitude
            self.rect.y += self.speed * v_speed_mult

        elif pattern_type == "circular":
            angular_speed = self.pattern_params.get("angular_speed", 0.05)
            radius = self.pattern_params.get("radius", 80)
            
            self.angle += angular_speed
            self.rect.x = self.base_x + math.cos(self.angle) * radius
            self.rect.y = self.base_y + math.sin(self.angle) * radius

        elif pattern_type == "spiral":
            radius_growth = self.pattern_params.get("radius_growth", 2)
            angular_speed = self.pattern_params.get("angular_speed", 0.1)
            
            self.angle += angular_speed
            radius = self.time * radius_growth
            self.rect.x = self.base_x + math.cos(self.angle) * radius
            self.rect.y = self.base_y + math.sin(self.angle) * radius

        elif pattern_type == "wave":
            amplitude = self.pattern_params.get("amplitude", 100)
            frequency = self.pattern_params.get("frequency", 0.15)
            v_speed_mult = self.pattern_params.get("vertical_speed_multiplier", 0.8)
            
            self.rect.x = self.base_x + math.sin(self.time * frequency) * amplitude
            self.rect.y += self.speed * v_speed_mult

        elif pattern_type == "approach_player" and self.player_target:
            speed_mult = self.pattern_params.get("speed_multiplier", 1.0)
            effective_speed = self.speed * speed_mult
            
            dx = self.player_target.rect.centerx - self.rect.centerx
            dy = self.player_target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                self.rect.x += (dx / distance) * effective_speed
                self.rect.y += (dy / distance) * effective_speed
        else:
            self.rect.y += self.speed

        self._handle_screen_wrapping()
        # Try to shoot after movement
        try:
            self._try_shoot()
        except Exception:
            pass

    def _handle_screen_wrapping(self):
        """Handle screen wrapping for enemies"""
        if self.rect.right < 0:
            self.rect.left = self.screen_width
        elif self.rect.left > self.screen_width:
            self.rect.right = 0

        if self.rect.bottom < 0:
            self.rect.top = self.screen_height
        elif self.rect.top > self.screen_height:
            self.rect.bottom = 0

        pattern_type = self.pattern_params.get("type", self.flight_pattern)
        if pattern_type not in ["circular", "spiral"]:
            if self.rect.top > self.screen_height + 100 or self.rect.bottom < -100:
                self.kill()
            if self.rect.right < 0 or self.rect.left > self.screen_width:
                self.kill()
