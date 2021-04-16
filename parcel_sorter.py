# -*- coding: utf-8 -*-
"""
The main file for the parcel sorter
"""
import yolov5_Interface as yolov5
import realsense_depth as rs
import cv2


if __name__ == '__main__':
    #Initialize Object Detection Model
    model, objects, obj_colors = yolov5.create_model('weight_v1.pt')
    
    #Initialize Intel Realsense Sensor
    sensor = rs.DepthCamera()
    
    #
    while True:
        ret, depth_frame, color_frame = sensor.get_frames()
        
        #Note model was trained on images that are sized 192x192 
        status, depth, bounds, img = yolov5.detect(model, color_frame, depth_frame, 192, objects, obj_colors)
            
        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', img)
        cv2.waitKey(1)

