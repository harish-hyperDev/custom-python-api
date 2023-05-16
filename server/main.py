import csv
import json
import logging
import os
import sys
import threading
import time

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))  # getting the project base path
sys.path.append(BASE_PATH)  # Adding project base path to sys.path, for reading config.py

from urllib.request import Request, urlopen
from datetime import datetime
from config import config  # Importing config.py from base path to main.py


class APIClass:

    def __init__(self, url, csv_file):

        # Instance variables
        self.timestamp_list = []
        self.url = url
        self.csv_file = csv_file
        self.nearest_timestamp_occurrences = 0
        self.timestamp = datetime.now()
        self.current_time = 0
        self.wait = False
        self.threads = []
        self.remaining_timestamps = 1
        # self.nearest_timestamp_duration = 0

    def get_current_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_time = datetime.strptime(current_time, "%H:%M:%S")

        self.current_time = current_time
        return current_time

    # Read the timestamps from csv file
    def get_timestamps(self):
        timestamp_list = []

        """
        Read the timestamps present in csv file and 
        store them in a list with elements(timestamps) as string type
        """

        try:
            with open(self.csv_file, newline='') as csvfile:
                spam_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in spam_reader:
                    timestamp_list.append(', '.join(row))

        except FileNotFoundError:
            return 1
            # logger.warning("CSV file is not found on the given path! Terminating the program.")
            # exit(1)

        """
        Store the timestamps in instance variable except the first value
        (The first value of instance contains the Title of CSV file)
        """

        self.timestamp_list = timestamp_list[1:]
        return timestamp_list[1:]

    """
    Calculate the nearest timestamp occurrences from given timestamps(argument)
    and assign its value to instance variable
    """

    def get_minimum_timestamp(self, timestamps):

        # get the time of the present day in HH:MM:SS format
        current_time = self.get_current_time()

        """
        Calculate seconds remaining from timestamps to current time
        If the difference in seconds are positive values then store the value in list
        else store the value as 0
        """

        timestamp_in_seconds = [(x - current_time).total_seconds() if (x - current_time).total_seconds() > 0
                                else 0
                                for x in timestamps]

        # filter the timestamps whose difference value is positive and non-zero
        filtered_timestamps = []
        for x in range(0, len(timestamp_in_seconds)):
            if timestamp_in_seconds[x] > 0:
                filtered_timestamps.append(timestamps[x])

        # remove the difference values which are negative and zero
        timestamp_in_seconds = [i for i in timestamp_in_seconds if i > 0]
        self.remaining_timestamps = len(filtered_timestamps)

        # get the nearest timestamp seconds and the number of occurrences(repetitions) of the timestamp
        if self.remaining_timestamps > 0:

            nearest_timestamp_duration = min(timestamp_in_seconds)
            nearest_timestamp_occurrences = filtered_timestamps.count(
                filtered_timestamps[timestamp_in_seconds.index(nearest_timestamp_duration)])

            self.timestamp = filtered_timestamps[timestamp_in_seconds.index(nearest_timestamp_duration)]
            self.nearest_timestamp_occurrences = nearest_timestamp_occurrences

        else:
            self.nearest_timestamp_occurrences = 0
            # logger.debug("No timestamps remaining! Terminating the program.")
            # exit(0)

        # assign the seconds remaining for nearest timestamp and its occurrences to instance variables
        # self.nearest_timestamp_duration = nearest_timestamp_duration

    def main(self):

        timestamp_data = []
        timestamp_datetime = []

        # check if timestamps are passed as arguments from the CLI
        if len(sys.argv) == 2:
            timestamp_data = (sys.argv[1].replace(" ", "")).split(",")

        # otherwise read data from csv file
        else:
            logger.info("Reading data from csv.")
            timestamp_result = self.get_timestamps()  # read timestamps from csv file and store in instance variable "timestamp_list"
            if timestamp_result == 1:
                logger.warning("CSV file is not found on the given path! Terminating the program.")
                exit(1)

            timestamp_data = self.timestamp_list

        # check if the timestamps are in valid format else log and throw exception
        try:
            timestamp_datetime = [datetime.strptime(x, "%H:%M:%S") for x in timestamp_data]

        except ValueError:
            logger.error("Time format is incorrect! Terminating the program.")
            return

        self.wait = False
        self.threads = []

        while self.remaining_timestamps > 0:
            self.call_fetch_url(timestamp_datetime)

        if self.remaining_timestamps == 0:
            return 1

    def call_fetch_url(self, timestamp_datetime):

        """
        Retrieve the nearest timestamp and its occurrences by calling "get_minimum_timestamp"
        and wait until the threads have started (self.wait = True)
        """
        if not self.wait:
            self.get_minimum_timestamp(timestamp_datetime)
            self.threads = [threading.Thread(target=self.fetch_url) for x in
                            range(0, self.nearest_timestamp_occurrences)]

            if self.remaining_timestamps == 0:  # if there are no remaining timestamps, then exit the program
                return 1

            self.wait = True

        # get time in HH:MM:SS (current time can be accessed with self.current_time)

        get_time_thread = threading.Thread(target=self.get_current_time)
        get_time_thread.start()
        get_time_thread.join()

        """
        Start the threads when the current time and nearest timestamp are equal
        and stop the wait, to retrieve nearest timestamp and occurrences.
        
        The both values in below condition are assigned when "get_minimum_timestamp" instance method is called
        """
        if self.current_time == self.timestamp:
            for t in self.threads:
                t.start()
            for t in self.threads:
                t.join()

            self.wait = False

            if self.timestamp:  # don't return self.timestamp if it's value is None
                return self.timestamp.strftime("%H:%M:%S")

    def fetch_url(self):

        """
        Send GET request to the given url and add the response to log
        The response is scraped in dict type for better readability
        """
        with urlopen(self.url) as response:
            body = response.read().decode("UTF-8")  # converting bytes data to str
            json_data = json.loads(body)  # deserializing str to dict

        if logger:
            logger.info("GET request for %s result - (IP : %s)", self.timestamp, json_data['ip'])  # log the response data


if __name__ == "__main__":

    # Create and configure logger
    logging.basicConfig(filename=f"{BASE_PATH}/logger.log",
                        format="%(asctime)s(%(levelname)s) - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.DEBUG,
                        filemode='a')

    # Creating logger for displaying logs in console as well
    console_format = logging.Formatter("%(asctime)s - (%(levelname)s) - %(message)s", "%Y-%m-%d %H:%M:%S")
    console_log = logging.StreamHandler(sys.stdout)
    console_log.setFormatter(console_format)

    # Creating an object for logging to file
    logger = logging.getLogger()

    # Adding logger created for console as event handler to logger
    logger.addHandler(console_log)
    logger.info("Program started!")

    csv_file_path = config['FILE_PATH']
    url = config['URL']

    # GET request without Headers is giving an HTTP Error 403: Forbidden
    request_url = Request(url, headers={"User-Agent": "Mozilla/5.0",
                                        "Accept": "application/json"})

    try:
        sample_obj = APIClass(request_url, csv_file_path)
        main_result = sample_obj.main()

        if main_result == 1:
            logger.debug("No timestamps found! Terminating the Program.")

    # throw exception if user stops the program
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: Program has been terminated by the user!")
        exit(1)
