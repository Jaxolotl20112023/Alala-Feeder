import pandas as pd 
import uuid
import requests
from Constants import API_BASE_URL
from Utility import date_generator#, get_file

def start_up() :
    
#     feeder_id =
    
    err = False
    
    try: 
        df = pd.read_json(f"./stationProps.json", lines="true").to_dict()
        print("ok")
#     df = get_file("./stationData", "*.json")
#     if (not df) :
    except:
        # feeder_id = df["Feed-Station-Data"][0]["feederID"]
        print("First time booting up")
        err = True
        
        feeder_id = uuid.uuid4()
        df = {
            "Feed-Station-Data" : {
                "feederID" : str(feeder_id),
                "foodLeft" : 500,
                "days_operating" : 0
            }
        }
        
        pd.DataFrame(df).to_json(f"./stationProps.json")
        
    print("Config data properly stored")
    print("Init data: ",df["Feed-Station-Data"])
    return df["Feed-Station-Data"][0] if not err else df["Feed-Station-Data"]

         
    
if __name__ == "__main__" :
    start_up()
