import socket
import random


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


def getRandomFact():
    # use import random for this bit
    #opens file for read and reads into the list, line by line
        
    myFile = open("random_facts.txt", "r")
    randomList = myFile.readlines()
    randomFact = random.choice(randomList)

    return randomFact

    
#establishes connection to the server 
ircSocket.connect((HOST,PORT))

#sets the bots identity on the server
ircSocket.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick + "\r\n", "UTF-8")) 
ircSocket.send(bytes("NICK "+ botnick +"\r\n", "UTF-8"))




class Channel:

    #joinChannel function to take a channel name and join a channel on the IRC server
    def __init__(self, channel):
        ircSocket.send(bytes("JOIN "+ channel +"\r\n", "UTF-8"))

    def getInitialChannelUsers(self, channel):
        data = ircSocket.recv(2048)
        data = data.decode('UTF-8')

        userInfo = data.split("\r\n")
        userInfoSplit = userInfo[8].split(" :")

        userNamesList = userInfoSplit[1].split() 
        
        return userNamesList


    
    def addUserToChannel(self, channel, data):
        data = data.decode('UTF-8')

        joinedUserInfo = data.split(":")
        joinedUserNames = joinedUserInfo[1].split("!")
        joinedUser = joinedUserNames[0]

        namesList.append(joinedUser) 





    def removeUserFromChannel(self, channel, data):
        data = data.decode('UTF-8')

        removeUserInfo = data.split(":")
        removedUserNames = removeUserInfo[1].split("!")
        removedUser = removeUserNames[0]

        namesList.remove(removedUser)


     
            
        
        


#joins a channel and gets information on its users 
newChannel = Channel(channel)
#newChannel.joinChannel(channel)
namesList = newChannel.getInitialChannelUsers(channel)
print(namesList)            




#loop for the bot to receive information sent from the server and process it
while active:

    data = ircSocket.recv(2048)

    if data.find(bytes("PING :", "UTF-8")) != -1:
        ping()

    if data.find(bytes("JOIN", "UTF-8")) != -1:
        newChannel.addUserToChannel(channel,data)
        print(namesList)  

    if data.find(bytes("PART", "UTF-8")) != -1:
        newChannel.removeUserFromChannel(channel,data)
        print(namesList)  

    if data.find(bytes("QUIT", "UTF-8")) != -1:
        data = data.decode('UTF-8')

        quitUserInfo = data.split(":")
        quitUserNames = quitUserInfo[1].split("!")
        quitUser = quitUserNames[0]

        if quitUser in namesList:
            newChannel.removeUserFromChannel(channel,data)
        print(namesList) 

    #replies to the user with a random fun fact  
    if data.find(bytes("PRIVMSG", "UTF-8")) != -1:
        nicknameData = data.split (":")
        nicknameSplit = nickname[1].split ("!")
        nickname = nicknameSplit[0]
        randomFact = getRandomFact()
        ircSocket.send(bytes("PRIVMSG " + nickname + " : Did you know " + randomFact + "\r\n", "UTF-8"))
        
        
