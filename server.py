import socket
import datetime

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



# Server

# Could use select mechanism to handle waiting for data and threads for sending the data

# for selftesting host = "::1"
# for the project subsmission hots = "fc00:1337::17"
host = "fc00:1337::17"
port = 6667
# stores the clients that connect to the server
clients = []

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
serverName = "server"
serverVersion = "server-05.10.22"
serverDate = datetime.datetime.now()

def sendMsg(client, msg):
    client.getConnection().send((msg + '\n').encode("utf-8"))
    print( "[{}:{}] <- ".format(client.getHost()[0], client.getHost()[1]) + msg)

def receiveMsg(client, msg):
    if not msg:
        return
    print("[{}:{}] -> ".format(client.getHost()[0], client.getHost()[1]) + msg.decode())

def welcomeMessage(client):
    welcomeMsg = "Welcome to the Internet Relay Network {}!{}@{}".format(client.getNickname(), client.getUsername(), client.getHost()[0])
    msg2 = "Your host is {}, running version {}".format(serverName, serverVersion)
    msg3 = "This server was created {}".format(serverDate)
    msg4 = "{} {} o o ".format(serverName, serverVersion)

    sendMsg(client, welcomeMsg)
    sendMsg(client, msg2)
    sendMsg(client, msg3)
    sendMsg(client, msg4)




s.bind((host, port))
s.listen(5)
connection, clientAddress = s.accept()

while True:
    try:
        print(f"received connection from {clientAddress}")
        while True:

            # Create a new client instance and add it to the list
            newClient = Client(connection, clientAddress)

            data = connection.recv(1024)
            if data:
                # when testing data is received as in byte form and we need to decode it using .decode()
                # b'NICK Else\r\nUSER Elsed 0 * :realname\r\n'
                messages = data.split(b"\r\n")
                
                if len(messages) > 1:
                    receiveMsg(newClient, messages[0])
                    receiveMsg(newClient, messages[1])
                else:
                    receiveMsg(data)

                for i in messages:
                    if b"NICK" in i:

                        nickMessage = messages[0].split()
                        nickString = nickMessage[1]
                        # changes the nickname byte object into a string
                        # setting its nickname into the new client object
                        newClient.setNickname(nickString.decode("utf-8"))

                        # used for testing
                        # print(nickString[0].decode("utf-8"))

                    if b"USER" in i:

                        # The byte string is received with other parameters attached to it
                        # this splits the byte string to get the nickname
                        userMessage = messages[1].split()
                        userString = userMessage[1]
                        # changes the nickname byte object into a string
                        # setting its nickname into the new client object
                        newClient.setUsername(userString.decode("utf-8"))
                        # used for testing
                        # print(userString.decode("utf-8"))

                        welcomeMessage(newClient)
                        clients.append(newClient)

            else:
                print("No data from: ", clientAddress)
                break
            
    except socket.error as e:
        print(e)

    finally:
        print("Closing server")
        connection.close()
        break
