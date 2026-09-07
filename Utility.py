from datetime import datetime 
from pathlib import Path
from enum import Enum

import pandas as pd

def date_generator() :
    return datetime.now().strftime("%m-%d-%Y")

def hms_generator() : 
    return datetime.now().strftime("%H-%M-%S")

def get_file(path, file_type="*.json") :

    folder_path = Path(path)

    files = folder_path.glob(file_type)

    filtered =  max(files, key=lambda x: x.stat().st_mtime)

    try :
        convert = pd.read_csv(filtered).to_dict() if "csv" in file_type else pd.read_json(filtered).to_dict() if "json" in file_type else None
    except :
        return None 
    
    return convert

def save_file(path, data, file_type="*.json") : 
    if "json" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")
    elif "csv" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")

class Status(Enum) :
    BAD_CONNECTION = "Bad Connection"
    GOOD_CONNECTION = "Good Connection"

    NO_POWER = "No Power"
    HAS_POWER = "Has Power"

    INVALID_READINGS = "Invalid Readings"
    VALID_READINGS = "Valid Readings"





