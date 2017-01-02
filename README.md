# rpi-sensorlog
My Raspberpi inspired sensors loging to postgresql and monitoring with munin

# Preface
I am a [MS Dynmaics NAV] (https://de.wikipedia.org/wiki/Microsoft_Dynamics_NAV) Developer and a Linux-hobbyist. In Python I am at this time an absolute beginner, also what a beginner what belongs to postgresql.

## Target of this project
I have some Rasperry Pis with sensors such as:

* DS18B20S temperature sensors 
* The [Adafruit BME280] (https://www.adafruit.com/product/2652) temperature, humidity and pressure sensor
* The [Adafruit BMP085/BMP180] (https://www.adafruit.com/product/1603) pressure and temperature sensor
* And finaly a [USB WDE 1 from elv.ch] (http://www.elv.ch/usb-wetterdaten-empfaenger-usb-wde1-komplettbausatz-1.html) which monitors my combi sensors

This sensors are connected to different Rasperry Pis for measuring temperature, humidity around the house and also gathering data from my elv combi sensor in the garden.

I did use some munin plugins on all the different Rasperry Pis. To have all the temperature sensor  values graphed in a single graph, had to push value files over ssh to a single Pi and a plugin reading all those files. Adding more sensors means, pushing more files to the master Pi.
So I decided to let those Pis log into a postgresql database on my server machine and have the munin plugins also on the main server.


## What you need

### General
* [Rasbian] (https://www.raspberrypi.org/downloads/raspbian/) on all Pis (LITE version will do)
* Python3 installed
* For accessing postgresql the python3-psycopg2 package is needed

### Machine with postgresql
* You need to have a machine with postgresql installed
* Create a database (i. e. sensorlog), a user, grant permissions for user
* Grant access to the database to your network
* Use the sensoring_tables.psql SQL-scripts to create the tables and sensor_types
* Create entries for your sensors in the sensor_device tables
After that you shoud be able to setup your loging machines for the different sensors

### Pi with DS18B20S sensor
* Install a DS18B20S sensor ([Adafruit usage instructions] (https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware))
* Copy the 1Wire folder to /usr/local/bin/
* Move or copy the config-dist.json to config.json and fill in the fields
* Create a file in /etc/cron.d/ with the following content:

    */5 * * * * root test -x /usr/local/bin/1Wire/DSTemp2sql.py && /usr/local/bin/1Wire/DSTemp2sql.py

### Pi with BME280 sensor
* Install a BME280 sensor ([Adafruit instructions] (https://github.com/adafruit/Adafruit_Python_BME280))
* Copy the BME280 folder to /usr/local/bin/
* Move or copy the config-dist.json to config.json and fill in the fields
* Create a file in /etc/cron.d/ with the following content:

    */5 * * * * root test -x /usr/local/bin/BME280/BME280Values2sql.py && /usr/local/bin/BME280/BME280Values2sql.py

### Pi with BMP085/BMP180 sensor
* Install a BMP085 or BMP180 sensor ([Adafruit instructions] (https://github.com/adafruit/Adafruit_Python_BMP))
* Copy the BMP085 folder to /usr/local/bin/
* Move or copy the config-dist.json to config.json and fill in the fields
* Create a file in /etc/cron.d/ with the following content:

    */5 * * * * root test -x /usr/local/bin/BMP085/BME085Values2sql.py && /usr/local/bin/BMP085/BMP085Values2sql.py

### Pi or other Linux machine with USB-WDE1 dongle
* Connect the USB-WDE1 dongle to a usb port
* Install python3-serial package
* Copy the WDE1 folder to /usr/local/bin/
* Move or copy the config-dist.json to config.json and fill in the fields
* Create a file in /etc/cron.d/ with the following content:

    */5 * * * * root test -x /usr/local/bin/WDE1/WDE1Values2sql.py && /usr/local/bin/WDE1/WDE1Values2sql.py

### Machine where munin-server is installed
* Copy the Munin folder to /usr/local/bin/
* Move or copy the config-dist.json to config.json and fill in the fields
* Move the plugin files (rpi-sensors-*) to /usr/share/munin/plugins
* In /etc/munin/plugins create symlinks to the plugin files
* Do a restart of the munin-node


Enjoy and use at your own risk ;-)
