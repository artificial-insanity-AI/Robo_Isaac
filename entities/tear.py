from config import SCREEN_WIDTH, SCREEN_HEIGHT


class Tear:
    def __init__(self, x:int, y:int, direction:str, speed:int, color:tuple, size:int, borders:tuple) -> None:
        self.top, self.left, self.right, self.bottom = borders
        self.x = x + 25
        self.y = y + 15
        self.speed = min(speed, 20)  # tear speed limit is 20
        self.direction = direction
        self.color = color
        self.size = size
        self.is_dead = False # is "dead" means it is no longer on the screen and can be overwritten by a new tear

    def move_tear(self):
        if self.direction == "left":
            self.x -= self.speed
            if self.x <= self.left:      # hit the wall
                self.tear_collision()
        if self.direction == "right":
            self.x += self.speed
            if self.x >= SCREEN_WIDTH - self.right:
                self.tear_collision()
        if self.direction == "top":
            self.y -= self.speed
            if self.y <= self.top:
                self.tear_collision()
        if self.direction == "bottom":
            self.y += self.speed
            if self.y >= SCREEN_HEIGHT - self.bottom:
                self.tear_collision()

    def tear_collision(self):     # called on tear collision
        self.color = (255,0,0)    # change color
        self.size = self.size*4   # increase size
        self.is_dead = True       # and set the dead status