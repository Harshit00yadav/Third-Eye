import socket
from threading import Thread


class NetListener:
    def __init__(self):
        self.HOST = '0.0.0.0'
        self.LPORT = 9999

    def send_command(self):
        while True:
            cmd = input() + '\n'
            self.conn.send(cmd.encode())
            if cmd == "exit\n":
                break

    def recv_output(self):
        while True:
            data = self.conn.recv(1024).decode(errors="ignore")
            print(data)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.HOST, self.LPORT))
        print("listening on", self.HOST, self.LPORT)
        self.socket.listen(1)
        self.conn, addr = self.socket.accept()
        print("connected to", addr)
        Thread(target=self.recv_output, args=[], daemon=True).start()
        m_ = Thread(target=self.send_command, args=[])
        m_.start()
        m_.join()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
