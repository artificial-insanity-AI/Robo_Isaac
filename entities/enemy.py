import random

from assets import MONSTER_IMG
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class Enemy:
    def __init__(self, level:int, borders) -> None:
        self.top_border, self.left_border, self.right_border, self.bottom_border = borders
        self.level = level              # need to know level for monster stats progression
        self.image = MONSTER_IMG
        self.speed = random.randint(3,min((4+level//3), 7))  # 3 - 7
        self.hp = random.randint(8,(15+level*5))    # 8 - no limit

        buffer = 150                    # safe perimeter "buffer"
        self.x = random.randint(self.left_border+buffer, SCREEN_WIDTH-buffer-self.right_border - self.image.get_width())
        self.y = random.randint(self.top_border+buffer, SCREEN_HEIGHT-buffer-self.bottom_border - self.image.get_height())
        self.steps_counter = 0
        self.direction = random.randint(1,4)
        self.is_dead = False

    def rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

    def move(self):
        self.change_direction()
        if self.direction == 1:
            if self.x < SCREEN_WIDTH-self.right_border - self.image.get_width():
                self.x += self.speed
        if self.direction == 2:
            if self.x > 0+self.left_border:
                self.x -= self.speed
        if self.direction == 3:
            if self.y > 0+self.top_border-50:
                self.y -= self.speed
        if self.direction == 4:
            if self.y <= SCREEN_HEIGHT-self.bottom_border - self.image.get_height():
                self.y += self.speed
        self.steps_counter += self.speed

    def change_direction(self):
        if self.steps_counter >= 20:                    # after enough steps were made
            self.steps_counter = 0                      # reset the counter
            if not random.randint(0,2):                 # ~33% chance to change the direction
                self.direction = random.randint(1,4)    # generate random direction (including the same one)
