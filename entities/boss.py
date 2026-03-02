import pygame

from assets import BOSS_IMG
from config import SCREEN_WIDTH, LEFT_BORDER, RIGHT_BORDER
from entities.enemy import Enemy


class Boss(Enemy):       # basically just an enemy with increased image size and stats
    def __init__(self, level: int, borders) -> None:
        super().__init__(level, borders)

        self.image = BOSS_IMG
        self.speed += 1
        self.hp *= 10
        self.starting_hp = self.hp
        self.x = 500
        self.y = 400

        self.attack_state = "idle"   # idle, charging, firing
        self.state_start_time = 0
        self.attack_cooldown = 4000
        self.charge_duration = 1000
        self.fire_duration = 1500
        self.last_attack_time = pygame.time.get_ticks()

    def move(self):
        now = pygame.time.get_ticks()

        # Start attack if idle and cooldown passed
        if self.attack_state == "idle":
            if now - self.last_attack_time > self.attack_cooldown:
                self.attack_state = "charging"
                self.state_start_time = now
            else:
                super().move()
                return

        # Charging phase (boss flashes)
        if self.attack_state == "charging":
            if now - self.state_start_time > self.charge_duration:
                self.attack_state = "firing"
                self.state_start_time = now
            return  # stop moving while charging

        # Firing phase
        if self.attack_state == "firing":
            if now - self.state_start_time > self.fire_duration:
                self.attack_state = "idle"
                self.last_attack_time = now
            return  # stop moving while firing

    def get_lasers(self):

        if self.attack_state == "charging":
            laser_height = 3
            color = (255, 255, 255)
        elif self.attack_state == "firing":
            laser_height = 30
            color = (255, 0, 0)
        else: return [], 0

        laser_y = self.y + self.image.get_height() // 5 - laser_height // 2

        left_laser = pygame.Rect(
            LEFT_BORDER,                # left border
            laser_y,
            max(0, self.x - LEFT_BORDER),  # width
            laser_height
        )

        right_laser = pygame.Rect(
            self.x + self.image.get_width(),
            laser_y,
            max(0, SCREEN_WIDTH - RIGHT_BORDER - (self.x + self.image.get_width())),  # width
            laser_height
        )

        return [left_laser, right_laser], color
