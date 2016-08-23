# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:01:01 2016

@author: Chang
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from scipy.stats import pearsonr
import numpy as np
import sqlite3 as lit
import time
from dateutil.parser import parse 
import collections

r = requests.get('https://feeds.citibikenyc.com/stations/stations.json')

key_list = []
for station in r.json()['stationBeanList']:
    for k in station.keys():
        if k not in key_list:
            key_list.append(k)
            
df = json_normalize(r.json()['stationBeanList'])

df['In_Service'] = df.statusValue.factorize()[0]

for i in range(len(df.In_Service)):
    if df.In_Service[i]:
        df.In_Service[i] = 0
    else:
        df.In_Service[i] = 1
        
cond = (df.In_Service == 1)
df = df[cond]

con= lit.connect('city_bike.db')

with con:   
    cur = con.cursor()
    cur.execute('''CREATE TABLE citibike_reference (id INT PRIMARY KEY, 
    totalDocks INT, city TEXT, altitude INT, stAddress2 TEXT, longitude NUMERIC, postalCode TEXT, 
    testStation TEXT, stAddress1 TEXT, stationName TEXT, landMark TEXT, latitude NUMERIC, 
    location TEXT )''')

sql = '''INSERT INTO citibike_reference (id, totalDocks, city, altitude, stAddress2, longitude, 
       postalCode, testStation, stAddress1, stationName, landMark, latitude, location) 
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'''

with con:
    cur = con.cursor()
    for station in r.json()['stationBeanList']:
        cur.execute(sql,(station['id'],station['totalDocks'],station['city'],station['altitude'],
                         station['stAddress2'],station['longitude'],station['postalCode'],station['testStation'],
                         station['stAddress1'],station['stationName'],station['landMark'],station['latitude'],
                         station['location']))

station_ids = df['id'].tolist() 
station_ids = ['_' + str(x) + '_INT' for x in station_ids]

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE available_bikes ( execution_time INT, " +  ", ".join(station_ids) + ");")

exec_time = parse(r.json()['executionTime'])
s = exec_time.strftime('%s')

with con:
    cur = con.cursor()
    cur.execute('INSERT INTO available_bikes (execution_time) VALUES ({0})'.format(s))

id_bikes = collections.defaultdict(int)
for k,v in df.iterrows():
    id_bikes[v['id']] = v['availableBikes']

with con:
    for k, v in id_bikes.iteritems():
        cur.execute("UPDATE available_bikes SET _" + str(k) + "_INT = " + str(v) + " WHERE execution_time = " + exec_time.strftime('%s'))
    cur.execute("select * from available_bikes")
    data = cur.fetchall()
    print(data)
        
