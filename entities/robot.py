from assets import ROBOT_IMG
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from entities.tear import Tear


class Robot:
    def __init__(self, borders:tuple) -> None:
        self.borders = borders
        self.top_border, self.left_border, self.right_border, self.bottom_border = borders
        self.image = ROBOT_IMG
        self.speed = 3         # min 3 max 7
        self.tear_speed = 4   # min 4 max 20
        self.tears = 2        # min 2 max 10
        self.health_points = 2 # min 0 max 5 - "extra life". 0 == last life
        # self.eye_color =  #[gave up the idea to change eye/tear color depending on the damage/level/size]
        self.tear_color = (0, 0, 200)
        self.tear_size = 4     # min 4 max 8
        self.damage = 2        # min 2 max 'no limit'
        self.total_damage = self.damage * self.tear_size
        # meaning 4 is the starting damage and at maximum tear size all damage is basically doubled

        self.x = int(SCREEN_WIDTH/2)
        self.y = int(SCREEN_HEIGHT/2)
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.door_collision = None

        self.active_tears = [] # max can be up to self.tears stat but no more than 10

    def rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

    def move_robot(self):
        self.door_collision = None
        speed = min(self.speed, 7)  # speeed limit is 7
        if self.move_right:
            if self.x < SCREEN_WIDTH-self.right_border - self.image.get_width():
                self.x += speed
            elif SCREEN_HEIGHT /2-60 < self.y < SCREEN_HEIGHT /2+5:   # pressing against the right wall
                self.door_collision = "right"       ## so we set the direction
        if self.move_left:
            if self.x > 0+self.left_border:
                self.x -= speed
            elif SCREEN_HEIGHT/2-60 < self.y < SCREEN_HEIGHT /2+5:
                self.door_collision = "left"
        if self.move_up:
            if self.y > 0+self.top_border-50:
                self.y -= speed
            elif SCREEN_WIDTH/2-80 < self.x < SCREEN_WIDTH/2-50:
                self.door_collision = "top"
        if self.move_down:
            if self.y <= SCREEN_HEIGHT-self.bottom_border - self.image.get_height():
                self.y += speed
            elif SCREEN_WIDTH/2-80 < self.x < SCREEN_WIDTH/2-50:
                self.door_collision = "bottom"

    def shoot(self, direction:str):        # generate a new tear if possible
        if len(self.active_tears) < 10 and len(self.active_tears) < self.tears: # active tears list is not full
            self.active_tears.append(Tear(self.x, self.y, direction, self.tear_speed, self.tear_color, self.tear_size, self.borders)) # add new Tear object
        else:                              # active list is full
            for i in range(0, len(self.active_tears)): # look if there are any "dead" tears that can be overwritten
                if self.active_tears[i].is_dead:
                    self.active_tears[i] = Tear(self.x, self.y, direction, self.tear_speed, self.tear_color, self.tear_size, self.borders)
                    break

    def upgrade(self, color:tuple):   # called when an upgrade is picked up
        if color == (200,200,50): self.speed = min(self.speed + 1, 7)
        elif color == (200,50,50):
            self.damage += 1
            self.total_damage = self.damage * self.tear_size
        elif color == (50,50,200): self.tears = min(self.tears + 1, 10)
        elif color == (50,200,50): self.tear_speed = min(self.tear_speed + 1, 20)
        elif color == (100,25,25):
            self.tear_size = min(self.tear_size + 1, 8)
            self.total_damage = self.damage * self.tear_size