from assets import BOSS_IMG
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
