# rpi-sensorlog
My Raspberpi inspired sensors loging to postgresql and monitoring with munin

# Preface
I am a [MS Dynmaics NAV] (https://de.wikipedia.org/wiki/Microsoft_Dynamics_NAV) Developer and a Linux-hobbyist. In Python I am at this time an absolute beginner, also what a beginner what belongs to postgresql.

## Target of this project
I have some Rasperry Pis with sensors such as:

* DS18B20S temperature sensors 
* The [Adafruit BME280] (https://www.adafruit.com/product/2652) temperature, humidity and pressure sensor
* The [Adafruit BMP085/BMP180] (https://www.adafruit.com/product/1603) pressure and temperature sensor
* And finaly a [USB WDE 1 from elv.ch] (http://www.elv.ch/usb-wetterdaten-empfaenger-usb-wde1-komplettbausatz-1.html) which monitors my compi sensors

This sensors are connected to different Rasperry Pis for measuring temperature, humidity around the house and also gathering data from my elv combi sensor in the garden.

I did use some munin plugins on all the different Rasperry Pis. To have all the temperature sensor  values graphed in a single graph, had to push value files over ssh to a single Pi and a plugin reading all those files. Adding more sensors means, pushing more files to the master Pi.
So I decided to let those Pis log into a postgresql database on my server machine and have the munin plugins also on the main server.

This repository shows my attempt on this.
