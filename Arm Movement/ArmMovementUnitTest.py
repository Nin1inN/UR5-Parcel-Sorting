import socket
import numpy as np
import json


#######################################################################################
#Allows you to send commands to Arm_Movement over the network, simulates the server
########################################################################################


HOST = '127.0.0.1'
PORT = 6000


def send(data, conn):
    jsonResult = json.dumps(data)
    conn.send(bytes(jsonResult, encoding="utf-8"))

def main():
    print()
    # Using IPv4 with a TCP socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket to a public host, and a well-known port
    serversocket.bind((HOST, PORT))
    # become a server socket
    serversocket.listen(5)

    conn, addr = serversocket.accept()     # Establish connection with client.


    #Change command and data as needed
    jsonResult = {"first":"command", "second": "data"}

    send(jsonResult, conn)

if __name__ == "__main__":
    main()
