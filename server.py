import socket

#for selftesting host = 'localhost'
#for the project subsmission hots = "fc00:b33f::17"
host = "fc00:b33f::17"
port = 6667

#To store the clients that connect to the server
clients = []


s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.bind(host, port)
s.listen(5)

while True:
    connection, client_address = s.accept()
    try:
        print("")
        while True:
            print(f"received connection from {client_address}")
            data = connection.recv()
            if not data:
                break
    finally:
        print("Closing server")
        connection.close()

