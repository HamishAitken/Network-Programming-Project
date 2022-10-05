#Trying to use the client

import socket


HOST = "fc00:1337::17" #IP for the virtual machine
PORT = 6667 #the port used


#Using AF_INET6 because the host is a string representing a hostname for IPV6
#We use SOCK_STREAM because is a TCP protocol, and not a UDP
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    #Equal line:
    #mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #mysocket.connect(HOST, 6667)
    s.connect((HOST,PORT))

    #Identifying myself!
    s.send(b"Hello! I'm SUPER BOT\n")
    #The b it's something about decoding or bytes
    s.sendall(b"TRYING THE CLIENT\n") #Sending data to the socket
    data = s.recv(1024)

print(f"Received {data!r}")
