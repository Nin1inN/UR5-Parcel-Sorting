"""
The main file for the parcel sorter
"""
import yolov5_Interface as yolov5
import realsense_depth as rs
from server import Server


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 6000

    """
    Initialization
    """
    server = Server(HOST, PORT)
    server.setup()
    model, objects, obj_colors = yolov5.create_model('weight_v1.pt')
    sensor = rs.DepthCamera()


    while True:
        """
        Deal with communication events and block only for a second
        """
        json = ''
        events = server.sel.select(timeout=1)
        for key, mask in events:
            if key.data is None:
                server.accept_conn(key.fileobj)
            else:
                json = server.service_conn(key, mask)


        #json will contain our messages obtained from either clients ;)

        """
        Process vision input
        """
        ret, depth_frame, color_frame = sensor.get_frames()

        #Note model was trained on images that are sized 192x192
        status, depth, bounds, frame = yolov5.detect(model, color_frame, depth_frame, 192, objects, obj_colors)

        server.current_frame = frame


        """
        DO SOMETHING WITH THE INFORMATION GREG
        Also you can do Server.send_to_arm( json/dictionary ) to send directly to arm
        """
