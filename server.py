"""
Used as a network interface for communication to the clients.

Derived from https://realpython.com/python-sockets/#handling-multiple-connections
"""

import socket
import threading
import selectors
import types
import json
import numpy as np

"""
Frame is a numpy array
Server
frame = frame.flatten()
data = frame.tostring()

Client
frame = numpy.fromtstring(data, dtype=numpy.uint8)
frame = numpy.reshape(frame, (640,480,3))
"""

class Server:
    def __init__(server, ip, port):
        server.ip = ip
        server.port = port
        server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.clients = {}
        server.stream_thread = ''
        server.sel = selectors.DefaultSelector()
        server.current_frame = np.zeros((640, 480), dtype=int)


    def setup(server):
        #Initiate socket communications
        server.socket.bind((server.ip, server.port))
        server.socket.listen(5)
        print('Listening on', (server.ip, server.port))

        #Prep for multiple socket clients
        server.socket.setblocking(False)
        server.sel.register(server.socket, selectors.EVENT_READ, data=None)


    def accept_conn(server, sock):
        #accept the client
        conn, addr = sock.accept()
        print('Accepted connection', addr)
        conn.setblocking(False)

        #Update the selector
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        #Add new client in the selector
        server.sel.register(conn, events, data=data)


    def service_conn(server, key, mask):
        conn = key.fileobj
        data = key.data
        msg = ''

        #Obtain message from connections
        if mask & selectors.EVENT_READ:
            recv_data = conn.recv(1024)
            
            if recv_data:
                data.outb += recv_data

                try:
                    jsonReceived = json.loads(recv_data.decode("utf-u"))
                    msg = jsonReceived
                    
                    #Check for ARM 
                    if(jsonReceived['first'] == 'ARM'):
                        server.clients['ARM'] = conn

                    #Check for CONTROL
                    elif(jsonReceived['first'] == 'CONTROL'):
                        server.clients['CONTROL'] = conn
                        
                        if (server.stream_thread == ''):
                            server.stream_thread = threading.Thread(target = server.stream_current_frame, args = (server, conn))
                            server.stream_thread.start()
                except:
                    pass

            else:
                print('closing connection to', data.addr)
                server.sel.unregister(conn)
                conn.close()
            

        #Echos message received
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = conn.send(data.outb)
                data.outb = data.outb[sent:]
        
        return msg


    def send_to_arm(server, data):
        out = json.dumps(data)
        server.clients['ARM'].send(bytes(out, encoding='utf-8'))


    def send_to_control(server, data):
        out = json.dumps(data)
        server.clients['CONTROL'].send(bytes(out, encoding='utf-8'))


    #Used to get visual feedback from vision systems
    def stream_current_frame(server, conn):
        try:
            while True:
                frame = server.current_frame.flatten()
                data = frame.tostring()

                out = { "Stream": data }
                out = json.dumps(out)

                conn.send(bytes(out, encoding="utf-8"))
        finally:
            print('Video Stream Ended')
