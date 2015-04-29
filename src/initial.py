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
data['util'][data['util'] == np.inf] = np.NaN
a = data['util'].hist(bins=500)
#a.set_yscale('log')

# Find out what jobs are in DLS
jn = pd.DataFrame(data['job_name'][data['project']=='dls'])
jn = jn.reset_index()
jn.pop('submission_time')
jnh = jn.apply(pd.value_counts)

mx_filter = data['job_name'].str.contains('forkintegrate_job|i[0,2][2,3,4]-?1?EDNAStrategy.|DIALS')
print mx_filter.sum()
data['project'][mx_filter] = 'dls_mx'

tomo_filter = data['job_name'].str.contains('run_slices.sh|dovslice_q|run_nxs2tiff.sh|chunk|run_compress.sh')
print tomo_filter.sum()
data['project'][tomo_filter] = 'dls_tomo'


# remap them to something beter




# fij = data['project'][data['job_name'] == 'forkintegrate_job']
# fij = fij.reset_index()
# fij.pop('submission_time')
# fijh = fij.apply(pd.value_counts)
# fijh

#job_name_histo = data['job_name'].apply(pd.value_counts)


#monthly_cpu_usage = data.cpu.resample('M', how=['sum'])
#monthly_cpu_usage.tail(23).plot()

project_info = data.groupby(['project', lambda x: "%04i-%02i" % (x.year, x.month)]).sum()

# cpu
dd = project_info['cpu'].unstack(0).tail(-1).fillna(0)
dd.to_csv('cpu_usage_all.csv')
dd.pop('dls')

dd['MX'] = dd.pop('i02') + dd.pop('i03') + dd.pop('i04') + dd.pop('i04-1') + dd.pop('i24') + dd.pop('external') + dd.pop('dls_mx')
dd['Tomography'] = dd.pop('i12') + dd.pop('i13') + dd.pop('imagej') + dd.pop('tomography') + dd.pop('tomography_external') + dd.pop('dls_tomo')
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
# dd = project_info['ru_wallclock'].unstack(0).tail(-1).fillna(0)
# dd.to_csv('wallclock_all.csv')
# dd.pop('dls')
# 
# dd['MX'] = dd.pop('i02') + dd.pop('i03') + dd.pop('i04') + dd.pop('i04-1') + dd.pop('i24') + dd.pop('external')
# dd['Tomography'] = dd.pop('i12') + dd.pop('i13') + dd.pop('imagej') + dd.pop('tomography') + dd.pop('tomography_external')
# dd['Scattering'] = dd.pop('i11') + dd.pop('i11-1') + dd.pop('i16') + dd.pop('i22') + dd.pop('ncd_auto') + dd.pop('b21')
# dd['Systems'] = dd.pop('dls_sysadmin') + dd.pop('p45')
# dd.to_csv('wallclock_sections.csv')
# 
# axis = dd.plot(kind='bar', stacked=True, colormap='terrain', title="Cluster Wall Time per Month per Project")
# axis.set_ylabel("Total Walltime (Seconds x 10 ^ 7)")
# fig = axis.get_figure()
# fig.set_figwidth(16)
# fig.set_figheight(12)
# fig.canvas.draw()
# fig.savefig("Walltime.png")
