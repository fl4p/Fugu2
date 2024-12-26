import glob
import os
import time

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools
from matplotlib import pyplot as plt

matplotlib.use("macosx")

files = glob.glob("/Volumes/NO NAME/MXO44/Waveforms/*.csv")

latest_fn = sorted(files, key=os.path.getctime, reverse=True)[0]
print(latest_fn)
file_ctime = os.path.getctime(latest_fn)
df = pd.read_csv(latest_fn, header=None)


s = df[50:].astype(float).set_index(0)[1]
dts = set(round(pd.Series(s.index).diff().dropna() * 1e15) * 1e-15)
assert len(dts) == 1
sample_period = next(iter(dts))

print('loaded', len(s), 'samples', 'f=', 1/sample_period*1e-6, 'mhz')

print('autocorr..')
acf= statsmodels.tsa.stattools.acf(s.values, nlags=int(len(s)/2))
#a = np.correlate(s.values,s.values, "same")
print('done.')

# find acf zero-crossing
i = 0
while i < len(acf):
    if acf[i] < 0:
        break
    i+=1


samples_per_sig_period = np.argmax(acf[i:]) + i


print('signal freq', round(1/(samples_per_sig_period * sample_period)))

#
# np.arg

s.plot()
s[s.index[samples_per_sig_period]:].plot()
s.rolling(window=samples_per_sig_period).mean().plot()

i = 0

period_means = []

while i+samples_per_sig_period < len(s):
    m = np.mean(s.values[i:i+samples_per_sig_period])
    period_means.append(m)
    i+=samples_per_sig_period


print('file', latest_fn, 'is', round(time.time() - file_ctime), 's old')
print('Period means:', ', '.join(str(round(m,3)) for m in period_means))

print('Total Mean', round(np.mean(period_means),4), 'std=', round(np.std(period_means), 4))




plt.show()
#pd.Series(a).plot()
#plt.show()
