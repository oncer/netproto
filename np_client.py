#!/usr/bin/python

from pygame import display, event, draw, time
from pygame.locals import *
from threading import Thread, Lock

from globals import *
from packet import Packet
from udp import UdpClient 

"""let's talk about multiplayer"""

class GameState:
    def __init__(self, num_players=1):
        self.players = [Player(i*40, 40) for i in xrange(1,num_players + 1)]

class Player:
    MAX_SPEED = 7
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
            self.vx += self.ax / 2.0
            if self.vx > Player.MAX_SPEED:
                self.vx = Player.MAX_SPEED
            if self.vx < -Player.MAX_SPEED:
                self.vx = -Player.MAX_SPEED
        else:
            self.vx *= 0.94
            if self.vx > 0 and self.vx < 0.33\
                or self.vx < 0 and self.vx > -0.33:
                self.vx = 0

        if self.ay != 0:
            self.vy += self.ay / 2.0
            if self.vy > Player.MAX_SPEED:
                self.vy = Player.MAX_SPEED
            if self.vy < -Player.MAX_SPEED:
                self.vy = -Player.MAX_SPEED
        else:
            self.vy *= 0.94
            if self.vy > 0 and self.vy < 0.33\
                or self.vy < 0 and self.vy > -0.33:
                self.vy = 0

        self.x += self.vx
        if self.x < Player.RADIUS and self.vx < 0:
            self.x = 2 * Player.RADIUS - self.x
            self.vx = -self.vx
        elif self.x > (WIDTH - Player.RADIUS) and self.vx > 0:
            self.x = 2 * (WIDTH - Player.RADIUS) - self.x
            self.vx = -self.vx

        self.y += self.vy
        if self.y < Player.RADIUS and self.vy < 0:
            self.y = 2 * Player.RADIUS - self.y
            self.vy = -self.vy
        elif self.y > (HEIGHT - Player.RADIUS) and self.vy > 0:
            self.y = 2 * (HEIGHT - Player.RADIUS) - self.y
            self.vy = -self.vy
    
    def draw(self, s):
        color = (255, 255, 255)
        pos = (int(self.x), int(self.y))
        draw.circle(s, color, pos, Player.RADIUS)


class SocketThread(Thread):
    def __init__(self, parent):
        self.parent = parent
        self.lock = parent.lock

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

    def set_state(self, pkg):
        for p in pkg.players:
            id, x, y, vx, vy, ax, ay = p
            while id >= len(self.gamestate.players):
                self.gamestate.players.append(Player(200, 200))
            player = self.gamestate.players[id]
            player.x = x
            player.y = y
            player.vx = vx
            player.vy = vy
            player.ax = ax
            player.ay = ay
        self.net_tick = pkg.tick
        pass # TODO: truncate command queue

    def authenticate(self):
        """ call this before opening the game
        gets the current tick from the server
        and synchronizes the game state """

        def threaded_recv(retlist):
            response, addr = self.client.recv()
            retlist.append(response)

        pkg_request = Packet(0)
        self.client.send(pkg_request)
        retlist = []
        t = Thread(target = lambda: threaded_recv(retlist))
        t.daemon = True
        t.start()
        wait_start = time.get_ticks()
        wait_end = wait_start + 1000
        while len(retlist) <= 0 and time.get_ticks() < wait_end:
            time.wait(1)

        if len(retlist) > 0:
            response = retlist[0]
            pkg_response = Packet.unpack(response)
            self.tick_offset = pkg_response.tick + 5 # start 5 ticks ahead of the server
            self.id = pkg_response.players[0][0]
            self.set_state(pkg_response)
        else:
            raise RuntimeError("Server not responding")

    def send_state(self):
        """ call only after authenticate, otherwise self.id is undefined """

        ticks = self.net_tick + self.tick_offset
        pkg = Packet(ticks)
        pkg.add(self.id, self.gamestate.players[self.id])
        self.client.send(pkg)

    def run(self):
        self.screen = display.set_mode((WIDTH, HEIGHT), 0, 0)
        display.set_caption("NetProto Client", "np_cli")
        self.quit = False
        self.gamestate = GameState(0)

        self.lock = Lock()
        self.client = UdpClient("127.0.0.1", 25000)

        print "Authenticating..."
        try:
            self.authenticate()
        except RuntimeError as e:
            print e
            return
        self.net_tick = 0
        print "Start game at tick %d." % self.tick_offset
        t_start = time.get_ticks()
        while not self.quit:

            t = time.get_ticks() - t_start - self.net_tick * FRAMETIME

            # GAMESTATE LOGIC
            ticks = t / FRAMETIME
            for i in xrange(ticks):
                events = self.input()
                for player in self.gamestate.players:
                    player.input(events)
                    player.logic()
                self.send_state()
                self.net_tick += 1

            # DISPLAY LOGIC
            if ticks > 0:
                self.screen.fill((120, 120, 128))
                for player in self.gamestate.players:
                    player.draw(self.screen)
                    display.flip()

            time.wait(1)


if __name__ == "__main__":
    Game()

