#!/usr/bin/python

from pygame import display, event, draw, time
from pygame.locals import *
from threading import Thread, Lock

from globals import *
from player import Player
from packet import Packet
from udp import UdpClient 

"""let's talk about multiplayer
    TODO: receive server state (processing functions already implemented)
"""

class GameState:
    def __init__(self):
        self.players = {}


class SocketThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.daemon = True
        self.lock = parent.lock
        self.client = parent.client
        self.parent = parent

    def run(self):
        while True:
            data, addr = self.client.recv()
            print "client received: %s %s" % (data, addr)


class TickEvent:
    def __init__(self, tick, event):
        self.tick = tick
        self.event = event

class Game:
    def __init__(self):
        display.init()
        self.run()

    def input(self):
        events = []
        for e in event.get():
            events.append(e)
            self.past_events.append(TickEvent(self.net_tick, e))
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.quit = True
        return events

    def process_tick(self, events):
        for id, player in self.gamestate.players.items():
            if id == self.id:
                player.input(events)
            player.logic()

    def set_state(self, pkg, backtrack=True):
        for p in pkg.players:
            id, x, y, vx, vy, ax, ay = p
            if id not in self.gamestate.players:
                self.gamestate.players[id] = Player(0,0)
            player = self.gamestate.players[id]
            player.x = x
            player.y = y
            player.vx = vx
            player.vy = vy
            player.ax = ax
            player.ay = ay
        if backtrack:
            tick = pkg.tick
            while tick < self.net_tick + self.tick_offset: # apply user input to new state
                trunc_indices = [] # list indices to remove (too old)
                events = [] # list of events to apply
                for i in xrange(len(self.past_input)):
                    if self.past_input[i].tick < tick:
                        trunc_queue.append(i)
                    elif self.past_input[i].tick == tick:
                        apply_list.append(self.past_input[i].event)
                    elif self.past_input[i].tick > tick:
                        break # assuming the list is sorted in ascending order
                tick += 1
                for idx in trunc_indices:
                    del self.past_input[idx]
                self.process_tick(events)

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
            self.set_state(pkg_response, backtrack=False)
        else:
            raise RuntimeError("Server not responding")

    def send_state(self, events):
        ticks = self.net_tick + self.tick_offset
        pkg = Packet(ticks)
        for event in events:
            if event.type in [KEYDOWN, KEYUP]:
                pkg.add_input(event)
        self.client.send(pkg)

    def run(self):
        self.screen = display.set_mode((WIDTH, HEIGHT), 0, 0)
        display.set_caption("NetProto Client", "np_cli")
        self.quit = False
        self.gamestate = GameState()

        self.lock = Lock()
        self.client = UdpClient("127.0.0.1", 25000)

        print "Authenticating..."
        try:
            self.authenticate()
        except RuntimeError as e:
            print e
            return
        self.past_events = []
        self.net_tick = 0
        print "Start game at tick %d." % self.tick_offset
        t_start = time.get_ticks()
        while not self.quit:

            t = time.get_ticks() - t_start - self.net_tick * FRAMETIME

            # GAMESTATE LOGIC
            ticks = t / FRAMETIME
            for i in xrange(ticks):
                events = self.input()
                self.send_state(events)
                self.process_tick(events)
                self.net_tick += 1

            # DISPLAY LOGIC
            if ticks > 0:
                self.screen.fill((120, 120, 128))
                for player in self.gamestate.players.values():
                    player.draw(self.screen)
                display.flip()

            time.wait(1)


if __name__ == "__main__":
    Game()

