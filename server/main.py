import time, csv, json
import os, sys
import logging

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))   # getting the project base path
sys.path.append(BASE_PATH)     # Adding project base path to sys.path, for reading config.py

from urllib.request import Request, urlopen
from datetime import datetime
from config import config           # Importing config.py from base path to main.py


url = config['URL']
file_path = config['FILE_PATH']
request_site = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})    # remove "Accept": "application/json" to retrieve response as "application/body" from GET request

# Create and configure logger
logging.basicConfig(filename=f"{BASE_PATH}/logger.log",
                    format="%(asctime)s(%(levelname)s) - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG,
                    filemode='a')

# Creating logger for displaying logs in console as well
console_format = logging.Formatter("%(asctime)s - %(name)s - (%(levelname)s) - %(message)s", "%Y-%m-%d %H:%M:%S")
console_log = logging.StreamHandler(sys.stdout)
console_log.setFormatter(console_format)

# Creating an object for logging to file
logger = logging.getLogger()

# Adding logger created for console as event handler to logger
logger.addHandler(console_log)

logger.info("Program started!")


# Function for reading the timestamps from csv file

def get_timestamps():
    
    timestamp_list = []
    
    """
    Read the timestamps present in csv file and 
    store them in a list with elements(timestamps) as string type
    """
    
    try:
        logger.info("Reading data from csv.")
        with open(file_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                timestamp_list.append(', '.join(row))
            
    except FileNotFoundError:
        logger.warning("CSV file is not found on the given path! Terminating the program.")
        exit(1)  
      
    """
    If the list is empty then, return None
    else return list by removing first element of list (first element of list contains title of the csv file) 
    """
    return timestamp_list[1:] if len(timestamp_list) else None


# Function for calculating the nearest timestamp

def get_minimum_timestamp(timestamps):
    
    """
    Calculate and return the seconds of nearest timestamp from given timestamps(argument)
    """
    # get the time of the present day in HH:MM:SS format
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.strptime(current_time, "%H:%M:%S")
    
    '''logging.StreamHandler(sys.stdout)
    Calculate seconds remaining from timestamps to current time
    If the difference in seconds are positive values then store the value in list
    else store the value as 0
    '''
    timestamp_in_seconds = [(x - current_time).total_seconds() if (x - current_time).total_seconds() > 0 else 0 for x in timestamps]
    
    # filter the timestamps whose difference value is positive and non-zero
    filtered_timestamps = []
    for x in range(0,len(timestamp_in_seconds)):
        if timestamp_in_seconds[x] > 0:
            filtered_timestamps.append(timestamps[x])
    
    # remove the difference values which are negative and zero
    timestamp_in_seconds = [i for i in timestamp_in_seconds if i > 0]
    
    # get the nearest timestamp seconds and the number of occurences(repetitions) of the timestamp
    try:
        min_timestamp_seconds = min(timestamp_in_seconds)
        timestamp_occurences = filtered_timestamps.count(filtered_timestamps[timestamp_in_seconds.index(min_timestamp_seconds)])
        
    except ValueError:
        logger.debug("No timestamps remaining! Terminating the program.")
        exit(0)
        
    return min_timestamp_seconds, timestamp_occurences

def main():

    timestamp_data = []
    timestamp_datetime_data = []
    
    # check if timestamps are passed as arguments from the CLI
    if len(sys.argv) == 2:
        timestamp_data = (sys.argv[1].replace(" ", "")).split(",")
            
    # otherwise read data from csv file
    else:
        timestamp_data = get_timestamps() 
    
    # check if the timestamps are in valid format else log and throw exception
    try:
        timestamp_datetime_data = [datetime.strptime(x, "%H:%M:%S") for x in timestamp_data]
        
    except ValueError:
        logger.error("Time format is incorrect! Terminating the program.")
        exit(1)
    
    while True:
        # get the nearest timestamp seconds and its occurences (repetitions)
        min_timestamp_seconds, timestamp_occurences = get_minimum_timestamp(timestamp_datetime_data)
        
        # sleep till the nearest timestamp duration
        time.sleep(min_timestamp_seconds)
        
        count = 0
        while count < timestamp_occurences:
            send_request()
            count += 1
        

def send_request():
    """
    Send GET request to the given url and add the response to log
    The response is scraped in dict type for better readability 
    """
    with urlopen(request_site) as response:
        body = response.read().decode("UTF-8")      # converting bytes data to str
        json_data = json.loads(body)                # deserializing str to dict

    logger.info("GET request result - (IP : %s)", json_data['ip'])  # log the response data


if __name__ == "__main__":
    try:
        main()
        
    # throw excepction if the user stop program
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: Program has been terminated by the user!")
        exit(1)