import socket
import random
import datetime
import argparse

HOST = "fc00:1337::17" #IP for the server on Ubuntu virtual machine
PORT = 6667 #port the IRC server is using

#initialising variables for server communication
botnick = "bot"
channel = "#test"
active = True
ircSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

parser = argparse.ArgumentParser()
parser.add_argument('--host', action='store_true')
parser.add_argument('--port', action='store_true')
parser.add_argument('--name', action='store_true')
parser.add_argument('--channel', action='store_true')
args = parser.parse_args()

if args.host:
    print("Host is: " + HOST)
if args.port:
    print("Port is: " + PORT)
if args.name:
    print("Nickname is: " + botnick)
if args.channel:
    print("Channel is: " + channel)    

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

def getUserNickname(data):
    data = data.decode('UTF-8')

    UserInfo = data.split(":")
    UserNames = UserInfo[1].split("!")
    UserNickname = UserNames[0]


    return UserNickname

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


    
    def addUserToChannel(self, data):
        
        joinedUser = getUserNickname(data)
        namesList.append(joinedUser) 





    def removeUserFromChannel(self, data):
        
        removedUser = getUserNickname(data)
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
        newChannel.addUserToChannel(data)
        print(namesList)  

    if data.find(bytes("PART", "UTF-8")) != -1:
        newChannel.removeUserFromChannel(data)
        print(namesList)  

    if data.find(bytes("QUIT", "UTF-8")) != -1:
        
        quitUser = getUserNickname(data)

        if quitUser in namesList:
            newChannel.removeUserFromChannel(data)
        print(namesList) 

    #replies to the user with a random fun fact  
    if data.find(bytes("PRIVMSG " + channel, "UTF-8")) != -1:
        nickname = getUserNickname(data)    

        if data.find(bytes(":!hello", "UTF-8")) != -1:
            
            dateAndTime = datetime.datetime.now()
            shorterDateAndTime = dateAndTime.strftime("%c")
            ircSocket.send(bytes("PRIVMSG " + channel + " :Hello there " + nickname + ", the date and time is: " + shorterDateAndTime + "\r\n", "UTF-8"))

        


        
        
        if data.find(bytes(":!slap", "UTF-8")) != -1:
            
            data = data.decode('UTF-8')

            userInfo = data.split("\r\n")
            userToSlapSplit = userInfo[0].split(":!slap ")

            tempNamesList = namesList.copy()
            tempNamesList.remove(nickname)

            if len(userToSlapSplit) < 2:
                tempNamesList.remove(botnick)
                if not tempNamesList:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :Not enough people to slap" + "\r\n", "UTF-8"))
                else:
                    randomUser = random.choice(tempNamesList)
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + randomUser + " has been slapped by a trout"+ "\r\n", "UTF-8"))
            else:

                userToSlap = userToSlapSplit[1]
                if userToSlap in tempNamesList:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + userToSlap + " has been slapped by a trout"+ "\r\n", "UTF-8"))
                else:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + nickname + " has slapped themselves with a trout"+ "\r\n", "UTF-8"))

    elif data.find(bytes("PRIVMSG" , "UTF-8")) != -1:
        
        nickname = getUserNickname(data)
        randomFact = getRandomFact()
        ircSocket.send(bytes("PRIVMSG " + nickname + " :Did you know that " + randomFact + "\r\n", "UTF-8"))

