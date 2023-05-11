import time, csv, json
import os, sys
import logging

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))   # getting the project base path
sys.path.append(BASE_PATH)

from server.main import get_timestamps

def main():
    timestamps = get_timestamps()
    res = all(isinstance(ele, str) for ele in timestamps)
    assert res == True
    

main()