from enum import Enum
from Utility import get_file

API_BASE_URL = 'http://172.20.10.9:3500'

class Status(Enum) :
    BAD_CONNECTION = "Bad Connection"
    GOOD_CONNECTION = "Good Connection"

    NO_POWER = "No Power"
    HAS_POWER = "Has Power"

    INVALID_READINGS = "Invalid Readings"
    VALID_READINGS = "Valid Readings"

ALLOWED_IDS = get_file('./allowedIDs.json')
