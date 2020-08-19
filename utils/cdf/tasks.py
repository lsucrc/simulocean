import os, errno
import sys
import pandas as pd
import urllib.request
from celery import Celery
import datetime
import json

app = Celery('tasks', broker='pyamqp://localhost//')


@app.task
def data_pull(filename):
    now = datetime.datetime.now()
    bigdf = pd.DataFrame()
    try:
        os.makedirs('cache')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    try:
        os.makedirs('csv')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(filename) as jsondata:
        data=json.load(jsondata)

        year, month, day = map(int, data["startdate"].split('-'))
        data["startdate"] = datetime.date(year, month, day)

        year, month, day = map(int, data["enddate"].split('-'))
        data["enddate"] = datetime.date(year, month, day)

    if data["startdate"].strftime("%m%Y") == now.strftime("%m%Y") or data["enddate"].strftime("%m%Y")==now.strftime("%m%Y"): #current year and month - past 45 days data
        for i in range(len(data["stationid"])):
            url="https://www.ndbc.noaa.gov/data/realtime2/"+data["stationid"][i]+".txt"
            try:
                urllib.request.urlretrieve(url, 'cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt')
                df = pd.read_csv('cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt',sep="\s+")
                bigdf = pd.concat([bigdf,df],axis=0,sort=False)
            except OSError as e:
                print('Data does not exist!')
                pass

    if data["startdate"].strftime("%Y") == now.strftime("%Y") or data["enddate"].strftime("%Y")==now.strftime("%Y"): #monthly data for the current year
        months = pd.date_range(start=data["startdate"],end=data["enddate"],freq="SMS",normalize=True)
        for i in range(len(data["stationid"])):
            for j in range(len(months)):
                pd.to_datetime(months[j],infer_datetime_format=True)
                url = "https://www.ndbc.noaa.gov/data/"+data["urldata"]+"/"+months[j].strftime("%b")+"/"+data["stationid"][i]+".txt"
                print(url)
                try:
                    urllib.request.urlretrieve(url, 'cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt')
                    df = pd.read_csv('cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt',sep="\s+")
                    bigdf = pd.concat([bigdf,df],axis=0,sort=False)
                except OSError as e:

                    pass

    if data["startdate"].strftime("%Y") < now.strftime("%Y") or data["enddate"].strftime("%Y") < now.strftime("%Y"):  #older data
        years = pd.date_range(start=data["startdate"],end=data["enddate"],freq="A",normalize=True)
        for i in range(len(data["stationid"])):
            for j in range(len(years)):
                pd.to_datetime(years[j],infer_datetime_format=True)
                url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + data["stationid"][i] + data["datatype"] + years[j].strftime("%Y") + '.txt.gz&dir=data/historical/' + data["urldata"] + '/'
                try:
                    urllib.request.urlretrieve(url, 'cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt')
                    df = pd.read_csv('cache/' + data["stationid"][i] + data["datatype"] + data["startdate"].strftime("%b%Y") + '.txt',sep="\s+")
                    bigdf = pd.concat([bigdf,df],axis=0,sort=False)
                    print(url)
                except OSError as e:
                    print('Data does not exist!')
                    pass


    bigdf = bigdf.drop_duplicates(keep='first')
    bigdf.to_csv('csv/' + data["startdate"].strftime("%b%Y") + data["enddate"].strftime("%b%Y") + '.csv', index=False)
