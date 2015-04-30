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
time_data = pd.to_datetime(pd.Series(timestamps))
data = pd.DataFrame({'time':time_data,
                     'action':pd.Series(actions),
                     'content':pd.Series(content)})


data['users'] = data['content'].str.findall("\w+@\w+").str.get(0)

tmp = data['users'].str.split("@")

data['users'] = tmp.str.get(0)
data['machine'] = tmp.str.get(1)

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

data = data.set_index('time', drop=False)

# get a baseline as there are issues when the server resets sometimes
data['licenses_out'] = (data['licenses_out'] - pd.rolling_min(data['licenses_out'][::-1], 1500)[::-1])

data['licenses_out'].plot()

machines = pd.DataFrame({'time':data.time})
machines = machines.set_index('time')

# specific licences could also be dealt with.
for machine in data['machine'].unique():
    print machine
    mask = data['machine'].values == machine
    machines['%s'%machine] = data['licenses_val'] * 0
    machines['%s'%machine][mask] = data['licenses_val'][mask]
    machines['%s'%machine] = machines['%s'%machine].cumsum()

mask = data.machine.str.contains('^(DIAMR\w\d+|diamr\w\d+|i\d+|cs\d+r|ws\d+|b24)$')
mask = mask.fillna(False)
data['dls_licenses'] = data['licenses_val'] * 0
data['dls_licenses'][mask] = data['licenses_val'][mask]
data['dls_licenses'] = data['dls_licenses'].cumsum()

# normalise in case
data['dls_licenses'] = (data['dls_licenses'] - pd.rolling_min(data['dls_licenses'][::-1], 1500)[::-1])

data['dls_licenses'].plot()

# should resample and plot as a bar chart.
lic_bar = pd.DataFrame({'time':time_data, 'all':data.licenses_out.values, 'dls':data.dls_licenses.values})
lic_bar = lic_bar.set_index('time')

fig = lic_bar.resample('M', how='max').plot(kind='bar')
