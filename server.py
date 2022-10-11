import socket
import datetime


# Server
# Datastructure to hold server information
# Could use select mechanism to handle waiting for data and threads for sending the data
class Server:

    # Server info
    # stores the clients that connect to the server
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
        print("[{}:{}] -> ".format(client.getHost()[0], client.getHost()[1]) + msg.decode())

    def processMsg(self, currentClient):
        while True:
            try:
                # print(f"received connection from {clientAddress}")
                while True:

                    data = currentClient.getConnection().recv(1024)
                    if data:
                        # when testing data is received as in byte form and we need to decode it using .decode()
                        # b'NICK Else\r\nUSER Elsed 0 * :realname\r\n'
                        messages = data.split(b"\r\n")
                        
                        if len(messages) > 1:
                            self.receiveMsg(currentClient, messages[0])
                            self.receiveMsg(currentClient, messages[1])
                        else:
                            self.receiveMsg(data)

                        for i in messages:
                            if b"NICK" in i:

                                nickMessage = messages[0].split()
                                nickString = nickMessage[1]
                                # changes the nickname byte object into a string
                                # setting its nickname into the new client object
                                currentClient.setNickname(nickString.decode("utf-8"))

                                # used for testing
                                # print(nickString[0].decode("utf-8"))

                            elif b"USER" in i:

                                # The byte string is received with other parameters attached to it
                                # this splits the byte string to get the nickname
                                userMessage = messages[1].split()
                                userString = userMessage[1]
                                # changes the nickname byte object into a string
                                # setting its nickname into the new client object
                                currentClient.setUsername(userString.decode("utf-8"))
                                # used for testing
                                # print(userString.decode("utf-8"))

                                self.welcomeMessage(currentClient)
                                self.clients.append(currentClient)

                            elif b"PING" in i:
                                pongMsg = ":{} PONG {}".format(self.serverName, self.serverName)
                                self.sendMsg(currentClient, pongMsg)

                            elif b"QUIT" in i:
                                client = self.findClient(currentClient.getConnection())
                                quitMsg = " User {} has left IRC".format(client.getNickname())
                                print(quitMsg)

                            # else:
                            #     unknownMsg = ":{} 421 {} {}:Unknown command".format(serverName, currentClient.getUsername(), data)
                            #     sendMsg(currentClient, unknownMsg)

                    else:
                        pingMsg = "PING {}".format(currentClient.getNickname())
                        self.sendMsg(currentClient, pingMsg)
                        # print("No data from: ", clientAddress)
                        # break
                    
            except socket.error as e:
                if "10054" in e:
                    break

            finally:
                print("Closing server")
                currentClient.getConnection().close()
                break

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

    def findClient(self, conn):
        for i in self.clients:
            if conn == self.clients[i].getConnection():
                return self.clients[i]
        print("Error, client not found")
        return 0


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
    s = Server("fc00:1337::17", 6667)
    s.openConnection()

main()
