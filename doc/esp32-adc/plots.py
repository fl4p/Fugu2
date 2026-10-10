#!/usr/bin/env python3
"""Figures and numbers for doc/ESP32 ADC Calibration.md, from data/*.csv only.

    python3 doc/esp32-adc/plots.py      # numpy, pandas, scipy, matplotlib

data/*.csv come from pwr-metering's esp32-adc-extract.py (needs its influx access). Figures go to
doc/img/esp32-adc-*.png.

Also fits the universal INL correction and prints the coefficients that go into the firmware
(fugu-mppt-firmware src/adc/adc_esp32_cont.cpp, inlDelta()).
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from numpy.polynomial import legendre as L  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RL = 1 / (1 / 7.5e3 + 1 / 500e3)            # firmware adcVDiv: 7.5k parallel the ADC's 500k
K = (200e3 + RL) / RL                        # bus volts per pin volt, both boards
LSB = 3100 / 4095                            # ~mV per code at 12 dB
BIAS = 0.5 * LSB * 31 / 32                 # old path floored the avg of 32 codes; the new one does not
BOARDS = ('fboost', 'fmetal')
COL = {'fboost': 'C0', 'fmetal': 'C1'}

d = pd.read_csv(os.path.join(HERE, 'data/dense.csv'))
h = pd.read_csv(os.path.join(HERE, 'data/aug_hp.csv'))
run1 = d.run == '2026-10-09T22-23-51Z'


def board(name, df=d):
    g = df.dropna(subset=[name])
    return g[(g[name] - g.U).abs() < 1.5].sort_values('U')


def rms(e):
    return np.sqrt(np.mean(np.square(e)))


def line_resid(x, y):
    return y - np.polyval(np.polyfit(x, y, 1), x)


def save(fig, name):
    name = 'esp32-adc-' + name.replace('.png', '.webp')
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, '..', 'img', name), dpi=110, pil_kwargs={'lossless': True})
    plt.close(fig)
    print('wrote', name)


out = {}

# ---------------------------------------------------------------- 1. the reference
hh = h[(h.HP > 10) & (h.HP < 90)].dropna(subset=['U2'])
e = line_resid(hh.HP.values, hh.U2.values)
out['ref'] = (len(hh), rms(e) * 1e3, abs(e).max() * 1e3)
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(hh.HP, e * 1e3, '.', color='C2', ms=4)
ax.set(xlabel='HP3458A [V]', ylabel='INA228_2 INL vs HP3458A [mV]',
       title='The reference: INA228_2 against the HP3458A, %d rungs (Aug 2026)' % len(hh))
ax.set_ylim(-250, 250); ax.grid(alpha=.3)
ax.text(.01, .93, 'rms %.2f mV, peak %.2f mV -- on the scale of the plots that follow, flat'
        % out['ref'][1:], transform=ax.transAxes, fontsize=9)
save(fig, 'reference.png')

# ---------------------------------------------------------------- 2. raw error, both boards
fig, ax = plt.subplots(figsize=(9, 4.2))
ga = board('fboost', h.rename(columns={'U2': 'U'}))
ax.plot(ga.HP, (ga.fboost - ga.HP) * 1e3, '.', color='0.65', ms=4, label='fboost vs HP3458A (Aug)')
for b in BOARDS:
    g = board(b)
    ax.plot(g.U, (g[b] - g.U) * 1e3, '.', color=COL[b], ms=4, label='%s vs INA228_2 (Oct, dense)' % b)
ax.set(xlabel='node voltage [V]', ylabel='reading - reference [mV]',
       title='Raw error of the ESP32-S3 ADC1 voltage reading (IDF curve-fitting calibration)')
ax.grid(alpha=.3); ax.legend(fontsize=8)
save(fig, 'raw-error.png')

# ---------------------------------------------------------------- 3. INL: the shared S-curve
fig, ax = plt.subplots(figsize=(9, 4.2))
e = line_resid(ga.HP.values, ga.fboost.values)
ax.plot(ga.HP, e * 1e3, '.', color='0.65', ms=4, label='fboost vs HP3458A (Aug), rms %.0f mV' % (rms(e) * 1e3))
out['inl_aug'] = rms(e) * 1e3
for b in BOARDS:
    g = board(b)
    e = line_resid(g.U.values, g[b].values)
    out['inl_' + b] = (rms(e) * 1e3, abs(e).max() * 1e3, len(g))
    ax.plot(g.U, e * 1e3, '.', color=COL[b], ms=4, label='%s (Oct), rms %.0f mV' % (b, rms(e) * 1e3))
ax.set(xlabel='node voltage [V]', ylabel='INL vs own best line [mV]',
       title='Same S-curve on both boards, and on fboost two months apart')
ax.grid(alpha=.3); ax.legend(fontsize=8)
save(fig, 'inl.png')

# ---------------------------------------------------------------- 4. repeatability across runs
fig, ax = plt.subplots(figsize=(9, 4.2))
g = board('fboost')
co = np.polyfit(g.U[run1[g.index]], g.fboost[run1[g.index]], 1)
for i, (run, gg) in enumerate(g.groupby('run')):
    ax.plot(gg.U, (gg.fboost - np.polyval(co, gg.U)) * 1e3, 'o' if i == 0 else 'x', ms=4,
            label='run %s (%d rungs)' % (run[5:16].replace('T', ' '), len(gg)))
ax.set(xlabel='node voltage [V]', ylabel='fboost INL vs run-1 line [mV]',
       title='fboost: four runs over 3 h fall on the same curve')
ax.grid(alpha=.3); ax.legend(fontsize=8)
save(fig, 'repeat.png')
a = g[run1[g.index]].set_index('count').fboost - np.polyval(co, g[run1[g.index]].set_index('count').U)
r5 = g[g.run == '2026-10-10T00-29-42Z'].set_index('count')
b5 = r5.fboost - np.polyval(co, r5.U)
j = pd.concat([a, b5], axis=1, keys=['a', 'b']).dropna()
pa = np.polynomial.Polynomial.fit(g.U[run1[g.index]], g.fboost[run1[g.index]], 5)
ra = (g[run1[g.index]].set_index('count').fboost - pa(g[run1[g.index]].set_index('count').U))
rb = r5.fboost - pa(r5.U)
jj = pd.concat([ra, rb], axis=1, keys=['a', 'b']).dropna()
out['repeat'] = (len(j), np.corrcoef(jj.a, jj.b)[0, 1], rms(jj.a - jj.b) / np.sqrt(2) * 1e3)

# ---------------------------------------------------------------- 5. universal fit
data = []
for b in BOARDS:
    g = board(b)
    data.append((g[b].values / K * 1e3 + BIAS, g.U.values / K * 1e3))   # pin mV: reading, truth
amin = min(x.min() for x, _ in data); amax = max(x.max() for x, _ in data)
MID, HALF = round((amax + amin) / 2), round((amax - amin) / 2)


TAPER = 0.25                                 # firmware kTaper: edge value fades to 0 over 261 mV


def dfun(c, a):
    x = (np.asarray(a, float) - MID) / HALF
    w = np.clip(1 - (np.abs(x) - 1) / TAPER, 0, 1)
    return L.legval(np.clip(x, -1, 1), np.r_[0, 0, c]) * np.where(np.abs(x) > 1, w, 1)


def resid(p, sets):
    return np.concatenate([p[4 + 2 * i] * (a + dfun(p[:4], a)) + p[5 + 2 * i] - u
                           for i, (a, u) in enumerate(sets)])


p = least_squares(resid, np.r_[np.zeros(4), [1, 0] * 2], args=(data,)).x
power = L.leg2poly(np.r_[0, 0, p[:4]])
out['fit'] = (MID, HALF, power, [(p[4 + 2 * i], p[5 + 2 * i] * K / 1e3) for i in range(2)])

fig, ax = plt.subplots(figsize=(9, 4.2))
for i, b in enumerate(BOARDS):
    a, u = data[i]
    g_, o_ = p[4 + 2 * i:6 + 2 * i]
    ax.plot(a, (u - o_) / g_ - a, '.', color=COL[b], ms=4, label='%s, after its own gain/offset' % b)
xs = np.linspace(amin - 300, amax + 300, 400)
ax.plot(xs, dfun(p[:4], xs), 'k-', lw=2, label='universal correction d(mV), tapered to 0 outside the fit range')
ax.axvspan(amin, amax, color='0.9', zorder=0)
ax.set(xlabel='ADC pin voltage [mV]', ylabel='correction [mV at the pin]',
       title='The universal correction: Legendre P2..P5, no gain or offset of its own')
ax.grid(alpha=.3); ax.legend(fontsize=8)
save(fig, 'correction.png')

# ---------------------------------------------------------------- 6. after correction, cross-board
fig, axs = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
out['xfer'] = {}
for hold, ax in zip((0, 1), axs):
    other = 1 - hold
    q = least_squares(resid, np.r_[np.zeros(4), 1, 0], args=([data[other]],)).x
    a, u = data[hold]
    x = a + dfun(q[:4], a)
    U = u * K / 1e3
    lo, hi = np.abs(U - 25).argmin(), np.abs(U - 65).argmin()        # 2-point calibration
    gg = (u[hi] - u[lo]) / (x[hi] - x[lo]); oo = u[lo] - gg * x[lo]
    e_cal = (gg * x + oo - u) * K / 1e3
    e_line = line_resid(a, u) * K / 1e3 * -1
    out['xfer'][BOARDS[hold]] = (BOARDS[other], rms(e_line) * 1e3, abs(e_line).max() * 1e3,
                                 rms(e_cal) * 1e3, abs(e_cal).max() * 1e3)
    ax.plot(U, e_line * 1e3, '.', color='0.65', ms=4,
            label='gain + offset only: rms %.0f mV' % (rms(e_line) * 1e3))
    ax.plot(U, e_cal * 1e3, '.', color=COL[BOARDS[hold]], ms=4,
            label="%s's curve + 2-point cal at 25/65 V: rms %.0f mV" % (BOARDS[other], rms(e_cal) * 1e3))
    ax.set_ylabel('%s error [mV]' % BOARDS[hold]); ax.grid(alpha=.3); ax.legend(fontsize=8)
axs[0].set_title("Corrected with the OTHER board's curve and a two-point calibration")
axs[1].set_xlabel('node voltage [V]')
save(fig, 'after.png')

# ---------------------------------------------------------------- 7. what IDF already corrects
# IDF 5.5 components/esp_adc/esp32s3/curve_fitting_coefficients.c, ADC1 atten3 (12 dB): the
# second-step error polynomial in first-step mV; IDF subtracts it. adc-cal tables are read back
# from both chips (data/adc-cal-*.txt) and must land on it.
IDF_K = (0.6444034182694780, 0.0644334888647536, 1.297891447611e-4, 7.0769718e-8, 1.3515e-11)
IDF_S = (-1, -1, 1, -1, 1)


def idf_err(v):
    return sum(s * k * v ** i for i, (s, k) in enumerate(zip(IDF_S, IDF_K)))


def adc_cal(b):
    rows = [l.split() for l in open(os.path.join(HERE, 'data/adc-cal-%s.txt' % b))
            if l.startswith('ADCCAL 3 ')]
    return np.array([(float(r[3]), float(r[5])) for r in rows])   # mv_idf, curve_mv


v1 = np.linspace(0, 3420, 800)
mv = v1 - idf_err(v1)                                    # IDF output
idf_curve = -idf_err(v1)                                 # what IDF adds to the first-step line
inr = (mv >= amin) & (mv <= amax)
idf_nl = idf_curve - np.polyval(np.polyfit(mv[inr], idf_curve[inr], 1), mv)
ours = dfun(p[:4], mv)
out['idf'] = {b: np.abs(adc_cal(b)[:, 1] - np.interp(adc_cal(b)[:, 0], mv, idf_curve)).max() for b in BOARDS}
out['idf_nl'] = [(f[inr].min(), f[inr].max()) for f in (idf_nl, ours, idf_nl + ours)]

fig, axs = plt.subplots(2, 1, figsize=(9, 7.5), sharex=True)
ax = axs[0]
ax.plot(mv, idf_curve, '-', color='C0', lw=1.5, label="IDF's fixed curve (same for every ESP32-S3)")
for b, mk in zip(BOARDS, ('o', 'x')):
    t = adc_cal(b)
    ax.plot(t[:, 0], t[:, 1], mk, color=COL[b], ms=6, mfc='none', label='read back with adc-cal from %s' % b)
ax.plot(mv, ours, 'k-', lw=2, label='our universal correction')
ax.axvspan(amin, amax, color='0.92', zorder=0)
ax.set(ylabel='correction added [mV at the pin]',
       title='12 dB: the correction IDF applies, and ours on top of it')
ax.grid(alpha=.3); ax.legend(fontsize=8, loc='lower left')
ax = axs[1]
m = (mv >= amin - 150) & (mv <= amax + 150)
ax.plot(mv[m], idf_nl[m], '-', color='C0', lw=1.5, label="IDF's curve, gain/offset removed over the measured range")
ax.plot(mv[m], ours[m], 'k-', lw=2, label='our universal correction')
ax.plot(mv[m], idf_nl[m] + ours[m], '--', color='C2', lw=1.5, label='total that these chips need (IDF + ours)')
ax.axvspan(amin, amax, color='0.92', zorder=0)
ax.set(xlabel='ADC pin voltage (IDF output) [mV]', ylabel='curvature [mV at the pin]')
ax.grid(alpha=.3); ax.legend(fontsize=8, loc='lower left')
save(fig, 'idf-curve.png')

# ---------------------------------------------------------------- numbers for the text
print('\nreference: n=%d INL rms %.2f mV, peak %.2f mV' % out['ref'])
print('fboost vs HP (Aug): INL rms %.0f mV' % out['inl_aug'])
for b in BOARDS:
    print('%s dense: INL rms %.0f, peak %.0f mV over %d rungs' % ((b,) + out['inl_' + b]))
print('repeat (fboost run1 vs run5): %d rungs, per-rung residual corr %.2f, rms diff/sqrt2 %.1f mV' % out['repeat'])
MID, HALF, power, go = out['fit']
print('fit: MID=%d HALF=%d' % (MID, HALF))
print('    c = {%s}' % ', '.join('%.6ff' % v for v in power))
for b, (g_, o_) in zip(BOARDS, go):
    print('    %s: vout_gain=%.6f vout_offset=%+.4f V' % (b, g_, o_))
for b, v in out['xfer'].items():
    print("%s with %s's curve: line %.0f/%.0f -> 2-point %.0f/%.0f mV (rms/max)" % ((b,) + v))
print('adc-cal vs IDF source curve: max deviation %s' % ', '.join('%s %.2f mV' % kv for kv in out['idf'].items()))
print('curvature over the fit range: IDF %.1f..%.1f, ours %.1f..%.1f, total %.1f..%.1f mV' % tuple(
    v for r in out['idf_nl'] for v in r))
