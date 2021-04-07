# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 00:08:22 2021

@author: Donny
"""
import cv2
import time
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized


def get_package_position(weights, imgsize, camera):
    attempts = 0
    
    #Initialize 
    set_logging()
    device = select_device(0)
    
    #Setup Model
    model = attempt_load(weights, map_location=device)
    stride = int(model.stride.max())
    imgsz = check_img_size(imgsz, s=stride)
    model.half()
    
    obj_names = model.module.names if hasattr(model, 'module') else model.names
    
    model(torch.zeros(1,3, imgsz, imgsz).to(device).type_as(next(model.parameters())))
    t0 = time.time()
    
    while(camera.isOpened()):
        valid, frame = camera.read()
        
        if (attempts >= 3):
            return False, []
        
        if (not valid):
            print("Failed to capture Image, trying again . . .")
            continue
        
        frame = cv2.resize(frame, (imgsize, imgsize))
        t1 = time_synchronized()
        pred = model(frame)[0]
        
        pred = non_max_suppression(pred, 0.8, 0.45)
        t2 = time_synchronized()
        
        for i, det in enumerate(pred):
            for *xyxy, conf, cls in reversed(det):
                print(xyxy)
        
        
cam = cv2.captureVideo(0)
get_package_position("best.pt", 192, cam)
cam.release()
        
        
        
        
        
        