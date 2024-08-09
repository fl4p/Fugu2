import ltspice
import matplotlib.pyplot as plt
import pandas as pd
import scipy

raw_path = '/Users/fab/Documents/LTspice/buck.raw'

l = ltspice.Ltspice(raw_path)
l.parse()

time = l.get_time()

idx = pd.TimedeltaIndex(time, unit='s')

df = pd.DataFrame(dict(
    Vi=l.get_data('V(vi)'),

    V_gH=l.get_data('V(VgH,Vsw)'),
    V_gL=l.get_data('V(VgL)'),

    I_dH=l.get_data('Ix(u3:1)'),
    I_gH=l.get_data('Ix(u3:2)'),

    V_sw=l.get_data('V(Vsw)'),
    I_dL=l.get_data('Ix(u2:1)'),
    I_gL=l.get_data('Ix(u2:2)'),

    P_LS=l.get_data('V(Vsw)*Ix(u2:1)+V(VgL)*Ix(u2:2)'),

    # V_sw=l.get_data('V(Vsw)'),
), index=idx)

# V(P003)*Ix(U3:D)+V(VgH)*Ix(U3:G)+V(Vsw)*Ix(U3:S)
# df.P_LS.rolling('100us').mean().plot()
# plt.show()

trig = (df.V_gH.rolling('20ns').mean() > 1).astype(int).diff().fillna(0) > 0
# trig = (df.V_gL.rolling('10ns').mean() > 4).astype(int).diff().fillna(0) > 0

trig_time = trig[trig]['4.2ms':].index
# assert len(set(trig_time.diff().dropna())) == 1, set(trig_time.diff().dropna())
tp = trig_time[2] - trig_time[1]

trig_time -= pd.Timedelta('20 ns')

df = (df[trig_time[1]:trig_time[-2]])

P_LS = df.V_sw * df.I_dL + df.V_gL * df.I_gL
P_HS = (df.Vi - df.V_sw) * df.I_dH + df.V_gH * df.I_gH
# the line above is equal to V(Vi)*Ix(U3:D)+V(VgH)*Ix(U3:G)+V(Vsw)*Ix(U3:S)
# P_HS = df.Vi* df.I_dH  + (df.V_gH +df.V_sw)* df.I_gH  + df.V_sw * (-df.I_dH-df.I_gH)


print('period=', round(tp.total_seconds() * 1e6, 2), 'us')
print('fsw=', round(1e-3 / tp.total_seconds(), 2), 'khz')

dt = df.index[-1] - df.index[0]
num_periods = round(dt / tp, 1)

print('integarting over', dt, '=', num_periods, 'periods')


def integrate(s, mask=None):
    if mask is not None:
        s = s.copy()
        s[~mask] = 0
    return scipy.integrate.trapezoid(s.values, s.index.values)


def mean(s, mask=None):
    return integrate(s, mask=mask) / dt


print('P(HS)=', round(mean(P_HS), 2), 'W')
print('P(LS)=', round(mean(P_LS), 2), 'W')

df.loc[:, 'P_LS'] = P_LS

is_shoot = (df.I_dL > 0.5)
print('P(shoot through)=', round(mean(df.Vi * df.I_dL, mask=is_shoot), 2), 'W')

is_ston = P_LS > 0.01 * P_LS.max()  # self turn on
print('  P(self turn-on)=', round(mean(P_LS, mask=is_ston), 2), 'W')

# reverse recovery discharge. the mosfet acts like a capacitor that is discharged -> negative power
is_rr = (P_LS <= 0.001 * P_LS.min()) & (df.I_dL > 0) & (df.V_gL < 3) & (df.V_sw < 0)

print('  P(RR)=', round(mean(df.Vi * df.I_dL, mask=is_rr), 2), 'W')

print('Q_rr=', round(integrate(df.I_dL, mask=is_rr) / pd.Timedelta('1s') / num_periods * 1e9, 2), 'nC')
print('IRM(RR)=', round(df.I_dL[is_rr].max()), 'A')

df.loc[:,'rr'] = is_rr*100

# +HS selfturn on

#df = df[is_ston]
#df = df[is_rr]
#df = df[is_rr]
df = df[is_rr][df.I_dL[is_rr].idxmax()-tp/4000 :df.I_dL[is_rr].idxmax()+ tp/8000 ]


#df = (df[trig_time[2]:trig_time[2] + tp / 100])
# df = (df[trig_time[1]:trig_time[2]]) # 'P_LS',


df[['V_gH', 'V_gL', 'I_dL', 'rr']].set_index((df.index.total_seconds() - df.index[0].total_seconds()) * 1e6).plot()
# plt.grid()


# pd.DataFrame(df.values, index=time)[trig_time[1]:trig_time[2]].plot()
# plt.plot(time, df)
# plt.plot(time, V_cap)
plt.show()
