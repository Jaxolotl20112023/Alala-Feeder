from datetime import datetime 
from pathlib import Path


import pandas as pd

def date_generator() :
    return datetime.now().strftime("%m-%d-%Y")

def hms_generator() : 
    return datetime.now().strftime("%H-%M-%S")

def get_recent_file(path, file_type="*.json") :

    folder_path = Path(path)

    files = folder_path.glob(file_type)
    
    print("file")
    for file in files:
        
        print(file.stat().st_mtime)

    filtered =  max(files, key=lambda x: x.stat().st_mtime)

    try :
        convert = pd.read_csv(filtered).to_dict() if "csv" in file_type else pd.read_json(filtered).to_dict() if "json" in file_type else None
    except :
        return None 
    
    return convert

def get_json(path) :
    return pd.read_json(path,lines="true").to_dict()

def save_file(path, data, file_type="*.json") : 
    if "json" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")
    elif "csv" in file_type : 
        pd.DataFrame(data).to_json(path, orient="records")






