import math

import ltspice
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

raw_path = '/Users/fab/Documents/LTspice/buck.raw'

_1ns = pd.to_timedelta('1ns')

def read_dcdc_simulation_out(raw_path):
    l = ltspice.Ltspice(raw_path)
    l.parse()

    time = l.get_time()

    df = pd.DataFrame(dict(
        Vi=l.get_data('V(vi)'),

        V_gH=l.get_data('V(VgH,Vsw)'),
        V_gL=l.get_data('V(VgL)'),

        I_dH=l.get_data('Ix(u1:1)'),
        I_gH=l.get_data('Ix(u1:2)'),

        V_sw=l.get_data('V(Vsw)'),
        I_dL=l.get_data('Ix(u2:1)'),
        I_gL=l.get_data('Ix(u2:2)'),

        P_LS=l.get_data('V(Vsw)*Ix(u2:1)+V(VgL)*Ix(u2:2)'),

        # V_sw=l.get_data('V(Vsw)'),
    ), index=time)
    return df


def analyze_dcdc(df):
    # V(P003)*Ix(U3:D)+V(VgH)*Ix(U3:G)+V(Vsw)*Ix(U3:S)
    # df.P_LS.rolling('100us').mean().plot()
    # plt.show()

    #dft = df.copy()
    #dft.index = pd.to_timedelta(df.index, unit='s')

    trig = (df.V_gH.rolling(20).mean() > 1).astype(int).diff().fillna(0) > 0
    # trig = (df.V_gL.rolling('10ns').mean() > 4).astype(int).diff().fillna(0) > 0

    trig_time = trig[trig][4.2e-3:].index
    # assert len(set(trig_time.diff().dropna())) == 1, set(trig_time.diff().dropna())
    tp = trig_time[2] - trig_time[1]

    trig_time -= 20e-9

    df = (df[trig_time[1]:trig_time[-2]])

    P_LS = df.V_sw * df.I_dL + df.V_gL * df.I_gL
    P_HS = (df.Vi - df.V_sw) * df.I_dH + df.V_gH * df.I_gH

    # the line above is equal to V(Vi)*Ix(U3:D)+V(VgH)*Ix(U3:G)+V(Vsw)*Ix(U3:S)
    # P_HS = df.Vi* df.I_dH  + (df.V_gH +df.V_sw)* df.I_gH  + df.V_sw * (-df.I_dH-df.I_gH)

    def pulse_analysis(s: pd.Series, low, high):
        # TODO https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks

        state = (s >= high).astype(int).values - (s <= low).astype(int).values
        t = s.index.values

        rise_times = []
        fall_times = []
        on_times = []
        off_times = []

        tt = t[0]
        for i in range(1, len(t)):
            if state[i - 1] != state[i]:
                if state[i] == 0:
                    tt = t[i]
                elif state[i] == 1:
                    rise_times.append(t[i] - tt)
                else:
                    fall_times.append(t[i] - tt)

        assert np.std(rise_times) / (np.mean(rise_times) + 5) < 0.1
        assert np.std(fall_times) / (np.mean(fall_times) + 5) < 0.1
        assert 0.1 < np.mean(rise_times) / np.mean(fall_times) < 2

        return dict(
            tRise=np.mean(rise_times),
            tFall=np.mean(fall_times),
        )

    print('period=', round(tp * 1e6, 2), 'us')
    print('fsw=', round(1e-3 / tp, 2), 'khz')

    t_sw = pulse_analysis(df.V_sw, low=df.Vi * 0.05, high=df.Vi * 0.95)
    print('tRise_sw', round(t_sw['tRise'] * 1e9, 1), 'ns') #, '(dv/dt=%.2fkV/s)' % (df.Vi.mean()/t_sw['tRise']/1000))
    print('tFall_sw', round(t_sw['tFall'] * 1e9, 1), 'ns')

    dt = df.index[-1] - df.index[0]
    num_periods = round(dt / tp, 1)

    print('integrating over', dt, '=', num_periods, 'periods')

    def integrate(s, mask=None):
        if mask is not None:
            s = s.copy()
            s[~mask] = 0
        return scipy.integrate.trapezoid(s.values, s.index.values)

    def mean(s, mask=None):
        return integrate(s, mask=mask) / dt

    print('P(HS)=', round(mean(P_HS), 2), 'W')
    print('P(LS)=', round(mean(P_LS), 2), 'W')
    print('P(HS+LS)=', round(mean(P_HS) + mean(P_LS), 1), 'W')

    df.loc[:, 'P_LS'] = P_LS

    is_shoot = (df.I_dL > 0.5)
    print('P(shoot through)=', round(mean(df.Vi * df.I_dL, mask=is_shoot), 2), 'W')

    is_ston = P_LS > 0.01 * P_LS.max()  # self turn on
    print('  P(self turn-on)=', round(mean(P_LS, mask=is_ston), 2), 'W')

    # reverse recovery discharge. the mosfet acts like a capacitor that is discharged -> negative power
    # see https://www.onsemi.com/download/application-notes/pdf/an-9010.pdf#page=15
    is_rr = (df.I_dL > 0) #& (df.V_gL < 2) #& (P_LS < 0) #&  & (df.V_sw < 0)
    is_rr = is_rr & (df.I_dL > .01 * df.I_dL[is_rr].max())

    I_RM = df.I_dL[is_rr].max()
    df.I_dL.groupby(pd.Grouper(freq='W')).sum()

    print('  P(RR)=', round(mean(df.Vi * df.I_dL, mask=is_rr), 2), 'W')

    #t_rr = pulse_analysis(df.I_dL, low=I_RM*0.1, high=I_RM * 0.9)

    print('Q_rr=', round(integrate(df.I_dL, mask=is_rr) / num_periods * 1e9, 2), 'nC')
    print('IRM(RR)=', round(I_RM), 'A')

    df.loc[:, 'rr'] = is_rr * 20

    # +HS selfturn on

    # df = df[is_ston]
    # df = df[is_rr]
    # df = df[is_rr]
    #df = df[is_rr][df.I_dL[is_rr].idxmax() - tp / 4000:df.I_dL[is_rr].idxmax() + tp / 8000]

    # df = (df[trig_time[2]:trig_time[2] + tp / 100])
    # df = (df[trig_time[1]:trig_time[2]]) # 'P_LS',

    def apply_mask(s, mask, value=0):
        mask = mask[s.index[0]:s.index[-1]]
        s = s.copy()
        s[~mask] = value
        return s

    def _plot(d, mask=None, **kwargs):
        if mask is not None:
            d = apply_mask(d, mask, value=math.nan)
        d = d.set_index((d.index - d.index[0]) * 1e9)
        d.plot(**kwargs)

    is_rr[is_rr].index[0]
    _plot(df[['V_gH', 'V_gL', 'I_dL', 'rr']][is_rr[is_rr].index[0]:is_rr[is_rr].index[0]+20e-9])
    plt.title('reverse recovery')


    t0 =  df.I_dL[is_rr].idxmax()
    print('IRM at', t0)
    _plot(df[['V_gH', 'V_gL', 'I_dL', 'rr']][t0-50e-9:t0 + 50e-9], mask=is_rr)
    plt.title('IRM')


    plt.figure()
    t0 = is_rr[is_rr].index[0]
    #t0 = is_rr[t0 + 20e-9:][is_rr[t0 + 20e-9:]].index[0]
    _plot(df[['V_gH', 'V_gL', 'I_dL', 'rr']][t0:t0+250e-9] ,mask=is_rr)

    #_plot(df[['V_gH', 'V_gL', 'I_dL', 'rr']])

    # plt.grid()

    # pd.DataFrame(df.values, index=time)[trig_time[1]:trig_time[2]].plot()
    # plt.plot(time, df)
    # plt.plot(time, V_cap)
    plt.show()


def run_ltspice(asc_path):
    from PyLTSpice import SimRunner, SpiceEditor, LTspice

    runner = SimRunner(output_folder='./lt-spice-out', simulator=LTspice)  # Configures the simulator to use and output
    # folder

    from PyLTSpice import SimCommander
    LTC = SimCommander(asc_path)
    netlist = SpiceEditor(asc_path, encoding='cp1252')  # Open the Spice Model, and creates the .net
    # set default arguments
    # netlist.set_parameters(res=0, cap=100e-6)
    # netlist.set_component_value('R2', '2k')  # Modifying the value of a resistor
    # netlist.set_component_value('R1', '4k')
    # netlist.set_element_model('V3', "SINE(0 1 3k 0 0 0)")  # Modifying the
    # netlist.set_component_value('XU1:C2', 20e-12)  # modifying a
    # define simulation
    netlist.add_instructions(
        "; Simulation settings",
        ".param run = 0"
    )

    # for opamp in ('AD712', 'AD820'):
    #    netlist.set_element_model('XU1', opamp)
    #    for supply_voltage in (5, 10, 15):
    #        netlist.set_component_value('V1', supply_voltage)
    ##        netlist.set_component_value('V2', -supply_voltage)
    #        # overriding he automatic netlist naming
    #        run_netlist_file = "{}_{}_{}.net".format(netlist.netlist_file.name, opamp, supply_voltage)
    #        raw, log = runner.run_now(netlist, run_filename=run_netlist_file)
    # Process here the simulation results

    run_netlist_file = "{}_.net".format(netlist.netlist_file.name)  # , opamp, supply_voltage)
    raw, log = runner.run_now(netlist, run_filename=run_netlist_file)


if __name__ == '__main__':
    matplotlib.use("macosx")

    df = read_dcdc_simulation_out(raw_path)

    #run_ltspice('/Users/fab/Documents/LTspice/buck.asc')

    analyze_dcdc(df)
