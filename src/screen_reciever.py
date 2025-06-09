import socket
import numpy
import cv2
import zlib
import stun
from random import randint


class Peer:
    def __init__(self):
        self.initialize_data()
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer_socket.bind(('', self.port))
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def initialize_data(self):
        self.public_ip = self.get_public_ip()
        self.private_ip = self.get_private_ip()
        self.port = randint(1000, 9999)

    def listen(self, buffersize):
        while True:
            data, addr = self.peer_socket.recvfrom(buffersize)
            try:
                decompressed = zlib.decompress(data)
                np_arr = numpy.frombuffer(decompressed, numpy.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow("Received", frame)
                if cv2.waitKey(1) == 27:
                    break
            except zlib.error as e:
                print("Decompression error:", e)

    def get_public_ip(self):
        _, public_ip, _ = stun.get_ip_info(
            stun_host="stun.l.google.com",
            stun_port=19302
        )
        return public_ip

    def get_private_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return None

    def get_rendezvous_data(self, server_addr):
        data = f"{self.public_ip}@{self.private_ip}@{self.port}"
        self.tcp_client.connect(server_addr)
        self.tcp_client.send(data.encode('utf-8'))
        data = self.tcp_client.recv(1024).decode('utf-8')
        data = data.split('@')
        port = int(data[2])
        if data[0] == self.public_ip:
            return (data[1], port)
        else:
            return (data[0], port)

    def punch_hole(self, address):
        self.peer_socket.sendto(b'0', address)


def view_agentscreen(addr_str):
    BUFFERSIZE = 65536
    p = Peer()
    tcp_saddr = (addr_str.split(':')[0], int(addr_str.split(':')[1]))
    p2addr = p.get_rendezvous_data(tcp_saddr)
    p.punch_hole(p2addr)
    p.listen(BUFFERSIZE)
