import random
import sys

import pygame

from assets import DOOR_IMG
from config import BORDERS, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from entities.boss import Boss
from entities.coin import Coin
from entities.enemy import Enemy
from entities.robot import Robot
from systems.level_generator import LevelGenerator
from systems.ui import UISystem


# I found out pygame has build-in collision detection after a big part of the game was already done...
# so some parst are kind of weird improvisation
class RoboIsaac:
    def __init__(self) -> None:
        pygame.init()

        self.floor = 1              # current game level(stage) number
        self.level = None           # will hold Level object
        self.current_room = None    # will hold Level object

        # per-level state
        self.robot = Robot(BORDERS) # robot object
        self.dropped_coins = []    # coins currently on the floor
        self.enemies = []          # enemies currently in the room
        self.new_level = True       # flag for new level generation
        self.coins = 0              # in-game coins
        self.kills = 0              # in-game score/kill counter

        # UI & window
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # initial plan was to make resolution configurable, currently it is hard-coded
        self.game_font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Robo-Isaac Game")
        self.ui = UISystem()

        # helper variables
        self.running = False
        self.map_on = False        # displaying the mini-map
        self.game_over = False     # displaying game-over screen
        self.pause = False         # displaying pause screen

        self.run()

    def run(self):
        self.running = True
        while self.running:
            if self.new_level:
                self.start_level()
            self.check_events()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def start_level(self):
        gen = LevelGenerator(self.floor)
        self.level = gen.generate()
        self.current_room = self.level.start_room

        # reset per-level state
        self.robot.active_tears = []    # clear all tears
        self.dropped_coins = []         # clear coins
        self.enemies = []               # clear enemies
        self.new_level = False          # new_level = False



    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.robot.shoot("left")
                if event.key == pygame.K_RIGHT:
                    self.robot.shoot("right")
                if event.key == pygame.K_UP:
                    self.robot.shoot("top")
                if event.key == pygame.K_DOWN:
                    self.robot.shoot("bottom")
                if event.key == pygame.K_a:
                    self.robot.move_left = True
                if event.key == pygame.K_d:
                    self.robot.move_right = True
                if event.key == pygame.K_w:
                    self.robot.move_up = True
                if event.key == pygame.K_s:
                    self.robot.move_down = True
                if event.key in (pygame.K_m, pygame.K_TAB):
                    self.map_on = True
                if event.key == pygame.K_SPACE and self.game_over:
                    self.restart_game()
                if event.key == pygame.K_ESCAPE:
                    if self.game_over: self.running = False
                    elif self.pause: self.pause = False
                    else: self.pause = True
                if event.key == pygame.K_p:
                    if self.pause: self.pause = False
                    else: self.pause = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.robot.move_left = False
                if event.key == pygame.K_d:
                    self.robot.move_right = False
                if event.key == pygame.K_w:
                    self.robot.move_up = False
                if event.key == pygame.K_s:
                    self.robot.move_down = False
                if event.key in (pygame.K_m, pygame.K_TAB):
                    self.map_on = False

            if event.type == pygame.QUIT:
                self.running = False

    def render(self):

        self.window.fill((150, 150, 150))
        self.ui.draw_frame(self)
        if self.game_over:
            self.ui.draw_game_over(self)
        elif self.pause:
            self.ui.draw_pause(self)
        elif self.map_on:
            self.ui.draw_map(self)
        else:
            self.update_game()

            self.window.blit(self.robot.image, (self.robot.x, self.robot.y)) # draw robot
            self.draw_room()
            self.process_tears()
            self.ui.draw_coins(self)
            self.draw_enemies()

        pygame.display.flip()



    def update_game(self):
        self.update_room_transition()
        self.update_room_logic()
        self.update_coin_pickups()
        self.robot.move_robot()
        for enemy in self.enemies:
            enemy.move()

    def update_room_transition(self):
        if self.robot.door_collision is None:           # not near the door
            return

        if not self.level.flag(self.current_room, 0):   # room is not cleared
            return

        direction = self.robot.door_collision
        next_room = self.level.navigate(self.current_room, direction)

        if not self.level.flag(next_room, 2):   # not visible => should not have a door
            return

        self.current_room = next_room

        if direction in ["left", "right"]:
            self.robot.x = SCREEN_WIDTH/2 + (SCREEN_WIDTH/2 - self.robot.x  - 130)
        if direction in ["top", "bottom"]:
            self.robot.y = SCREEN_HEIGHT/2 + (SCREEN_HEIGHT/2 - self.robot.y - 140)

        self.robot.active_tears = []
        self.dropped_coins = []

    def update_room_logic(self):

        if self.level.flag(self.current_room, 0):   # uncleared room?
            return

        room_color = self.level.rgb(self.current_room)

        if room_color == (0, 255, 1):   # UPGRADE ROOM
            pass

        elif room_color == (250, 255, 1):   # SHOP ROOM
            pass

        elif room_color == (0, 1, 61):      # SECRET ROOM
            for _ in range(random.randint(5, 9)):
                self.dropped_coins.append(Coin(BORDERS))    # spawn some coins
            self.level.set_flag(self.current_room, 0)       # set "cleared" flag

        elif room_color == (250, 0, 1):     # BOSS ROOM
            if not self.enemies:            # add boss enemy
                self.enemies.append(Boss(self.floor, BORDERS))

        elif room_color == (0, 222, 221):   # NORMAL ROOM
            if not self.enemies:            # spawn some enemies
                for _ in range(random.randint(1, 3) + self.floor // 2):
                    self.enemies.append(Enemy(self.floor, BORDERS))


    def draw_room(self):

        room_color = self.level.rgb(self.current_room)

        ### what to do in the room ###
        if not self.level.flag(self.current_room, 0):       # uncleared room?
            if room_color == (0, 255, 1):                   # green room?
                self.draw_upgrade((450, 375))   # spawn upgrade, approx middle if the room
            elif room_color == (250, 255, 1):               # shop room?
                self.draw_upgrade((350, 375))               # draw upgrade  (free)
                self.draw_extra_life((550, 365))            # draw extra life (cost coins)

                stats = self.game_font.render(f"CHOOSE ONE", True, (0, 0, 0))
                self.window.blit(stats, (400, 320))

                stats = self.game_font.render(f"free                                 $20", True, (0, 0, 0))
                self.window.blit(stats, (350, 450))

            elif room_color == (250,0,1):       # boss room?
                ### draw BOSS HP bar
                if self.enemies:
                    hp = self.enemies[0].hp                          ## get current hp
                    one_bar = int(self.enemies[0].starting_hp/10)    ## calculate based on initial boss hp
                    hp_bar = f"BOSS HP: [{"="*(hp//one_bar):_<10}]"
                    text = self.game_font.render(hp_bar, True, (255, 0, 0))
                    self.window.blit(text, (400, (75-24)/2))

        else: self.draw_doors() # !- only if cleared

    def process_tears(self):
        for tear in self.robot.active_tears:
            if not tear.is_dead:     # any active tears
                tear.move_tear()     # move
                pygame.draw.circle(self.window, tear.color, (tear.x, tear.y), tear.size, tear.size)

    def draw_doors(self):
        top, left, right, bottom = BORDERS
        door = DOOR_IMG
        neighbours = [i for i in self.level.neighbors(self.current_room) if not self.level.in_bounds(i)]
        position = {"top":((SCREEN_WIDTH - left - right) / 2 + left - door.get_width() / 2, top / 2),
                    "bottom":((SCREEN_WIDTH - left - right) / 2 + left - door.get_width() / 2, SCREEN_HEIGHT - bottom * 1.5),
                    "left":(left*0.7,(SCREEN_HEIGHT-top-bottom)/2+top-door.get_height()/2),
                    "right":(SCREEN_WIDTH-right*1.15,(SCREEN_HEIGHT-top-bottom)/2+top-door.get_height()/2)}

        def find_position(room:tuple):  # door! where?
            if room[1] == self.current_room[1]:
                return "bottom" if room[0] > self.current_room[0] else "top"
            else: return "right" if room[1] > self.current_room[1] else "left"
        def secret_door_hit(room):      # check if hidden door was hit
            secret_pos = find_position(room)
            for tear in [i for i in self.robot.active_tears if i.is_dead == True]:
                if secret_pos == tear.direction:
                    x1 = (SCREEN_WIDTH-left-right)/2+left-door.get_width()
                    x2 = (SCREEN_WIDTH-left-right)/2+left+door.get_width()
                    y1 = (SCREEN_HEIGHT-top-bottom)/2+top-door.get_height()/2
                    y2 = (SCREEN_HEIGHT-top-bottom)/2+top+door.get_height()/2
                    if (x1 <= tear.x <= x2) or (y1 <= tear.y <= y2):
                        return True
            return False

        for i in neighbours:        # go thru connected rooms
            if self.level.flag(i, 1):    # except secret room if it was
                if not secret_door_hit(i) and not self.level.flag(i, 2):
                    continue       # not hit and not discovered
            if self.level.rgb(i) == (0,0,0): continue # also skip empty cells
            self.level.set_flag(i, 2)           # set room as visible
            self.window.blit(door, position[find_position(i)])  # draw a door icon

        if self.level.rgb(self.current_room) == (251,0,1):  # cleared boss room
            pos = pygame.Rect(450,350, door.get_width(), door.get_height())
            randwidth = random.randint(2,5)
            randcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            pygame.draw.rect(self.window, randcolor, pos, width=randwidth) # flashy border
            self.window.blit(door, pos)               # draw a door icon on the floor
            if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
                self.floor += 1                       # increase level count
                self.new_level = True                 # set generate new level flag

    def draw_upgrade(self, position:tuple):
        upgrd = self.level.upgrades[self.level.rgb(self.current_room)]
        # if upgrd.is_dead: return
        x,y = position
        randcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        randwidth = random.randint(2,5)
        pos = pygame.Rect((x, y, 40, 40))
        pygame.draw.rect(self.window, upgrd.color, pos)       # color = the type of the upgrade
        pygame.draw.rect(self.window, randcolor, pos, width=randwidth) # flashy border
        if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
            self.robot.upgrade(upgrd.color)       # upgrade robot stat
            self.level.set_flag(self.current_room,0)    # and set "cleared" flag for the room

    def draw_extra_life(self, position:tuple):
        image = self.robot.image
        image = pygame.transform.scale(image, (image.get_width()*0.7, image.get_height()*0.7))
        x,y = position
        self.window.blit(image, (x, y))
        pos = pygame.Rect((x, y, image.get_width(), image.get_height()))
        if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
            if self.robot.health_points > 5 or self.coins < 20:
                color = random.choice([(255,0,0),(155,0,0),(55,0,0)])
                randwidth = random.randint(2,25)
                pygame.draw.rect(self.window, color, pos, width=randwidth) # flashy border
            else:
                self.robot.health_points += 1         # add one life
                self.level.set_flag(self.current_room,0)    # and set "cleared" flag for the room
                self.coins -= 20

    def update_coin_pickups(self):
        for coin in self.dropped_coins:
            if not coin.is_dead and coin.rect().colliderect(self.robot.rect()):
                coin.is_dead = True
                self.coins += 1

    def draw_enemies(self):
        top, left, right, bottom = BORDERS
        if self.enemies:
            for enemy in self.enemies:
                if not enemy.is_dead:                                    # if enemy alive
                    self.window.blit(enemy.image, (enemy.x, enemy.y))    # draw it
                    pos = pygame.Rect(enemy.image.get_rect(topleft = (enemy.x, enemy.y)))
                    pos_r = self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))
                    if pos.colliderect(pos_r):                           # if robot collision
                        self.robot.health_points -= 1                    # spend one extra life
                        pygame.draw.rect(self.window, (255,0,0), pos, width=50)    #  highlight enemy
                        pygame.display.flip()
                        pygame.time.wait(1000)
                        pygame.draw.rect(self.window, (155,0,0), pos_r, width=100) #  red robot
                        pygame.display.flip()
                        pygame.time.wait(1000)
                        pygame.draw.rect(self.window,(25,0,0),(top,left,SCREEN_WIDTH-left-right,SCREEN_HEIGHT-top-bottom),width=1000)
                        pygame.display.flip()                                      #  red screen
                        if self.robot.health_points >= 0:          # if was not last life
                            self.enemies = []
                            self.dropped_coins = []
                            self.robot.active_tears = []
                            self.current_room = 3,4                ## respawn in the starting room
                            pygame.time.wait(500)
                        else:
                            self.game_over = True                  ## else - game over!
                    for tear in self.robot.active_tears:
                        if not tear.is_dead:
                            if pos.collidepoint(tear.x, tear.y):         # detected tear collision
                                enemy.hp -= self.robot.total_damage      # reduce enemy hp
                                if enemy.hp <= 0:                        # killed?
                                    enemy.is_dead = True
                                    self.kills += 1
                                tear.tear_collision()                    # call method for tear explosion
                                pygame.draw.circle(self.window, tear.color, (tear.x, tear.y), tear.size, tear.size)
            if len([i for i in self.enemies if i.is_dead == True]) == len(self.enemies): # all enemies killed!
                if self.level.rgb(self.current_room) == (250,0,1):               # boss room:
                    self.draw_upgrade((self.enemies[0].x, self.enemies[0].y))  ## spawn item
                elif not self.level.rgb(self.current_room) == (251,0,1) and not self.current_room == (3,4):                                                      # non-boss room:
                    for i in range(random.randint(0,3)):                     ## spawn some coins
                        self.dropped_coins.append(Coin(BORDERS))
                    self.level.set_flag(self.current_room, 0)   # if all dead => set "cleared" room flag
                    self.enemies = []                     ## reset the enemies list


    def restart_game(self):
        self.floor = 1
        self.coins = 0
        self.kills = 0
        self.game_over = False
        self.pause = False
        self.new_level = True

        self.robot = Robot(BORDERS)
        self.dropped_coins = []
        self.enemies = []
