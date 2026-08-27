import pandas as pd 
import uuid
import requests
from Constants import API_BASE_URL

def start_up() :
    
    feeder_id = None 
    
    try : 
        df = pd.read_json('feederProps.json', lines="true").to_dict()
        feeder_id = df["Feed-Station-Data"][0]["feederID"]
    except :
        
        feeder_id = uuid.uuid4()
        df = {
            "Feed-Station-Data" : {"feederID" : str(feeder_id)}
        }
        
        pd.DataFrame(df).to_json("feederProps.json")
        
    print("Config data properly stored")
    return feeder_id
         
    
if __name__ == "__main__" :
    start_up()
