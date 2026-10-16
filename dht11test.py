import dht11
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
s = dht11.DHT11(pin=21)

while True:
    
    result = s.read()
    
    if result.is_valid():
        print("temperature: ",(result.temperature*1.8) + 32)
        print("humidity: ",result.humidity)
    
    sleep(0.2)