from datetime import datetime
import os, sys
import logging

import pytest

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))  # getting the project base path
sys.path.append(BASE_PATH)

from server.main import APIClass
from config import config
from urllib.request import Request

csv_file_path = config['FILE_PATH']
url = config['URL']

# GET request without Headers is giving an HTTP Error 403: Forbidden
request_url = Request(url, headers={"User-Agent": "Mozilla/5.0",
                                    "Accept": "application/json"})


class TestAPIClass:
    def test_get_timestamps(self):
        api = APIClass(request_url, csv_file_path)

        """
        Read timestamps from gives csv_file_path and store them in timestamps as a list
        """
        timestamps = api.get_timestamps()

        # check if all the timestamps in list are of str type
        res = all(isinstance(ele, str) for ele in timestamps)
        assert res == True

    def test_nearest_timestamp(self):
        api = APIClass(request_url, csv_file_path)

        # a list of timestamps in str type
        timestamps_list = ["23:50:00", "23:55:00", "23:50:00", "23:50:00", "23:59:00"]

        # converting timestamps from str type to datetime.datetime type
        timestamps_datetime_list = [datetime.strptime(x, "%H:%M:%S") for x in timestamps_list]

        # finds the nearest timestamp by calculating difference from timestamps with current time
        api.get_minimum_timestamp(timestamps_datetime_list)

        # Actual output
        actual_output = {
            "Nearest Timestamp": api.timestamp.strftime("%H:%M:%S"),
            "Nearest Timestamp Occurrences": api.nearest_timestamp_occurrences
        }

        """
        Need to change the expected values to an appropriate value
        based on timestamps given in above "timestamps_list" variable
        
        On the given timestamps the nearest timestamp is "23:50:00" and
        its occurrences(repetitions) are 3
        """
        # Expected output
        expected_output = {
            "Nearest Timestamp": "23:50:00",
            "Nearest Timestamp Occurrences": 3
        }

        assert actual_output == expected_output

    def test_sent_get_request_on_timestamp(self):
        api = APIClass(request_url, csv_file_path)

        # a list of timestamps in str type
        # timestamps_list = ["17:10:41", "17:10:41", "23:50:00", "23:55:00", "23:50:00", "23:50:00", "23:59:00"]
        timestamps_list = ["19:47:21", "19:47:21", "19:05:01"]
        # converting timestamps from str type to datetime.datetime type
        timestamps_datetime_list = [datetime.strptime(x, "%H:%M:%S") for x in timestamps_list]

        # print(len(timestamps_datetime_list))

        # assert "hello" == "hello"

        # finds the nearest timestamp by calculating difference from timestamps with current time
        # sample_obj.get_minimum_timestamp(timestamps_datetime_list)

        timestamp = 0
        while api.remaining_timestamps > 0:
            api.call_fetch_url(timestamps_datetime_list)
            timestamp = api.timestamp.strftime("%H:%M:%S")

        assert timestamp == "19:47:21"


if __name__ == "__main__":
    pass
    # api_obj = APIClass(request_url, csv_file_path)

    # test_obj = TestSampleClass()
    # test_obj.test_sent_get_request_on_timestamp()

    # test_get_timestamps()
    # test_sent_get_request_on_timestamp()
    # test_nearest_timestamp()
