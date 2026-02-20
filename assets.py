import pygame
import os

ASSET_DIR = "assets"

def load_image(name):
    return pygame.image.load(os.path.join(ASSET_DIR, name))

ROBOT_IMG = load_image("robot.png")
EXTRA_LIFE_IMG = pygame.transform.scale(ROBOT_IMG, (ROBOT_IMG.get_width()*0.7, ROBOT_IMG.get_height()*0.7))
MONSTER_IMG = load_image("monster.png")
BOSS_IMG = pygame.transform.scale(MONSTER_IMG, (MONSTER_IMG.get_width()*2, MONSTER_IMG.get_height()*2))
COIN_IMG = load_image("coin.png")
DOOR_IMG = load_image("door.png")
