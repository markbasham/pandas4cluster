'''
Created on 28 Apr 2015

@author: ssg37927
'''
import numpy as np
import pandas as pd
import logging
import os

# get the data locatation
data_loc = os.path.split(os.path.realpath(__file__))[0]
data_loc = os.path.split(data_loc)[0]
data_loc = os.path.join(data_loc, 'data')
data_loc = os.path.join(data_loc, 'mcslmd.log')

f = open(data_loc, 'r')

# need to do a first pass as the formating is nasty
times = []
actions = []
content = []

for line in f.readlines():
    l = line.split()
    if len(l) > 2 and "Socket" not in l[0] and "Communications" not in l[0]:
        times.append(l[0])
        actions.append(l[2])
        content.append(' '.join(l[3:]))
    else :
        print("skipped line '%s'" % line)

f.close()

# No add the date to all the timestamps from the 
timestamps = []
datestring = '5/14/2014'
for i in range(len(times)):
    if "TIMESTAMP" in actions[i]:
        datestring = content[i].split()[0]
    timestamps.append(datestring+' '+times[i])

pdts = pd.Series(timestamps)
pdts = pd.to_datetime(pd.Series(timestamps))

# now build the dataframe
data = pd.DataFrame({'time':pd.to_datetime(pd.Series(timestamps)),
                     'action':pd.Series(actions),
                     'content':pd.Series(content)})


data['users'] = data['content'].str.findall("\w+@\w+").str.get(0)

data['licenses'] = data['content'].str.findall("(\d+ licenses)").str.get(0)

data['licenses_val'] = data['licenses'].str.split().str.get(0)
data['licenses_val']

# this is to deal with Upgrades of the number of licences in use
tmp = data['content'].str.findall("\d+->\d+").str.get(0).str.split('->')
data['from'] = tmp.str.get(0)
data['to'] = tmp.str.get(1)

data = data.convert_objects(convert_numeric=True, convert_dates=True)

# general calculations for all licences

mask = data.action.values == "OUT:"
data['licenses_val'][mask] = data['licenses_val'][mask].fillna(1)

mask = data.action.values == "IN:"
data['licenses_val'][mask] = data['licenses_val'][mask].fillna(1)
data['licenses_val'][mask] = data['licenses_val'][mask] * -1

mask = data.action.values == "UPGRADE:"
data['licenses_val'][mask] = data['to'][mask] - data['from'][mask]

data['licenses_val'] = data['licenses_val'].fillna(0)

data['licenses_out'] = data['licenses_val'].cumsum()

data = data.set_index('time')

# get a baseline as there are issues when the server resets sometimes
data['licenses_out'] = (data['licenses_out'] - pd.rolling_min(data['licenses_out'][::-1], 1500)[::-1])

data['licenses_out'].plot()

# specific licences could also be dealt with.

