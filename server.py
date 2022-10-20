import socket
import selectors
import types
import datetime


# Server
# Datastructure to hold server information
# Could use select mechanism to handle waiting for data and threads for sending the data
class Server:

    # Server info
    # stores the channels and clients that connect to the server
    channels = []
    clients = []
    selector = selectors.DefaultSelector()
    serverName = "server"
    serverVersion = "server-05.10.22"
    serverDate = datetime.datetime.now()

    # validation info
    channelPrefix = ['&', '#', '+', '!']
    retrying = False
    retryClientList = []
    retryList = []
    retryPreviousUser = []

    def __init__(self, host, port):
        # for selftesting pass into host = "::1"
        # for the project subsmission host = "fc00:1337::17"
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def openConnection(self):
        self.socket.listen(5)
        self.socket.setblocking(False)
        self.selector.register(self.socket, selectors.EVENT_READ, data=None)


    def receiveMsg(self, client, msg):
        if not msg:
            return
        print("[{}:{}] -> ".format(client.getHost()[0], client.getHost()[1]) + msg)

    def processConnections(self):
        try:
            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.acceptConnection(key.fileobj)
                    else:
                        self.serviceConnection(key, mask)
        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            self.selector.close()

    def processMsg(self, data, currentClient):
        if data:
                messages = data.split("\r\n")

                for i in messages:

                    if i == '':
                        continue

                    self.receiveMsg(currentClient, i)

                    receivedCommand = i.split()
                    command = receivedCommand[0]
                    target = receivedCommand[1]

                    if command == "NICK":


                        if currentClient.getRegisterStatus == False & len(target) > 9:
                            rpl432 = f":{target} 432 :Erroneous nickname"
                            self.sendMsg(currentClient, rpl432)
                            

                        existingNickname = self.checkNickName(target)
                        if existingNickname == True:
                            self.retryClientList.append(currentClient)
                            self.retryList.append(1)
                            currentClient.setPreviousNick(target)
                            print(currentClient.getNickRetryStatus())
                            errNicknameInUseMsg = f":{self.serverName} 433 {target} :Nickname is already in use"
                            self.sendMsg(currentClient, errNicknameInUseMsg)
                        else:
                            currentClient.setNickname(target)

                            # Trying this method of registering a new user that entered an existing nickname
                            retry = False
                            retryIndex = 0
                            for i in self.retryClientList:
                                if currentClient.getConnection() == i.getConnection():
                                    retry = True
                                retryIndex += 1
                            
                            if retry == True:
                                self.retrying = True
                                self.retryList[retryIndex] = 1
                                pass
                            
                            
                            
                            
                    elif command == "PRIVMSG":
                        client = self.findClient(currentClient.getConnection())

                        # :TheOnePieceIsReal!WhiteBeard@::1 PRIVMSG #test :test
                        fullMsg = ""

                        for j in range(2, len(receivedCommand)):
                            if j > 2 & j < len(receivedCommand):
                                fullMsg = fullMsg + " " + receivedCommand[j]
                            else:
                                fullMsg = fullMsg + receivedCommand[j]
                            


                        detectChannel = self.validateChannel(target)
                        detectedUser = self.findUser(target)


                        if detectChannel == True:
                            chan = self.getChannel(target)
                            privMsg = f":{client.getNickname()}!{client.getUsername()}@{client.getHost()[0]} PRIVMSG {chan.getName()} {fullMsg}"
                            self.sendChannelMsg(client, privMsg, chan)
                        elif detectedUser != None:
                            privMsg = f":{client.getNickname()}!{client.getUsername()}@{client.getHost()[0]} PRIVMSG {detectedUser.getNickname()} {fullMsg}"
                            self.sendMsg(detectedUser, privMsg)
                            

                    elif command == "USER":

                        print("USER COMMAND " + i)

                        retry = False
                        retryIndex = 0
                        for i in self.retryClientList:
                            if currentClient.getConnection() == i.getConnection():
                                retry = True
                            else:
                                retryIndex += 1

                        print(retry)
                        print(retryIndex)
                        print(self.retryClientList)
                        print(self.retryList)
                        print("NICK " + currentClient.getNickname())

                        if existingNickname == True and self.retryList[retryIndex] == 1:
                            newUserMsg = f"USER {target} 0 * :realname"
                            messages.append(newUserMsg)
                            self.retryList[retryIndex] = 0
                            continue

                        if currentClient.getRegisterStatus() == True:
                            rpl462 = f":{self.serverName} 462 :Unauthorised command (already registered)"
                            self.sendMsg(currentClient, rpl462)
                            
                        
                        currentClient.setUsername(target)

                        if retry == True:
                            self.retryClientList.remove((currentClient))
                            newNickMsg = f":{currentClient.getPreviousNick()}!{currentClient.getUsername()}@{currentClient.getHost()[0]} NICK {currentClient.getNickname()}"
                            self.sendMsg(currentClient, newNickMsg)
                        
                        self.welcomeMessage(currentClient)
                        currentClient.register()
                        self.clients.append(currentClient)

                    elif command == "JOIN":
                        client = self.findClient(currentClient.getConnection())

                        validateChannel = self.getChannel(target)
                        if validateChannel is None:
                            newChannel = Channel(target)
                            newChannel.addMember(client)
                            client.addJoinedChannel(newChannel)
                            self.channels.append(newChannel)
                            self.joinMsg(client, newChannel)
                        else:
                            validateChannel.addMember(client)
                            client.addJoinedChannel(validateChannel)
                            self.joinMsg(client, validateChannel)
                            
                    elif command == "MODE":
                        chan = self.getChannel(target)
                        modeMsg = f":{self.serverName}" + f" 324 {currentClient.getNickname()} {chan.getName()} :No topic is set"
                        self.sendMsg(currentClient, modeMsg)

                    elif command == "WHO":
                        chan = self.getChannel(target)
                        whoMsg = f":{self.serverName}" + f" 352 {chan.getName()} {currentClient.getUsername()}  {currentClient.getHost()[0]} {self.serverName} {currentClient.getNickname()} H :0 realname"
                        self.sendMsg(currentClient, whoMsg)

                        whoList = chan.getMemberList()
                        whoListMsg = f":{self.serverName}" + f" 315 {whoList} {chan.getName()} :End of WHO list"
                        self.sendMsg(currentClient, whoListMsg)


                    elif command == "PING":
                        pongMsg = ":{} PONG {}".format(self.serverName, self.serverName)
                        self.sendMsg(currentClient, pongMsg)

                    elif command == "QUIT":
                        client = self.findClient(currentClient.getConnection())
                        client.leaveJoinedChannels()
                        quitMsg = "User {} has left IRC".format(client.getNickname())
                        self.clients.remove(client)
                        print(quitMsg)

                    elif len(i) > 0:
                        unknownMsg = ":{} 421 {} {}:Unknown command".format(self.serverName, currentClient.getUsername(), data)
                        self.sendMsg(currentClient, unknownMsg)

        else:
            pingMsg = "PING {}".format(currentClient.getNickname())
            self.sendMsg(currentClient, pingMsg)
            # print("No data from: ", clientAddress)
    
    def acceptConnection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)

    def serviceConnection(self, key, mask):
        sock = key.fileobj
        data = key.data

        # Create a new client instance and add it to the list
        newClient = Client(sock, data.addr)

        if mask & selectors.EVENT_READ:
            recvData = sock.recv(1024)
            recvData = recvData.decode("utf-8")
            if recvData:
                self.processMsg(recvData, newClient)
                recvData = recvData.encode(encoding="utf-8")
                # data.outb += recvData
            else:
                self.selector.unregister(sock)
                sock.close()
        # if mask & selectors.EVENT_WRITE:
        #     if data.outb:
        #         sent = sock.send(data.outb)
        #         data.outb = data.outb[sent:]

    def sendMsg(self, client, msg):
        client.getConnection().send((msg + '\n').encode("utf-8"))
        print( "[{}:{}] <- ".format(client.getHost()[0], client.getHost()[1]) + msg)

    def sendChannelMsg(self, src, msg, chan):
        for i in chan.members:
            if i.getConnection() != src.getConnection():
                i.getConnection().send((msg + '\n').encode("utf-8"))
                print( "[{}:{}] <- ".format(src.getHost()[0], src.getHost()[1]) + msg)

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
        listOFMembers = ""     
        listOFMembers = chan.getMemberList()
        msg = ":{}!{}@{}".format(client.getNickname(), client.getUsername(), client.getHost()[0]) + " JOIN " + chan.getName()
        rpl331 = f":{self.serverName}" + f" 331 {client.getNickname()} {chan.getName()} :No topic is set"
        rpl353 = f":{self.serverName}" + f" 353 {client.getNickname()} = {chan.getName()} :{listOFMembers}"
        rpl366 = f":{self.serverName}" + f" 366 {chan.getName()} :End of NAMES list"

        self.sendMsg(client, msg)
        self.sendMsg(client, rpl331)
        self.sendMsg(client, rpl353)
        self.sendMsg(client, rpl366)
        self.sendChannelMsg(client, msg, chan)

    def checkNickName(self, name):
        foundName = False
        for i in range(len(self.clients)):
            if name == self.clients[i].getNickname():
                foundName = True
        return foundName

    def listClients(self):
        for i in range(len(self.clients)):
            print(self.clients[i].getNickname())
        return None

    def findClient(self, conn):
        for i in range(len(self.clients)):
            if conn == self.clients[i].getConnection():
                return self.clients[i]
        print("Error, client not found")
        return None

    # Returns a client object
    def findUser(self, nick):
        for i in self.clients:
            if i.getNickname() == nick:
                return i
        return None

    def validateChannel(self, name):
        for i in range(len(self.channelPrefix)):
            if self.channelPrefix[i] == name[0]:
                return True
        return False
    
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

    def removeMember(self, client):
        self.members.remove(client)

    def getName(self):
        return self.name

    def getMembers(self):
        return self.members

    def getMemberList(self):
        memberList = ""
        for i in range(len(self.members)):
            memberList = memberList + " " + self.members[i].getNickname()
        return memberList

# Client 
# Datastructure to hold the clients that connect to the server
class Client:
    nickname = ""
    username = ""
    joinedChannels = []
    timer = 0

    # validation
    registered = False
    retryNick = False
    previousNick = ""
    previousUser = ""

    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def setUsername(self, user):
        self.username = user

    def getUsername(self):
        return self.username

    def setNickname(self, nick):
        self.nickname = nick

    def setPreviousNick(self, pNick):
        self.previousNick = pNick

    def getPreviousNick(self):
        return self.previousNick
    
    def setPreviousUser(self, pUser):
        self.previousUser = pUser

    def getPreviousUser(self):
        self.previousUser

    def getNickname(self):
        return self.nickname

    def getConnection(self):
        return self.connection
    
    def getHost(self):
        return self.address

    def register(self):
        self.registered = True
    
    def getRegisterStatus(self):
        return self.registered

    def toggleNickRetryStatus(self):
        self.retryNick = not self.retryNick

    def getNickRetryStatus(self):
        return self.retryNick

    def addJoinedChannel(self, chan):
        self.joinedChannels.append(chan)

    def leaveJoinedChannels(self):
        for i in self.joinedChannels:
            i.removeMember(self)

    def findJoinedChannel(self, chan):
        for i in self.joinedChannels:
            if i.getName() == chan.getName():
                return True
        return False
        

def main():
    s = Server("::1", 6667)
    s.openConnection()
    s.processConnections()

main()
