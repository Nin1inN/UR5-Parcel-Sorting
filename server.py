"""
Used as a self manage interface for communication to the client.

Derived from https://realpython.com/python-sockets/#handling-multiple-connections
"""

import socket
import threading
import selectors
import types
import json

class Server: 
    def __init__(server, ip, port):
        server.ip = ip
        server.port = port
        server.sockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.pending_msgs = []
        server.threads = []
        server.sel = selectors.DefaultSelector()
        server.state = 'Offline'
        
        
    def start(server):
        #Initiate socket communications
        server.socket.bind((server.ip, server.port))
        server.socket.listen(5)
        print('Listening on', (server.ip, server.port))
        
        #Prep for multiple clients 
        server.socket.setblocking(False)
        server.sel.register(server.socket, selectors.EVENT_READ, data=None)
        
        #Process connections and communications
        while True:
            events = server.sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    server.accept_client(key.fileobj)
                else:
                    server.service_client(key, mask)
                    
    
    def accept_client(server):
        #accept the client
        conn, addr = server.socket.accept()
        print('Accepted connection', addr)
        conn.setblocking(False)
        
        server.clients.append(conn)
        
        #Update the selector
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        server.sel.register(conn, events, data=data)
    
    
    def service_client(server, key, mask):
        client_sock = key.fileobj
        data = key.data
        
        if mask & selectors.EVENT_READ:
            recv_data = client_sock.recv(1024)
            if recv_data:
                data.outb += recv_data
                
                #Process json commands 
                try:
                    jsonReceived = json.loads(recv_data.decode("utf-u"))
                    if(jsonReceived['first'] == 'Client 1'):
                        if(jsonReceived['second'] == 'Ready for TCP Values'):
                            readyForTCPValues = 'Yes'
                            
                    elif(jsonReceived['first'] == 'Client 2'):
                        if(jsonReceived['second'] == 'Start Up System'):
                            if(server.state == 'Offline'):
                                jsonResult = {'first':'System Started'}
                                jsonResult = json.dumps(jsonResult)
                                client_sock.send(bytes(jsonResult, encoding='utf-8'))
                                
                                server.state = 'Online'
                                
                                #t1 = threading.Thread(target = videoStream, args=(client_sock))
                                #t1.start()
                                
                                print('Starting up')
                                
                        elif(jsonReceived['second'] == 'Resume System'):
                            jsonResult = {'first':'System Resume'}
                            jsonResult = json.dumps(jsonResult)
                            client_sock.send(bytes(jsonResult, encoding='utf-8'))
                                
                            server.state = 'Online'
                            
                            print('System Resuming')
                                
                        elif(jsonReceived['second'] == 'Pause System'):
                            jsonResult = {'first':'Go into Standby'}
                            jsonResult = json.dumps(jsonResult)
                            client_sock.send(bytes(jsonResult, encoding='utf-8'))
                                
                            server.state = 'Standby'
                            
                            print('System going into standby')
                            
                        elif(jsonReceived['second'] == 'Drop Location'):
                            if(server.state == 'Online'):
                                jsonResult = {'first':'Drop Location', 'second': jsonReceived["third"], "third": jsonReceived["fourth"], "fourth": jsonReceived["fifth"], "fifth": jsonReceived["sixth"], "sixth": jsonReceived["seventh"], "seventh": jsonReceived["eight"]}
                                
                                print(jsonResult)
                                
                        elif(jsonReceived['second'] == 'Set Velocity'):
                            if(server.state == 'Online'):
                                jsonResult = {'first':'Velocity Change', 'second': jsonReceived['third']}
                                jsonResult = json.dumps(jsonResult)
                                client_sock.send(bytes(jsonResult, encoding='utf-8'))
                                
                                
                        elif(jsonReceived['second'] == 'Shut Down System'):
                            server.state = 'Offline'
                            
                            #Client 0 for testing, client 1 for final version

                            #Disconnect socket for video feed here
                            try:
                                client_sock.close()
                                #VidGearServer.close()
                                #stream.release()
                                #temp = clients[0]
                                #Keeping the first client (Arm Movement)
                                #clients = []
                                #clients.append(temp)
            
                            except Exception as e:
                                pass
                                #logging.error(e)
                            
                            finally:
                                return
                except:
                    pass
                
            else:
                print('closing connection to', data.addr)
                server.sel.unregister(client_sock)
                client_sock.close()
                
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = client_sock.send(data.outb)
                data.outb = data.outb[sent:]
        
        
                    