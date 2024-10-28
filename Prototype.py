import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import numpy as np
from pygrabber.dshow_graph import FilterGraph
import pygame
import serial.tools.list_ports
import serial
import random

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

dot_position = None

temp = []
valo = 100

# arduino = serial.Serial('COM5', 19200)

class Main(ctk.CTk):            
    def __init__(self):
        super().__init__()
        #self.geometry(f"{700}x{450}")
        self.title('Tracker')
        
        # self.attributes('-fullscreen', True)
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((1,2), weight=0)
        self.grid_rowconfigure((1), weight=1)
        self.grid_rowconfigure((0,2), weight=0)

        """Universal dimensions"""
        self.capx = 300
        self.capy = 300

        """Get available devices"""
        self.num_devices = self.getcapdevice()

        """Get available arduino port"""
        self.num_port = self.find_arduino_port()

        """Main Panel"""
        self.test = ctk.CTkFrame(self,corner_radius=7)
        self.test.grid(row=0, column=0, rowspan=2, padx=(20,10), pady=(20,0), sticky="NWSE")
        self.test.grid_columnconfigure((0,1), weight=1)
        self.test.grid_columnconfigure(2, weight=0)
        self.test.grid_rowconfigure((0,2), weight=0)
        self.test.grid_rowconfigure(1, weight=1)

        self.cammenu_var = ctk.StringVar(value = 'Choose Camera')
        self.cammenu = ctk.CTkOptionMenu(self.test,
                                         values=self.num_devices,
                                         command=self.selOpt, variable=self.cammenu_var)
        self.cammenu.grid(row=0, column=0, padx=(10,0), pady=(20,0), sticky='WE')

        self.portmenu_var = ctk.StringVar(value = 'Choose Port')
        self.portmenu = ctk.CTkOptionMenu(self.test,
                                         values=self.num_port,
                                         command=self.selOpt, variable=self.portmenu_var)
        self.portmenu.grid(row=0, column=1, padx=(10,10), pady=(20,0), sticky='WE')

        self.refresh = ctk.CTkButton(self.test,text='Refresh List', command=self.refreshgetcapdevice)
        self.refresh.grid(row=0, column=2, padx=(0,20), pady=(20,0),stick='E')

        self.vidContain = ctk.CTkLabel(self.test,width=700,height=500, text ='')
        self.vidContain.grid(row=1,column=0,columnspan=3, padx=20, pady=(10,10),sticky='NSWE')
        
        self.resetN = ctk.CTkButton(self,text='Next',command=self.reset,state='disabled')
        self.resetN.grid(row=2,column=2,padx=(0,20),stick='WE')
        self.themeswt_var = ctk.StringVar(value = 'on')
        self.themeswt = ctk.CTkSwitch(self, text = "Dark",
                                      command=self.themeswitch,
                                      variable = self.themeswt_var,
                                      onvalue= 'on',offvalue = 'off')
        self.themeswt.grid(row=2,column = 0, padx=10,pady=10,sticky='SW')
        self.move = ctk.CTkSlider(self.test,from_=0, to=1000,state='disabled',command=self.move1)
        self.move.grid(row=2,column=0,padx=(20,5),columnspan=2,pady=(5,20),sticky='EW')
        self.move.set(0)
        self.moveactive = False
        self.enmove_var = ctk.StringVar(value = 'off')
        self.enmove = ctk.CTkSwitch(self.test, text = "Off",
                                      command=self.enmoveswitch,
                                      variable = self.enmove_var,
                                      onvalue= 'on',offvalue = 'off')
        self.enmove.grid(row=2,column=2,padx=(5,20),pady=(5,20),sticky='E')

        """Left side bar"""
        self.sidebar_frame = ctk.CTkFrame(self,corner_radius=7)
        self.sidebar_frame.grid(row=0, column=2, padx=(0,20), pady=(20,5), sticky="NE")
        
        self.start = ctk.CTkButton(self.sidebar_frame,height=50,text='START', command=self.strt,state='disabled')
        # self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AGOYAO", font=ctk.CTkFont(size=25, weight="bold"),anchor='n')
        self.start.grid(row=0,padx=20,pady=(20,5),sticky='NSWE')
        self.On = False
        self.vidContainCap = ctk.CTkLabel(self.sidebar_frame,height=self.capx,width=self.capy,text='',bg_color='BLACK',anchor='s')
        self.vidContainCap.grid(row=1,padx=20, pady=(5,20),sticky='NSWE')
        # self.temp = ctk.CTkLabel(self.sidebar_frame, text="Temp:", font=ctk.CTkFont(size=25, weight="bold"))
        # self.temp = ctk.CTkLabel(self.sidebar_frame, text="Status:", font=ctk.CTkFont(size=25, weight="bold"))
        self.sidebarstatus_frame = ctk.CTkFrame(self,corner_radius=7)
        self.sidebarstatus_frame.grid(row=1, column=2,padx=(0,20), pady=(5,0), sticky="NSWE")
        self.sidebarstatus_frame.grid_rowconfigure((0), weight=0)
        self.sidebarstatus_frame.grid_rowconfigure((1), weight=1)
        self.sidebarstatus_frame.grid_columnconfigure((0), weight=1)
        self.sidebarstatus_frame.grid_columnconfigure((1), weight=0)

        self.status_frame = ctk.CTkFrame(self.sidebarstatus_frame,corner_radius=0,width=100)
        self.status_frame.grid(row=0, rowspan=2,column=1,sticky="NSE")
        self.status_frame.grid_rowconfigure((0,1,2),weight=1)
        self.tempstatus = ctk.CTkProgressBar(self.status_frame,corner_radius=0,width=30,orientation='vertical')
        self.tempstatus.grid(row=0,column=1,rowspan=3,padx=10,pady=10,sticky="NSE")
        self.tempstatus.set(0)
        self.status = ctk.CTkLabel(self.status_frame,font=ctk.CTkFont(size=13,family='Century Gothic'), text ='High Risk')
        self.status1 = ctk.CTkLabel(self.status_frame,font=ctk.CTkFont(size=13,family='Century Gothic'), text ='Warning')
        self.status2 = ctk.CTkLabel(self.status_frame,font=ctk.CTkFont(size=13,family='Century Gothic'), text ='Okay')
        self.status.grid(row=0,column=1,padx=(10,50), pady=10,sticky="E")
        self.status1.grid(row=1,column=1,padx=(10,50), pady=10,sticky="E")
        self.status2.grid(row=2,column=1,padx=(10,50), pady=10,sticky="E")

        self.templabel= ctk.CTkLabel(self.sidebarstatus_frame, text ='TEMP',font=ctk.CTkFont(size=15, weight="normal"))      
        self.templabel.grid(row=0,column=0, pady=10,sticky="N")
        self.tempcontain = ctk.CTkFrame(self.sidebarstatus_frame,height=200)
        self.tempcontain.grid_rowconfigure(0,weight=1)
        self.tempcontain.grid_columnconfigure(0,weight=1)
        self.tempcontain.grid(row=1,column=0, padx=10,pady=(0,10),sticky='WE')
        self.tempcontain.grid_propagate(0)
        self.temp = ctk.CTkLabel(self.tempcontain, text ='',font=ctk.CTkFont(size=60, weight="bold"))      
        self.temp.grid(pady=10,sticky="NSWE")

        self.cap = cv2.VideoCapture()

    def find_arduino_port(self):
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # Modify this condition based on your Arduino's description
        ]

        if not arduino_ports:
            print("No Arduino found.")
        else:
            print("Multiple Arduinos found. Using the first one.")
        
        return arduino_ports

    def strt(self):
        if not self.On:
            self.start.configure(text='STOP',fg_color='red')
            self.On = True
        else:
            self.start.configure(text='START',fg_color='DodgerBlue3')
            self.reset()
            self.resetN.configure(state='disabled')
            self.On = False

    def alert(self,x):
        pygame.mixer.init()
        alert = pygame.mixer.Sound('alert.mp3')
        valid = pygame.mixer.Sound('valid.mp3')
        if x == True:
            alert.play()
        else:
            valid.play()

    def setStatus(self,x):
        self.tempa = x
        tcolor = 'white'

        if 0 <= self.tempa < 37.3:
            self.tempstatus.set(0.14)
            self.tempstatus.configure(progress_color='green2')
            print('Status: Okay')
            tcolor = 'green2'
            self.coloring = (0,238,0)
        elif 37.4 < self.tempa < 38.4:
            self.tempstatus.set(0.5)
            self.tempstatus.configure(progress_color='orange')
            print('Status: Warning')
            tcolor = 'Orange'
            self.coloring = (0,128,255)
        elif 38.5 < self.tempa < 40:
            self.tempstatus.set(0.87)
            self.tempstatus.configure(progress_color='red')
            print('Status: Risk')
            tcolor = 'Red'
            self.coloring = (0,0,255)
        elif self.tempa > 40:
            self.tempstatus.set(1)
            self.tempstatus.configure(progress_color='red')
            tcolor = 'Red'
            self.coloring = (0,0,255)
        if self.tempa > 38.3:
            x = True
            self.alert(x)
        else:
            x = False
            self.alert(x)
        
        unit = (str(round(self.tempa,1)) + "°C")
        self.temp.configure(text=unit,text_color=tcolor)

    def getcapdevice(self):
        devices = FilterGraph().get_input_devices()

        self.capdevices = {}
        self.capdevices_name = []

        for i in range(len(devices)):
            self.capdevices[devices[i]] = i
            self.capdevices_name.append(devices[i])

        self.capdevices['Video'] = 'sample.mp4'
        self.capdevices_name.append('Video')
        print(self.capdevices_name)

        return self.capdevices_name

    def refreshgetcapdevice(self):
        self.start.configure(state='disabled')
        if temp:
            temp.clear()
            print('Device Released')
            self.cap.release()
            self.stop1()
        else:
            pass

        temp_var = ctk.StringVar(value = 'Choose Camera')
        self.cammenu.configure(variable=temp_var)
        self.num_devices = self.getcapdevice()
        self.cammenu.configure(values=self.num_devices)
        print('Devices:',self.capdevices)
        self.vidContain.configure(text='',width=700,height=500)
        self.start.configure(text='START',fg_color='DodgerBlue3',state='disabled')
        self.On = False
        self.flagsize = True

    def themeswitch(self):
        if self.themeswt_var.get() == 'on':
            ctk.set_appearance_mode("dark")
            self.themeswt.configure(text = 'Dark')
        else:
            ctk.set_appearance_mode("light")
            self.themeswt.configure(text = 'Light')

    def enmoveswitch(self):
        if self.enmove_var.get() == 'off':
            self.move.configure(state="disabled")
            self.moveactive = False
            self.enmove.configure(text = 'Off')
        else:
            self.move.configure(state='normal')
            self.moveactive = True
            self.enmove.configure(text = 'On')

    def selOpt(self,x):
        temp.append(x)
        self.num_devices.remove(x)

        if len(temp) > 1:
            self.cap.release()
            self.capdevices_name.append(temp.pop(0))
            self.stop1()
        else:
            pass

        self.cammenu.configure(values=self.num_devices)

        print('Device In-Use:',temp[0])
        print('Capture Devices Remaining:',self.num_devices)

        self.capVid(self.capdevices.get(temp[0]))

    def reset(self):
        photo = Image.new("RGBA",(self.capx, self.capy),(0,0,0))
        imgtk = ImageTk.PhotoImage(image=photo)
        self.vidContainCap.configure(image=imgtk)
        self.temp.configure(text='')
        self.tempstatus.set(-1)
        # self.tempa = 0
        self.flag=True
        self.gettemp=True
        self.vidContain.configure(text='',width=700,height=500)
        self.resetN.configure(state='disabled') 
        self.random_temp = 0

    def randomTemp(self):
        temp = random.gauss(36.7,2)
        return temp

    def faceDec(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=10,minSize=(30, 30))
        r,g,b = 255,255,0
        global arduino
        
        try:
            if len(faces) > 0:
                global dot_position
                (x, y, w, h) = faces[-1]  # Use the last detected face
                forehead_x = x + w // 2
                forehead_y = y + h // 5
                dot_position = (forehead_x, forehead_y)  # Update dot position
                
            # Draw the stable face box on the frame
            for (x, y, w, h) in faces:
                """Capture the face image within the rectangled area"""
                if self.flag == True:
                    self.temp_float = 0
                    if len(self.num_port) > 0:
                        temperature = arduino.readline().decode().strip()
                        self.temp_float = float(temperature)
                        # print("Received temperature:", self.temp_float)
                        self.setStatus(self.temp_float)
                    else:
                        self.temp_float = self.randomTemp()
                        self.setStatus(self.temp_float)
                        self.flag = False
                        self.gettemp = True

                    faceDisp = frame[y:y+h, x:x+w]
                    faceDisp = cv2.resize(faceDisp, (self.vidContainCap.winfo_width(), self.vidContainCap.winfo_height()))
                    rgb_capimg = cv2.cvtColor(faceDisp, cv2.COLOR_BGR2RGB)
                    capimg = Image.fromarray(rgb_capimg)
                    capimgtk = ImageTk.PhotoImage(image=capimg)
                    self.vidContainCap.imgtk=capimgtk
                    self.vidContainCap.configure(image=capimgtk)
                    # face = frame[y-100:y+h+150, x-50:x+w+50]
                    # filename = os.path.join(self.output_dir, f'{round(self.random_temp,1)}_face.jpg')
                    # cv2.imwrite(filename, face)
                    self.resetN.configure(state='normal')
                    # else:
                    #     continue
                                    
                x1,y1 = dot_position
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, str(round(self.temp_float,1)),
                            (x+3,y+18),
                            font, 
                            0.5, self.coloring, 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x-1,y-1),(x+w,y+h), (r,g,b),2)
            
            # if dot_position is not None:
            #     x1,y1 = dot_position  
            #     cv2.line(frame, (x1+2000,y1),(x1-2000,y1), (0, 0, 0), 1)
            #     cv2.line(frame, (x1,y1+2000),(x1,y1-2000), (0, 0, 0), 1)
            #     cv2.circle(frame, dot_position, 5, (255, 255, 255), -1)
                # arduino.write(str(x1).encode() + b'\n')
                # arduino.write(str(y1).encode() + b'\n')
        except Exception as e: 
            print(str(e))

    def ardPos(self,x1,y1,frame):
        height, width, _ = frame.shape
        ardx = int((x1 / width) * 180)
        ardy = int((y1 / height) * 180)

        return ardx,ardy

    def vidResize(self,vid):
        owidth = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        oheight = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        aspect_ratio = float(owidth) / float(oheight)
        newheight = self.vidContain.winfo_height()
        newwidth = int(newheight*aspect_ratio)
    
        return newwidth, newheight
    
    def move1(self,x):
        global valo
        valo = int(x)

    def roisize(self):
        r = 0
        r1 = valo
        w = 300 #width of the roi
        return r,r1,w

    def roi(self,frame,height):
        ry,rx,w  = self.roisize()
        cropped = frame[ry:ry+height, rx:rx+w]
        cv2.rectangle(cropped, (ry,ry),(ry+w,height), (0,255,0),2)
        if self.On:
            self.faceDec(cropped)

    def capVid(self,x):
        self.cap = cv2.VideoCapture(x)

        # self.gettemp = False
        self.flag = True
        self.flagbtn = False
        self.output_dir = 'detected_faces'
        self.flagsize = True
        
        """Option to choose the display method"""
        self.show_video()#most stable

    def show_video(self):
        ret, frame = self.cap.read()
        if ret:
            if not self.flagbtn:
                self.start.configure(state='normal')
                self.flagbtn = True
                
            self.vidContain.configure(text='')
            # set frame image size
            w,h = self.vidResize(self.cap)
            frame = cv2.resize(frame, (w,h))
            frame = cv2.flip(frame,1)
            if self.On and not self.moveactive:
                self.faceDec(frame)

            if self.moveactive:
                self.roi(frame,h)
                limit = w-200
                self.move.configure(to=limit)

            """Convert the frame from BGR to RGB format"""
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            """Create an ImageTk object from the RGB frame"""
            img_tk = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

            self.vidContain.imgtk=img_tk
            self.vidContain.configure(image=img_tk)

            self.after(1,self.show_video)          
        else:
            self.cap.release()
            photo = Image.new("RGBA",(700,500),(0,0,0,0))
            imgtk = ImageTk.PhotoImage(image=photo)

            self.vidContain.configure(text='Device Unavailable',image = imgtk)
        
main = Main()
main.mainloop()