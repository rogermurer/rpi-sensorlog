#!/usr/bin/env python3
""" This script reads the temperature and humidity values from a BMP085
sensor using the Adafruit_BMP module, which has to be installed on your
Rasperry Pi as per Adafruits instruction.
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

import Adafruit_BMP.BMP085 as BMP085


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

def get_sea_level_pressure(pres, alt):
    psea = pres / pow(1.0 - alt / 44330.0, 5.225)

    # pascal to hecto pascal
    psea = psea / 100.0
    return psea

def main():
    """Main routine to read sensor data and write the values to the database"""
    config = read_config_file()
    db_config = config["psql"]
    sensors = config["sensors"]
    altitude = float(config["misc"]["altitude"])
    sensor_values = {}

    sensor = BMP085.BMP085(mode=3)

    for sensor_type, sensor_id in sensors.items():
        temp = sensor.read_temperature()

        if sensor_type == "pres":
            raw_value = get_sea_level_pressure(sensor.read_pressure(), altitude)
        elif sensor_type == "temp":
            raw_value = temp
        else:
            break

        sensor_values.update({sensor_id: round(raw_value, 1)})

    write_to_db(db_config, sensor_values)

if __name__ == '__main__':
    main()
