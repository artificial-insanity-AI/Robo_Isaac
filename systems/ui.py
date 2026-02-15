import random

import pygame

from config import BORDERS, SCREEN_WIDTH, SCREEN_HEIGHT, FPS

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
        ...
    def draw_game_over(self, game):
        ...
    def draw_map(self, game):
        ...
