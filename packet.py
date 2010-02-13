import struct

def packet_unpack(binary_data):

class Packet:
    def __init__(self, tick, players=None):
        self.tick = tick
        if players:
            self.players = players
        else:
            self.players = []

    def add(self, id, player):
        self.players.append((id, player.x, player.y, player.vx, player.vy, player.ax, player.ay))

    def serialize(self):
        p_tick = struct.pack("L", self.tick)
        p_count = struct.pack("I", len(self.players))
        p_players = ""
        for p in self.players:
            p_players += struct.pack("Iiiiiii", *p)
        return p_tick + p_count + p_players

    @classmethod
    def unpack(cls, binary_data):
        players_offset = struct.calcsize("LI")
        player_size = struct.calcsize("Iiiiiii")
        header_data = binary_data[:players_offset]
        players_data = binary_data[players_offset:]
        tick, players_count = struct.unpack("LI", header_data)
        assert(len(players_data) == players_count * player_size)
        players = []
        for i in xrange(players_count):
            offset = i * player_size
            p = struct.unpack("Iiiiiii", players_data[offset:(offset+player_size)])
            players.append(p)
        return cls(tick, players)
 
if __name__ == "__main__": # test code
    p = Packet(2134, [(1, 22, 33, 0, 0, 1, 0), (2, 21, 23, 5, 5, 1, -1)])
    p2 = make_packet(p.serialize())
    assert(len(p.players) == len(p2.players) == 2)
    assert(p.tick == p2.tick)
    assert(p.players[0] == p2.players[0])
    assert(p.players[1] == p2.players[1])
    print "Test OK"

