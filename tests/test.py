import time, csv, json
import os, sys
import logging

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))  # getting the project base path
sys.path.append(BASE_PATH)

from server.main import Sample
from config import config
from urllib.request import Request


def test_get_timestamps():
    sample_obj = Sample(request_url, csv_file_path)

    """
    Read timestamps from gives csv_file_path and store them in timestamps as a list
    """
    timestamps = sample_obj.get_timestamps()

    # check if all the timestamps in list are of str type
    res = all(isinstance(ele, str) for ele in timestamps)

    assert res == True


def test_api_called_on_correct_time():
    sample_obj = Sample(request_url, csv_file_path)
    sample_obj.main()


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

    csv_file_path = config['FILE_PATH']
    url = config['URL']

    # GET request without Headers is giving an HTTP Error 403: Forbidden
    request_url = Request(url, headers={"User-Agent": "Mozilla/5.0",
                                        "Accept": "application/json"})

    test_get_timestamps()
    test_api_called_on_correct_time()
