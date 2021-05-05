import socket
import json
import numpy as np
import time
import threading
import math
#import rtde_control
#import rtde_receive
import cv2
import pyrealsense2
from queue import Queue
from threading import Event



# armVelocity = 0

#For the demo, there will only be one drop position.
#However, for future projects, more can be added
#Will be set to a default position, however, user can change this
# place_position = np.zeros(6)


#Ready to add other functions for arm movement






class Arm_Movement:
    def __init__(self):

        """
        Constructor:

        Setups up the parameters used by the rest of the system.

        Args:

            None.

        Returns:

            None.

        """
        self.serverIP = '127.0.0.1'
        self.serverPORT = 6000
        self.armIP = "10.0.0.4"
        self.armPORT = 30002
        self.systemStatus = "Offline"


    def setup(self):

        """
        Connects Arm Movement to the UR5 and the Server.

        Starts up the rest of the functionality for the class.

        Args:

            None.

        Returns:

            None.

        """



        connected = False

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        rtde_c = 0
        rtde_r = 0

        #Connect to arm
        while not(connected):
            try:
                #rtde_c = rtde_control.RTDEControlInterface(self.armIP)
               # rtde_r = rtde_receive.RTDEReceiveInterface(self.armIP)
                connected = True
            except Exception as e:
                print(e)
            finally:
                time.sleep(1)

        #Move arm to home position


        # Connect to server.
        connected = False
        while not(connected):
            try:
                conn.connect((self.serverIP, self.serverPORT))
                connected = True
            except Exception as e:
                print(e)
            finally:
                time.sleep(1)


        q = Queue()
        # t1 = threading.Thread(target = self.moniterUserInput, args = (q, conn, ))
        t2 = threading.Thread(target = self.TCPwrapper, args = (q, conn, rtde_c, rtde_r,  ))

        #t1.start()
        t2.start()

        #t1.join()
        t2.join()



    #z axis = 109mm at workcell level.
    #Tells server ready for TCP values
    def TCPwrapper(self, in_q, conn, rtde_c, rtde_r):


        """
        Main control logic for the arm. Moves and moniters the arm for pick and place operation.

        Tracks the position of the arm and moniters input from the user.

        Requests TCP values when in home position (system just started or dropped a parcel and ready for the next).

        Args:

            in_q (Queue): Queue shared between TCPwrapper and moniterUserInput (allows for thread-safe communication). Used to moniter input from the user (network).

            conn (socket): Socket connected to server.

            rtde_c (class): Control interface for the arm (send data).

            rtde_r (class): Receive interface for the arm (read data).

        Returns:

            None.

        """

        #For testing purposes
        self.systemStatus = "Online"



        #Place holders, set to defaults
        home_position = np.array([-0.093, -0.486, 0.530, 1.56, -2.62, -0.03])
        armVelocity = 0.3

        targetTCP = np.zeros(6)
        place_position = np.zeros(6)


        #Used for testing, remove for final version
        # jsonResult = {"first": "TCP Values", "second": "-0.514", "third": "-0.029" , "fourth": "0.220" , "fifth": "1.05" , "sixth": "-3", "seventh": "-0.15"  }
        #
        #
        # in_q.put(jsonResult)
        #
        # jsonResult = {"first": "Place Location", "second": "-0.050", "third": "-0.565" , "fourth": "0.270" , "fifth": "1.05" , "sixth": "-3", "seventh": "-0.15"  }
        #
        # in_q.put(jsonResult)

        while (True):


            if(self.systemStatus == "Online"):


                    jsonResult = {"first":"ARM", "second": "Ready for TCP Values"}
                    self.send(conn, jsonResult)
                    time.sleep(1)



                    #Will empty queue at the beginning of each sequence
                    #May check for velocity changes between each section.
                    while(in_q.empty() == False):
                        jsonReceived = in_q.get()

                        if(jsonReceived["first"] == "Target TCP"):
                            targetTCP[0] = float(jsonReceived["second"])
                            targetTCP[1] = float(jsonReceived["third"])
                            targetTCP[2] = float(jsonReceived["fourth"])

                            #For TCP orientation, probably wont need.
                            # targetTCP[3] = float(jsonReceived["fifth"])
                            # targetTCP[4] = float(jsonReceived["sixth"])
                            # targetTCP[5] = float(jsonReceived["seventh"])

                        elif(jsonReceived["first"] == "Place Location"):
                            place_position[0] = float(jsonReceived["second"])
                            place_position[1] = float(jsonReceived["third"])
                            place_position[2] = float(jsonReceived["fourth"])
                            place_position[3] = float(jsonReceived["fifth"])
                            place_position[4] = float(jsonReceived["sixth"])
                            place_position[5] = float(jsonReceived["seventh"])

                        elif(jsonReceived["first"] == "Velocity Change"):
                            armVelocity = jsonReceived["second"]

                    #Async allows us to stop the arm
                    #For safety or other issues


                    #Called here so if user changes place position while arm is in seqeuence, changes for next sequence.

                    #Not doing a current velocity since the user will likely will want the arm to change velocity as quickly as possible

                    #This section moves the arm to pickup a package
                    self.movRobot(rtde_c, targetTCP, armVelocity, 0.6, True, False)
                    time.sleep(1)

                    #armPosition = "Unknown"

                    self.checkTCPValues(rtde_r, rtde_c, targetTCP, armVelocity)
                    #
                    # pickParcel()
                    #
                    # #################################################################
                    #
                    # armVelocity = checkVelocity(in_q, armVelocity)
                    #
                    # #This section moves the arm to parcel drop location
                    self.movRobot(rtde_c, place_position, armVelocity, 1, True, True)
                    time.sleep(1)


                    self.checkTCPValues(rtde_r, rtde_c, place_position, armVelocity)
                    #
                    # placeParcel()

                    #################################################################

                    # armVelocity = checkVelocity(in_q, armVelocity)
                    #
                    self.movRobot(rtde_c, home_position, armVelocity, 1, True, False)
                    time.sleep(1)

                    self.checkTCPValues(rtde_r, rtde_c, home_position, armVelocity)

                    #Arm at home position, ready to repeat

                    #armPosition =  "Home"






    #Ready for code
    def pickParcel(self):


        #At this point (in checkTCPValues) can read the sensor (switch), if nothing, move lower in the z axis by small increments)
        pass

    #Ready for code
    def placeParcel(self):
        pass

    def stopRobot(self, rtde_c):

        """
        Stops the arm with a joint deceleration of 2 rad/s^2

        Args:

            rtde_c (class): Control interface for the arm (send stop command to arm).

        Returns:

            None.

        """
        rtde_c.stopJ(2.0)



    def movRobot(self, rtde_c, targetTCP,v, a, asyn, payload):

        """
        Moves the arm to the given targetTCP values.

        Depending on the velocity mode (ECO or constant), moves the arm at different speeds.

        Args:

            rtde_c (class): Control interface for the arm (send move command to arm).

            targetTCP (list): TCP values for arm to move to.

            v (int): velocity for arm (either value from 0 to 100 or ECO).

            a (int): accleration for arm.

            asyn (bool): Allows the arm to run in asynchronous mode

            payload (bool): Whether the arm currently has a payload (used in ECO mode)

        Returns:

            None.

        """

        if(v == "ECO"):
            if(payload == False):
                print()
                #Move at higher velocity
                rtde_c.moveL(targetTCP, v, a, asyn)

            elif(payload == True):
                print()
                #Reduce velocity by 20%
                rtde_c.moveL(targetTCP, v, a, asyn)

        else:
            #Assuming if v != ECO, is a int in string format
            v = int(v)
            rtde_c.moveL(targetTCP, 0.1, 0.1, asyn)
            print("MOVING TO POSITION")


    def checkVelocity(self, in_q, currentArmVelocity):

        """
        Checks the Queue to see if a arm velocity change has been received from the server.

        Returns new velocity, otherwise returns the current velocity.


        Args:

            in_q (Queue): Queue shared between TCPwrapper and moniterUserInput (allows for thread-safe communication).

            currentArmVelocity (int): If no velocity change (or queue is empty), returns this value.

        Returns:

            armVelocity (int or string): New velocity for arm

        """

        if (in_q.empty() == False):

            jsonReceived = in_q.get()

            if(jsonReceived["first"] == "Velocity Change"):
                armVelocity = jsonReceived["second"]
                return armVelocity
        else:
            #Get pops the data from the queue, putting data back into queue
            in_q.put(jsonReceived)
            return currentArmVelocity



    #This function will be used to compare target TCP vs current TCP
    def checkTCPValues(self, rtde_r, rtde_c, targetTCP, armVelocity):

        """
        Checks current TCP values of UR5 against target TCP values.

        Moniters input from user (e.g. system go into standby). Will restart arm movement if system goes into standby.

        Args:

            rtde_c (class): Control interface for the arm (restart arm movement if system pauses).

            rtde_r (class): Receive interface for the arm (get current TCP values of UR5).

            targetTCP (list): TCP values for arm to move to.

            armVelocity (int or string): velocity for arm (either value from 0 to 100 or ECO).



        Returns:

            None.

        """



        flag = 0

        currentTCPValues = rtde_r.getActualTCPPose()

        currentTCPValues = currentTCPValues[0:3]

        targetTCP = targetTCP[0:3]

        # print("Current TCP Values" + str(currentTCPValues))
        # print("Target TCP Values" + str(targetTCP))

        #Run in loop until arm arrives at targetTCP
        #Flag varible is used to moniter if the system is online
        #If flag is set to 1, means system stopped at some point.
        #Need to finish the last step before moving on.
        while ( np.allclose(currentTCPValues, targetTCP, 0.01) == False) :

            # print("Current TCP Values" + str(currentTCPValues))
            # print("Target TCP Values" + str(targetTCP))
            try:
                currentTCPValues = rtde_r.getActualTCPPose()
                time.sleep(1)
                currentTCPValues = currentTCPValues[0:3]

                if(flag == 0):

                    if(self.systemStatus != "Online"):
                        flag = 1
                        self.stopRobot(rtde_c)

                elif(self.systemStatus == "Online"):

                    if(flag == 1):
                        self.movRobot(rtde_c, targetTCP, armVelocity, 1, True)
            except Exception as error:
                print(error)
                print("Error is caught here")
                self.movRobot(rtde_c, targetTCP, armVelocity, 0.6, True, False)

                #currentTCPValues = rtde_r.getActualTCPPose()





    def receive(self, conn):

        """
        Returns data received from server.

        Args:

            conn (socket): socket connected to server.

        Returns:

            jsonReceived (JSON - dictionary): returns json data.
        """
        jsonReceived = conn.recv(1024)
        jsonReceived = json.loads(jsonReceived.decode("utf-8"))
        return jsonReceived

    def send(self, conn, data):

        """
        Sends data to the server.

        Args:

            conn (socket): socket connected to server.

            data (JSON - dictionary): data to send.

        Returns:

            None.

        """

        jsonResult = json.dumps(data)
        conn.send(bytes(jsonResult, encoding="utf-8"))


    def moniterUserInput(self, out_q, conn):

        """
        Moniters data received from the server and performs the command receieved.

        Args:

            out_q (Queue): Queue shared between TCPwrapper and moniterUserInput (allows for thread-safe communication). Puts commands on the queue for TCPWrapper to use.

            conn (socket): socket connected to server.

        Returns:

            None.

        """

        while(True):
            jsonReceived = self.receive(conn)

            #Add commands for this script
            #System Pasue, shutdown, velocity change, etc.

            if(jsonReceived["first"] == "System Started"):
                print("System online")
                self.systemStatus = "Online"

            elif(jsonReceived["first"] == "Go into Standby"):
                print("System in standby")
                self.systemStatus = "Standby"

            elif(jsonReceived["first"] == "Shut Down System"):
                print("System offline")
                self.systemStatus = "Offline"


            elif(jsonReceived["first"] == "Velocity Change"):
                print("Velocity Change")

                out_q.put((jsonReceived))

            elif(jsonReceived["first"] == "Place Location"):
                print("Drop Location Changed")

                out_q.put((jsonReceived))

            elif(jsonReceived["first"] == "TCP Values"):
                print("TCP Values")

                out_q.put((jsonReceived))



if __name__ == "__main__":

     armControl = Arm_Movement()
     armControl.setup()
