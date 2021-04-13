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


systemStatus = "Offline"

root = 0

HOST = '127.0.0.1'
PORT = 6000


class Menubar(ttk.Frame):
    """Builds a menu bar for the top of the main window"""

    def __init__(self, parent, *args, **kwargs):

        """
        Initializes the menubar for the GUI

        Calls the setup (init_menubar) for the rest of the menubar.

        Args:

            parent:

            *args:

            **kwargs:

        Returns:

            self (root): Explain

        """

        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_menubar()


    def display_help(self):

        """
        Displays the help document (How to use the GUI).

        Args: None.

        Returns: None.

        """
        webbrowser.open("README.txt")
        pass

    def display_about(self):

        """
        Displays info about program (purpose of the system).

        Args: None.


        Returns: None.

        """
        pass

    def init_menubar(self):

        """
        Creates the menubar (attached to root) and adds the functionaly for the menubar.

        Creates two commands - Help and About

        Args:

            self (root):

         Returns:

            self (menubar): Something

        """


        self.menubar = tkinter.Menu(self.root)
        self.menu_help = tkinter.Menu(self.menubar) #Creates a "Help" menu
        self.menu_help.add_command(label='Help', command=self.display_help)
        self.menu_help.add_command(label='About', command=self.display_about)
        self.menubar.add_cascade(menu=self.menu_help, label='Info')

        self.root.config(menu=self.menubar)

class GUI(ttk.Frame):
    """Main GUI class"""
    def __init__(self, parent, *args, **kwargs):

        """
        Initializes the GUI with the parmeters set by the user.

        Calls the setup (init_gui) for the rest of the GUI.

        Args:

            parent:

            *args:

            **kwargs:

        Returns:

            self (root): Something

        """

        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()


    def init_gui(self):

        """

        Something


        Args:

            self (root):

        Returns:

            self: Something

        """



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


    def sendPlaceLocation(self):
        global systemStatus

        try:
            data = self.place_position_data.get()

            self.place_position_data.set("")

            data = data.split()

            if(len(data) == 6):

                if(systemStatus == "Online"):
                    print()
                    jsonData = {"first": "Client 2", "second": "Drop Location", "third": data[0], "fourth": data[1], "fifth": data[2], "sixth": data[3], "seventh": data[4], "eight": data[5] }
                    self.send(jsonData)
                    self.placeLocationStatus.set("Parcel Drop Location Updated")
                else:
                    self.placeLocationStatus.set("System status: " + systemStatus)
            else:
                self.placeLocationStatus.set("Incorrect format")

        except Exception as error:
            print(error)
            self.placeLocationStatus.set("Error")



      #Work the styling for settings window
    def systemSettings(self):

        """
        Explain

        Args: None


        Returns: None.

        """

        self.settingsWindow = tkinter.Toplevel(self.root)

        self.settingsWindow.title("Settings")

        self.settingsWindow.geometry("400x400")

        self.velocity_scale = tkinter.Scale(self.settingsWindow, variable = self.speed, from_ = 1, to = 100, orient= tkinter.HORIZONTAL, length = 250, width=30)

        self.display_velocity = tkinter.Label(self.settingsWindow)

        self.set_velocity = tkinter.Button(self.settingsWindow, text ="Set Velocity",
            command = self.setVelocity)

        self.eco_button = tkinter.Button(self.settingsWindow, text = "ECO Mode", command = self.ecoMode)

        self.place_position_data = tkinter.StringVar()

        self.placeLocationStatus = tkinter.StringVar()
        self.placeLocationStatus.set("")

        # creating a label for
        # name using widget Label
        place_position_label = tkinter.Label(self.settingsWindow, text = 'Parcel Drop Location', font=('calibre',10, 'bold'))

        # creating a entry for input
        # name using widget Entry
        place_position_entry = tkinter.Entry(self.settingsWindow, textvariable = self.place_position_data, font=('calibre',10,'normal'))


        # creating a button using the widget
        # Button that will call the submit function
        sub_btn=tkinter.Button(self.settingsWindow, text = 'Update Location', command = self.sendPlaceLocation)

        notify_label = tkinter.Label(self.settingsWindow, textvariable = self.placeLocationStatus, font=('calibre',10, 'bold'))



        self.eco_button.pack()
        self.velocity_scale.pack(anchor = tkinter.CENTER)
        self.set_velocity.pack()
        self.display_velocity.pack()
        place_position_label.pack()
        place_position_entry.pack()
        sub_btn.pack()
        notify_label.pack()

#   # function for video streaming
    #Used for testing, change to network stream for final version
    def video_stream(self):

        """
        After user calls startup for the system and the User_Interface scripts connects to the server, this function is called.

        Creates a NetGear socket (IPC for network protocol) to handle video stream from server.


        Args:

            self (Tkinter Label): Label used to display frame

        Returns:

            self (NetGearclient): NetGearclient for the videos stream

        """


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

            if(systemStatus == "Online"):
                # receive frames from network
                frame = self.NetGearclient.recv()

                # check for received frame if Nonetype
                if frame is None:
                    break


                thread = threading.Thread(target = self.updateVideoWindow, args = (frame, ))

                thread.start()

    def updateVideoWindow(self, frame):


        """
        Function is called by video_stream() to update the frame (image) on the GUI.

        Ran in a thread to avoid blocking of new frame (update frame as fast as network transmits).

        Args:

           frame (OpenCV): frame (image) recieved by the server.

           self (tkinter Label): Label used to display image on the GUI.

        Returns: None.


        """


        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)



    #Modify function to return data decoded
    #Not sure if this function is really needed, used mostly for testing purposes
    def receive(self):
        jsonReceived = self.conn.recv(1024)
        jsonReceived = json.loads(jsonReceived.decode("utf-8"))
        print(jsonReceived["first"])


    def send(self, data):
        """
        Converts data (json dict.) into a string and transmits to connected server socket

        Args:

            self (socket): Uses socket connection (conn) defined in creation of class.

            data (dictionary): Data to be sent over network in the form of json.

        Returns: None.


        """
        jsonResult = json.dumps(data)
        self.conn.send(bytes(jsonResult, encoding="utf-8"))


    def on_exit(self):
        """

        Sends shutdown notification over the network to rest of the system (connected to button event).
        Shuts down video stream (NetGear) and the normal socket.
        Finally exits program

        Args:

            self (socket): Uses socket connection (conn) defined in creation of class

            self (NetGearSocket): Uses NetGearSocket defined in video_stream()

        Returns: None.

        """

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

        """
        Function is called when the user sets a new velocity (connected to button event).
        Transmits new velocity over the network to the arm.

        Args:

            self: Calls the send() function to transmit data payload
            self (Tkinter Label): Updates display_velocity to notify user velocity has been updated

        Returns: None.


        """
        try:

            jsonResult = {"first":"Client 2", "second":"Set Velocity", "third": str(self.speed.get())}
            self.send(jsonResult)

            sel = "New Velocity = " + str(self.speed.get())
            self.display_velocity.config(text = sel, font =("New Times Roman", 14))

        except Exception as e:
            print(e)



    #This is mostly a joke
    #However, it is possible to save alot of energy (up to 21% according to some research papers).
    #It seems as torque increases, running at about half betwen the torque-rpm curve is best
    #It seems the best thing to do is run at 80 to 90% speed with no payload, and reduce as payload increases (torque increases).
    #Can reduce velocity by about 20% with payload vs no payload
    #The e-series robots can measure torque change.
    #No way of knowing power savings (if any) without testing.
    def ecoMode(self):


        """
        Function is called when the user turns on ECO mode (connected to button event).
        Transmits new velocity over the network to the arm.

        Args:

            self: Calls the send() function to transmit data payload
            self (Tkinter Label): Updates display_velocity to notify user velocity has been updated

        Returns: None.


        """
        try:

            jsonResult = {"first":"Client 2", "second":"Set Velocity", "third": str(69)}
            self.send(jsonResult)

            sel = "New Velocity = " + str(69)
            self.display_velocity.config(text = sel, font =("New Times Roman", 14))

        except Exception as e:
            print(e)

    #Does not shut down the GUI program, goes into a standby mode, ready to start up again.
    def pauseSystem(self):

        """

        Function is called when the user puts the system in standby (connected to a button event).

        Sends standby notification over the network to the rest of the system.

        Args:

            self: Calls the send() function to transmit data payload
            self (Tkinter Label): Updates systemStatusLabel (displays system status on Interface) text and color

        Returns: None.




        """

        print("Putting system in Standby")
        global systemStatus


        try:
            jsonResult = {"first":"Client 2", "second":"Pause System"}

            self.send(jsonResult)


            self.systemStatusLabelText.set("System Status - Standby")
            self.systemStatusLabel.config(bg = '#f9ff54')
            systemStatus = "Standby"

        except Exception as e:
            print(e)







    def startSystem(self):

        """
        Function is called when the user starts up the system (connected to a button event).

        Sends startup notification over the network to the rest of the system.

        Runs video_stream() in a new thread.

        Args:

            self: Calls the send() function to transmit data payload.
            self (Tkinter Label): Updates systemStatusLabel (displays system status on Interface) text and color.


        Returns:

            self (socket): Creates socket variable used by the rest of the class.

        """

        global systemStatus


        #Create another client (with a different port) to handle the video stream.

        if(systemStatus == "Offline"):



            print("Starting up system")

            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.conn.connect((HOST, PORT))

                jsonResult = {"first":"Client 2", "second":"Start Up System"}
                self.send(jsonResult)

                #self.receive()

                self.systemStatusLabelText.set("System Status - Online")
                self.systemStatusLabel.config(bg = '#499c5f')
                systemStatus = "Online"


                #Start video stream here

                t1 = threading.Thread(target = self.video_stream)

                t1.start()

            except Exception as e:
                print(e)

        #At this point, if function is called, assuming system is in standby, send message to resume system
        elif(systemStatus == "Standby"):
            try:
                jsonResult = {"first":"Client 2", "second":"Resume System"}
                self.send(jsonResult)
                systemStatus = "Online"



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
