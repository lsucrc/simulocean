# NOAA

## National Data Buoy Center Historical Data Scraper


## Overview
This python program will download historical buoy data from the National Oceanic and Atmospheric Administration's National Data Buoy Center stored here:   
(https://www.ndbc.noaa.gov/historical_data.shtml)

The user is able to choose specific stations, years, and types of data (standard meteorological, winds, currents, water levels, etc.) and the program will download the text files and convert them to csv files and return them to the user. This application uses a celery backend to make the process faster and scalable for larger data sets. 

## Setup
The program currently requires that the same machine host the Jupyter Notebook and run the celery workers. The celery workers will be started with:
```
$ celery -A tasks worker --loglevel=info
```
On the host machine. (working on running as daemon) This sets up the celery worker to receive information and run its part of the code - the tasks.py file.

## Running the Program
Either the program NOAACelery.py or NOAAJupyter.ipynb will then be run with:
```
	$ python3 NOAACelery.py
```
The program will ask how many stations data need to be downloaded, ask for each station ID, ask for the year for the data, and finally for the data type. The corresponding data will then be pulled from the website and stored in the cache directory as a text file. The file’s name will correspond with the data pulled. If the user were to pull standard meteorological data from Station 41001 from the year 1976 the data will be stored as 41001h1976.txt. For ocean current data from station 42044 from 2014 the data will be stored as 42044a2014.txt. The program will then take these text files and convert them to CSV files and store them under the same file name.
