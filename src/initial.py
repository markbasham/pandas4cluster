'''
Created on 20 Mar 2015

@author: ssg37927
'''

# needs %pylab

import numpy as np
import pandas as pd
import logging

data = pd.read_csv('C:\\Users\\ssg37927\\Desktop\\ubmod_qacct_info.csv', sep='\t')

for times in ['submission_time', 'start_time', 'end_time']:
    try :
        data[times] = data[times].astype('datetime64[s]')
    except :
        logging.warn("Could not convert %s", times)

data.index = data.pop('submission_time')

# Some info
data['util'] = data['cpu']/(data['ru_wallclock']*data['slots'])
data['util'][data['util'] == inf] = np.NaN
a = data['util'].hist(bins=500)
a.set_yscale('log')


monthly_cpu_usage = data.cpu.resample('M', how=['sum'])
monthly_cpu_usage.tail(23).plot()

project_info = data.groupby(['project', lambda x: "%04i-%02i" % (x.year, x.month)]).sum()

# cpu
dd = project_info['cpu'].unstack(0).tail(-1).fillna(0)
dd.to_csv('cpu_usage_all.csv')
dd.pop('dls')

dd['MX'] = dd.pop('i02') + dd.pop('i03') + dd.pop('i04') + dd.pop('i04-1') + dd.pop('i24') + dd.pop('external')
dd['Tomography'] = dd.pop('i12') + dd.pop('i13') + dd.pop('imagej') + dd.pop('tomography') + dd.pop('tomography_external')
dd['Scattering'] = dd.pop('i11') + dd.pop('i11-1') + dd.pop('i16') + dd.pop('i22') + dd.pop('ncd_auto') + dd.pop('b21')
dd['Systems'] = dd.pop('dls_sysadmin') + dd.pop('p45')
dd.to_csv('cpu_usage_sections.csv')

axis = dd.plot(kind='bar', stacked=True, colormap='terrain', title="Cluster CPU usage per Month per Project")
axis.set_ylabel("Total CPU usage (Seconds x 10 ^ 7)")

fig = axis.get_figure()
fig.set_figwidth(16)
fig.set_figheight(12)
fig.canvas.draw()
fig.savefig("cpu_usage.png")


# walclock
dd = project_info['ru_wallclock'].unstack(0).tail(-1).fillna(0)
dd.to_csv('wallclock_all.csv')
dd.pop('dls')

dd['MX'] = dd.pop('i02') + dd.pop('i03') + dd.pop('i04') + dd.pop('i04-1') + dd.pop('i24') + dd.pop('external')
dd['Tomography'] = dd.pop('i12') + dd.pop('i13') + dd.pop('imagej') + dd.pop('tomography') + dd.pop('tomography_external')
dd['Scattering'] = dd.pop('i11') + dd.pop('i11-1') + dd.pop('i16') + dd.pop('i22') + dd.pop('ncd_auto') + dd.pop('b21')
dd['Systems'] = dd.pop('dls_sysadmin') + dd.pop('p45')
dd.to_csv('wallclock_sections.csv')

axis = dd.plot(kind='bar', stacked=True, colormap='terrain', title="Cluster Wall Time per Month per Project")
axis.set_ylabel("Total Walltime (Seconds x 10 ^ 7)")
fig = axis.get_figure()
fig.set_figwidth(16)
fig.set_figheight(12)
fig.canvas.draw()
fig.savefig("Walltime.png")
