from Integrated_Server import *
import socket
import threading





#################################
# Server and Client Setup
##################################

# Using IPv4 with a TCP socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host, and a well-known port
serversocket.bind((HOST, PORT))
# become a server socket
serversocket.listen(5)



while True:
    try:
        conn, addr = serversocket.accept()     # Establish connection with client.
        print("Client connected")

        clients.append(conn)

        t1 = threading.Thread(target = clientHandler, args = (conn, serversocket))

        t1.start()

    except Exception as e:
        print(e)
