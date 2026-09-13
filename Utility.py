from datetime import datetime 
from pathlib import Path
import os 
import json
# import pandas as pd

def date_generator() :
    return datetime.now().strftime("%m-%d-%Y")

def hms_generator() : 
    return datetime.now().strftime("%H-%M-%S")

def get_recent_file(path, file_type="*.json") :

    most_recent_file = None
    most_recent_time = 0 

    for file in os.scandir(path): 
        time = file.stat().st_mtime 
        if (time > most_recent_time): 
            most_recent_time = time 
            most_recent_file = file 

    filtered = most_recent_file

             
    try :
        with open(f"{path}/{filtered.name}") as f:
            return json.load(f)
    except :
        return "invalid" 
    
    
# def get_json(path) :
#     return pd.read_json(path,lines="true").to_dict()

def save_file(path, data, file_type="*.json") : 
    if "json" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")
    elif "csv" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")






