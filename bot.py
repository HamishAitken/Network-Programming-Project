#Trying to use the client

import socket


HOST = "fc00:1337::17" #IP for the virtual machine
PORT = 6667 #the port used

botnick = "bot"

#Using AF_INET6 because the host is a string representing a hostname for IPV6
#We use SOCK_STREAM because is a TCP protocol, and not a UDP
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    
    s.connect((HOST,PORT))
    s.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "n", "UTF-8")) #Wset all the fields to the bot nickname
    s.send(bytes("NICK "+ botnick +"n", "UTF-8")) # assign the nick to the bot

    def ping(): # respond to server Pings.  
    ircsock.send(bytes("PONG :pingisn", "UTF-8"))


    #Identifying myself!
    
    
    data = s.recv(1024)

print(f"Received {data!r}")
