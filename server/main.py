import time, csv, json
import os, sys
import logging, threading

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))  # getting the project base path
sys.path.append(BASE_PATH)  # Adding project base path to sys.path, for reading config.py

from urllib.request import Request, urlopen
from datetime import datetime
from config import config  # Importing config.py from base path to main.py


def get_current_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.strptime(current_time, "%H:%M:%S")

    return current_time


class Sample:

    def __init__(self, url, csv_file):
        self.timestamp_list = []
        self.url = url
        self.csv_file = csv_file
        self.nearest_timestamp_duration = 0
        self.nearest_timestamp_occurrences = 0
        self.timestamp = 0

    # Read the timestamps from csv file
    def get_timestamps(self):

        timestamp_list = []

        """
        Read the timestamps present in csv file and 
        store them in a list with elements(timestamps) as string type
        """

        try:
            logger.info("Reading data from csv.")
            with open(self.csv_file, newline='') as csvfile:
                spam_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in spam_reader:
                    timestamp_list.append(', '.join(row))

        except FileNotFoundError:
            logger.warning("CSV file is not found on the given path! Terminating the program.")
            exit(1)

        """
        Store the timestamps in instance variable except the first value
        (The first value of instance contains the Title of CSV file)
        """

        self.timestamp_list = timestamp_list[1:]

    """
    Calculate the seconds of nearest timestamp, and timestamp occurrences from given timestamps(argument)
    and assign their values to instance variables
    """
    def get_minimum_timestamp(self, timestamps):

        # get the time of the present day in HH:MM:SS format
        current_time = get_current_time()

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

        # get the nearest timestamp seconds and the number of occurences(repetitions) of the timestamp
        try:
            nearest_timestamp_duration = min(timestamp_in_seconds)
            nearest_timestamp_occurrences = filtered_timestamps.count(
                filtered_timestamps[timestamp_in_seconds.index(nearest_timestamp_duration)])

            self.timestamp = filtered_timestamps[timestamp_in_seconds.index(nearest_timestamp_duration)]
        except ValueError:
            logger.debug("No timestamps remaining! Terminating the program.")
            exit(0)

        # assign the seconds remaining for nearest timestamp and its occurrences to instance variables
        self.nearest_timestamp_duration = nearest_timestamp_duration
        self.nearest_timestamp_occurrences = nearest_timestamp_occurrences

    def main(self):

        timestamp_data = []
        timestamp_datetime = []

        # check if timestamps are passed as arguments from the CLI
        if len(sys.argv) == 2:
            timestamp_data = (sys.argv[1].replace(" ", "")).split(",")

        # otherwise read data from csv file
        else:
            # self.get_timestamps()
            timestamp_data = self.timestamp_list

        # check if the timestamps are in valid format else log and throw exception
        try:
            timestamp_datetime = [datetime.strptime(x, "%H:%M:%S") for x in timestamp_data]

        except ValueError:
            logger.error("Time format is incorrect! Terminating the program.")
            exit(1)

        sleep_flag = True
        threads = []

        while True:
            # get the nearest timestamp seconds and its occurrences (repetitions)
            get_time_thread = threading.Thread(target=get_current_time)
            get_time_thread.start()
            get_time_thread.join()

            print(get_time_thread)

            if sleep_flag:
                self.get_minimum_timestamp(timestamp_datetime)
                threads = [threading.Thread(target=self.fetch_url) for x in range(0, self.nearest_timestamp_occurrences)]
                time.sleep(self.nearest_timestamp_duration - 1)
                sleep_flag = False

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # sleep till the nearest timestamp duration
            # if self.nearest_timestamp_occurrences > 1:
            # else:
            #     time.sleep(self.nearest_timestamp_duration - 0.5)

            # count = 0
            # while count < self.nearest_timestamp_occurrences:
            #     self.fetch_url()
            #     count += 1

    def fetch_url(self):

        """
        Send GET request to the given url and add the response to log
        The response is scraped in dict type for better readability
        """
        with urlopen(self.url) as response:
            body = response.read().decode("UTF-8")  # converting bytes data to str
            json_data = json.loads(body)  # deserializing str to dict

        logger.info("GET request result - (IP : %s)", json_data['ip'])  # log the response data


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
        sample_obj = Sample(request_url, csv_file_path)
        sample_obj.get_timestamps()  # read timestamps from csv file and store them in instance variable
        sample_obj.main()
        # main()

    # throw exception if user stops the program
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: Program has been terminated by the user!")
        exit(1)
