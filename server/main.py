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
    
    timestamp_list = []
    
    try:
        with open('api_timestamp.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                timestamp_list.append(', '.join(row))
            
    except FileNotFoundError:
        print("File is not present in the given location!")
        
    # Removing first item from timestamps list (which contains Title of the csv file)
    return timestamp_list[1:] if len(timestamp_list) else None


def get_minimum_timestamp(timestamps):
    
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.strptime(current_time, "%H:%M:%S")
    
    timestamp_in_seconds = [(x - current_time).total_seconds() if (x - current_time).total_seconds() > 0 else 0 for x in timestamps]
    
    filtered_timestamps = []
    for x in range(0,len(timestamp_in_seconds)):
        if not timestamp_in_seconds[x] == 0:
            filtered_timestamps.append(timestamps[x])
    
    timestamp_in_seconds = [i for i in timestamp_in_seconds if i != 0]
    
    try:
        min_timestamp_seconds = min(timestamp_in_seconds)
        timestamp_occurences = filtered_timestamps.count(filtered_timestamps[timestamp_in_seconds.index(min_timestamp_seconds)])
        
    except ValueError:
        print("Sent requests on all the given timestamps, exiting!")
        exit(0)
        
    print("\nMin Value countdown - ", min_timestamp_seconds, " secs")
    print("Index of Min Value countdown - ", timestamp_in_seconds.index(min_timestamp_seconds))
    print("\nMin Value - ", filtered_timestamps[timestamp_in_seconds.index(min_timestamp_seconds)].time())
    print("Index of Min Value - ", filtered_timestamps.index(filtered_timestamps[timestamp_in_seconds.index(min_timestamp_seconds)]))
    print("Occurences of Min Value - ", timestamp_occurences)
    
    return min_timestamp_seconds, timestamp_occurences

def main():

    timestamp_data = get_timestamps() #.apply(lambda x: datetime.strftime(x, "%H:%M:%S"))
    timestamp_datetime_data = [datetime.strptime(x, "%H:%M:%S") for x in timestamp_data]
    
    while True:
        min_timestamp_seconds, timestamp_occurences = get_minimum_timestamp(timestamp_datetime_data)
        
        time.sleep(min_timestamp_seconds)
        print("\nCOUNTDOWN: ", min_timestamp_seconds)
        
        count = 0
        while count < timestamp_occurences:
            print("sending request")
            send_request()
            count += 1
        

def send_request():
    
    with urlopen(request_site) as response:
        body = response.read()

    print(body[:15])


if __name__ == "__main__":
    main()