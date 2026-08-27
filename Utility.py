from datetime import datetime 

def date_generator() :
    return datetime.now().strftime("%m-%d-%Y")

def hms_generator() : 
    return datetime.now().strftime("%H-%M-%S")

