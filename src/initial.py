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

project_info = data.groupby(['project', lambda x: "%04i-%02i" % (x.year, x.month)]).sum()
dd = project_info['cpu'].unstack(0).tail(-1).fillna(0)
dd.pop('dls')

dd['MX'] = dd.pop('i02') + dd.pop('i03') + dd.pop('i04') + dd.pop('i04-1') + dd.pop('i24') + dd.pop('external')
dd['Tomography'] = dd.pop('i12') + dd.pop('i13') + dd.pop('imagej') + dd.pop('tomography') + dd.pop('tomography_external')
dd['Scattering'] = dd.pop('i11') + dd.pop('i11-1') + dd.pop('i16') + dd.pop('i22') + dd.pop('ncd_auto') + dd.pop('b21')
dd['Systems'] = dd.pop('dls_sysadmin') + dd.pop('p45')

axis = dd.plot(kind='bar', stacked=True, colormap='terrain', title="Cluster CPU usage per month per Project")
axis.set_ylabel("Total CPU usage (Seconds x 10 ^ 7)")

