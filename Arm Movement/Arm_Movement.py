import socket
import json
import numpy as np


HOST = '127.0.0.1'
PORT = 6000





#Ready to add other functions for arm movement


def getTCPValues(socket):
    TCPvalues = np.zeros(6)
    
    
    jsonResult = {"first":"Client 1", "second":"Requesting TCP Values"}
    jsonResult = json.dumps(jsonResult)
    socket.send(bytes(jsonResult, encoding="utf-8"))

    jsonReceived = socket.recv(1024)
    jsonReceived = json.loads(jsonReceived.decode("utf-8"))
    
   
    #See if there is a better way to do this
    TCPvalues[0] = int(jsonReceived["first"])
    TCPvalues[1] = int(jsonReceived["second"])
    TCPvalues[2] = int(jsonReceived["third"])
    TCPvalues[3] = int(jsonReceived["fourth"])
    TCPvalues[4] = int(jsonReceived["fifth"])
    TCPvalues[5] = int(jsonReceived["sixth"])
    
    return TCPvalues


   
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.connect((HOST, PORT))
    
    
    #Call this function as needed. 
    #My suggestion would be to set the arm to the home location and then request new TCP values. 
    TCPValues = getTCPValues(s)
    
    
        
