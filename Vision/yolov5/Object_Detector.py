import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
import numpy as np
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams
from utils.general import check_img_size, check_imshow, non_max_suppression, \
    scale_coords, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized


def detect(weights = 'best.pt', device = '0', imgsize = 192, timeout = 2):
    # Initialize
    set_logging()
    sdevice = select_device('')
    half = sdevice.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load('best.pt', map_location=sdevice)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsize = check_img_size(imgsize, s=stride)  # check img_size
    if half:
        model.half()  # to FP16
        
    view_img = check_imshow()
    cudnn.benchmark = True  # set True to speed up constant image size inference
    dataset = LoadStreams(device, img_size=imgsize, stride=stride)
    
    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    fps = 30 #assumption
    frame_limit = timeout * fps #Time limit to be absoultely sure package is there
    avg_position = np.array([0.0, 0.0])
    
    
    if sdevice.type != 'cpu':
        model(torch.zeros(1, 3, imgsize, imgsize).to(sdevice).type_as(next(model.parameters())))  # run once
    
    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(sdevice)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment='store_true')[0]

        # Apply NMS
        #conf-thres = 0.80 (Tolerance for how sure its the object?), iou-thres = 0.50
        pred = non_max_suppression(pred, 0.80, 0.50)
        t2 = time_synchronized()

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()

            p = Path(p)  # to Path
            
            s += '%gx%g ' % img.shape[2:]  # print string
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    test = np.array(xyxy)
                    print(test)
                    
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)

            # Print time (inference + NMS)
            print(f'{s}Done. ({t2 - t1:.3f}s)')


            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond
            

    print(f'Done. ({time.time() - t0:.3f}s)')


if __name__ == '__main__':
    detect()
