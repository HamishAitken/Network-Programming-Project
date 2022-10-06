#Trying to use the client

import socket



ircSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) 

def ping(): # respond to server Pings.  
    ircSocket.send(bytes("PONG :pingis\n","UTF-8"))

HOST = "fc00:1337::17" #IP for the virtual machine
PORT = 6667 #the port used

botnick = "bot"
channel = "#test"


 
    
ircSocket.connect((HOST,PORT))
ircSocket.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick + "\n", "UTF-8")) #Wset all the fields to the bot nickname
ircSocket.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
ircSocket.send(bytes("JOIN "+ channel +"\n", "UTF-8"))

active = True
while active:

    data = ircSocket.recv(2048)

    #data = data.strip (bytes("\n\r", "UTF-8"))

    if data.find (bytes("PING :", "UTF-8")) != -1:
        ping()

  



#print(f"Received {data!r}")