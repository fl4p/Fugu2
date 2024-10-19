
Mounting the ESP32-S3 on a small break out enables easy replacement.
We can choose another chip with a different footprint.
MCU specific interfaces (USB etc) that do not belong to the board
can be moved to that break out.

KiCad SMD 2.54mm pin headers are ordinary 90deg THT headers with the odd pins
twisted. An SMD footprint of such headers can be placed inside the ESP32-S3-WROOM
footprint.
[SMD 2.54mmpin header](https://pt.farnell.com/fischer-elektronik/sl11-smd-062-40s/header-pin-2-54mm-40way/dp/9729046)


# Pin Considerations
check the [ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

* Vcc GND
* EN not normally not needed. The MCU can sleep and wake-up. The EN is just needed for programming
* Some pins have start up glitches (GPIO1-17 low, GPIO18-20 high!). don't use this for pwm signals
  * GPIO >= 21 for outputs
* ADC1 channels are useful (ADC2 conflicts with WiFi)
* SPI native pins?


Rust Dev Board Kicad https://github.com/esp-rs/esp-rust-board/tree/master/hardware/esp-rust-board
Power Supply https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf#cd-pwr-supply
