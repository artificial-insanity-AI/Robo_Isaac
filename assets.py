import pygame
import os

ASSET_DIR = "assets"

def load_image(name):
    return pygame.image.load(os.path.join(ASSET_DIR, name))

ROBOT_IMG = load_image("robot.png")
MONSTER_IMG = load_image("monster.png")
COIN_IMG = load_image("coin.png")
DOOR_IMG = load_image("door.png")
