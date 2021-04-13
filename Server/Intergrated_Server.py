import socket
import threading
import numpy as np
import json
from vidgear.gears import NetGear
import cv2
import cv2.aruco as aruco
import time
import logging





#Streamline code


#Deals with networking
systemStatus = "Offline"

#Can replace with queue
readyForTCPValues = "No"

#Wont need in final version
# stream = 0
# VidGearServer = 0

HOST = '127.0.0.1'
PORT = 6000


#Will need this DONNY
clients = []



#Deals with markers
# row_position_average = np.zeros(0)
# column_position_average = np.zeros(0)


#May not need this
#TCPValuesArray = np.zeros(6)

#Will check to see if anything is covering the markers.
#If so, will use the AI to detect if a parcel is present.
#If object detected will call findLocation and convertToWorldLocation to get x and y TCP values
#Expected value at end is an array of 6 values.
def checkArucoMarkers(clientsocket, frame):
    global readyForTCPValues

    return frame


    # row_position_average = np.zeros(0)
    # column_position_average = np.zeros(0)

    #id_matrix = np.zeros(20)
    #Length is same as moving average length
#    for counter in range(0, 20):
#        gray = cv2.cvtColor(stream, cv2.COLOR_BGR2GRAY)
#        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
#        arucoParameters = aruco.DetectorParameters_create()
#        corners, ids, rejectedImgPoints = aruco.detectMarkers(
#            gray, aruco_dict, parameters=arucoParameters)
#
#        #Set id matrix position to 1 (marker visible)
#        for i in range(0, len(ids)):
#            if(ids[i] > 20):
#                print("")


         #Call AI function()


         #Call findLocation in another thread.
#            else:
#                id_matrix[ids[i]] = 1
#
#        row_position_average, column_position_average, worldPosition = findLocation(id_matrix, row_position_average, column_position_average)
#
#        id_matrix = np.zeros(20)


    #At this point, I should have an x, y, z position.
    #If client 1 is ready, transmit, otherwise drop Values


    #Once TCP values are sent, set readyForTCPValues to No



#x is row position, y is column position
def convertToWorldLocation(x, y):
    num_of_rows = 4
    num_of_columns = 5

    #All positions values are in mm
    bottom_left = np.array([-745, 300])

    top_right = np.array([-330, -280])

    block_size = np.zeros(2)
    worldPosition = np.zeros(2)

    block_size[0] = ( np.abs(bottom_left[0] - top_right[0])/ num_of_rows)

    block_size[1] = ( np.abs(bottom_left[1] - top_right[1])/ num_of_columns)

    worldPosition[0] = -(block_size[0] * x) + top_right[0]
    worldPosition[0] -= 50

    worldPosition[1] = -(block_size[1] * y) - top_right[1]
    worldPosition[1] -= 35

    return worldPosition

    #Figure out the rest of the TCP Values



def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w



def findLocation(id_matrix, row_position_average, column_position_average):
    position_matrix = np.split(id_matrix,4)

    row_position = np.zeros(0)
    column_position = np.zeros(0)
    worldPosition = "Null"

    for i in range(len(position_matrix)):
        for j in range(len(position_matrix[i])):

            if(position_matrix[i][j] == 0):

                if i not in row_position:
                    row_position = np.append(row_position, i)

                if j not in column_position:
                    column_position = np.append(column_position, j)

    row_position = (np.sum(row_position)/(len(row_position)))
    column_position = (np.sum(column_position)/(len(column_position)))
#

    row_position_average = np.append(row_position_average, row_position)
    column_position_average = np.append(column_position_average, column_position)

    if(len(row_position_average)  == 20):
       row_position_average = moving_average(row_position_average, 20)
       print("Row Position")

       column_position_average = moving_average(column_position_average, 20)
       print("Column Position")

       worldPosition = convertToWorldLocation(row_position_average, column_position_average)
       row_position_average = np.zeros(0)
       column_position_average = np.zeros(0)

    return row_position_average, column_position_average, worldPosition






def clientHandler(clientsocket, serversocket):
    global systemStatus
    global clients
    global readyForTCPValues

    t1 = threading.Thread(target = videoStream, args = (clientsocket, ))

    while(True):

        try:
            jsonReceived = clientsocket.recv(1024)
            jsonReceived = json.loads(jsonReceived.decode("utf-8"))
          #  jsonReceived = json.loads(jsonReceived)
        except:
            pass


        if(jsonReceived["first"] == "Client 1"):

            if(jsonReceived["second"] == "Ready for TCP Values"):

                readyForTCPValues = "Yes"


        elif(jsonReceived["first"] == "Client 2"):

            if(jsonReceived["second"] == "Start Up System"):

                if(systemStatus == "Offline"):


                    print("Starting up")
                    jsonResult = {"first":"System Started"}
                    send(jsonResult, 1)

                    systemStatus = "Online"

                    #Start new thread to handle video stream
                    #At this point, should be a total of 3 threads


                    t1.start()



            elif(jsonReceived["second"] == "Resume System"):


                 print("System Resuming")
                 jsonResult = {"first":"System Resume"}

                 send(jsonResult, 1)
                 systemStatus = "Online"

            elif(jsonReceived["second"] == "Pause System"):


                 print("System going into standby")

                 jsonResult = {"first":"Go into Standby"}

                 send(jsonResult, 1)
                 systemStatus = "Standby"


            elif(jsonReceived["second"] == "Drop Location"):

                if(systemStatus == "Online"):



                    jsonResult = {"first": "Drop Location", "second": jsonReceived["third"], "third": jsonReceived["fourth"], "fourth": jsonReceived["fifth"], "fifth": jsonReceived["sixth"], "sixth": jsonReceived["seventh"], "seventh": jsonReceived["eight"] }
                    print(jsonResult)
                    #send(jsonResult, 1)

            elif(jsonReceived["second"] == "Set Velocity"):

                if(systemStatus == "Online"):
                    jsonResult = {"first":"Velocity Change", "second": jsonReceived["third"]}

                    send(jsonResult, 1)

            elif(jsonReceived["second"] == "Shut Down System"):

                systemStatus = "Offline"




                #Client 0 for testing, client 1 for final version


                #Disconnect socket for video feed here
                try:
                    clients[0].close()
                    VidGearServer.close()
                    stream.release()
                    temp = clients[0]
                    #Keeping the first client (Arm Movement)
                    clients = []
                    clients.append(temp)

                except Exception as e:
                    logging.error(e)

                finally:
                    return
                   #os._exit(1)
                    #os.execv(sys.executable, [sys.executable] + sys.argv)



#Flag will be used to indicate which client to send to
# 0 = both
# 1 = Client 1 (Arm Movement)
# 2 = Client 2 (User Interface)
def send(data, flag):
    jsonResult = json.dumps(data)

    try:
        if(flag == 0):

            for i in range(0, 2):
                clients[i].send(bytes(jsonResult, encoding="utf-8"))

        elif(flag == 1):
            clients[0].send(bytes(jsonResult, encoding="utf-8"))

        elif(flag == 2):
            clients[1].send(bytes(jsonResult, encoding="utf-8"))
    except Exception as e:
        print(e)


def videoStream(clientsocket):
    global systemStatus

    #Will not need in the final version
    #global stream
    #global VidGearServer

    #10 frames a sec is fine for the video stream
    #If not, you are welcome to increase (problems with the GUI appear if you do)
    frame_rate = 10
    prev = 0
    # Open suitable video stream, such as webcam on first index(i.e. 0)
    stream = cv2.VideoCapture(0)

    # define tweak flags
    options = {
    "compression_format": ".jpg",
    "compression_param": [cv2.IMWRITE_JPEG_QUALITY, 50],
}

    VidGearServer = NetGear(
        address=HOST,
        port="5454",
        protocol="udp",
        pattern=0,
        **options
    )

    # loop over until KeyBoard Interrupted
    while True:

        if(systemStatus == "Online"):

            try:

                time_elapsed = time.time() - prev



                if(time_elapsed > 1./frame_rate):
                    # read frames from stream
                    (grabbed, frame) = stream.read()

                    # check for frame if not grabbed
                    if not grabbed:
                        break

                    frame = checkArucoMarkers(clientsocket, frame)

                    prev = time.time()
                    VidGearServer.send(frame)

            except KeyboardInterrupt:
                break
        elif(systemStatus == "Offline"):
            return

def main():

    global clients

    #Create another server (with a different port) to handle the video stream.

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

if __name__=="__main__":
    main()
