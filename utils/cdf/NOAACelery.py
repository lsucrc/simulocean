import os, errno
import sys
import pandas as pd
import urllib.request
from celery import Celery
import numpy as np
from tasks import data_pull #can remove comment and .delay on line 134 for noncelery usage
import matplotlib.pyplot as plt
import datetime
import json

app = Celery('tasks', broker='pyamqp://localhost//')

stationid_list = []
startdate_list = []
enddate_list = []
datatype_list = []
urldata_list = []

data = {}
data["stationid"]=[]

def data_select(stationcount):
    now = datetime.datetime.now()
    while True:
        date_entry = input('Enter the start date in YYYY-MM-DD format: ')
        try:
            year, month, day = map(int, date_entry.split('-'))
            startdate = datetime.date(year, month, day)
            startdate_list.append(startdate)
            break
        except:
            print("Invalid start date")

    data["startdate"]=startdate

    while True:
        date_entry = input('Enter the end date in YYYY-MM-DD format: ')

        try:
            year, month, day = map(int, date_entry.split('-'))
            enddate = datetime.date(year, month, day)
            if enddate > startdate:
                enddate_list.append(enddate)
            else:
                raise
            break
        except:
            print("Invalid end date")

    data["enddate"]=enddate

    while True:
        datatype = str(input("Which type of data? "))
        if datatype == 'Standard Meteorological':
            datatype = 'h'
            urldata = 'stdmet'
            break
        elif datatype == 'test':
            datatype = 'h'
            urldata = 'stdmet'
            break
        elif datatype == 'Continuous Winds':
            datatype = 'c'
            urldata = 'cwind'
            break
        elif datatype == 'Ocean Current':
            datatype = 'a'
            urldata = 'adcp'
            break
        elif datatype == 'Oceanographic':
            datatype = 'o'
            urldata = 'ocean'
            break
        elif datatype == 'Spectral Wave Density':
            datatype = 'w'
            urldata = 'swden'
            break
        elif datatype == 'Spectral Wave alpha1':
            datatype = 'd'
            urldata = 'swdir'
            break
        elif datatype == 'Spectral Wave alpha2':
            datatype = 'i'
            urldata = 'swdir2'
            break
        elif datatype == 'Spectral Wave r1':
            datatype = 'j'
            urldata = 'swr1'
            break
        elif datatype == 'Spectral Wave r2':
            datatype = 'k'
            urldata = 'swr2'
            break
        elif datatype == 'Water-column Height':
            datatype = 't'
            urldata = 'dart'
            break
        else:
            print("Invalid data type.")
    datatype_list.append(datatype)
    urldata_list.append(urldata)

    data["datatype"]=datatype
    data["urldata"]=urldata
    for i in range(0,stationcount):
        stationid = str(input('Please enter station ID: '))
        stationid = stationid.lower()
        stationid_list.append(stationid)
        data["stationid"].append(stationid)


    with open('data.json','w') as fout:
        json.dump(data,fout,indent=2,sort_keys=True,default=str)

    return stationid_list, startdate_list, enddate_list, datatype_list, urldata_list

def graph():


    while True:
        try:
            filename = str(input("Enter the file you would like to plot or 'none': "))
            if filename == "none":
                break
            else:
                dataframe = pd.read_csv('csv/'+filename)
                try: #one line YYYY MM DD HH
                    dateparse = lambda x: pd.datetime.strptime(x, '%Y %m %d %H')
                    df = pd.read_csv('csv/'+filename, parse_dates=[[dataframe.columns[0],dataframe.columns[1],dataframe.columns[2],dataframe.columns[3]]],date_parser=dateparse)
                except:
                    pass
                try: #two line YYYY MM DD HH
                    dateparse = lambda x: pd.datetime.strptime(x, '%Y %m %d %H')
                    df = pd.read_csv('csv/'+filename, parse_dates=[[dataframe.columns[0],dataframe.columns[1],dataframe.columns[2],dataframe.columns[3]]], skiprows=[1],date_parser=dateparse)
                except:
                    pass
                try: #one line YY MM DD HH
                    dateparse = lambda x: pd.datetime.strptime(x, '%y %m %d %H')
                    df = pd.read_csv('csv/'+filename, parse_dates=[[dataframe.columns[0],dataframe.columns[1],dataframe.columns[2],dataframe.columns[3]]],date_parser=dateparse)
                except:
                    pass
                try:
                    df.pop('mm')
                except:
                    pass

                    df = df.replace(to_replace=9,value='nan')
                    df = df.replace(99,'nan')
                    df = df.replace(99.00,'nan')
                    df = df.replace(999,'nan')
                    df = df.replace(9999,'nan')
                while True:
                    plotvariable = str(input("What would you like to plot? (wave height,barometric pressure,wind speed or none): "))
                    x = df[[df.columns[0]]]
                    if plotvariable == "wave height" :
                        try:
                            WVHT = df.WVHT
                            plt.plot(x,WVHT)
                            plt.show()
                            break
                        except:
                            "Wave height not available for this data."
                    elif plotvariable == "barometric pressure":
                        try:
                            BAR = df.BAR
                            plt.plot(x,BAR)
                            plt.show()
                            break
                        except:
                            "Barometric pressure not available for this data."
                    elif plotvariable == "wind speed":
                        try:
                            WSPD = df.WSPD
                            plt.plot(x,WSPD)
                            plt.show()
                            break
                        except:
                            "Wind speed not available for this data."
                    elif plotvariable == "none":
                        break
                    else:
                        print("Invalid plot selection.")
        except:
            print("Invalid filename")



def main():
    count = 0

    stationcount = int(input('How many stations/years? '))

    stationid_list, startdate_list, enddate_list, datatype_list, urldata_list = data_select(stationcount)

    data_pull("data.json")

    graph()


main()
