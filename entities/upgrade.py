import random


class Upgrade:
    def __init__(self) -> None:
        def lottery():             ### generate a random upgrade ###
            colors = { # v--   how many upgrades possible    --v  == weight(chance) to spawn
                (200,200,50):5,  # yellow-ish     - speed upgrade  (5)
                (200,50,50):20,  # red-ish        - DMG upgrade    (20+)
                (50,50,200):9,   # blue-ish       - tears upgrade  (9)
                (50,200,50):16,  # green-ish      - tear velocity  (16)
                (100,25,25):4    # deep-red-ish   - tear size  (4)
            }
            lottery_colors = []
            for color in colors:
                for i in range(colors[color]):
                    lottery_colors.append(color)
            return random.choice(lottery_colors)

        self.color = lottery()       # color = type of the upgrade

        # self.position = ()     # x,y coordinates  # maybe not needed
        # self.is_dead = False         # set True when item is picked up
