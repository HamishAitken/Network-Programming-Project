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




class Channel:

    #joinChannel function to take a channel name and join a channel on the IRC server
    def __init__(self, channel):
        ircSocket.send(bytes("JOIN "+ channel +"\r\n", "UTF-8"))

    def getChannelUsers(self, channel):
        #ircSocket.send(bytes("WHO "+ channel +"\r\n", "UTF-8"))
        data = ircSocket.recv(2048)
        data = data.decode('UTF-8')

        userInfo = data.split("\r\n")

        userNamesArray = [] 
        counter = 0

        for i in userInfo: 
            if not ":End of WHO list" in i:
                userInfoSplit = userInfo[counter].split()
                print(userInfoSplit)
                userNamesArray.append(userInfoSplit[4]) 
                counter = counter + 1		
     
            
        
        return userNamesArray
    

#joins a channel and gets information on its users 
newChannel = Channel(channel)
#newChannel.joinChannel(channel)
namesArray = newChannel.getChannelUsers(channel)
print(namesArray)            




#loop for the bot to receive information sent from the server and process it
while active:

    data = ircSocket.recv(2048)

    if data.find(bytes("PING :", "UTF-8")) != -1:
        ircSocket.send(bytes("WHO "+ channel +"\r\n", "UTF-8"))
        ping()
