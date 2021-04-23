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
#import yolov5_Interface as yolov5
#import realsense_depth as rs


class Server:
    def __init__(server, ip, port):
        server.ip = ip
        server.port = port
        server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.clients = []
        server.systemStatus = "Offline"
        server.readyForTCPValues = False
      
    
    def setup(server):     
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
                
                t1 = threading.Thread(target = server.clientHandler, args = (conn, serversocket))
        
                t1.start()
        
            except Exception as e:
                print(e)

    
    
    
    def clientHandler(server, clientsocket, serversocket):
    
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
    
    
                    #Disconnect socket for video feed here
                    try:
                        server.clients[0].close()
                        
                        #Rest of code will not need in final version
                        # temp = server.clients[0]
                        # #Keeping the first client (Arm Movement)
                        server.clients = []
                        # server.clients.append(temp)
    
                    except Exception as e:
                        logging.error(e)
    
                    finally:
                        return
                       #os._exit(1)
    
    
    
    
    #Flag will be used to indicate which client to send to
    # 0 = both
    # 1 = Client 1 (Arm Movement)
    # 2 = Client 2 (User Interface)
    def send(server, data, flag):
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
        
        pass
        #Not needed, used for testing.
        # stream = cv2.VideoCapture(0)
        
        # while(server.systemStatus != "Offline"):
        #     if(in_q.empty() == True):
        
        #         #ret, depth_frame, color_frame = sensor.get_frames()
        #         color_frame = stream.read()
        #         in_q.put(color_frame)
                
        # stream.release()
    
    
    
    
    
    
        # #Check this function call.
        # #Add error handling
        # sensor = rs.DepthCamera()
        # model, objects, obj_colors = yolov5.create_model('weight_v1.pt')
        #
        # while(systemStatus != "Offline"):
        #
        #     row_position_average = np.zeros(0)
        #     column_position_average = np.zeros(0)
        #
        #     id_matrix = np.zeros(20)
        #
        #     worldPosition = 0
        #
        #     if(readyForTCPValues == True):
        #
        #         ret, depth_frame, color_frame = sensor.get_frames()
        #         status, depth, bounds, frame = yolov5.detect(model, color_frame, depth_frame, 192, objects, obj_colors)
        #
        #         if(status == False):
        #             continue
        #
        #         readyForTCPValues == False
        #
        #         #Length is same as moving average length
        #     #    for counter in range(0, 20):
        #     #        gray = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
        #     #        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
        #     #        arucoParameters = aruco.DetectorParameters_create()
        #     #        corners, ids, rejectedImgPoints = aruco.detectMarkers(
        #     #            gray, aruco_dict, parameters=arucoParameters)
        #     #
        #     #        #Set id matrix position to 1 (marker visible)
        #     #        for i in range(0, len(ids)):
        #     #            if(ids[i] > 20):
        #     #                print("")
        #     #            else:
        #     #                id_matrix[ids[i]] = 1
        #     #
        #     #        row_position_average, column_position_average, worldPosition = findLocation(id_matrix, row_position_average, column_position_average)
        #     #
        #     #        id_matrix = np.zeros(20)
        #
        #
        #
        #     else:
        #         ret, depth_frame, color_frame = sensor.get_frames()
        #
        #         if(in_q.empty() == True):
        #             in_q.put(color_frame)
    
    
    
    #x is row position, y is column position 
    
    def convertToWorldLocation(server, x, y):
        
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
    
    
    
    def moving_average(server, x, w):
        return np.convolve(x, np.ones(w), 'valid') / w
    
    
    
    def findLocation(server, id_matrix, row_position_average, column_position_average):
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
           row_position_average = np.zeros(0)
           column_position_average = np.zeros(0)
    
        return row_position_average, column_position_average, worldPosition
    
    
    
    def videoStream(server, in_q):
        #global systemStatus
        
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
    
                        VidGearServer.send(frame[1])
    
                except KeyboardInterrupt:
                    break
            elif(server.systemStatus == "Offline"):
                VidGearServer.close()
                return
