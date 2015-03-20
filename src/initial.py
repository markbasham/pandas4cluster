'''
Created on 20 Mar 2015

@author: ssg37927
'''

# needs %pylab

import pandas as pd
import logging

data = pd.read_csv('C:\\Users\\ssg37927\\Desktop\\ubmod_qacct_info.csv', sep='\t')

for times in ['submission_time', 'start_time', 'end_time']:
    try :
        data[times] = data[times].astype('datetime64[s]')
    except :
        logging.warn("Could not convert %s", times)

data.index = data.pop('submission_time')

monthly_cpu_usage = data.cpu.resample('M', how=['sum'])
monthly_cpu_usage.tail(23).plot()

project_info = data.groupby('project').sum()
project_info.plot()

data.index.year == 2015
