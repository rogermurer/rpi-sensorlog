#!/usr/bin/env python3
""" This script reads value string from an usb-wde1 device (www.elv.de).
The usb-wde1 device can read different sensors and returns the values in a
csv-string.
pyserial is used to read from the usb-port and must therefore be installed.
The configuration is read from a file called config.json residing in the
scrpits path. A config-dist.jason is provided, copy it to config.json and
modify it as needed.
This script is intended to be called from a cron job.
"""

import os
import sys
import datetime

import json
import serial
import psycopg2

def open_db(db_name, user, host, port, pwd):
    """Try to open a connection to postgresql and return connection object"""
    connstring = "dbname='{}' user='{}' host='{}' port='{}' password='{}'"
    try:
        conn = psycopg2.connect(connstring.format(db_name,
                                                  user, host,
                                                  port, pwd))
    except psycopg2.OperationalError as error_string:
        print('Unable to connect!\n{}').format(error_string)
        sys.exit(1)
    return conn

def write_to_db(db_conf, sensor_values):
    """Insert sensor values into sensor_values table"""
    db_conn = open_db(db_conf["db"], db_conf["user"],
                      db_conf["host"], db_conf["prt"], db_conf["pwd"])

    sql_str = "INSERT INTO sensor_values (device_id,log_value,log_time) VALUES (%s,%s,%s)"

    cur = db_conn.cursor()
    for sensor_id, sensor_value in sensor_values.items():
        cur.execute(sql_str, (sensor_id, sensor_value, datetime.datetime.now()))

    db_conn.commit()
    cur.close()    
    db_conn.close()

def read_config_file():
    """read the config from json file"""
    conf_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')

    with open(conf_file) as json_conf:
        config = json.load(json_conf)

    return config

def line_is_valid(csv_line):
    """Checks if the USB-WDE1 line is in a valid format"""
    csv_line = csv_line.strip()
    fields = csv_line.split(';')
    valid = (len(fields) == 25 and fields[0] == u'$1' and fields[24] == u'0')
    return valid

def get_wde1_value_line(serial_port):
    """try to read sensors values from usb-wde1 dongle"""
    is_valid = False

    with serial.Serial(serial_port, 9600, timeout=180) as ser:
        try:
            ser.isOpen()
        except:
            sys.exit(1)

        if ser.isOpen():
            try:
                while is_valid != True:
                    line = ser.readline()
                    line = line.decode('utf-8')
                    is_valid = line_is_valid(line)
            except Exception:
                sys.exit(1)

        if is_valid != True:
            line = ''
        return line

def main():
    """Main routine to read sensor data and write the values to the database"""

    config = read_config_file()
    db_config = config["psql"]
    sensors = config["sensors"]
    usb_port = config["misc"]["usb-port"]
    sensor_values = {}

    value_line = get_wde1_value_line(usb_port)
    if value_line != '':
        data = value_line.split(';')
        for sensor, sensor_setting in sensors.items():
            if int(sensor_setting["enabled"]) == 1:
                val = float(data[int(sensor_setting["csv-id"])].replace(',', '.'))
                sensor_values.update({sensor_setting["db-id"]: round(val, 1)})

        write_to_db(db_config, sensor_values)

if __name__ == '__main__':
    main()
