#!/usr/bin/python

from pygame import display, event, draw, time
from pygame.locals import *

"""for now, we make it a single player game"""

class GameState:
    def __init__(self, num_players=1):
        self.players = [Player(i*40, 40) for i in xrange(1,num_players + 1)]

class Player:
    MAX_SPEED = 4
    RADIUS = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0

    def input(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.ax = -1
                elif e.key == K_RIGHT:
                    self.ax = 1
                elif e.key == K_UP:
                    self.ay = -1
                elif e.key == K_DOWN:
                    self.ay = 1
            elif e.type == KEYUP:
                if e.key == K_LEFT and self.ax == -1\
                    or e.key == K_RIGHT and self.ax == 1:
                    self.ax = 0
                if e.key == K_UP and self.ay == -1\
                    or e.key == K_DOWN and self.ay == 1:
                    self.ay = 0

    def logic(self):
        if self.ax != 0:
            self.vx += self.ax / 5.0
            if self.vx > Player.MAX_SPEED:
                self.vx = Player.MAX_SPEED
            if self.vx < -Player.MAX_SPEED:
                self.vx = -Player.MAX_SPEED
        else:
            self.vx *= 0.97
            if self.vx > 0 and self.vx < 0.33\
                or self.vx < 0 and self.vx > -0.33:
                self.vx = 0

        if self.ay != 0:
            self.vy += self.ay / 5.0
            if self.vy > Player.MAX_SPEED:
                self.vy = Player.MAX_SPEED
            if self.vy < -Player.MAX_SPEED:
                self.vy = -Player.MAX_SPEED
        else:
            self.vy *= 0.97
            if self.vy > 0 and self.vy < 0.33\
                or self.vy < 0 and self.vy > -0.33:
                self.vy = 0

        self.x += self.vx
        self.y += self.vy
    
    def draw(self, s):
        color = (255, 255, 255)
        pos = (int(self.x), int(self.y))
        draw.circle(s, color, pos, Player.RADIUS)

class Game:
    def __init__(self):
        display.init()
        self.run()

    def input(self):
        events = []
        for e in event.get():
            events.append(e)
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.quit = True
        return events

    def run(self):
        self.screen = display.set_mode((640, 480), 0, 0)
        self.quit = False
        self.gamestate = GameState()
        while not self.quit:
            events = self.input()
            ticks_left = 0
            for player in self.gamestate.players:
                player.input(events)
                player.logic()

                self.screen.fill((120, 120, 128))
                player.draw(self.screen)
                display.flip()

                time.wait(5)

if __name__ == "__main__":
    Game()

