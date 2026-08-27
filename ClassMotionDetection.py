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
from picamera2.encoders import Quality
from Constants import API_BASE_URL


GPIO.setmode(GPIO.BCM)
MIN_BIRD_WEIGHT = 70 # change to the actual miniumum weight of the alala bird
WEIGHT_CHANGE_ERR = 30 # the amount of change in weight that the program deems valid
 # this is temporary. need to replace it to the IPv4 address that is associated with the laptop using to run this

class Camera() :
    
    def __init__(self) :
        self.picam = Picamera2()
        self.video = None
        
        self.record_num = 0
        self.capture_start = False
        self.start = None
        self.capture_end = False
        self.name = "\0"
        self.is_recording = False
        
    def start_preview(self):
        self.picam.start_preview()
    
    def end_preview(self):
        self.picam.stop_preview()
        self.picam.close()

    def simple_record(self,duration) :
        print("start recording") 
        self.record_num += 1
        self.name = f"./videos/{self.record_num}.mp4" 
        self.picam.start_and_record_video(self.name, duration=duration, quality=Quality.MEDIUM)

class storage() :
    
    def __init__(self,name,path) :
        self.name = name
        self.path = path
        self.dfData = []
        self.currData = {
            "id" : 0,
            "weights" : [],
            "avgWeight" : 0.0
        }
        self.file_name = f"./{self.path}/{self.name}_{datetime.now().month}-{datetime.now().day}-{datetime.now().year}.json"
    
    def append(self,attr,data) :
        self.currData[attr] = data
        print(f"appended {data} at {attr}")
        print(self.currData) 
        
    def save(self) :
        self.dfData.append(self.currData)
        self.currData = {
            "id" : 0,
            "weights" : [],
            "avgWeight" : 0.0
        }
        
    def fileSave(self) :
        print(f"{self.name}_{datetime.now().month}-{datetime.now().day}-{datetime.now().year}.json")
        pd.DataFrame(self.dfData).to_json(self.file_name, orient="records")
        self.file_name = f"./{self.path}/{self.name}_{datetime.now().month}-{datetime.now().day}-{datetime.now().year}.json"
        
    def getData(self) :
        return self.dfData
    
    def getFilePath(self) :
        return self.file_name
    
class load_cell() : 

    def __init__(self,dout,sck,ratio,file_name) : 
        self.dout = dout
        self.sck = sck
        self.ratio = ratio
        self.file_name = file_name
        self.hx = HX711(dout_pin=self.dout, pd_sck_pin=self.sck) 
        self.hx.zero() 
        self.hx.set_scale_ratio(ratio) 

    def activate(self) : 

        hx = self.hx
        file_name = self.file_name
        
        prevWeight = 0
        totalWeight = 0
        weight = 0
        
        numInvalidWeights = 0 
        i = 0
        maxReadings = 4
        
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
            
            birdStorer.currData["weights"].append(weight) 
            
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
            print("NO IDS DETECTED")
                
            return False 
        else :
            self.id = q.get()
            birdStorer.append("id", self.id)
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
GPIO.setup(sensor, GPIO.IN)
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
bird_cell = load_cell(4,17,ratio,"ALALA_BIRD_DATA")
# feeder_cell = load_cell(0,0,ratio,"ALALA_FEEDER_DATA")

birdStorer = storage("BirdData","birdData")
feederStorer = storage("FeederData", "feederData")
foodStorer = storage("FoodData", "foodData") 
duration = 5
recording_thread = threading.Thread(target=cam1.simple_record, args=(duration,))    

start_time = perf_counter() 

print("start_time: ", start_time)

index = 0

print("Time: ",datetime.strftime(datetime.now(),"%H"))

# set the servo to starting position
# servo.detach()
# servo.min()
# time.sleep(3)
    
def MotionDetectionMain() :
    global recording_thread
    global start_time
    
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

        if motionDetector:
             
            print("Motion Detected")
             
            recording_thread.start()
             
            if rfid1.getIDMain() :
                bird_cell.activate()
                birdStorer.save()
                birdStorer.fileSave()
             
            recording_thread.join()
            print("join thread") 
            recording_thread = threading.Thread(target=cam1.simple_record, args=(duration,))    

        else:
            print("No motion")
    
if __name__ == "__main__":
    MotionDetectionMain()
