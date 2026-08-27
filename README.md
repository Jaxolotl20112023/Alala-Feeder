# Alala Feeder Code ** STILL IN PROTOTYPE STAGE **

## Overview
This repo contains the code used to operate the feeder stations. 
Four folders are mainly used to store data collected from the feeder stations. 
1. "ClassMotionDetection.py" is the main script of our feeder and runs all of the logic, sensors, and sending of data.
2. "Constants.py" contains some constant values that the code uses.
3. "Utility.py" contains some commonly used functions that do not depend on inputs from the data/the feeder itself.
4. "feederProps.json" stores the data about the feeder station itself (id, location, etc). 
5. "startUp.py" is the script that assigns id and some other data about the feeder station, which is then stored in the "feederProps.json"

## Electronics / Sensors Used
The feeder uses and implements: 
1. Load sensor (weight) ✅
2. Motion detector ✅
3. RFID scanner ✅
4. PiCamera ✅
5. Humidity & Temperature ❌
6. Battery Percentage ❌
   
The ones with the checkmarks are the electronics that have been implemented and are handled within the code. The ones with the x-marks are the ones that have yet to be implemented.
The data from these is then used to fill in the data within the folders.  

