#!/usr/bin/env python3
""" This script reads the diverent sensor values from the postgresql
database and returns them to the command line.
It is writen for use in a munin-plugin in mind.
"""

import os
import sys
import datetime
import getopt

import psycopg2
import json

def read_config_file():
    """read the config from json file"""
    conf_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')

    with open(conf_file) as json_conf:
        config = json.load(json_conf)

    return config

def get_args(sensor_list, argv):
    """parse command line arguments """
    shortopts = "t:c"
    types_posibel = {}
    my_args = {"config":False}

    for key, type_id in sensor_list.items():
        types_posibel.update({key: type_id})
    try:
        opts, args = getopt.getopt(argv, shortopts)
    except getopt.GetoptError:
        usage(types_posibel)

    for opt, arg in opts:
        if opt == '-t':
            if arg in types_posibel:
                my_args.update({"type_id": types_posibel[arg]})
                my_args.update({"type_name": arg})
            else:
                usage(types_posibel)
        elif opt == '-c':
            my_args.update({"config" : True})
        else:
            usage(types_posibel)

    if not("type_id" in my_args):
        usage(sensor_list)

    return my_args

def usage(sensor_types):
    """print usage of this script"""
    print("usage: GetSensorValuesSql.py -t <sensor-type> [-c]")
    print("The following sensor types are supported:")
    for sensor_type, sensor_id in sensor_types.items():
        print("   {}".format(sensor_type))
    print("\nThe -c option is used to retrieve munin config lines")

    sys.exit()

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

def get_config_values(db_conf, device_type):
    """returns the list of the sensor devices"""
    db_conn = open_db(db_conf["db"], db_conf["user"],
                      db_conf["host"], db_conf["prt"], db_conf["pwd"])
    sql_str = "SELECT id, location FROM sensor_device WHERE \
               sensor_device.device_type = %s;"
    cur = db_conn.cursor()
    cur.execute(sql_str, [device_type, ])
    config_values = cur.fetchall()
    cur.close()
    db_conn.close()
    return config_values

def get_sensor_values(db_conf, device_type):
    """returns the list of the sensor devices"""
    db_conn = open_db(db_conf["db"], db_conf["user"],
                      db_conf["host"], db_conf["prt"], db_conf["pwd"])
    sql_str = "SELECT device_id, log_time, log_value \
               FROM ( \
                     SELECT *, \
                     row_number() over (partition by sensor_values.device_id order by sensor_values.log_time desc) as row_number \
               FROM sensor_values, sensor_device \
               WHERE \
	           sensor_values.device_id = sensor_device.id AND \
	           sensor_device.device_type = %s \
               ) as rows \
               where row_number = 1"

    time2 = datetime.datetime.now()
    time1 = time2 - datetime.timedelta(minutes=5)
    cur = db_conn.cursor()
    cur.execute(sql_str, [device_type, ])
    sensor_values = cur.fetchall()
    cur.close()
    db_conn.close()
    return sensor_values

def main():
    """Main function to read and return sensor values"""
    config = read_config_file()
    db_config = config["psql"]
    sensors = config["sensors"]

    arg_dict = get_args(sensors, sys.argv[1:])

    if arg_dict["config"]:
        sensor_list = get_config_values(db_config, arg_dict["type_id"])
        for sensor in sensor_list:
            print("{}{}.label {}".format(arg_dict["type_name"], sensor[0], sensor[1]))
    else:
        sensor_values = get_sensor_values(db_config, arg_dict["type_id"])
        for sensor in sensor_values:
            val = sensor[2]
            time_diff = datetime.datetime.now() - sensor[1]
            if time_diff.total_seconds() > 360:
                val = ''
            print("{}{}.value {}".format(arg_dict["type_name"], sensor[0], val))


if __name__ == '__main__':
    main()