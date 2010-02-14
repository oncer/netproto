from socket import *
from time import time

class UdpServer:
    def __init__(self, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("", port))

    def send(self, packet, addr):
        self.socket.sendto(packet.serialize(), 0, addr)

    def recv(self):
        return self.socket.recvfrom(1024)
        

class UdpClient:
    def __init__(self, host, port):
        """ client sends to specified server address """
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("", 27000))
        self.addr = (host, port) # address to send packets to

    def send(self, packet):
        self.socket.sendto(packet.serialize(), 0, self.addr)

    def recv(self):
        return self.socket.recvfrom(1024)

if __name__ == "__main__": # test code
    srv = UdpServer(20000)
    cli = UdpClient("127.0.0.1", 20000)
    
    from threading import Thread
    from time import sleep

    def srv_recv():
        data, addr = srv.recv()
        print "received %s from %s" % (data, addr)

    class DummyPacket:
        def __init__(self, value):
            self.value = value

        def serialize(self):
            return self.value

    t = Thread(target = srv_recv)
    t.daemon = True
    t.start()
    cli.send(DummyPacket("hello world"))
    sleep(1)

