#!/usr/bin/env python3
""" This script reads the temperature value from a DS18B20 device connected
to a Rasperry Pi GPIO header and writes the value to a postgresql database.
This script is intended to be called from a cron job.
The Configuration is read from a file called config.json residing in the
scrpits path.
"""

import os
import sys
import time
import datetime

import json
import psycopg2



def read_temp_raw(device_file):
    """ Read the raw lines from DS18B20 and return them as list"""
    with open(device_file, 'r') as sensor_file:
        lines = sensor_file.readlines()
    return lines

def read_temp(device_file):
    """Call read_raw_temp and convert raw lines to a temperature value"""
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines.readtempraw()
    equalspos = lines[1].find('t=')
    if equalspos != -1:
        tempstring = lines[1][equalspos + 2:]
        tempc = round(float(tempstring) / 1000.0, 1)
        return tempc

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

def main():
    """ Main function """
    device_file_raw = '/sys/bus/w1/devices/{}/w1_slave'
    config = read_config_file()

    db_config = config["psql"]
    sensors = config["sensors"]
    sensor_values = {}

    for sensor_id, sensor_serial_no in sensors.items():
        device_file = device_file_raw.format(sensor_serial_no)
        sensor_values.update({sensor_id: read_temp(device_file)})

    write_to_db(db_config, sensor_values)

if __name__ == '__main__':
    main()

