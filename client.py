#Trying to use the client

import socket

HOST = "fc00:1337::17" #IP for the virtual machine
PORT = 6667 #the port used

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.sendall(b"TRYING THE CLIENT")
    data = s.recv(1024)

print(f"Received {data!r}")
