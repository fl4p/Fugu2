fugu metal in a aluminium case

Input Caps 

left it outisde at night it was raining
suced water inside. found water on the pcb and chips
ESP32 metal shield looks oxidated. Have problems to communicate with INA226 and external IC2 display whic i connected for testing.

Sometimes it worked, sometimes not. I could see the device in the battery current graph turning on and off.

I heated the PCB with a hear dryer for some minutes but it didnt help. Now my idea is to turn on WiFi so the ESP32
generates some heat that will eventually evaporate the water from the inside.
THe only problem was, I didn"t have the right firmware version at hand (my laptop died 2 weeks ago),
so before flashing a new firmware that enables the WiFi hardware, I tried to create a flash dump with esptool.py (read_flash).
That didn't work, it just didn"t start to download after it uploaded the stub.

Next effort: try to run a binary from RAM
https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/advanced-commands.html#load-ram
esptool.py --no-stub load_ram ./test/images/helloworld-esp8266.bin
# validate image with image_info

Then i tried to read 