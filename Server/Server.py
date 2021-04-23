from Integrated_Server import *
import socket
import threading



HOST = '127.0.0.1'
PORT = 6000


server = Server(HOST, PORT)
serversocket = server.setup()


#Wow, such empty