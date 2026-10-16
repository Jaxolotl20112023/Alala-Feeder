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
from gpiozero import Motor, RotaryEncoder
from rclone_python import rclone
import os
import threading
from picamera2 import Picamera2
from picamera2.encoders import Quality, H264Encoder
from picamera2.outputs import CircularOutput
from Constants import API_BASE_URL
from Utility import date_generator,hms_generator,get_recent_file
from startUp import start_up
from Constants import Status
import dht11
# from Constants import ALLOWED_IDS

init_data = start_up()


GPIO.setmode(GPIO.BCM)
MIN_BIRD_WEIGHT = 70 # change to the actual miniumum weight of the alala bird
WEIGHT_CHANGE_ERR = 30 # the amount of change in weight that the program deems valid
 # this is temporary. need to replace it to the IPv4 address that is associated with the laptop using to run this
INIT_FOOD = 500  # in grams 
FOOD_DISPENSED =  200
days_operating = init_data["days_operating"]
ALLOWED_IDS = [223041367485,288073526777]

def get_dht_reading(s):
    result = s.read() 
    
    while not result.is_valid():
        result = s.read()
        sleep(0.05)
        
    return result

class Camera() :
    
    def __init__(self, pin=0) :
        self.picam = Picamera2()
        self.pin = pin 
        # self.encoder = H264Encoder() 
        # self.buffer_output = CircularOutput(buffersize=150)
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
        self.storer.append("date",f"{date_generator()} {hms_generator()}")
        self.storer.append("iteration", self.num_recording)
        self.picam.start_and_record_video(self.name, duration=duration, quality=Quality.MEDIUM)
    
    def save_capture_data(self) :
            
        #self.storer.save()
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

        self.currData = self.data_outline.copy()

        self.name = name
        self.path = f"./{path}"
        
        existing_data = get_recent_file(self.path)
        self.dfData:list[dict] = [] if not existing_data else existing_data
        self.file_name = f"{self.path}/{self.name}_{date_generator()}.json"
    
    def append(self,attr,data) :
        
        if type(self.currData[attr]) == list:
            print(f"appending {attr} to list") 
            self.currData[attr].append(data)
            return
        
        self.currData[attr] = data
#         print(f"\nappended {data} at {attr}")
#         print(f"data outline: ",self.data_outline)
#         print("dfData when currData appends ",self.dfData)
        
        # print(self.currData) 
        
    # def save(self) :
    #     self.dfData.append(self.currData)
    #     self.currData = self.data_outline 
        
    def fileSave(self) :
        # print("\ndfData right before appending: ",self.dfData)
        self.dfData.append(self.currData)
        # print("dfData right after appending: ",self.dfData)
        self.currData = self.data_outline.copy()
 
        print(f"{self.name}_{date_generator()}.json")
        pd.DataFrame(self.dfData).to_json(self.file_name, orient="records")
        self.file_name = f"{self.path}/{self.name}_{date_generator()}.json"
        
    def getData(self) :
        return self.dfData
    
    def getFilePath(self) :
        return self.file_name
    
    def isEmpty(self,index=None):
        
        if not index:
            return currData == []
        
        return currData[index] == None or currData[index] == [] or currData[index] == 0 
    
class load_cell() : 

    def __init__(self,dout,sck,ratio,load_name) : 
        self.dout = dout
        self.sck = sck
        self.ratio = ratio
        self.hx = HX711(dout_pin=self.dout, pd_sck_pin=self.sck) 
        self.hx.zero() 
        self.hx.set_scale_ratio(ratio) 
        self.load_name = load_name 

    def activate(self, storer) : 

        hx = self.hx
        
        prevWeight = 0
        totalWeight = 0
        weight = 0
        weights = [] 
        
        numInvalidWeights = 0 
        i = 0
        maxReadings = 4

        storer.append("date", f"{date_generator()} {hms_generator()}")
        
        while i < maxReadings :
            prevWeight = weight
            weight = hx.get_weight_mean()
            
            if weight <= MIN_BIRD_WEIGHT or (weight > MIN_BIRD_WEIGHT and weight-prevWeight > WEIGHT_CHANGE_ERR and prevWeight != 0):
                print("invalid weight: ", weight)
                numInvalidWeights+=1
                
                if numInvalidWeights > 10 :
                    print("TOO MANY INVALID WEIGHTS... SKIPPING...")
                    storer.append("weights", None)
                    storer.append("avgWeight", None)

                    deviceStorer.append(self.load_name, Status.INVALID_READINGS)
                    
                    return
                continue
            
            numInvalidWeights = 0 
            totalWeight += weight
            
            weights.append(weight)
            storer.append("weights",weight) 
            
            print(weight,'grams')
            i+=1
                
        averageWeight = totalWeight/maxReadings
        
        print("Average Weight: ", averageWeight)
        storer.append("avgWeight", averageWeight) 
        stationStorer.append(self.load_name, Status.VALID_READINGS)

    def deactivate(self) : 
        GPIO.output(self.dout,GPIO.LOW)
        GPIO.output(self.sck, GPIO.LOW) 
        GPIO.cleanup()
        
class rfid() : 

    def __init__(self, name, pin=0) : 
        # GPIO.setmode(GPIO.BCM)                
        self.reader = SimpleMFRC522()
        self.id = None
        self.name = name
        self.pin = pin 

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
            print(f"id: {self.id}")

            if self.id not in ALLOWED_IDS:
                print(self.id)
                print("BIRD NOT ASSOCIATED WITH THIS FEEDER")
                return False 
            
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

def query(endpoint, data, callback): 
    try : 
        print("SEND DATA TO THE API")
        r = requests.post(f'{API_BASE_URL}/{endpoint}', json=data)
        
        callback(r)

    except :
        print("failed to connect") 

def faultDetection(devices, storer:storage) :

    GPIO.setmode(GPIO.BCM)

    for key in devices.keys(): 

        for i in range(0,len(key)):
            pin = key[i]

            off_callback = lambda channel: storer.append(key,Status.NO_POWER) 

            GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

            GPIO.add_event_callback(pin,GPIO.FALLING,callback=off_callback)

            sleep(0.25)

            GPIO.cleanup()

    return storer


# Motion sensor set up
sensor = 27
GPIO.setup(27, GPIO.IN)
# Servo set up
# servo1 = servo(18)

#Motion Detector
motionDetector = GPIO.input(sensor)

# Camera set up
cam1 = Camera() # specify the GPIO pin

# RFID set up 
rfid1 = rfid(name="rfid1") # specify the GPIO pin 

# Load cell set up 
ratio = 111 # kinda correct ratio is -95.4
birdCell = load_cell(4,17,ratio,"birdLoadCell")

dhtSens = dht11.DHT11(pin=21)
# feeder_cell = load_cell(0,0,ratio,"ALALA_FEEDER_DATA")

birdStorer = storage("BirdData","birdData", {
    "date": None, 
    "id": 0, 
    "weights": [], 
    "avgWeight": 0
})

feederStorer = storage("FeederData", "foodData", {
    "id": 0, 
    "weights": [], 
    "avgWeight": 0
})

devicePin = {
    birdCell.load_name: [birdCell.dout, birdCell.sck], 
    rfid1.name: [rfid1.pin],
    cam1.name: [cam1.pin]
}

deviceStorer = storage("DeviceData", "deviceData", {
    birdCell.load_name: Status.VALID_READINGS, 
    rfid1.name: Status.HAS_POWER,
    cam1.name: Status.HAS_POWER
})

stationStorer = storage("StationData", "stationData", {
    "date": None, 
    # "battery":
    "temperature": 0,
    "humidity": 0,
    "foodLeft": 0, 
    "fault": False
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
    global days_operating

    bird_present = False

    while True:
        
        sleep(0.2)
        
        if (perf_counter() - start_time)/3600 > 19 :
            start_time = perf_counter()
            query("pushBirdWeight", birdStorer.dfData, lambda r: os.remove(birdStorer.getFilePath()) if r.status_code == 201 or r.status_code == 200 else print("could not send bird weight"))
            query("pushStationData", stationStorer.dfData, lambda r: os.remove(stationStorer.getFilePath()) if r.status_code == 201 or r.status_code == 200 else print("could not report pi health"))
            days_operating+=1

        if (perf_counter() - start_time)/60 >= 2: # divide parenthesis by 60
            
            start_time = perf_counter()
            result = get_dht_reading(dhtSens) 
            deviceStorer = faultDetection(devicePin,deviceStorer)

            stationStorer.append("date", f"{date_generator()} {hms_generator()}")
            stationStorer.append("foodLeft", INIT_FOOD-(FOOD_DISPENSED*days_operating))
            stationStorer.append("temperature (F)", (result.temperature*1.8) + 32)
            stationStorer.append("humidity", result.humidity)
            stationStorer.fileSave()
            deviceStorer.fileSave()
            
        if GPIO.input(27) or bird_present:
             
            print("Motion Detected")
            recording_thread.start()
             
            bird_present = rfid1.getIDMain()
            
            if bird_present: 
                birdCell.activate(birdStorer)
            #else:
                print("file save weights")
                birdStorer.fileSave()
               
            recording_thread.join()
            cam1.save_capture_data()
            print("join thread") 
            recording_thread = threading.Thread(target=cam1.simple_record, args=(duration,))    

        else:
            print("No motion")
    
if __name__ == "__main__":
    MotionDetectionMain()
