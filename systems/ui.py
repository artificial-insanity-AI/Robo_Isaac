import random

import pygame

from assets import EXTRA_LIFE_IMG
from config import BORDERS, SCREEN_WIDTH, SCREEN_HEIGHT

class UISystem:

    def draw_frame(self, game):  # it could've been done much easier, but now it is too late to redo everything =/
        top, left, right, bottom = BORDERS
        frame_color = (50, 50, 50)
        if game.level.flag(game.current_room,1):   # if gg1 (secret room)
            border_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else: border_color = game.level.rgb(game.current_room)
        text_color = (220, 220, 220)

        pygame.draw.rect(game.window, frame_color, (0, 0, SCREEN_WIDTH, top)) # top frame
        pygame.draw.line(game.window, border_color, (left, top), (SCREEN_WIDTH-right, top), width=5) # top-border line
        pygame.draw.rect(game.window, frame_color, (0, 0, left, SCREEN_HEIGHT)) # left frame
        pygame.draw.line(game.window, border_color, (left, top), (left, SCREEN_HEIGHT-bottom), width=5) # left-border line
        pygame.draw.rect(game.window, frame_color, (SCREEN_WIDTH-right, 0, right, SCREEN_HEIGHT)) # right frame
        pygame.draw.line(game.window, border_color, (SCREEN_WIDTH-right, top), (SCREEN_WIDTH-right,SCREEN_HEIGHT-bottom), width=5) # right-border line
        pygame.draw.rect(game.window, frame_color, (0, SCREEN_HEIGHT-bottom, SCREEN_WIDTH, bottom)) # bottom frame
        pygame.draw.line(game.window, border_color, (SCREEN_WIDTH-right, SCREEN_HEIGHT-bottom), (left, SCREEN_HEIGHT-bottom), width=5) # bottom-border line

        current_level = game.game_font.render(f"Current Level: {game.floor}{" "*90}MOOC   <3", True, text_color)
        game.window.blit(current_level, (left+left, (top-24)/2)) # draw current level counter

        for i in range(1,game.robot.health_points + 1): # draw "extra life" indicators on the left
            game.window.blit(game.robot.image, ((left - game.robot.image.get_width())/2-5, top*i + i*25))

        stats = game.game_font.render(f"Robot Stats: ", True, text_color)
        game.window.blit(stats, (SCREEN_WIDTH-right+right/10, top+40)) # draw stats header
        speed = game.game_font.render(f"Speed: {game.robot.speed}", True, (200,200,50))
        game.window.blit(speed, (SCREEN_WIDTH-right+right/5, top+80)) # draw speed stat
        damage = game.game_font.render(f"Dmg: {game.robot.total_damage}", True, (200,00,00))
        game.window.blit(damage, (SCREEN_WIDTH-right+right/5, top+120)) # draw damage stat
        tears = game.game_font.render(f"Tears: {game.robot.tears}", True, (25,25,255))
        game.window.blit(tears, (SCREEN_WIDTH-right+right/5, top+160)) # draw tears stat (max tears on screen)
        tears_speed = game.game_font.render(f"Velocity: {game.robot.tear_speed}", True, (50,200,50))
        game.window.blit(tears_speed, (SCREEN_WIDTH-right+right/5, top+200)) # draw tears velocity stat

        stats = game.game_font.render(f"Total Score: ", True, text_color)
        game.window.blit(stats, (SCREEN_WIDTH-right+right/10, SCREEN_HEIGHT/2 + 100)) # draw score header
        kills = game.game_font.render(f"Kills: {game.kills}", True, text_color)
        game.window.blit(kills, (SCREEN_WIDTH-right+right/5, SCREEN_HEIGHT/2 + 140)) # draw kills score
        coins = game.game_font.render(f"Coins: {game.coins}", True, text_color)
        game.window.blit(coins, (SCREEN_WIDTH-right+right/5, SCREEN_HEIGHT/2 + 180)) # draw coins score

        help_text = game.game_font.render(f"Move:  WASD  |  Shoot:  Arrows  |  Pause:  P or Esc  |  Map:  M or Tab", True, text_color)
        game.window.blit(help_text, (left + left, SCREEN_HEIGHT - bottom * 0.7)) # draw help

    def draw_pause(self, game):
        text = game.game_font.render(f"PAUSE", True, (225,225,225))
        game.window.blit(text, (333, 333))

    def draw_game_over(self, game):
        top, left, right, bottom = BORDERS
        pygame.draw.rect(game.window,(15,0,0),(top,left,SCREEN_WIDTH-left-right,SCREEN_HEIGHT-top-bottom),width=1000)
        text = game.game_font.render(f"GAME OVER", True, (222,222,222))
        text2 = game.game_font.render(f"Press Space to start over", True, (222,222,222))
        text3 = game.game_font.render(f"Press ESC to quit", True, (222,222,222))
        game.window.blit(text, (333, 333))
        game.window.blit(text2, (333, 366))
        game.window.blit(text3, (333, 399))

    def draw_map(self, game):
        k = 45      # size of the squares on the mini-map
        header = game.game_font.render(f"Map: ", True, (40, 40, 40)) # mini-map header
        game.window.blit(header, (150, 120))

        pygame.draw.rect(game.window, (40, 40, 40), (150, 150, 9*k, 7*k)) # mini-map background
        for x in range(9):                            # traverse game.map
            for y in range(7):
                if game.level.flag((y,x), 2):               # check room visible flag
                    if game.level.flag((y,x), 0):           # check cleared flag
                        color = game.level.rgb((y,x))       # use it's real color
                    else:
                        c = game.level.rgb((y,x))       # use darker shades:
                        color = max(c[0]-100, 0),max(c[1]-100, 0),max(c[2]-100, 0)
                else: color = (0,0,0)             # else the room is black on the map until found
                pygame.draw.rect(game.window, color, (150+x*k, 150+y*k, k, k)) # fill current square with color
                pygame.draw.rect(game.window, (111,111,111), (150+x*k, 150+y*k, k, k), width=1) # thin border around each square
                if (y,x) == game.current_room:                                  # mark current room
                    small = pygame.transform.scale(game.robot.image, (k/2, k))  # with small robot icon
                    game.window.blit(small, (150+x*k+0.2*k, 150+y*k, k, k))

    def draw_coins(self, game):
        for coin in game.dropped_coins:
            if not coin.is_dead:
                game.window.blit(coin.image, (coin.x, coin.y))

    def draw_shop_text(self, game):
        stats = game.game_font.render(f"CHOOSE ONE", True, (0, 0, 0))
        game.window.blit(stats, (400, 320))

        stats = game.game_font.render(f"free                                 $20", True, (0, 0, 0))
        game.window.blit(stats, (350, 450))

    def draw_boss_hp_bar(self, game):
        hp = game.enemies[0].hp                          ## get current hp
        one_bar = int(game.enemies[0].starting_hp/10)    ## calculate based on initial boss hp
        hp_bar = f"BOSS HP: [{"="*(hp//one_bar):_<10}]"
        text = game.game_font.render(hp_bar, True, (255, 0, 0))
        game.window.blit(text, (400, (75-24)/2))


# TODO move logic out of two bottom ones back into game.py
    def draw_upgrade(self, position, color, game):
        randcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        randwidth = random.randint(2,5)
        pygame.draw.rect(game.window, color, position)       # color = the type of the upgrade
        pygame.draw.rect(game.window, randcolor, position, width=randwidth) # flashy border

    def draw_extra_life(self, pos, game, state=None):
        game.window.blit(EXTRA_LIFE_IMG, pos)

        if state == "not_allowed":
            color = random.choice([(255,0,0),(155,0,0),(55,0,0)])
            randwidth = random.randint(2,25)
            pygame.draw.rect(game.window, color, pos, width=randwidth)