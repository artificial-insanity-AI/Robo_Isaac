import pygame
import os

ASSET_DIR = "assets"

def load_image(name):
    return pygame.image.load(os.path.join(ASSET_DIR, name))

ROBOT_IMG = load_image("robot.png")
MONSTER_IMG = load_image("monster.png")
BOSS_IMG = pygame.transform.scale(MONSTER_IMG, (MONSTER_IMG.get_width()*2, MONSTER_IMG.get_height()*2))
COIN_IMG = load_image("coin.png")
DOOR_IMG = load_image("door.png")
