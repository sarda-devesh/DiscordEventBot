from collections import defaultdict
from datetime import datetime
import pytz
from time import strptime

naive_dt = datetime(2020, 9, 20, 8, 30)

def get_current_time(): 
    return datetime.utcnow()

def get_possibilities(actual, time_object):
    starting_names = {}
    full_names = {}
    for name in pytz.all_timezones:
        tzone = pytz.timezone(name)
        tzabbrev = datetime.now(tzone).tzname()
        zone_name = str(tzone)
        if(tzabbrev == actual and zone_name.count("/") == 1): 
            starting = zone_name[ : zone_name.index("/")]
            if starting not in starting_names: 
                starting_names[starting] = 1
                full_names[zone_name] = time_object.astimezone(tzone)
    return full_names

def filter_locations(possibilities): 
    to_consider = []
    valid = []
    for key in possibilities: 
        timestamp = str(possibilities[key])
        exists = False 
        for item in valid:
            if(item == timestamp):
                exists = True
                break
        if not exists: 
            valid.append(timestamp)
            to_consider.append(key)
    filtered_data = {}
    for zone_name in to_consider: 
        time_object = possibilities[zone_name]
        filtered_data[zone_name] = time_object.astimezone(pytz.utc)
    return filtered_data

def get_user_timing(to_process, remind_before = 15): 
    current_time = datetime.now()
    broken = to_process.strip().split(",")
    timezone = broken.pop().strip()
    
    date_string = broken[0].strip()
    if(len(broken) == 1):
        time_string = date_string
        date_string = ""
    else:
        time_string = broken[1].strip()

    date_data = date_string.strip().split(" ")
    starting_date = datetime(current_time.year, current_time.month, current_time.day, tzinfo= None)
    if(len(date_string) == 0): 
        date_string = None
    elif(len(date_data) == 1):
        starting_date = starting_date.replace(day = int(date_string))
    elif(len(date_data) == 2): 
        date_object = datetime.strptime(date_string,"%b %d")
        starting_date = starting_date.replace(month = date_object.month, day = date_object.day)
    elif(len(date_data) == 3): 
        starting_date = datetime.strptime(date_string, "%b %d %Y")
    
    starting_time = None
    if(time_string.count(":")): 
        starting_time = datetime.strptime(time_string, "%I:%M %p")
    else: 
        starting_time = datetime.strptime(time_string, "%I %p")
    complete_object = starting_date.replace(hour = starting_time.hour, minute = starting_time.minute) 
    possibilities = get_possibilities(timezone, complete_object)
    if(timezone == "PST" and "US/Pacific" not in possibilities): 
        possibilities = get_possibilities("PDT", complete_object)
    return filter_locations(possibilities)

if __name__ == "__main__":
    to_process = input("Enter the time you are considering: ")
    actual = get_user_timing(to_process)
    print("Found the following unique timezones: ")
    for zone_name in actual: 
        converted_object = actual[zone_name]
        print(str(zone_name) + " -> " + str(converted_object))