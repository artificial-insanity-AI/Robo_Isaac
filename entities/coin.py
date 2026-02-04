import random

from assets import COIN_IMG
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class Coin:
    def __init__(self, borders:tuple) -> None:
        self.image = COIN_IMG
        top_border, left_border, right_border, bottom_border = borders
        self.x = random.randint(left_border, SCREEN_WIDTH-right_border - self.image.get_width())
        self.y = random.randint(top_border, SCREEN_HEIGHT-bottom_border - self.image.get_height())
        self.is_dead = False