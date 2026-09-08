# Alala Feeder Code ** STILL IN PROTOTYPE STAGE **

## Overview
This repo contains the code used to operate the feeder stations. 
Seven folders are mainly used to store data collected from the feeder stations. 
1. "ClassMotionDetection.py" is the main script of our feeder and runs all of the logic, sensors, and sending of data.
2. "Constants.py" contains some constant values that the code uses.
3. "Utility.py" contains some commonly used functions that do not depend on inputs from the data/the feeder itself.
4. "feederProps.json" stores the data about the feeder station itself (id, location, etc). 
5. "startUp.py" is the script that assigns an ID and some other data about the feeder station, which is then stored in "feederProps.json"

## Electronics / Sensors Used
The feeder uses and implements: 
1. Load sensor (weight) ✅
2. Motion detector ✅
3. RFID scanner ✅
4. PiCamera ✅
5. Humidity & Temperature ❌
6. Battery Percentage ❌
   
The ones with the checkmarks are the electronics that have been implemented and are handled within the code. The ones with the X marks are the ones that have yet to be implemented.
The data from these is then used to fill in the data within the folders.  

## startUp.py
This file contains a function that will be run whenever the ClassMotionDetection.py file runs. This fetches the most recent data from the stationData, which contains the feeder's id, time it has been operating, and other data that has yet been discussed/added. This will be returned as a dictionary and used in the ClassMotionDetection.py file to fill in variables.  
This is primarily used as a way for the program to "pick up where it left off" if the Raspberry Pi does ever unexpectedly power-off or shutdown. Preventing inaccurate data from being sent to the app/researchers. 

## ClassMotionDetection.py
This file contains the main control of each sensor, storing their data, and the overall loop of the whole system. This will eventually be spread out into seperate files, but are stuck into one for easier navigation when testing and constantly tweaking the code.  
It also contains the code that handles the connecting to and requesting to the API that will handle the data from the Pi. 

## Utility.py
This file contains general functions that do not need any sensor input. It contains functions like date generators, file openers, and file writing. This is to decrease the amount of clutter in the ClassMotionDetection.py file. 

## Constants.py
This file contains any variables, enums, or classes that store values that WILL not change. These set values are like states for each system, base_url for the API, etc. 

## birdData, foodData, imgsData, videoData 
These folders contain JSON files that store the data being captured through the sensors. The imgsData and videoData store metadata about each video/img, so it can be properly processed and used by the API. 

## imgs, videos
These folders contain the images and videos from the day. These will be cleared out after it has been sent over to the API / back to the researchers. 

## allowedIDs.json, feederProps.json 
These two JSON files each have their own purpose in storing data. The allowedIDs.json is a file that stores the specific IDs that the feeder allows access to the food. While the feederProps.json file stores the general information about the feeder (ID, days in operation, etc). 
