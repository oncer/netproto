from threading import Thread, Lock
from pygame import time

from udp import UdpServer
from globals import FRAMETIME
from packet import Packet
from np_client import Player

class Client:
    INITIAL_TIMEOUT = FRAMETIME * 2
    def __init__(self, addr, player):
        self.addr = addr
        self.player = player
        self.timeout = Client.INITIAL_TIMEOUT

    def countdown(self):
        self.timeout -= 1

    def ack(self):
        self.timeout = Client.INITIAL_TIMEOUT


class SocketThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.daemon = True
        self.server = parent.server
        self.players = parent.players
        self.lock = parent.lock
        self.pkg_queue = parent.pkg_queue
        self.parent = parent

    def run(self):
        while True:
            data, addr = self.server.recv()
            pkg = Packet.unpack(data)
            with self.lock:
                net_tick = self.parent.net_tick
                if pkg.tick >= net_tick
                    if net_tick not in pkg_queue:
                        pkg_queue[net_tick] = []
                    pkg_queue[net_tick].insert(0, pkg)
                else:
                    print "discard packet (too old)"


class GameServer:
    def __init__(self):
        pass

    def update(self):
        

    def send_new_state(self):
        pass

    def run(self):
        self.net_tick = 0
        self.players = {}
        self.lock = Lock()
        self.server = UdpServer(25000)
        self.socket_thread = SocketThread(self)
        self.pkg_queue = {}

        ticks_start = time.get_ticks()
        while True:
            ticks = time.get_ticks() - ticks_start - self.net_tick * FRAMETIME
            update_count = ticks / FRAMETIME
            with self.lock:
                for i in xrange(update_count):
                    self.update()
                    self.send_new_state()
            time.wait(1)


if __name__ == "__main__":
    GameServer().run()

