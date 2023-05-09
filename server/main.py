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

    timestamp_data = get_timestamps()
    # print("timestamp data ", timestamp_data)
    print(get_time_diff(timestamp_data[0], timestamp_data[1]))
    
    # time.sleep(10)
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
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


def send_request():
    
    with urlopen(request_site) as response:
        body = response.read()

    print(body[:15])


if __name__ == "__main__":
    main()