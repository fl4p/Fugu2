To measure high voltages, we use two resistor to form a voltage divider.
Parallel to the lower resistor we add a capacitor, which serves two purposes:

1. Buffering ADC input. Filter capacitance should be much higher than ADC input capacitance.
2. RC low-pass to filter aliasing frequencies

We can compute the cut-off frequency of the "filtered voltage divider" with $f_c = \frac{1}{2\pi * (R_1//R_2) * C_1}$
and with $R2 << R1$ it is simply $f_c = \frac{1}{2\pi * R_2 * C_1}$

Let's use some real values:


We chose R1 = 200k and R2 = 7.5k for a max. input voltage of 80V.
With an input capacitor value of 100nF, the cut-off frequency (-3dB = 0.5 attenuation) will be 212 Hz .
At 2 kHz, attenuation will be -20dB, which is a factor of 0.01. At 20 kHz, -40dB = 1e-4.

Rise time (10% to 90%) of an RC low-pass is $t_r = RC \cdot 2.2$, so here 1.65 ms.


## Non-linearity
The the ESP-IDF API reference about
the [ESP32-S3 ADC](https://docs.espressif.com/projects/esp-idf/en/v4.4/esp32s3/api-reference/peripherals/adc.html)
mentions some non-linearity at the upper voltage end. We can ignore this, or implement some polynominal curve fit
calibration. We can calibrate each chip individually or use the same coefficients we are chips.
Here we use a voltage range of 0 .. 2.86V and ignore the non-linearity.


## ADC input impedance
$R_1$ should be << $R_{ADC}$.


