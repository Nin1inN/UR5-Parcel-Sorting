"""
Used as an interface to the yolov5 model specifically for usage in the
UR5 Parcel Sorter

Note: Derived from detect.py

-Donny
"""
import numpy as np
from numpy import random
import torch
import cv2

from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.datasets import letterbox
from utils.torch_utils import select_device


#Used to create a yolov5 model to detect objects
def create_model(weight = 'weight.pt'):
    model = attempt_load(weight)
    obj_names = model.module.names if hasattr(model, 'module') else model.names
    obj_colors = [[random.randint(0, 255) for _ in range(3)] for _ in obj_names]

    return model, obj_names, obj_colors


#Tries to detect any objects and extract key information
def detect(model, color_frame, depth_frame, imgsz, obj_names, obj_colors):
    stride = int(model.stride.max())
    
    #Image prep
    img = process_img(color_frame, imgsz, stride)
    img = torch.from_numpy(img).to(select_device(''))
    img = img.float()  # uint8 to fp16/32
    img /= 255.0 #0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    prediction = model(img, augment='store_true')[0]

    #Apply confidence threshold on prediction (0.80, conf-thres), iou-thres = 0.50
    prediction = non_max_suppression(prediction, 0.80, 0.50)

    #Process detections
    img_params = []
    bounds = []
    depth = 0.0
    valid = False
    label = ''
    for i, det in enumerate(prediction):

        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], color_frame.shape).round()

            #Data extraction from detection
            max_conf = 0.0
            for *xyxy, conf, cls in reversed(det):
                
                #Prioritize the highest confidence detection                
                if (conf > max_conf):
                    max_conf = conf
                    
                    bounds = np.array(xyxy)
                    mid_x = int((bounds[0] + bounds[2]) / 2)
                    mid_y = int((bounds[1] + bounds[3]) / 2)
        
                    #Get depth info based on center in mm
                    depth = depth_frame[mid_y, mid_x]

                    img_params = [xyxy, cls, mid_x, mid_y]
                    label = f'{obj_names[int(cls)]} {conf:.2f}'
                    valid = True

    #Edit video frame to include data
    if len(img_params):
        plot_one_box(img_params[0], color_frame, label=label, color=obj_colors[int(img_params[1])], line_thickness=4)
        cv2.circle(color_frame, (img_params[2], img_params[3]), 8, (0, 0, 255))
        cv2.putText(color_frame, "{}mm".format(depth), (img_params[2], img_params[3] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    
    return valid, depth, bounds, color_frame


#Transform the image to be used in the mode
def process_img(img0, img_size, img_stride):
    img = letterbox(img0, new_shape=(img_size, img_size), stride=img_stride)[0]
    img = img[:, :, ::-1].transpose(2,0,1)
    img = np.ascontiguousarray(img)

    return img
