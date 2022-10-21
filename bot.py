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

class Channel:

    #joinChannel function to take a channel name and join a channel on the IRC server
    def __init__(self, channel):
        ircSocket.send(bytes("JOIN "+ channel +"\r\n", "UTF-8"))

    #stores a list of channel users from parsing the initial data sent by the server about the channel
    def getInitialChannelUsers(self, channel):
        data = ircSocket.recv(2048)
        data = data.decode('UTF-8')

        userInfo = data.split("\r\n")

        #identifies the section that has the channel user nicknames and parses them
        userInfoSplit = userInfo[8].split(" :")

        userNamesList = userInfoSplit[1].split() 
        
        return userNamesList


    #updates the namesList if a user has joined the channel
    def addUserToChannel(self, data):
        
        joinedUser = getUserNickname(data)
        namesList.append(joinedUser) 


    #updates the namesList if a user has left the channel
    def removeUserFromChannel(self, data):
        
        removedUser = getUserNickname(data)
        namesList.remove(removedUser)

#ping function used to maintain a conection to the server by responding to pings
def ping():  
    ircSocket.send(bytes("PONG :bot\r\n","UTF-8"))

#opens file for read and reads into the list line by line an returns a random fact
def getRandomFact():
        
    myFile = open("random_facts.txt", "r")
    randomList = myFile.readlines()

    #store random item from the list of facts 
    randomFact = random.choice(randomList)

    return randomFact

#extracts the users nickname from the data line the bot receives
def getUserNickname(data):
    data = data.decode('UTF-8')

    #spliting the irc data to seperate the nickname from the rest of the message
    UserInfo = data.split(":")
    UserNames = UserInfo[1].split("!")
    UserNickname = UserNames[0]

    return UserNickname

#adding in command line parameters
parser = argparse.ArgumentParser()
parser.add_argument('--host', action='store_true')
parser.add_argument('--port', action='store_true')
parser.add_argument('--name', action='store_true')
parser.add_argument('--channel', action='store_true')
args = parser.parse_args()

#if functions to print the command line parameters information
if args.host:
    print("Host is: " + HOST)
if args.port:
    print("Port is: " + str(PORT))
if args.name:
    print("Nickname is: " + botnick)
if args.channel:
    print("Channel is: " + channel)    


#establishes connection to the server 
ircSocket.connect((HOST,PORT))

#sets the bots identity on the server
ircSocket.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick + "\r\n", "UTF-8")) 
ircSocket.send(bytes("NICK "+ botnick +"\r\n", "UTF-8"))


#joins a channel and gets information on its users 
ircChannel = Channel(channel)

#namesList variable retains initial channel users
namesList = newChannel.getInitialChannelUsers(channel)
            


#loop for the bot to receive and process information sent from the server
while active:

    #receives message sent from the server
    data = ircSocket.recv(2048)

    #if ping recived from server, send pong back to retain server connection
    if data.find(bytes("PING :", "UTF-8")) != -1:
        ping()

    #if server sends update of a user joining the channel, add user to channel user list 
    if data.find(bytes("JOIN", "UTF-8")) != -1:
        ircChannel.addUserToChannel(data)
          

    #if server sends update of a user leaving the channel, remove user from channel namesList 
    if data.find(bytes("PART", "UTF-8")) != -1:
        ircChannel.removeUserFromChannel(data)
          

    #if a user leaves the server and was in the channel, remove user from channel namesList  
    if data.find(bytes("QUIT", "UTF-8")) != -1:
        
        quitUser = getUserNickname(data)

        if quitUser in namesList:
            ircChannel.removeUserFromChannel(data)
         

    #if the message received was from the channel
    if data.find(bytes("PRIVMSG " + channel, "UTF-8")) != -1:
        nickname = getUserNickname(data)    

        #responds to !hello command in the channel by greeting the user and sending the date and time
        if data.find(bytes(":!hello", "UTF-8")) != -1:
            
            dateAndTime = datetime.datetime.now()
            shorterDateAndTime = dateAndTime.strftime("%c")
            ircSocket.send(bytes("PRIVMSG " + channel + " :Hello there " + nickname + ", the date and time is: " + shorterDateAndTime + "\r\n", "UTF-8"))

        #responds to !slap command in the channel 
        if data.find(bytes(":!slap", "UTF-8")) != -1:
            
            data = data.decode('UTF-8')

            #checks slap command for if a target user was specified after the command
            userInfo = data.split("\r\n")
            userToSlapSplit = userInfo[0].split(":!slap ")

            #creates new list of channel names and removes the sender from the list             
            tempNamesList = namesList.copy()
            tempNamesList.remove(nickname)

            #if there was not a user specifed with the slap command
            if len(userToSlapSplit) < 2:
                #removes the bot from the potential targets 
                tempNamesList.remove(botnick)

                #validation for if there is no people in the channel left to slap 
                if not tempNamesList:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :Not enough people to slap" + "\r\n", "UTF-8"))
                else:
                    #selects random user from the channel and slaps them 
                    randomUser = random.choice(tempNamesList)
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + randomUser + " has been slapped by a trout"+ "\r\n", "UTF-8"))

            #if there was a user specifed for the slap command
            else:
                userToSlap = userToSlapSplit[1]
                if userToSlap in tempNamesList:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + userToSlap + " has been slapped by a trout"+ "\r\n", "UTF-8"))

                #if the user specified was not in the channel, the sender slaps themselves
                else:
                    ircSocket.send(bytes("PRIVMSG " + channel + " :" + nickname + " has slapped themselves with a trout"+ "\r\n", "UTF-8"))

    #if the message received was a private message to the bot, bot responds to the sender with a random fact
    elif data.find(bytes("PRIVMSG" , "UTF-8")) != -1:
        
        nickname = getUserNickname(data)
        randomFact = getRandomFact()
        ircSocket.send(bytes("PRIVMSG " + nickname + " :Did you know that " + randomFact + "\r\n", "UTF-8"))

