# -*- coding: utf-8 -*-
"""
Testing out Model Function through a single frame
"""
import yolov5_Interface as yolov5
import cv2


if __name__ == '__main__':
    model, objects, obj_colors = yolov5.create_model('weight_v1.pt')
    img0 = cv2.imread('test_image.jpg')

    status, Bounds, Depths = yolov5.detect(model, img0, img0, 192, objects, obj_colors)

    print(Bounds)
    print(Depths)
