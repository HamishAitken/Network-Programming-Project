#Trying to use the client

import socket

#def ping(): # respond to server Pings.  
#    ircSocket.send(bytes("PONG :pingisn", "UTF-8"))

ircSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) 

HOST = "fc00:1337::17" #IP for the virtual machine
PORT = 6667 #the port used

botnick = "bot"
channel = "#test"


 
    
ircSocket.connect((HOST,PORT))
ircSocket.send(bytes("USER "+ botnick + "\n", "UTF-8")) #Wset all the fields to the bot nickname
ircSocket.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
ircSocket.send(bytes("JOIN "+ channel +"\n", "UTF-8"))

active = True
while active:
    data = ircSocket.recv(1024)
    
    if text.find('PING') != -1:
		irc.send(tbytes('PONG ' + text.split() [1] + '\r\n'))

  

data = ircSocket.recv(1024)

print(f"Received {data!r}")
