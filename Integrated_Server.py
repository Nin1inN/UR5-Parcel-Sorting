import socket
import threading
import numpy as np
import json
from vidgear.gears import NetGear
import cv2
import cv2.aruco as aruco
import time
import logging
from queue import Queue
import yolov5_Interface as yolov5
import realsense_depth as rs
import math


class Server:
    def __init__(server, ip, port):

        """

        Constructor:

        Initalizes the variables needed for the server class.

        Args:

            ip (string): IP address of the server.

            port (string): Port number of the server.


        Returns:

            None


        """


        server.ip = ip
        server.port = port
        server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.clients = []
        server.systemStatus = "Offline"
        server.readyForTCPValues = False
        server.marker_distance = [584, 470, 365, 260]


    def setup(server):

        """

        Setups the server socket and listens for connecting clients.

        Once a client is connected, spawns a thread to handle client (clientHandler).

        Args:

            server.clients (list): List of connected clients. Adds clients to the list as they connect.


        Returns:

            None


        """

        # Using IPv4 with a TCP socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to a public host, and a well-known port
        serversocket.bind((server.ip, server.port))
        # become a server socket
        serversocket.listen(5)

        while True:
            try:
                conn, addr = serversocket.accept()     # Establish connection with client.

                server.clients.append(conn)
                print("Client connected")

                t1 = threading.Thread(target = server.clientHandler, args = (conn, ))

                t1.start()

            except Exception as e:
                print(e)




    def clientHandler(server, clientsocket):


        """

        Receives data from client(s) and performs the command receieved.

        Args:

            server.readyForTCPValues (bool): Used to determine when to use the vision system (works on client request).

            server.systemStatus (string):  Used to determine if the system needs to shutdown or go to standby.

            server.clients (list): List of connected clients. Used to disconnect from User Interface client.

            clientsocket (socket): Current client connected (multiple threads running clientHandler, each instance has a different clientsocket).


        Returns:

            None


        """

        while(True):

            try:
                jsonReceived = clientsocket.recv(1024)
                jsonReceived = json.loads(jsonReceived.decode("utf-8"))
              #  jsonReceived = json.loads(jsonReceived)
            except Exception as error:
                print(error)
                continue



            #Arm command
            if(jsonReceived["first"] == "ARM"):

                if(jsonReceived["second"] == "Ready for TCP Values"):

                    server.readyForTCPValues = True



            #Client Commands
            elif(jsonReceived["first"] == "Client 2"):

                if(jsonReceived["second"] == "Start Up System"):

                    if(server.systemStatus == "Offline"):


                        print("Starting up")
                        jsonResult = {"first":"System Started"}
                        server.send(jsonResult, 1)

                        server.systemStatus = "Online"

                        q = Queue()

                        visionSystemThread = threading.Thread(target = server.videoStream, args = (q, ))

                        videoStreamThread = threading.Thread(target = server.visionSystem, args = (q, ))

                        visionSystemThread.start()

                        videoStreamThread.start()



                elif(jsonReceived["second"] == "Resume System"):


                     print("System Resuming")
                     jsonResult = {"first":"System Resume"}

                     server.send(jsonResult, 1)
                     server.systemStatus = "Online"

                elif(jsonReceived["second"] == "Pause System"):


                     print("System going into standby")

                     jsonResult = {"first":"Go into Standby"}

                     server.send(jsonResult, 1)
                     server.systemStatus = "Standby"


                elif(jsonReceived["second"] == "Drop Location"):

                    if(server.systemStatus == "Online"):

                        jsonResult = {"first": "Drop Location", "second": jsonReceived["third"], "third": jsonReceived["fourth"], "fourth": jsonReceived["fifth"], "fifth": jsonReceived["sixth"], "sixth": jsonReceived["seventh"], "seventh": jsonReceived["eight"] }
                        print(jsonResult)
                        #send(jsonResult, 1)

                elif(jsonReceived["second"] == "Set Velocity"):

                    if(server.systemStatus == "Online"):
                        jsonResult = {"first":"Velocity Change", "second": jsonReceived["third"]}

                        server.send(jsonResult, 1)

                elif(jsonReceived["second"] == "Shut Down System"):

                    server.systemStatus = "Offline"




                    #Client 0 for testing, client 1 for final version

                    try:

                        clientsocket.close()


                    except Exception as e:
                        logging.error(e)

                    finally:
                        #Will need in final version.
                        #del server.clients[1]
                        return
                       #os._exit(1)




    #Flag will be used to indicate which client to send to
    # 0 = both
    # 1 = Client 1 (Arm Movement)
    # 2 = Client 2 (User Interface)
    def send(server, data, flag):

        """

        Send data over the socket to the clients.

        Args:

            server.clients (list): List of connected clients. Used to send data to client.

            data (JSON - dict): JSON data

            flag (int): Used to identify which client to send to. Client 1 is Arm Movement, Client 2 is User Interface.


        Returns:

            None


        """
        jsonResult = json.dumps(data)

        try:
            if(flag == 0):

                for i in range(0, 2):
                    server.clients[i].send(bytes(jsonResult, encoding="utf-8"))

            elif(flag == 1):
                server.clients[0].send(bytes(jsonResult, encoding="utf-8"))

            elif(flag == 2):
                server.clients[1].send(bytes(jsonResult, encoding="utf-8"))
        except Exception as e:
            print(e)





    #Will check to see if anything is covering the markers.
    #If so, will use the AI to detect if a parcel is present.
    #If object detected will call findLocation and convertToWorldLocation to get x and y TCP values
    #Expected value at end is an array of 6 values.
    def visionSystem(server, in_q):

        """

        Vision functionality for the system (includes AI-yolo5 and aruco marker detection).

        If the arm is ready to pickup a package, determines what the parcel is (AI) and the postion of said parcel.

        Using the bounding box (if parcel was detected), gets center of parcel and returns a depth value. Used for TCP values.

        Args:

            server.systemStatus (string): Used to determine if the vision system needs to shutdown or go to standby.

            in_q (Queue): Queue shared between videoStream and the visionSystem (allows for thread-safe communication). Inserts a frame into the queue to send to the user client.


        Returns:

            None


        """

        # #Check this function call.
        # #Add error handling
        sensor = rs.DepthCamera()
        model, objects, obj_colors = yolov5.create_model('weight_v1.pt')

        while(server.systemStatus != "Offline"):
            if(server.readyForTCPValues == True):
                row_position_average = np.zeros(0)
                column_position_average = np.zeros(0)

                id_matrix = np.zeros(20)

                worldPosition = 0


                ret, depth_frame, color_frame = sensor.get_frames()
                # status, depth, bounds, frame = yolov5.detect(model, color_frame, depth_frame, 192, objects, obj_colors)
                #
                # if(in_q.empty() == True):
                #     in_q.put(frame)

                # if(status == False):
                #     print("Restarting loop")
                #     continue



                #Length is same as moving average length


                #Works
                for counter in range(0, 20):
                    gray = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
                    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
                    arucoParameters = aruco.DetectorParameters_create()
                    corners, ids, rejectedImgPoints = aruco.detectMarkers(
                        gray, aruco_dict, parameters=arucoParameters)

                    try:
                        #Set id matrix position to 1 (marker visible)
                        for i in range(0, len(ids)):
                            if(ids[i] > 20):
                                print("")
                            else:
                                id_matrix[ids[i]] = 1

                        row_position_average, column_position_average, worldPosition = server.findLocation(id_matrix, row_position_average, column_position_average)

                        id_matrix = np.zeros(20)

                        frame = aruco.drawDetectedMarkers(color_frame, corners)
                        if(in_q.empty() == True):
                            in_q.put(frame)

                        ret, depth_frame, color_frame = sensor.get_frames()
                    except Exception as error:
                        print(error)

                server.readyForTCPValues = "False"
                #server.readyForTCPValues == False

                #At this point, because we know the camera angle (45 degrees), can use simple trig to get an aproximate of the depth.

                # marker_distance would hold the values for the displacement between the markers and the camera (x-axis)

                index =  round(row_position_average)
                x_distance = server.marker_distance[index]

                depth = math.sqrt( pow(depth, 2) - pow(x_distance, 2) )

                #jsonResult = {"first":"Target TCP", "second": (worldPosition[0]/1000), "third": (worldPosition[1]/1000), "fourth": (depth/1000) }

                #server.send(jsonResult, 1)

            else:

                gray = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
                aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
                arucoParameters = aruco.DetectorParameters_create()
                corners, ids, rejectedImgPoints = aruco.detectMarkers(
                    gray, aruco_dict, parameters=arucoParameters)


                frame = aruco.drawDetectedMarkers(color_frame, corners)
                if(in_q.empty() == True):
                    in_q.put(frame)



    #x is row position, y is column position

    def convertToWorldLocation(server, x, y):
        """

        Using x and y (row and column position), finds the real world Position.

        Done by measureing the grid (work cell) in TCP values (relative to arm base).

        Args:

            x (numpy array): row position average.

            y (numpy array): column position average.


        Returns:

            realWorldPosition (numpy array): Returns world real Position (both X and Y).


        """


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





    def moving_average(server, x, w):

        """

        Gets the moving average by convolution.

        Args:

            x (numpy array): average to be convolved.

            w (int): length of varible x.

        Returns:

            average(numpy array): returns either row or column position average


        """
        return np.convolve(x, np.ones(w), 'valid') / w



    def findLocation(server, id_matrix, row_position_average, column_position_average):

        """

        Finds the location of a parcel within the grid.

        Uses a matrix to determine the center point of a parcel (0 shows marker is covered).

        Function is called n times (reason to keep track of row position and column position) to get a average.

        Args:

            row_position_average (numpy array): Used to keep track of the row position average for each iteration.

            column_position_average (numpy array): Used to keep track of the column position average for each iteration.

            id_matrix (2d numpy array): Matrix holding the values for each Arcuo marker.


        Returns:

            row_position_average (numpy array): Used to keep track of the row position average for each iteration.

            column_position_average (numpy array): Used to keep track of the column position average for each iteration.

            worldPostiion (numpy array): Returns the TCP values (real world position).


        """

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
           row_position_average = server.moving_average(row_position_average, 20)
           print("Row Position")

           column_position_average = server.moving_average(column_position_average, 20)
           print("Column Position")

           worldPosition = server.convertToWorldLocation(row_position_average, column_position_average)
           # row_position_average = np.zeros(0)
           # column_position_average = np.zeros(0)

        return row_position_average, column_position_average, worldPosition



    def videoStream(server, in_q):

        """

        Creates a Netgear socket (TCP for network protocol) to stream video to the client.

        Allows us to use compression and other protocols for the video stream.

        Args:

            server.clients (list): List of connected clients. Used to get IP of user client (uses a different port).

            in_q (Queue): Queue shared between videoStream and the visionSystem (allows for thread-safe communication).


        Returns:

            None


        """

        ipOfClient = server.clients[0].getpeername()


        #10 frames a sec is fine for the video stream
        #If not, you are welcome to increase (problems with the GUI appear if you do)
        frame_rate = 10
        prev = 0

        # define tweak flags
        options = {
        "compression_format": ".jpg",
        "compression_param": [cv2.IMWRITE_JPEG_QUALITY, 50],
    }



        VidGearServer = NetGear(
            address = ipOfClient[0],
            port = "5454",
            protocol="tcp",
            pattern=0,
            **options
        )

        # loop over until KeyBoard Interrupted
        while True:

            if(server.systemStatus == "Online"):

                try:
                    time_elapsed = time.time() - prev

                    if(time_elapsed > 1./frame_rate):
                        # read frames from stream
                        frame = in_q.get()
                        #print(frame)

                        prev = time.time()

                        VidGearServer.send(frame)

                except KeyboardInterrupt:
                    break
            elif(server.systemStatus == "Offline"):
                VidGearServer.close()
                return


if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 6000

    server = Server(HOST, PORT)
    server.setup()
