import time, csv, json
import os, sys
import logging

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))   # getting the project base path
sys.path.append(BASE_PATH)

from server.main import Sample
from config import config
from urllib.request import Request

def test_main():

    csv_file_path = config['FILE_PATH']
    url = config['URL']

    # GET request without Headers is giving an HTTP Error 403: Forbidden
    request_url = Request(url, headers={"User-Agent": "Mozilla/5.0",
                                        "Accept": "application/json"})

    s1 = Sample(csv_file_path, request_url)
    timestamps = s1.get_timestamps()
    res = all(isinstance(ele, str) for ele in timestamps)

    assert res == True
    

main()