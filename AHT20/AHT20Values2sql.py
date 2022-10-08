#!/usr/bin/env python3
""" This script reads the temperature and humidity values from a RPI Sense Hat
sensor using the Adafruit_BME280 module, which has to reside in the same
directory as this script.
The configuration is read from a file called config.json residing in the
scrpits path. A config-dist.jason is provided, copy it to config.json and
modify it as needed.
This script is intended to be called from a cron job.
"""

import os
import sys
import datetime

import psycopg2
import json
import board
import adafruit_ahtx0

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
    config = read_config_file()
    db_config = config["psql"]
    sensors = config["sensors"]
    sensor_values = {}

    sensor = adafruit_ahtx0.AHTx0(board.I2C())

    for sensor_type, sensor_id in sensors.items():
        temp = sense.get_temperature_from_pressure()
        if sensor_type == "humid":
            raw_value = sensor.relative_humidity()
        elif sensor_type == "temp":
            raw_value = sensor.temperature()
        else:
            break
        sensor_values.update({sensor_id: round(raw_value, 1)})

    write_to_db(db_config, sensor_values)

if __name__ == '__main__':
    main()

