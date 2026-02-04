import pygame, random

from assets import ROBOT_IMG, MONSTER_IMG, BOSS_IMG, DOOR_IMG
from config import BORDERS, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from entities.coin import Coin


# I found out pygame has build-in collision detection after a big part of the game was already done...
# so some parst are kind of weird improvisation
class RoboIsaac:
    def __init__(self) -> None:
        pygame.init()

        self.borders = BORDERS
        self.robot = Robot(self.borders) # robot object

        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # initial plan was to make resolution configurable, currently it is hard-coded
        self.game_font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Robo-Isaac Game")

        self.level = 1            # game level(stage)
        self.new_level = True     # flag for new level generation
        self.coins = 0            # in-game coins
        self.kills = 0            # in-game score/kill counter
        self.map = [  # 7x9 map, room = RGB tuple(rrr,ggg,bbb). supposed to be temporal, but then I liked it
                      # last number is a flag (it doesn't make the difference for the actual color)
                      # bb1 == room is discovered, visible on the map
                      # gg1 == is a secret room
                      # rr1 == room is cleared, no need to do some things upon entering etc.
                    ]
        self.current_room = 3,4    # starting room is always map[3][4]
        self.upgrades = {}         # upgrades list generated on level creation
        self.dropped_coins = []    # coins currently on the floor        
        self.enemies = []          # enemies currently in the room
        self.map_on = False        # helper variable for displaying the mini-map 
        self.game_over = False     # helper variable for displaying game-over screen
        self.pause = False         # helper variable for displaying pause screen

        self.main_loop()

        ### helper functions ---vvv
    @staticmethod
    def get_n(i:tuple)->list: # returns *n*eighbours (x,y) -> [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        return [(i[0]+1,i[1]),(i[0]-1,i[1]),(i[0],i[1]+1),(i[0],i[1]-1)]
    @staticmethod
    def check_b(n:tuple)->bool: # check if outside the mab *b*orders
        return n[0] > 6 or n[0] < 0 or n[1] > 8 or n[1] < 0
    def rgb(self, i:tuple)->tuple: # just return the elements value (x,y)->(r,g,b)
        return self.map[i[0]][i[1]]
    def set_rgb(self, room:tuple, rgb:tuple)->None: # set new rgb value for (x,y) room
        self.map[room[0]][room[1]] = rgb
    def flag(self, room:tuple, flag:int)->bool: # flag position: 0 or 1 or 2
        return str(self.rgb(room)[flag])[-1] == "1" # True if flag == 1
    def set_flag(self, room:tuple, flag:int)->None: # set flag to 1
        flag_str = str(self.map[room[0]][room[1]][flag])
        flag_str = flag_str[0:-1] + "1"
        rgb_as_list = [self.rgb(room)[0], self.rgb(room)[1], self.rgb(room)[2]]
        rgb_as_list[flag] = int(flag_str)
        self.set_rgb(room, tuple(rgb_as_list))
        ### helper functions ---^^^
    
    def main_loop(self): ####################---main---#########################
        while True:
            if self.new_level:
                self.generate_new_level()
            self.check_events()
            self.draw_window()
            # print(self.rgb(self.current_room)) # test
            self.clock.tick(FPS)

    def generate_new_level(self): # generate current level map

        self.current_room = (3,4) # set starting room <-- and reset the map --v
        self.map = [ #7x9 map, room = RGB tuple(rrr,ggg,bbb). supposed to be temporal but then I liked it
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]
                     #bb1 == room discovered, visible on the map
                     #gg1 == is a secret room
                     #rr1 == room is cleared, no need to do some things upon entering 
        ]
        self.upgrades = {          # pre-generate upgrade objects for each room
            (0, 255, 1):Upgrade(),    # green room upgrade
            (250, 255, 1):Upgrade(),  # yellow room upgrade
            (250, 0, 1): Upgrade()}   # red room upgrade
        self.robot.active_tears = []  # clear all tears
        self.dropped_coins = []       # clear coins

        def how_many_n(target_room:tuple)->int: # how many neighbours exists (helper function)
            neighbour_rooms = self.get_n(target_room)                         # get neighbour cells
            return sum(el in rooms_created for el in neighbour_rooms)  # how many of them are rooms
        
        how_many_rooms = random.randint(1,2) + 6 + min(self.level, 8) * 2   # how many rooms to generate
        rooms_created = [(3,4)] # currently existing rooms ((3,4) is always starting room)
        ends = []          # list of the dead end rooms
        
        while len(rooms_created) < how_many_rooms:    ### generate rooms
            for room in rooms_created:
                neighbours = self.get_n(room)
                if how_many_n(room) < 2:   # check there is no 2 adjacent rooms already
                    for n in neighbours:
                        if len(rooms_created) == how_many_rooms: break # already have enough rooms
                        if n in rooms_created: continue  # already existing room
                        if self.check_b(n):continue      # out of the map range
                        if how_many_n(n) >= 2: continue  # there are 2 adjacent to "n" rooms
                        if random.choice([True, False]): continue # 50% to give up
                        rooms_created.append(n)          # room added to the list
        #                               *** test generated map***
        many_n = False   # clusters helper flag
        for r in rooms_created:
            if how_many_n(r) == 1 and r != (3,4):  # look for dead ends excluding starting room
                ends.append(r)                     # add it to the list of dead ends
            if how_many_n(r) > 3: many_n = True    # if a room somehow got too many neighbours
            
        #     incorrect amount of rooms?            not enough "ends"?   clusters?
        if how_many_rooms != len(set(rooms_created)) or len(ends) < 3 or many_n:
            self.generate_new_level()             # generate the level anew
            return
        #                    *** passed tests. generate map layout ***
        for r in rooms_created:                 # mark all created rooms
            self.set_rgb(r, (0,222,220))        # with the "regular room" color 
        self.new_level = False                  # turn off the new_lvl flag 
        #                            ***SPECIAL ROOMS***
        self.set_rgb((3,4), (251, 255, 251))       # **STARTING** room is white, visible from spawn
        for i in range(-1, -len(ends)-1, -1):      # reverse: should be less likely to get one near the start
            if (3,4) not in self.get_n(ends[i]):   # **BOSS** room can not be adjacent to start room
                self.set_rgb((ends[i]),(250,0,0))  # boss room created = red
                break
        s = random.choice([i for i in ends if self.rgb(i) == (0,222,220)])   # random unused dead end room
        self.set_rgb(s, (250, 255, 0))             # **SHOP** room = yellow
        i = random.choice([i for i in ends if self.rgb(i) == (0,222,220)])
        self.set_rgb(i, (0, 255, 0))               # **UPGRADE** room = green
        
        #**SECRET ROOM** = random non-existing room among those that have most existing neighbours
        # NOTE: undiscovered secret room will not have a visible door or minimap visibility
        ##      to find it shoot the wall in the middle
        candidates = [] # [(n,(x,y)),...] where n is how many non-boss neighbours
        for room in rooms_created:
            for n in self.get_n(room):
                if self.check_b(n): continue        # square is outside the map
                if self.rgb(n) != (0,0,0): continue # square is occupied
                if (250,0,0) in [self.rgb(i) for i in self.get_n(n) if not self.check_b(i)]:
                        continue                             # the boss room is neighbour
                rgb_in_range = [self.rgb(i) for i in self.get_n(n) if not self.check_b(i)]
                r = len(rgb_in_range) - rgb_in_range.count((0,0,0)) # how many adjacent non-boss rooms
                candidates.append((r, n)) # candidate found
        for i in range(4,0,-1): # i = how many existing neighbours, start with maximum 4, then 3...
            roms = [r[1] for r in candidates if r[0] == i] # list all rooms with "i" neighbours
            if roms: # if none with "i" neighbours go look with "i-1" in the next loop
                s = random.choice(roms) # pick random location
                self.set_rgb(s, (0,1,60)) # **secret** room created
                break                     ## 1 == secret room flag

        #########---for testing purposes---########
        # for i in candidates: ### for testing possible secret locations
        # #     self.map[i[1][0]][i[1][1]] = (0,0,251)
        # for i in rooms_created: # turn on visibility for all rooms
        #     self.set_flag(i,2)  ## secret room visibility? edit flag at creation


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
                    # self.game_over = False
                    # self.new_level = True
                    # self.level = 1
                    # self.coins = 0
                    # self.kills = 0
                    RoboIsaac()
                if event.key == pygame.K_ESCAPE:
                    if self.game_over: exit()
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
                exit()

    def draw_window(self):                       # when and what to draw on the screen
        self.window.fill((150, 150, 150))
        self.draw_frame()
        if self.game_over:
            self.draw_game_over()
        elif self.pause:
            self.draw_pause_screen()
        else:
            self.display_map()
            self.robot.move_robot()
            self.window.blit(self.robot.image, (self.robot.x, self.robot.y)) # draw robot
            for enemy in self.enemies:
                enemy.move()
            self.draw_room()
            self.draw_tears()
            self.draw_coins()
            self.draw_enemies()

        pygame.display.flip()
    
    def draw_frame(self):  # it could've been done much easier, but now it is too late to redo everything =/
        top, left, right, bottom = self.borders
        frame_color = (50, 50, 50)
        if self.flag(self.current_room,1):
            border_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else: border_color = self.rgb(self.current_room)
        text_color = (220, 220, 220)
        
        pygame.draw.rect(self.window, frame_color, (0, 0, SCREEN_WIDTH, top)) # top frame
        pygame.draw.line(self.window, border_color, (left, top), (SCREEN_WIDTH-right, top), width=5) # top-border line
        pygame.draw.rect(self.window, frame_color, (0, 0, left, SCREEN_HEIGHT)) # left frame
        pygame.draw.line(self.window, border_color, (left, top), (left, SCREEN_HEIGHT-bottom), width=5) # left-border line
        pygame.draw.rect(self.window, frame_color, (SCREEN_WIDTH-right, 0, right, SCREEN_HEIGHT)) # right frame
        pygame.draw.line(self.window, border_color, (SCREEN_WIDTH-right, top), (SCREEN_WIDTH-right,SCREEN_HEIGHT-bottom), width=5) # right-border line
        pygame.draw.rect(self.window, frame_color, (0, SCREEN_HEIGHT-bottom, SCREEN_WIDTH, bottom)) # bottom frame
        pygame.draw.line(self.window, border_color, (SCREEN_WIDTH-right, SCREEN_HEIGHT-bottom), (left, SCREEN_HEIGHT-bottom), width=5) # bottom-border line
        
        current_level = self.game_font.render(f"Current Level: {self.level}{" "*90}MOOC   <3", True, text_color)
        self.window.blit(current_level, (left+left, (top-24)/2)) # draw current level counter

        for i in range(1,self.robot.health_points + 1): # draw "extra life" indicators on the left
            self.window.blit(self.robot.image, ((left - self.robot.image.get_width())/2-5, top*i + i*25))

        stats = self.game_font.render(f"Robot Stats: ", True, text_color)
        self.window.blit(stats, (SCREEN_WIDTH-right+right/10, top+40)) # draw stats header
        speed = self.game_font.render(f"Speed: {self.robot.speed}", True, (200,200,50))
        self.window.blit(speed, (SCREEN_WIDTH-right+right/5, top+80)) # draw speed stat
        damage = self.game_font.render(f"Dmg: {self.robot.total_damage}", True, (200,00,00))
        self.window.blit(damage, (SCREEN_WIDTH-right+right/5, top+120)) # draw damage stat
        tears = self.game_font.render(f"Tears: {self.robot.tears}", True, (25,25,255))
        self.window.blit(tears, (SCREEN_WIDTH-right+right/5, top+160)) # draw tears stat (max tears on screen)
        tears_speed = self.game_font.render(f"Velocity: {self.robot.tear_speed}", True, (50,200,50))
        self.window.blit(tears_speed, (SCREEN_WIDTH-right+right/5, top+200)) # draw tears velocity stat

        stats = self.game_font.render(f"Total Score: ", True, text_color)
        self.window.blit(stats, (SCREEN_WIDTH-right+right/10, SCREEN_HEIGHT/2 + 100)) # draw score header
        kills = self.game_font.render(f"Kills: {self.kills}", True, text_color)
        self.window.blit(kills, (SCREEN_WIDTH-right+right/5, SCREEN_HEIGHT/2 + 140)) # draw kills score
        coins = self.game_font.render(f"Coins: {self.coins}", True, text_color)
        self.window.blit(coins, (SCREEN_WIDTH-right+right/5, SCREEN_HEIGHT/2 + 180)) # draw coins score

        help_text = self.game_font.render(f"Move:  WASD  |  Shoot:  Arrows  |  Pause:  P or Esc  |  Map:  M or Tab", True, text_color)
        self.window.blit(help_text, (left + left, SCREEN_HEIGHT - bottom * 0.7)) # draw help
    
    def draw_room(self):
        ### draw new room if door entered ###
        if self.robot.door_collision is not None and self.flag(self.current_room, 0): # near the door and room is cleared
        # if self.robot.door_collision != None: # test option instead of above (no cleared requirement)
            direction = self.robot.door_collision

            def navigate(move_direction:str):   # returns connected room in "direction"
                if move_direction == "left":
                    return self.current_room[0], self.current_room[1]-1
                if move_direction == "right":
                    return self.current_room[0], self.current_room[1]+1
                if move_direction == "top":
                    return self.current_room[0]-1, self.current_room[1]
                if move_direction == "bottom":
                    return self.current_room[0]+1, self.current_room[1]
                return None

            if self.flag(navigate(direction),2):        # if visible => should have a door
                self.current_room = navigate(direction) # assign new current room
                if direction in ["left", "right"]:
                    self.robot.x = SCREEN_WIDTH/2 + (SCREEN_WIDTH/2 - self.robot.x  - 130)  # position robot
                if direction in ["top", "bottom"]:                          # approximately
                    self.robot.y = SCREEN_HEIGHT/2 + (SCREEN_HEIGHT/2 - self.robot.y - 140)     # on opposite side
                self.robot.active_tears = []         # delete all tears
                self.dropped_coins = []              # dropped coins are lost if room exited
        ### what to do in the room ###
        if not self.flag(self.current_room, 0):            # uncleared room?
            if self.rgb(self.current_room) == (0, 255, 1):     # green room?
                self.draw_upgrade((450, 375))                    ## spawn upgrade, approx middle if the room
            elif self.rgb(self.current_room) == (250, 255, 1): # shop room?
                self.draw_upgrade((350, 375))                    ## draw upgrade  (free)
                self.draw_extra_life((550, 365))                 ## draw extra life (cost coins)
                stats = self.game_font.render(f"CHOOSE ONE", True, (0, 0, 0))
                self.window.blit(stats, (400, 320))
                stats = self.game_font.render(f"free                                 $20", True, (0, 0, 0))
                self.window.blit(stats, (350, 450))
            elif self.rgb(self.current_room) == (0,1,61):      # secret room?
                for i in range(random.randint(5,9)):             ## spawn some coins
                    self.dropped_coins.append(Coin(self.borders))
                self.set_flag(self.current_room, 0)              ## and set "cleared" flag
            elif self.rgb(self.current_room) == (250,0,1):     # boss room?
                if not self.enemies:                             ## add boss enemy
                    self.enemies.append(Boss(self.level, self.borders))
                    ### draw BOSS HP bar
                hp = self.enemies[0].hp                          ## get current hp
                one_bar = int(self.enemies[0].starting_hp/10)    ## calculate based on initial boss hp
                hp_bar = f"BOSS HP: [{"="*(hp//one_bar):_<10}]"
                text = self.game_font.render(hp_bar, True, (255, 0, 0))
                self.window.blit(text, (400, (75-24)/2))
            elif self.rgb(self.current_room) == (0,222,221):   # regular uncleared room:
                if not self.enemies:                           # spawn some enemies
                    for i in range(random.randint(1,3) + self.level//2):
                        self.enemies.append(Enemy(self.level, self.borders))
        else: self.draw_doors() # !- only if cleared

    def draw_tears(self):
        for tear in self.robot.active_tears: 
            if not tear.is_dead:     # any active tears
                tear.move_tear()     # move
                pygame.draw.circle(self.window, tear.color, (tear.x, tear.y), tear.size, tear.size)

    def draw_doors(self):
        top, left, right, bottom = self.borders
        door = DOOR_IMG
        neighbours = [i for i in self.get_n(self.current_room) if not self.check_b(i)]
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
            if self.flag(i, 1):    # except secret room if it was
                if not secret_door_hit(i) and not self.flag(i, 2):
                    continue       # not hit and not discovered
            if self.rgb(i) == (0,0,0): continue # also skip empty cells
            self.set_flag(i, 2)           # set room as visible 
            self.window.blit(door, position[find_position(i)])  # draw a door icon

        if self.rgb(self.current_room) == (251,0,1):  # cleared boss room
            pos = pygame.Rect(450,350, door.get_width(), door.get_height())
            randwidth = random.randint(2,5)
            randcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            pygame.draw.rect(self.window, randcolor, pos, width=randwidth) # flashy border
            self.window.blit(door, pos)               # draw a door icon on the floor
            if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
                self.level += 1                       # increase level count
                self.new_level = True                 # set generate new level flag

    def draw_upgrade(self, position:tuple):
        upgrd = self.upgrades[self.rgb(self.current_room)]
        # if upgrd.is_dead: return
        x,y = position
        randcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        randwidth = random.randint(2,5)
        pos = pygame.Rect((x, y, 40, 40))
        pygame.draw.rect(self.window, upgrd.color, pos)       # color = the type of the upgrade
        pygame.draw.rect(self.window, randcolor, pos, width=randwidth) # flashy border
        if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
            self.robot.upgrade(upgrd.color)       # upgrade robot stat
            self.set_flag(self.current_room,0)    # and set "cleared" flag for the room

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
                self.set_flag(self.current_room,0)    # and set "cleared" flag for the room
                self.coins -= 20

    def draw_coins(self):
        # if self.dropped_coins:
        for coin in self.dropped_coins:
            if not coin.is_dead:                                     # if not picked up yet
                self.window.blit(coin.image, (coin.x, coin.y))       # draw it on the map
                pos = pygame.Rect(coin.image.get_rect(topleft = (coin.x, coin.y)))
                if pos.colliderect(self.robot.image.get_rect(topleft = (self.robot.x, self.robot.y))):
                    coin.is_dead = True                          # collision detected: mark as dead
                    self.coins += 1                              # and increase coins counter  

    def draw_enemies(self):
        top, left, right, bottom = self.borders
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
                if self.rgb(self.current_room) == (250,0,1):               # boss room:
                    self.draw_upgrade((self.enemies[0].x, self.enemies[0].y))  ## spawn item
                elif not self.rgb(self.current_room) == (251,0,1) and not self.current_room == (3,4):                                                      # non-boss room:
                    for i in range(random.randint(0,3)):                     ## spawn some coins
                        self.dropped_coins.append(Coin(self.borders))
                    self.set_flag(self.current_room, 0)   # if all dead => set "cleared" room flag
                    self.enemies = []                     ## reset the enemies list


    def display_map(self):
        if self.map_on:
            k = 45      # size of the squares on the mini-map
            header = self.game_font.render(f"Map: ", True, (40, 40, 40)) # mini-map header
            self.window.blit(header, (150, 120))

            pygame.draw.rect(self.window, (40, 40, 40), (150, 150, 9*k, 7*k)) # mini-map background
            for x in range(9):                            # traverse self.map
                for y in range(7):
                    if self.flag((y,x), 2):               # check room visible flag
                        if self.flag((y,x), 0):           # check cleared flag
                            color = self.rgb((y,x))       # use it's real color
                        else:
                            c = self.rgb((y,x))       # use darker shades:
                            color = max(c[0]-100, 0),max(c[1]-100, 0),max(c[2]-100, 0)
                    else: color = (0,0,0)             # else the room is black on the map until found
                    pygame.draw.rect(self.window, color, (150+x*k, 150+y*k, k, k)) # fill current square with color
                    pygame.draw.rect(self.window, (111,111,111), (150+x*k, 150+y*k, k, k), width=1) # thin border around each square
                    if (y,x) == self.current_room:                                  # mark current room
                        small = pygame.transform.scale(self.robot.image, (k/2, k))  # with small robot icon
                        self.window.blit(small, (150+x*k+0.2*k, 150+y*k, k, k))
    
    def draw_game_over(self):
        if self.game_over:
            top, left, right, bottom = self.borders
            pygame.draw.rect(self.window,(15,0,0),(top,left,SCREEN_WIDTH-left-right,SCREEN_HEIGHT-top-bottom),width=1000)
            text = self.game_font.render(f"GAME OVER", True, (222,222,222))
            text2 = self.game_font.render(f"Press Space to start over", True, (222,222,222))
            text3 = self.game_font.render(f"Press ESC to quit", True, (222,222,222))
            self.window.blit(text, (333, 333))
            self.window.blit(text2, (333, 366))
            self.window.blit(text3, (333, 399))

    def draw_pause_screen(self):
        if self.pause:
            text = self.game_font.render(f"PAUSE", True, (225,225,225))
            self.window.blit(text, (333, 333))
        
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

class Boss(Enemy):       # basically just an enemy with increased image size and stats
    def __init__(self, level: int, borders) -> None:
        super().__init__(level, borders)
        self.image = BOSS_IMG
        self.speed += 1
        self.hp *= 10
        self.starting_hp = self.hp
        self.x = 500
        self.y = 400

if __name__ == "__main__":
    RoboIsaac()