from enum import Enum
from Utility import get_recent_file
import pandas as pd
import uuid
from Utility import get_feederID

API_BASE_URL = 'http://172.20.10.9:3500'

class Status(Enum) :
    BAD_CONNECTION = "Bad Connection"
    GOOD_CONNECTION = "Good Connection"

    NO_POWER = "No Power"
    HAS_POWER = "Has Power"

    INVALID_READINGS = "Invalid Readings"
    VALID_READINGS = "Valid Readings"

FEEDER_ID = get_feederID()

print(FEEDER_ID)


# ALLOWED_IDS = pd.read_json("./allowedIDs.json",lines="true").to_dict()
