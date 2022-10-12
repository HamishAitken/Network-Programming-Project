import socket
import datetime


# Server
# Datastructure to hold server information
# Could use select mechanism to handle waiting for data and threads for sending the data
class Server:

    # Server info
    # stores the channels and clients that connect to the server
    channels = []
    clients = []
    serverName = "server"
    serverVersion = "server-05.10.22"
    serverDate = datetime.datetime.now()

    def __init__(self, host, port):
        # for selftesting pass into host = "::1"
        # for the project subsmission host = "fc00:1337::17"
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def openConnection(self):
        self.socket.listen(5)
        conn, addr = self.socket.accept()
        # Create a new client instance and add it to the list
        newClient = Client(conn, addr)
        self.processMsg(newClient)


    def receiveMsg(self, client, msg):
        if not msg:
            return
        print("[{}:{}] -> ".format(client.getHost()[0], client.getHost()[1]) + msg)

    def processMsg(self, currentClient):
        while True:
            data = currentClient.getConnection().recv(1024)
            data = data.decode('utf-8')
            if data:
                # when testing data is received as in byte form and we need to decode it using .decode()
                # b'NICK Else\r\nUSER Elsed 0 * :realname\r\n'
                messages = data.split("\r\n")
                
                if len(messages) > 1:
                    self.receiveMsg(currentClient, messages[0])
                    self.receiveMsg(currentClient, messages[1])
                else:
                    self.receiveMsg(data)

                for i in messages:
                    if "NICK" in i:

                        nickMessage = messages[0].split()
                        nickString = nickMessage[1]
                        # changes the nickname byte object into a string
                        # setting its nickname into the new client object
                        currentClient.setNickname(nickString)

                        # used for testing
                        # print(nickString[0].decode("utf-8"))

                    elif "USER" in i:

                        # The byte string is received with other parameters attached to it
                        # this splits the byte string to get the nickname
                        userMessage = messages[1].split()
                        userString = userMessage[1]
                        # changes the nickname byte object into a string
                        # setting its nickname into the new client object
                        currentClient.setUsername(userString)
                        # used for testing
                        # print(userString.decode("utf-8"))

                        self.welcomeMessage(currentClient)
                        self.clients.append(currentClient)

                    elif "JOIN" in i:
                        channelMsg = i.split()
                        channelString = channelMsg[1]

                        validateChannel = self.getChannel(channelString)
                        if validateChannel is None:
                            newChannel = Channel(channelString)
                            newChannel.addMember(currentClient)
                            self.channels.append(newChannel)
                            self.joinMsg(currentClient, newChannel)
                        else:
                            validateChannel.addMember(currentClient)
                            self.joinMsg(currentClient, validateChannel)
                            
                    elif "MODE" in i:
                        channelMsg = i.split()
                        channelString = channelMsg[1]
                        chan = self.getChannel(channelString)
                        modeMsg = f":{self.serverName}" + f" 324 {currentClient.getUsername()} {chan.getName()} :No topic is set\r\n"
                        self.sendMsg(currentClient, modeMsg)

                    elif "WHO" in i:
                        channelMsg = i.split()
                        channelString = channelMsg[1]
                        chan = self.getChannel(channelString)
                        whoMsg = f":{self.serverName}" + f" 352 {chan.getName()} {currentClient.getUsername()}  {currentClient.getHost()[0]} {self.serverName} {currentClient.getNickname()} H :0 realname\r\n"
                        self.sendMsg(currentClient, whoMsg)

                        whoList = chan.getMemberList()
                        whoListMsg = f":{self.serverName}" + f" 315 {whoList} {chan.getName()} :End of WHO list\r\n"
                        self.sendMsg(currentClient, whoListMsg)

                    elif "PING " in i:
                        pongMsg = ":{} PONG {}".format(self.serverName, self.serverName)
                        self.sendMsg(currentClient, pongMsg)

                    elif "QUIT " in i:
                        client = self.findClient(currentClient.getConnection())
                        quitMsg = "User {} has left IRC".format(client.getNickname())
                        print(quitMsg)

                    elif len(i) > 0:
                        unknownMsg = ":{} 421 {} {}:Unknown command".format(self.serverName, currentClient.getUsername(), data)
                        self.sendMsg(currentClient, unknownMsg)

            else:
                pingMsg = "PING {}".format(currentClient.getNickname())
                self.sendMsg(currentClient, pingMsg)
                # print("No data from: ", clientAddress)
                # break
                    

    def sendMsg(self, client, msg):
        client.getConnection().send((msg + '\n').encode("utf-8"))
        print( "[{}:{}] <- ".format(client.getHost()[0], client.getHost()[1]) + msg)

    def welcomeMessage(self, client):
        welcomeMsg = "001 Welcome to the Internet Relay Network {}!{}@{}".format(client.getNickname(), client.getUsername(), client.getHost()[0])
        msg2 = "002 Your host is {}, running version {}".format(self.serverName, self.serverVersion)
        msg3 = "003 This server was created {}".format(self.serverDate)
        msg4 = "004 {} {} r r".format(self.serverName, self.serverVersion)

        self.sendMsg(client, welcomeMsg)
        self.sendMsg(client, msg2)
        self.sendMsg(client, msg3)
        self.sendMsg(client, msg4)

    def joinMsg(self, client, chan):
        msg = ":{}!{}@{}".format(client.getNickname(), client.getUsername(), client.getHost()[0]) + " JOIN " + chan.getName() + "\r\n"
        rpl331 = f":{self.serverName}" + f" 331 {client.getUsername()} {chan.getName()} :No topic is set\r\n"
        rpl353 = f":{self.serverName}" + f" 353 {client.getUsername()} = {chan.getName()} :{client.getUsername()}\r\n"
        listOFMembers = ""
        
        listOFMembers = chan.getMemberList()
        rpl366 = f":{self.serverName}" + f" 366 {listOFMembers} {chan.getName()} :End of NAMES list\r\n"

        self.sendMsg(client, msg)
        self.sendMsg(client, rpl331)
        self.sendMsg(client, rpl353)
        self.sendMsg(client, rpl366)

    def findClient(self, conn):
        for i in range(len(self.clients)):
            if conn == self.clients[i].getConnection():
                return self.clients[i]
        print("Error, client not found")
        return 0
    
    def getChannel(self, name):
        for i in range(len(self.channels)):
            if name == self.channels[i].getName():
                return self.channels[i]
        return None


# Channel
# Datastructure to hold channel information
class Channel:
    members = []
    def __init__(self, name):
        self.name = name
    
    def addMember(self, client):
        self.members.append(client)

    def getName(self):
        return self.name

    def getMembers(self):
        return self.members

    def getMemberList(self):
        memberList = ""
        for i in range(len(self.members)):
            memberList = memberList + " " + self.members[i].getUsername()
        return memberList

# Client 
# Datastructure to hold the clients that connect to the server
class Client:
    nickname = ""
    username = ""
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def setUsername(self, user):
        self.username = user

    def getUsername(self):
        return self.username

    def setNickname(self, nick):
        self.nickname = nick

    def getNickname(self):
        return self.nickname

    def getConnection(self):
        return self.connection
    
    def getHost(self):
        return self.address


def main():
    s = Server("::1", 6667)
    s.openConnection()

main()
