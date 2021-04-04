import tkinter
from tkinter import ttk
#import numpy as np
import cv2
from PIL import Image, ImageTk
import socket
import json
from vidgear.gears import NetGear
import threading
import os
import webbrowser

systemStatus = False

systemConnected = False

root = 0

HOST = '127.0.0.1'
PORT = 6000

class Menubar(ttk.Frame):
    """Builds a menu bar for the top of the main window"""
    def __init__(self, parent, *args, **kwargs):
        ''' Constructor'''
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_menubar()

    def display_help(self):
        '''Displays help document (How to use the GUI)'''
        
        webbrowser.open("README.txt")
        pass

    def display_about(self):
        '''Displays info about program (DDS)'''
        pass

    def init_menubar(self):
        self.menubar = tkinter.Menu(self.root)
        self.menu_help = tkinter.Menu(self.menubar) #Creates a "Help" menu
        self.menu_help.add_command(label='Help', command=self.display_help)
        self.menu_help.add_command(label='About', command=self.display_about)
        self.menubar.add_cascade(menu=self.menu_help, label='Info')

        self.root.config(menu=self.menubar)

class GUI(ttk.Frame):
    """Main GUI class"""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()
        

    def init_gui(self):
        
        #Rename, socket for client
        
        
        self.root.title('Arm Solutions')
        self.root.geometry("1200x800")


        self.background_image = Image.open("Flat_colorful_background.png")
        self.background_image = self.background_image.resize((2000,1200), Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(self.background_image)
        
        self.label = tkinter.Label(self.root, image=self.background_image)
        
        self.label.image = self.background_image
        self.label.place(x=0,y=0, relwidth=1, relheight=1)
       
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
       
        self.root.option_add('*tearOff', 'FALSE') # Disables ability to tear menu bar into own window
#       
        self.systemStatusLabelText = tkinter.StringVar()
        
      
        
        self.systemStatusLabel = tkinter.Label(textvariable= self.systemStatusLabelText , bg = '#e81a1a', width = 25)
        
        
        self.startup_button = tkinter.Button(self.root, text ="Start Up/Resume System", command = self.startSystem, height=3, width= 35, bg = '#499c5f')
        self.pause_button = tkinter.Button(self.root, text ="Put System in Standby", command = self.pauseSystem, height=3, width= 35, bg ='#f9ff54')
        self.settings_button = tkinter.Button(self.root, text ="System Settings", command = self.systemSettings, height=3, width= 35, bg = '#adaaaa')
        self.exit_button = tkinter.Button(self.root, text ="Shut Down System", command = self.on_exit, height=3, width= 35, bg = '#e81a1a')
        
      
        self.imageFrame = tkinter.Frame(self.root)
        self.imageFrame.grid(row=0, column=1, padx=10, pady=50, rowspan=4)
        
        
        
        
        self.startup_button.grid(row=0,column=0, padx=50, pady=(60,100))
        self.pause_button.grid(row=1,column=0, padx=50, pady=(0,100))
        self.settings_button.grid(row=2, column=0, padx=50, pady=(0,100))
        self.exit_button.grid(row=3, column=0, padx=50)
        self.systemStatusLabel.grid(row=3, column=1, pady=10, padx=240)
        
        
        
        
        self.systemStatusLabel.config(font=("New Times Roman", 20))
        self.startup_button.config(font=("New Times Roman", 16))
        self.pause_button.config(font=("New Times Roman", 16))
        self.settings_button.config(font=("New Times Roman", 16))
        self.exit_button.config(font=("New Times Roman", 16))
        
        
        # Menu Bar
        self.menubar = Menubar(self.root)
        
        # Padding
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=5)
    
            
        self.lmain = tkinter.Label(self.imageFrame)
        
        #Variables used later on
        self.speed = tkinter.DoubleVar()
        self.systemStatusLabelText.set("System Status - Offline")
        


#   # function for video streaming
    #Used for testing, change to network stream for final version 
    def video_stream(self):
        global systemStatus
        
        
        # define tweak flags
        options = {"compression_format": ".jpg", "compression_param": cv2.IMREAD_COLOR}
        
        # Define Netgear Client at given IP address and define parameters 
        # !!! change following IP address '192.168.x.xxx' with yours !!!
        self.NetGearclient = NetGear(
            address=HOST,
            port="5454",
            protocol="udp",
            pattern=0,
            receive_mode=True,
            **options
        )
        self.lmain.grid(row=0, column=1, rowspan=3)
        # loop over
        while True:
        
            if(systemStatus == True):
                # receive frames from network
                frame = self.NetGearclient.recv()
            
                # check for received frame if Nonetype
                if frame is None:
                    break
            
                
                thread = threading.Thread(target = self.updateVideoWindow, args = (frame, ))
           
                thread.start()
            
    def updateVideoWindow(self, frame):
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

            
    
    #Modify function to return data decoded
    def receive(self):
        jsonReceived = self.conn.recv(1024)
        jsonReceived = json.loads(jsonReceived.decode("utf-8"))
        print(jsonReceived["first"])
        
  
    def send(self, data):
        
        jsonResult = json.dumps(data)
        self.conn.send(bytes(jsonResult, encoding="utf-8"))
        
        
    def on_exit(self):
        '''Exits program'''
        global root
        
        
        try:
            jsonResult = {"first":"Client 2", "second":"Shut Down System"}
            self.send(jsonResult)
        
        except:
            print("Error sending close command to server")
            
        try:
            root.destroy()
            self.NetGearclient.close()
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            
        except:
            print("Error closing sockets")
        
        finally:
            os._exit(1)
        
    def setVelocity(self):  
      
        try:
            sel = "New Velocity = " + str(self.speed.get())
            self.display_velocity.config(text = sel, font =("New Times Roman", 14)) 
            
            
            jsonResult = {"first":"Client 2", "second":"Set Velocity", "third": str(self.speed.get())}
            self.send(jsonResult)
        
        except Exception as e:
            print(e)
        
        
    def ecoMode(self):
        
        try:
            sel = "New Velocity = " + str(69)
            self.display_velocity.config(text = sel, font =("New Times Roman", 14)) 
            
            
            jsonResult = {"first":"Client 2", "second":"Set Velocity", "third": str(69)}
            self.send(jsonResult)
            
        except Exception as e:
            print(e)

    #Does not shut down the GUI program, goes into a standby mode, ready to start up again.        
    def pauseSystem(self):
        print("Putting system in Standby")
        global systemStatus
        
        
        try:
            jsonResult = {"first":"Client 2", "second":"Pause System"}
            
            self.send(jsonResult)
            
            
            self.systemStatusLabelText.set("System Status - Standby")
            self.systemStatusLabel.config(bg = '#f9ff54')
            systemStatus = False
                                          
        except Exception as e:
            print(e)

        
    #Work the styling for settings window
    def systemSettings(self):
        #Open new window
        
        self.settingsWindow = tkinter.Toplevel(self.root)
        
        self.settingsWindow.title("Settings")
        
        self.settingsWindow.geometry("400x400")
        
        self.velocity_scale = tkinter.Scale(self.settingsWindow, variable = self.speed, from_ = 1, to = 100, orient= tkinter.HORIZONTAL, length = 250, width=30)
        
        self.display_velocity = tkinter.Label(self.settingsWindow)
        
        self.set_velocity = tkinter.Button(self.settingsWindow, text ="Set Velocity", 
            command = self.setVelocity)  
        
        self.eco_button = tkinter.Button(self.settingsWindow, text = "ECO Mode", command = self.ecoMode)
        
        self.velocity_scale.pack(anchor = tkinter.CENTER) 
        self.set_velocity.pack()
        self.eco_button.pack()
        self.display_velocity.pack()
        
        
        

    def startSystem(self):
        global systemConnected
        global systemStatus
       
        
        #Create another client (with a different port) to handle the video stream. 
        
        if(systemConnected == False):
           
            
            
            print("Starting up system")
      
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
                self.conn.connect((HOST, PORT))
                
                jsonResult = {"first":"Client 2", "second":"Start Up System"}
                self.send(jsonResult)
                
                self.receive()
                
                self.systemStatusLabelText.set("System Status - Online")
                self.systemStatusLabel.config(bg = '#499c5f')
                systemStatus = True
                systemConnected = True
                
                #Start video stream here
                
                t1 = threading.Thread(target = self.video_stream)
           
                t1.start()
                
            except Exception as e:
                print(e)
              
        #At this point, if function is called, assuming system is in standby, send message to resume system
        else:
            try:
                jsonResult = {"first":"Client 2", "second":"Resume System"}
                self.send(jsonResult)
                systemStatus = True 
                
                
                
                self.systemStatusLabelText.set("System Status - Online")
                self.systemStatusLabel.config(bg = '#499c5f')
            except Exception as error:
                print(error)
        
       
        
        
def main():
    global root
    root = tkinter.Tk()
    GUI(root)
    root.mainloop()
    
if __name__ == '__main__':
    
    main()
    