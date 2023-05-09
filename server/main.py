import threading
import time, csv
import os, sys
sys.path.insert(0, os.getcwd())     # Adding project base path to sys.path

from urllib.request import Request, urlopen
from datetime import datetime
from config import config           # Importing config.py from base path to main.py


url = config['URL']
request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})


def get_timestamps():
    
    timestamps = []
    
    try:
        with open('api_timestamp.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                timestamps.append(', '.join(row))
            
    except FileNotFoundError:
        print("File is not present in the given location!")
        
    # Removing first item from timestamps list (which contains Title of the csv file)
    return timestamps[1:] if len(timestamps) else None


def get_time_diff(t1, t2):
    
    time_format = "%H:%M:%S"
    return (datetime.strptime(t2, time_format) - datetime.strptime(t1, time_format)).total_seconds()


def main():

    timestamp_data = get_timestamps() #.apply(lambda x: datetime.strftime(x, "%H:%M:%S"))
    timestamp_datetime_data = [datetime.strptime(x, "%H:%M:%S") for x in timestamp_data]
    
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.strptime(current_time, "%H:%M:%S")
    
    timestamp_diff = [(x - current_time).total_seconds() if (x - current_time).total_seconds() > 0 else 0 for x in timestamp_datetime_data]
    
    filtered_timestamps = []
    for x in range(0,len(timestamp_diff)):
        if not timestamp_diff[x] == 0:
            filtered_timestamps.append(timestamp_datetime_data[x])
    
    timestamp_diff = [i for i in timestamp_diff if i != 0]
    

    print("--------------")
    print(filtered_timestamps)
    print(timestamp_diff)
    print("--------------")
    
    min_timestamp_seconds = min(timestamp_diff)
    timestamp_occurences = filtered_timestamps.count(filtered_timestamps[timestamp_diff.index(min_timestamp_seconds)])
    print("Min Value countdown - ", min_timestamp_seconds)
    print("Index of Min Value countdown - ", timestamp_diff.index(min_timestamp_seconds))
    print("\nMin Value - ", filtered_timestamps[timestamp_diff.index(min_timestamp_seconds)].time())
    print("Index of Min Value - ", filtered_timestamps.index(filtered_timestamps[timestamp_diff.index(min_timestamp_seconds)]))
    print("Occurences of Min Value - ", filtered_timestamps.count(filtered_timestamps[timestamp_diff.index(min_timestamp_seconds)]))
    
    time.sleep(min_timestamp_seconds)
    print(timestamp_diff.index(min_timestamp_seconds))
    
    
    while True:
        count = 0
        while count < timestamp_occurences:
            print("sending request")
            send_request()
            count += 1
    
    # threading.Timer(timestamp_diff.index(min_timestamp_seconds), send_request()).start()
    # return
    
    # time.sleep(10)
    '''
    while True:
        # current_time = datetime.now().strftime("%H:%M:%S")
        print(current_time)
        
        timestamp_occurences = 0
        for timestamp in timestamp_data:
            if timestamp == current_time:
                timestamp_occurences += 1
            
        count = 0
        while count <= timestamp_occurences:
            send_request()
            print("request sent")
            count += 1
                
            # exit(1)
        
        time.sleep(0.5)
    '''


def send_request():
    
    with urlopen(request_site) as response:
        body = response.read()

    print(body[:15])


if __name__ == "__main__":
    main()