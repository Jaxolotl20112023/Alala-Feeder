import RPi.GPIO as GPIO
from hx711 import HX711                # import the class HX711
from mfrc522 import SimpleMFRC522
from multiprocessing import Process, Queue
from datetime import datetime
import pandas as pd
import numpy as np
import requests
from time import sleep, perf_counter
from gpiozero import Servo
from rclone_python import rclone
import os
import threading
from picamera2 import Picamera2
from picamera2.encoders import Quality, H264Encoder
from picamera2.outputs import CircularOutput
from Constants import API_BASE_URL
from Utility import date_generator,hms_generator

GPIO.setmode(GPIO.BCM)
MIN_BIRD_WEIGHT = 70 # change to the actual miniumum weight of the alala bird
WEIGHT_CHANGE_ERR = 30 # the amount of change in weight that the program deems valid
 # this is temporary. need to replace it to the IPv4 address that is associated with the laptop using to run this

class Camera() :
    
    def __init__(self) :
        self.picam = Picamera2()
        self.encoder = H264Encoder() 
        self.buffer_output = CircularOutput(buffersize=150)
        self.storer = storage("Video","videoData",{
            "id": 0,
            "date": None, 
            "iteration": 0
        })

        self.num_recording = 0
        self.num_pictures = 0
        self.name = "\0"
        
    def start_preview(self):
        self.picam.start_preview()
    
    def end_preview(self):
        self.picam.stop_preview()
        self.picam.close()

    def simple_record(self,duration) :
        date = date_generator() 
        self.num_recording+=1 
        print("start recording") 
        self.name = f"./videos/{date}-{self.num_recording}.mp4" 
        self.storer.append("date",f"{date} {hms_generator()}")
        self.storer.append("iteration", self.num_recording)
        self.picam.start_and_record_video(self.name, duration=duration, quality=Quality.MEDIUM)
    
    def save_capture_data(self,override_path=None) :
        if (override_path) :
            self.storer.path = override_path
            
        self.storer.save()
        self.storer.fileSave() 

    def capture_pic(self) :
        self.num_pictures+=1 
        name = f"{date_generator}-{self.num_recording}.png"
        self.picam.start() 
        sleep(2)
        self.picam.capture_file(f"./imgs/{name}")

        self.storer.append("date", f"{date_generator()} {hms_generator()}")
        self.storer.append("iteration", self.num_pictures)

    # def buffer_recording(self,duration): 
    #     self.num_recording+=1 
    #     self.name = f"./videos/{date_generator()}-{self.num_recording}.mp4" 
    #     self.picam.start_recording(self.encoder,self.buffer_output)
    #     sleep(duration) 
    #     self.buffer_output.fileoutput = self.name 
    #     self.buffer_output.stop()
    #     self.picam.stop_recording()

class storage() :
    
    def __init__(self,name,path,data_outline:dict) :
        self.data_outline = data_outline
        self.currData = self.data_outline

        self.name = name
        self.path = path
        self.dfData:list[dict] = [{}] 
        self.file_name = f"./{self.path}/{self.name}_{date_generator()}.json"
    
    def append(self,attr,data) :
        self.currData[attr] = data
        print(f"appended {data} at {attr}")
        print(self.currData) 
        
    def save(self) :
        self.dfData.append(self.currData)
        self.currData = self.data_outline 
        
    def fileSave(self) :
        print(f"{self.name}_{date_generator()}.json")
        pd.DataFrame(self.dfData).to_json(self.file_name, orient="records")
        self.file_name = f"./{self.path}/{self.name}_{date_generator()}.json"
        
    def getData(self) :
        return self.dfData
    
    def getFilePath(self) :
        return self.file_name
    
class load_cell() : 

    def __init__(self,dout,sck,ratio,file_name) : 
        self.dout = dout
        self.sck = sck
        self.ratio = ratio
        self.hx = HX711(dout_pin=self.dout, pd_sck_pin=self.sck) 
        self.hx.zero() 
        self.hx.set_scale_ratio(ratio) 

    def activate(self) : 

        hx = self.hx
        
        prevWeight = 0
        totalWeight = 0
        weight = 0
        
        numInvalidWeights = 0 
        i = 0
        maxReadings = 4

        birdStorer.append("hms", hms_generator())
        
        while i < maxReadings :
            prevWeight = weight
            weight = hx.get_weight_mean()
            
            if weight <= MIN_BIRD_WEIGHT or (weight > MIN_BIRD_WEIGHT and weight-prevWeight > WEIGHT_CHANGE_ERR and prevWeight != 0):
                print("invalid weight: ", weight)
                numInvalidWeights+=1
                
                if numInvalidWeights > 10 :
                    print("TOO MANY INVALID WEIGHTS... SKIPPING...")
                    return
                continue
            
            numInvalidWeights = 0 
            totalWeight += weight
            
            birdStorer.append("weights",weight) 
            
            print(weight,'grams')
            i+=1
                
        averageWeight = totalWeight/maxReadings
        
        print("Average Weight: ", averageWeight)
        birdStorer.append("avgWeight", averageWeight) 

    def deactivate(self) : 
        GPIO.output(self.dout,GPIO.LOW)
        GPIO.output(self.sck, GPIO.LOW) 
        GPIO.cleanup()
        
class rfid() : 

    def __init__(self) : 
        GPIO.setmode(GPIO.BCM)                
        self.reader = SimpleMFRC522()
        self.id = None

    def getIDMain (self):
        q = Queue()
        p = Process(target=self.readCard, args=(q,))
        p.start()
        
        p.join(timeout=5)

        if p.is_alive() :
            p.terminate()
            cam1.storer.append("id", "UNIDENTIFIED")
            print("NO IDS DETECTED")
                
            return False 
        else :
            self.id = q.get()
            birdStorer.append("id", self.id)
            cam1.storer.append("id", self.id)
            p.terminate()
            
            return True

    def readCard (self,q): 

        reader = self.reader
        print('Place Card on Reader')
        
        try :
            birdId,text = reader.read()
        except:
            print("id reading error")
            self.readCard()
        
        q.put(birdId)
            

class servo() : 

    def __init__(self, pin) :
        self.pin = pin 
        self.servo = Servo(self.pin);
        
        self.servo.detach()
        self.servo.min()
        sleep(3)
        
    def move_servos(self) :
        global start_time
        servoc = self.servo

        start_time = datetime.now().minute
        servo.detach()
        
        for i in range(0,5) :
            print("i: ", i)
            
            print("max")
            servo.max()
            sleep(5)
            
            print("min")
            servo.min()
            sleep(5)
        
        servo.detach()
    
    def reset_servo(self) :
        self.servo.value = None

# Motion sensor set up
sensor = 27
GPIO.setup(27, GPIO.IN)
# Servo set up
servo1 = servo(18)

#Motion Detector
motionDetector = GPIO.input(sensor)

# Camera set up
cam1 = Camera()

# RFID set up 
rfid1 = rfid() 

# Load cell set up 
ratio = 111 # kinda correct ratio is -95.4
bird_cell = load_cell(4,17,ratio,"birdData")
# feeder_cell = load_cell(0,0,ratio,"ALALA_FEEDER_DATA")

birdStorer = storage("BirdData","birdData", {
    "hms": None, 
    "id": 0, 
    "weights": [], 
    "avgWeight": 0
})

feederStorer = storage("FeederData", "feederData", {
    "id": 0, 
    "weights": [], 
    "avgWeight": 0
})

#foodStorer = storage("FoodData", "foodData") 
duration = 5
recording_thread = threading.Thread(target=cam1.simple_record, args=(duration,))    
static_img_thread = threading.Thread(target=cam1.capture_pic)

start_time = perf_counter() 

print("start_time: ", start_time)

index = 0

print("Time: ",datetime.strftime(datetime.now(),"%H"))

# set the servo to starting position
# servo.detach()
# servo.min()
# time.sleep(3)
    
def MotionDetectionMain() :
    global static_img_thread
    global recording_thread
    global start_time

    bird_present = False

    while True:
        
        sleep(0.2)
        
        if (perf_counter() - start_time) >= 10: #(perf_counter() - start_time)/360 > 19 :
            try : 
                start_time = perf_counter()
                print("SEND DATA TO THE API")
                r = requests.post(f'{API_BASE_URL}/pushBirdWeight', json=birdStorer.dfData)
                
                if r.status_code == 201 or r.status_code == 200 :
                    os.remove(birdStorer.getFilePath())
            except :
                print("failed to connect") 

        if GPIO.input(27) or bird_present:
             
            print("Motion Detected")
            recording_thread.start()
             
            if rfid1.getIDMain() :
                bird_present = True

                bird_cell.activate()
                birdStorer.save()
                birdStorer.fileSave()
            else : 
                bird_present = False 
                # get weight of food, etc... 
             
            recording_thread.join()
            cam1.save_capture_data()
            print("join thread") 
            recording_thread = threading.Thread(target=cam1.simple_record, args=(duration,))    

        else:
            print("No motion")
    
if __name__ == "__main__":
    MotionDetectionMain()
