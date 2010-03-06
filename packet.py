import struct
from pygame.event import Event
from pygame.locals import *

class Packet:
    def __init__(self, tick, players=None, input=None):
        """players: [(id, x, y, vx, vy, ax, ay)]
           input: [(key, down)]

           client-to-server: input
           server-to-client: players
        """
        self.tick = tick
        if players:
            self.players = players
        else:
            self.players = []
        if input:
            self.input = input
        else:
            self.input = []

    def add_player(self, id, player):
        self.players.append((id, player.x, player.y, player.vx, player.vy, player.ax, player.ay))

    def add_input(self, event):
        self.input.append(event)

    def serialize(self):
        p_ret = ""
        p_ret += struct.pack("L", self.tick) # current tick
        p_ret += struct.pack("I", len(self.players)) # number of player states
        p_ret += struct.pack("I", len(self.input)) # numer of input events
        for p in self.players:
            p_ret += struct.pack("Iiiiiii", *p) # player state
        for i in self.input:
            p_ret += struct.pack("II", i.key, i.type) # input event
        return p_ret

    @classmethod
    def unpack(cls, binary_data):
        player_size = struct.calcsize("Iiiiiii")
        input_size = struct.calcsize("II")
        players_offset = struct.calcsize("LII")
        header_data = binary_data[:players_offset]
        tick, players_count, input_count = struct.unpack("LII", header_data)
        players_length = players_count * player_size
        input_offset = players_offset + players_length
        input_length = input_count * input_size
        players_data = binary_data[players_offset:(players_offset + players_length)]
        input_data = binary_data[input_offset:(input_offset + input_length)]
        players = []
        for i in xrange(players_count):
            offset = i * player_size
            t = struct.unpack("Iiiiiii", players_data[offset:(offset + player_size)])
            players.append(t)
        input = []
        for i in xrange(input_count):
            offset = i * input_size
            key, type = struct.unpack("II", input_data[offset:(offset + input_size)])
            input.append(Event(type,key=key))
        return cls(tick, players, input)
 
if __name__ == "__main__": # test code
    p1 = Packet(2134, [(1, 22, 33, 0, 0, 1, 0), (2, 21, 23, 5, 5, 1, -1)])
    p1u = Packet.unpack(p1.serialize())
    assert(len(p1.players) == len(p1u.players) == 2)
    assert(len(p1.input) == len(p1u.input) == 0)
    assert(p1.tick == p1u.tick == 2134)
    assert(p1.players[0] == p1u.players[0])
    assert(p1.players[1] == p1u.players[1])
    print "--> Packing/Unpacking of players OK"
    
    p2 = Packet(2135, [], [Event(KEYDOWN,key=K_LEFT), Event(KEYUP,key=K_UP)])
    p2u = Packet.unpack(p2.serialize())
    assert(len(p2.players) == len(p2u.players) == 0)
    assert(len(p2.input) == len(p2u.input) == 2)
    assert(p2.tick == p2u.tick == 2135)
    assert(p2.input[0].key == p2u.input[0].key)
    assert(p2.input[1].type == p2u.input[1].type)
    print "--> Packing/Unpacking of input events OK"

    print "==> Test OK"

