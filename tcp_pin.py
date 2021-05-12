import socket
import time
import math
import rtde_control
import rtde_receive
import cv2
import pyrealsense2

import threading

import RPi.GPIO as GPIO

switch = 18
pump = 7


GPIO.setmode(GPIO.BOARD)
GPIO.setup(switch, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(pump, GPIO.OUT)

#####################################################
def movRobot(tcpPose,v, a, asnc):
	rtde_c.moveL(tcpPose[0], v, a, False)

	rtde_c.moveL(tcpPose[1], v, a, True)
	while ( not GPIO.input(18)):
		print("not pressed")
	
	rtde_c.moveL(tcpPose[2], v, a, False)
	rtde_c.moveL(tcpPose[3], v, a, False)

	rtde_c.moveL(tcpPose[4], v, a, False)
	print("Turn Off Pump")
	# time.sleep(2)

	rtde_c.moveL(tcpPose[5], v, a, False)
	rtde_c.moveL(tcpPose[6], v, a, False)


	if(GPIO.input(18)):
		print("Button Pressed")
		GPIO.output(led,GPIO.HIGH)
	else:
		print("not pressed")
		GPIO.output(led,GPIO.LOW)


def movRobotPath(tcpPose, asnc):
	rtde_c.moveL(tcpPose, asnc)
	print("MOVING TO POSITION")

def BSFunction(tcpPose):
	rtde_c.moveL(tcpPose, False)
	rtde_c.moveL(tcpPose, True)


def stopRobt():
	rtde_c.stopJ(2.0)

def getForce():
	rst = rtde_c.zeroFtSensor()
	print(rst, "=== Force Reset")
	for i in range(5):
		contact = rtde_r.getActualTCPForce()
		print("Current Force Values ", contact)
	# 	print("Forces #",i," ->",contact,rtde_c.isSteady())
		time.sleep(0.5)
	# while (contact[2] > 20):
	# 	contact = rtde_r.getActualTCPForce()
	# stopRobt()
#####################################################
# UR COMM CODE
HOST = "10.0.0.6"   # The remote host
PORT = 30002

rtde_c = rtde_control.RTDEControlInterface(HOST)
rtde_r = rtde_receive.RTDEReceiveInterface(HOST)
###################################################

v = 2
a = 0.3
blend =0.00

print("Connection: ",rtde_c.isConnected())
# coordinates
move_joints_1 = [-0.5,-0.22,0.3,2.89,-1.29,0.126]
move_joints_2 = [-0.5,-0.22,0.4,2.89,-1.29,0.126]

drop =     [ 0.145, -0.623, 0.0479, 3.09,  0.0169, -0.041]
placing =  [ 0.116, -0.559, 0.4300, 3.10,  0.0169, -0.050]
# placing1 = [-0.252, -0.511, 0.4300,  2.95, -0.9491, -0.063]
home =     [-0.537, -0.193, 0.4300, 2.40, -2.0000, -0.079] # We might not need this

marker1 =  [-0.695, -0.215, 0.1416, 2.34, -2.1194, -0.041]
marker2 =  [-0.698, -0.105, 0.1351, 2.16, -2.2841, -0.060]

marker3 =  [-0.703, -0.023, 0.154, 1.95, -2.48, -0.02]


marker4 =  [-0.693, -0.128, 0.141, 1.77, -2.63, -0.00]

package1 = [-0.693, -0.128, 0.141, 1.77, -2.63, -0.00]
package2 = [-0.645,  0.136, 0.096, 1.21, -2.94,  0.03]
package3 = [-0.425,  0.130, 0.096, 0.93, -2.96,  0.02]


# marker5 =  [-0.678, -0.218, 0.1440, 1.56, -2.6799, -0.170]
# marker6 =  [-0.582, -0.229, 0.1388, 1.47, -2.7888, -0.060]

# marker7 =  [-0.581, -0.135, 0.1331, 1.65, -2.6666, -0.089]
# marker8 =  [-0.695, -0.215, 0.1416, 2.34, -2.1194, -0.041]
# marker9 =  [-0.695, -0.215, 0.1416, 2.34, -2.1194, -0.041]




coordinates = []
# MUST APPEND IN ORDER OF PATH TRAVELLING
coordinates.append(home) 	 # 0
coordinates.append(package1) # 1

coordinates.append(home)	 # 2 
coordinates.append(placing)  # 3
coordinates.append(drop)     # 4
coordinates.append(placing)  # 5
coordinates.append(home)     # 6

coordinates.append(package2)
coordinates.append(home)
coordinates.append(placing)
coordinates.append(drop)
coordinates.append(placing)
coordinates.append(home)

coordinates.append(package3)
coordinates.append(home)
coordinates.append(placing)
coordinates.append(drop)
coordinates.append(placing)
coordinates.append(home)

# coordinates.append(home)
# coordinates.append(marker2)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)

# coordinates.append(home)
# coordinates.append(marker3)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)

# coordinates.append(home)
# coordinates.append(marker4)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)


# coordinates.append(home)
# coordinates.append(marker5)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)

# coordinates.append(home)
# coordinates.append(marker6)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)

# coordinates.append(home)
# coordinates.append(marker7)
# coordinates.append(home)
# coordinates.append(placing)
# coordinates.append(drop)

# coordinates.append(move_joints_1)
# coordinates.append(move_joints_2)
# # coordinates.append(placing1)
# coordinates.append(placing)
# coordinates.append(drop)

# append velocity, acceleration, blend to each coordinate vector
# for waypoints in coordinates:
# 	waypoints.append(v)
# 	waypoints.append(a)
# 	waypoints.append(blend)


# move_joints_1.append(v)
# move_joints_1.append(a)
# move_joints_1.append(0.0)


# move_joints_2.append(v)
# move_joints_2.append(a)
# move_joints_2.append(0.0)

# drop.append(v)
# drop.append(a)
# drop.append(0.0)

# placing.append(v)
# placing.append(a)
# placing.append(0.0)

# home.append(v)
# home.append(a)
# home.append(0.0)
###########################
# Creates path by packing in order of coordinates
path = []

for waypoints in coordinates:
	path.append(waypoints)
path.append(home)
# # path.append(placing1)

# path.append(home)
# combined.append(move_joints_1)
# combined.append(move_joints_2)
# combined.append(placing)

# combined.append(drop)
# combined.append(home)






# runs = rtde_c.moveL(move_joints_2,v,a,False)

# Spawning thread for movement
move = threading.Thread(target = movRobot, args = (coordinates,v,a,False))
move.start()
# for i in range(9):

# movePath = threading.Thread(target = movRobotPath, args = (path,False))
# movePath.start()
# movePath.join()

# FREE MODE
# rtde_c.teachMode()
# time.sleep(300)

# EndFreedrive Mode
rtde_c.endTeachMode()
time.sleep(5)

# print("5 seconds done - getting force")

# force = threading.Thread(target = getForce)
# force.start()

# stop = threading.Thread(target = stopRobt)
# stop.start()

# tcp = rtde_r.getTargetTCPPose()
# print ("tcp",tcp)
# rtde_c.stopJ(2.0)





###################################################
### EVERYTHING BELOW DOES NOT WORK OR IS SUPPOSE TO INTEGRATE WITH DEPT
# while True:
#     #show distance for a specific point
#     # (X,Y)
#     ret,depth_frame,color_frame = dc.get_frame()
#     cv2.circle(color_frame, point,4,(0,0,255))
#     # [y] [x] when using cv2
#     distance = depth_frame[point[1],[point[0]]]

#     cv2.putText(color_frame,"{}mm".format(distance),(point[0],point[1]-20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)


#     cv2.imshow("depth frame",depth_frame)
#     cv2.imshow("Color frame", color_frame )
#     cv2.waitKey(1)






# while (runs):
	#tcp = rtde_r.getTargetTCPPose()
	#print ("tcp",tcp)
	# direction = [0.00,0.00,1.001,0.001,0.001,1.001]
	
	# contact = rtde_r.getActualTCPForce()
	#print ("Force",contact)
	#print ("Force",contact[2])
	#if((contact[2] < -10 ) or (contact[2] > 30 ) ):
	#	runs = False
	#	rtde_c.stopJ(2.0)
	#	time.sleep(5)
	

#actual_q = rtde_r.getActualQ()
#print ("Move Joint Angles:",actual_q)


