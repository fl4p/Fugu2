running fine with 2p solar panels at 27V bat voltage
then changed to 2s and after sweep heard the fuse burn. this is the last log:
```
I (7641925) mppt: Start sweep
I (7641925) mppt: Start calibration
I (7641926) sensor: U_in_raw reset calibration
I (7641926) sensor: Ii reset calibration
I (7641926) sensor: U_out_raw reset calibration
I (7641926) sensor: NTC reset calibration
E (7641972) sampler: Calibration failed, Ii stddev -0.743303 > 0.100000 (last=-0.292657, avg=-0.331661)
W (7641972) sampler: Ii last=-0.292657 med3=-0.334465 avg=-0.331661 num=60
V=77.4/27.2 I=-0.34/-0.90A -26.2W 43℃35℃ 1430947082sps  0㎅/s PWM(H|L|Lm)=   0|   0| 123 st=↑MPPT,0 lag=63275㎲ N=3015 rssi=-67
I (7645973) mppt: Start sweep
I (7645973) mppt: Start calibration
I (7646019) sampler: Sensor U_out_raw calibration: avg=27.2535 std=0.000000
I (7646020) sampler: Sensor NTC calibration: avg=2.6454 std=0.000001
I (7646020) sampler: Sensor U_in_raw calibration: avg=77.7054 std=0.000000
I (7646020) sampler: Sensor Ii calibration: avg=-0.3433 std=0.002150
I (7646020) sampler: Sensor Ii midpoint-calibrated: -0.343344
I (7646020) sampler: Calibration done!
W (7646021) mppt: Control value nan not finite act=nan tgt=20.000 idx=2
W (7646022) mppt: Control value nan not finite act=nan tgt=25.000 idx=3
W (7646022) mppt: Control value nan not finite act=nan tgt=800.000 idx=4
V=77.7/27.2 I=0.00/0.00A   0.3W 43℃35℃ 1431602806sps  0㎅/s PWM(H|L|Lm)=  90| 123| 123 st=SWEEP,1 lag=63275㎲ N=1624 rssi=-68
V=77.5/27.2 I=0.07/0.18A   5.6W 43℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 235| 123| 232 st=SWEEP,1 lag=63275㎲ N=5475 rssi=-67
(3355963202): Current above threshold 0.20
(3355963476): Back-flow switch enabled
(3355963533): Low-side switch enabled
V=77.0/27.2 I=0.35/0.95A  26.7W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 380| 376| 376 st=SWEEP,1 lag=63275㎲ N=9325 rssi=-67
V=76.7/27.3 I=0.70/1.92A  53.8W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 525| 519| 519 st=SWEEP,1 lag=63275㎲ N=13173 rssi=-66
V=76.3/27.3 I=1.08/2.93A  82.1W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 670| 663| 663 st=SWEEP,1 lag=63275㎲ N=17023 rssi=-67
(3365689673): buck: DCM -> CCM (vr=0.3608, pwmMaxLs=1279.1, lsCCM=1279)

V=73.6/27.6 I=3.34/8.69A 245.9W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 814|1036|1220 st=SWEEP,1 lag=63275㎲ N=20872 rssi=-67
V=62.9/28.0 I=8.09/17.6A 508.8W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)= 959|1077|1077 st=SWEEP,1 lag=63275㎲ N=24724 rssi=-70
V=54.2/27.8 I=8.71/16.5A 472.3W 44℃35℃ 1278sps  0㎅/s PWM(H|L|Lm)=1104| 933| 933 st=SWEEP,1 lag=63275㎲ N=28571 rssi=-67
I (7668949) mppt: Stop sweep after 22.93s at controlMode=CV (limIdx=1) PWM=1132, MPP=(516.6W,PWM=935,65.0V)
I (7668955) mppt: Grouping 148 V points (52.44,463.03)~(77.71,nan) into 100 bins, binW=0.253
512 ┤               ╭─╮╭╮╭─╮╭─────────────────────────────╮                              ????480 ┼───────────────╯ ╰╯╰╯ ╰╯                             ╰───╮╭╮                        ????449 ┤                                                         ╰╯╰───────╮                                
418 ┤                                                                   ╰─╮                              
386 ┤                                                                     ╰──╮                           
355 ┤                                                                        ╰─╮                         
323 ┤                                                                          ╰──╮                      
292 ┤                                                                             ╰──╮╭╮                 
260 ┤                                                                                ╰╯╰╮                
229 ┤                                                                                   ╰─╮              
197 ┤                                                                                     ╰╮╭╮           
166 ┤                                                                                      ╰╯╰╮╭╮        
135 ┤                                                                                         ╰╯╰─╮      
103 ┤                                                                                             ╰╮     
 72 ┤                                                                                              ╰─╮   
 40 ┤                                                                                                ╰╮  
  9 ┼                                                                                                 ╰─ 
  P|V     52.4 .. 77.7



I (7669208) mppt: Grouping 124 D points (0.00,nan)~(0.59,471.91) into 100 bins, binW=0.006
#


Connection closed by foreign host.
(base) fab@MacBook-Pro mcu-head % telnet 192.168.1.208

```