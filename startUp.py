import pandas as pd 
import uuid
import requests
from Constants import API_BASE_URL
from Utility import date_generator#, get_file

def start_up() :
    
#     feeder_id =
    
    try: 
        df = pd.read_json(f"./stationData/stationData_{date_generator()}.json", lines="true").to_dict()
#     df = get_file("./stationData", "*.json")
#     if (not df) :
    except:
        # feeder_id = df["Feed-Station-Data"][0]["feederID"]
        
        feeder_id = uuid.uuid4()
        df = {
            "Feed-Station-Data" : {
                "feederID" : str(feeder_id),
                "foodLeft" : 500,
                "days_operating" : 0
            }
        }
        
        pd.DataFrame(df).to_json(f"./stationData/StationData_{date_generator()}.json")
        
    print("Config data properly stored")
    return df["Feed-Station-Data"]

         
    
if __name__ == "__main__" :
    start_up()
