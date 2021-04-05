import socket
import json
import numpy as np
import time
import threading



systemStatus = "Offline"
armPosition = "Unknown"

HOST = '127.0.0.1'
PORT = 6000





#Ready to add other functions for arm movement




#Tells server ready for TCP values
def TCPwrapper(conn):
    global systemStatus
    global armPosition
    
    if(systemStatus == "Online"):
        if(armPosition == "Home"):
            
            jsonResult = {"first":"Client 1", "second": "Ready for TCP Values"}
            send(conn, jsonResult)
    

def getTCPValues(jsonReceived):
    TCPvalues = np.zeros(6)
    
    #See if there is a better way to do this
   
    TCPvalues[0] = int(jsonReceived["second"])
    TCPvalues[1] = int(jsonReceived["third"])
    TCPvalues[2] = int(jsonReceived["fourth"])
    TCPvalues[3] = int(jsonReceived["fifth"])
    TCPvalues[4] = int(jsonReceived["sixth"])
    TCPvalues[5] = int(jsonReceived["seventh"])
    
    #Call arm movement here


    

def send(conn, data):
        
    jsonResult = json.dumps(data)
    conn.send(bytes(jsonResult, encoding="utf-8"))
    
    
def moniterUserInput(conn):
    global systemStatus 
    
    while(True):
        jsonReceived = conn.recv(1024)
        jsonReceived = json.loads(jsonReceived.decode("utf-8"))
        
        #Add commands for this script
        #System Pasue, shutdown, velocity change, etc. 
        
        
        if(jsonReceived["first"] == "System Started"):
            print("System online")
            systemStatus = "Online"
            
        elif(jsonReceived["first"] == "Go into Standby"):
            print("System in standby")
            systemStatus = "Standby"
            
        elif(jsonReceived["first"] == "Shut Down System"):
            print("System offline")
            systemStatus = "Offline"
          
            
            #Move arm to home position
              
        elif(jsonReceived["first"] == "Velocity Change"):
            print("Velocity change")
            print(jsonReceived["second"])
            #Call function to change arm velocity
        
        
        elif(jsonReceived["first"] == "TCP Values"):
            print("TCP Values")
            
            #If the system isnt in standby or shutdown, allowed to move the arm
            if(systemStatus == "Online"):
                print()
                
                
                #Request TCP values
                #Move arm to pick up parcel
                #Sort parcel
                #Move to home position
                #Repeat
      
            
def main():
 
    connected = False
    
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    while not(connected):
    
        try:
            conn.connect((HOST, PORT))
            connected = True
        except Exception as e:
            print(e)
        finally:
            time.sleep(1)
    
    
    
    
    t1 = threading.Thread(target = moniterUserInput, args = (conn, ))
           
    t1.start()
                  
    #Move arm to home position 
    
    
    #May put this in a while loop, run forever
    #Not sure yet. 
    #TCPwrapper()
    
    
    t1.join()
    
   

   
if __name__ == "__main__":
    main()
        
