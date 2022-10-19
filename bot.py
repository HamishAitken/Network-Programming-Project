import socket


HOST = "fc00:1337::17" #IP for the server on Ubuntu virtual machine
PORT = 6667 #port the IRC server is using

#initialising variables for server communication
botnick = "bot"
channel = "#test"
active = True
ircSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)


#ping function used to maintain a conection to the server by responding to pings
def ping():  
    ircSocket.send(bytes("PONG :bot\r\n","UTF-8"))




    
#establishes connection to the server 
ircSocket.connect((HOST,PORT))

#sets the bots identity on the server
ircSocket.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick + "\r\n", "UTF-8")) 
ircSocket.send(bytes("NICK "+ botnick +"\r\n", "UTF-8"))

#joins a channel and gets information on its users 
Channel.joinChannel(channel)
namesArray = Channel.getChannelUsers(channel)


class Channel:

    #joinChannel function to take a channel name and join a channel on the IRC server
    def joinChannel(channel):
        ircSocket.send(bytes("JOIN "+ channel +"\r\n", "UTF-8"))

    def getChannelUsers(channel):
        ircSocket.send(bytes("WHO "+ channel +"\r\n", "UTF-8"))
        data = ircSocket.recv(2048)
        data = data.decode('UTF-8')

        userInfo = data.split("\r\n")

        userNamesArray[len(userInfo-1)] 
        i = 0

        while userInfo.find(bytes(":End of WHO list", "UTF-8")) != -1:

            userNamesArray[i] = userInfo[4]
     
            i = i + 1
        
        return userNamesArray
    


            




#loop for the bot to receive information sent from the server and process it
while active:

    data = ircSocket.recv(2048)

    if data.find(bytes("PING :", "UTF-8")) != -1:
        ping()

    



