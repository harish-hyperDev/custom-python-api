## Custom Python API


Python program for performing GET request(s) on given timestamp(s).

Before running this program, install the dependencies with

    pip install -r requirements.txt

When the program is run, it makes GET request at the timestamp to the url given in **config.py** present in base path. Feel free to replace the url :)

The program can be run in two-ways

1. Running the program with timestamps given from command-line arguments.

        cd server
        python main.py "HH:MM:SS, HH:MM:SS, ..."

2. Running the program with timestamps present in a csv file
        
        cd server
        python main.py

    The url for file will be automatically taken from config.py

    You can change the FILE_PATH value in config.py to give your own path
