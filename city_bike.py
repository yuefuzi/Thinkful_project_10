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

con = lit.connect('city_bike.db')
cur = con.cursor()
with con:
    cur.execute("delete from available_bikes")

for i in range(60):
    
    r = requests.get('https://feeds.citibikenyc.com/stations/stations.json')

    key_list = []
    for station in r.json()['stationBeanList']:
        for k in station.keys():
            if k not in key_list:
                key_list.append(k)
            
    df = json_normalize(r.json()['stationBeanList'])

    df['In_Service'] = df.statusValue.factorize()[0]

      


    station_ids = df['id'].tolist() 
    station_ids = ['_' + str(x) + '_INT' for x in station_ids]

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
    
    time.sleep(60)    
con.close()