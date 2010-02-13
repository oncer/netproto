from socket import *

class UdpServer:
    def __init__(self, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("", port))

    def recv(self):
        return self.socket.recvfrom(1024)
        

class UdpClient:
    def __init__(self, host, port):
        """ client sends to specified server address """
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("", 27000))
        self.addr = (host, port) # address to send packets to

    def send(self, packet):
        self.socket.sendto(packet.serialize(), self.addr)

