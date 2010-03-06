from threading import Thread, Lock
from pygame import time

from udp import UdpServer
from globals import FRAMETIME
from packet import Packet
from player import Player

class Client:
    INITIAL_TIMEOUT = FRAMETIME * 2
    def __init__(self, addr, id, player):
        self.addr = addr
        self.id = id
        self.player = player
        self.timeout = Client.INITIAL_TIMEOUT
        self.events = {}

    def countdown(self):
        self.timeout -= 1

    def ack(self):
        self.timeout = Client.INITIAL_TIMEOUT

    def is_dead(self):
        return self.timeout <= 0


class InputThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent

    def run(self):
        print "Press ENTER to exit."
        a = raw_input()
        self.parent.quit = True


class SocketThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.daemon = True
        self.server = parent.server
        self.clients = parent.clients
        self.lock = parent.lock
        self.parent = parent
        self.next_id = 0

    def run(self):
        while True:
            data, addr = self.server.recv()
            pkg = Packet.unpack(data)
            print "got packet: %s, %s" % (pkg.tick, pkg.players)
            with self.lock:
                net_tick = self.parent.net_tick
                if addr not in self.clients:
                    if pkg.tick == 0 and len(pkg.players) == 0 and len(pkg.input) == 0:
                        self.clients[addr] = Client(addr, self.next_id, Player(50 + self.next_id * 30, 50))
                        self.next_id += 1
                        pkg_response = Packet(net_tick)
                        pkg_response.add(self.clients[addr].id, self.clients[addr].player)
                        self.server.send(pkg_response, addr)
                        print "authenticating new client: %s -> %s" % (addr, self.clients[addr].id)
                    else:
                        print "invalid authentication attempt: %s, %s, %s" % (pkg.tick, pkg.players, pkg.input)
                else:
                    client = self.clients[addr]
                    client.ack()
                    if pkg.tick >= net_tick:
                        if len(pkg.input) > 0:
                            client.events[pkg.tick] = pkg.input
                        #if net_tick not in self.pkg_queue:
                            #self.pkg_queue[net_tick] = []
                        #self.pkg_queue[net_tick].insert(0, pkg)
                    else:
                        print "discard packet (too old: %d < %d)" % (pkg.tick, net_tick)


class GameServer:
    def __init__(self):
        self.quit = False

    def update(self):
        for client in self.clients.values():
            if self.net_tick in client.events: # input events to process
                client.player.input(client.events[self.net_tick])
                del client.events[self.net_tick]
            client.player.logic()
        self.net_tick += 1

    def send_new_state(self):
        pass

    def run(self):
        self.net_tick = 0
        self.clients = {}
        self.lock = Lock()
        self.server = UdpServer(25000)

        self.socket_thread = SocketThread(self)
        self.socket_thread.start()

        print "Server up and running."

        self.input_thread = InputThread(self)
        self.input_thread.start()

        ticks_start = time.get_ticks()
        while not self.quit:
            ticks = time.get_ticks() - ticks_start - self.net_tick * FRAMETIME
            update_count = ticks / FRAMETIME
            with self.lock:
                for i in xrange(update_count):
                    self.update()
                    self.send_new_state()
                    dead_clients = []
                    for addr, client in self.clients.items():
                        client.countdown()
                        if client.is_dead():
                            dead_clients.append(addr)
                    for addr in dead_clients:
                        print "removing client %s (timeout)" % str(addr)
                        del self.clients[addr]
            time.wait(1)


if __name__ == "__main__":
    GameServer().run()

