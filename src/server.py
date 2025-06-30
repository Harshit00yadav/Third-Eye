import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 8888))

server.listen(2)

while True:
    print("listening for connections...")
    client1, addr1 = server.accept()
    data1 = client1.recv(1024)
    print(f"client1 connected from {addr1}")
    client2, addr2 = server.accept()
    data2 = client2.recv(1024)
    print(f"client2 connected from {addr2}")

    print("swaping data")
    client2.send(data1)
    client2.close()
    client1.send(data2)
    client1.close()
