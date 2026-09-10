from datetime import datetime 
from pathlib import Path
import json
# import pandas as pd

def date_generator() :
    return datetime.now().strftime("%m-%d-%Y")

def hms_generator() : 
    return datetime.now().strftime("%H-%M-%S")

def get_recent_file(path, file_type="*.json",date=None) :

    folder_path = Path(path)

    files = folder_path.glob(file_type)
    
    print("file")
    for file in files:
        print(file.stat().st_mtime)

    if not date: 
        filtered = max(files, key=lambda x: x.stat().st_mtime) 
    else :
        for file in files:
            if datetime.fromtimestamp(file.stat().st_mtime) == date:
                filtered = file
             
    try :
        with open(f"{folder_path}/{filtered.name}") as f:
            return json.load(f)
    except :
        return None 
    
    
# def get_json(path) :
#     return pd.read_json(path,lines="true").to_dict()

def save_file(path, data, file_type="*.json") : 
    if "json" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")
    elif "csv" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")






