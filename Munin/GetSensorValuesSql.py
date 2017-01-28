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

def get_args(type_list, category_list, argv):
    """parse command line arguments """
    shortopts = "cg:t:"
    types_posibel = {}
    cat_posibel = {}
    my_args = {"config":False}

    for stype in type_list:
        types_posibel.update({stype[1]: stype[0]})

    for category in category_list:
        cat_posibel.update({category[0]: category[1]})

    try:
        opts, args = getopt.getopt(argv, shortopts)
    except getopt.GetoptError:
        usage(type_list, category_list)

    for opt, arg in opts:
        if opt == '-t':
            if arg in types_posibel:
                my_args.update({"type_id": types_posibel[arg]})
                my_args.update({"type_name": arg})
            else:
                usage(type_list, category_list)
        elif opt == '-g':
            if int(arg) in cat_posibel:
                my_args.update({"category_name": cat_posibel[int(arg)]})
                my_args.update({"category_id": arg})
            else:
                usage(type_list, category_list)
        elif opt == '-c':
            my_args.update({"config" : True})
        else:
            usage(type_list, category_list)

    if not("type_id" in my_args) or not("category_id" in my_args):
        usage(type_list, category_list)

    return my_args

def usage(sensor_types, categories):
    """print usage of this script"""
    print("usage: GetSensorValuesSql.py -t <sensor-type> -g <sensor-category> [-c]")
    print("The following sensor types are supported:")
    for sensor in sensor_types:
        print("   {}".format(sensor[1]))
    print("The following categories are supported:")
    for category in categories:
        print("   {} ({})".format(category[0],category[1]))
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

def get_sensor_types(db_conn):
    """returns the list of the sensor devices"""
    sql_str = "SELECT \
                    sensor_type.id, \
                    sensor_type.description\
               FROM \
                    public.sensor_type"

    cur = db_conn.cursor()
    cur.execute(sql_str)
    type_list = cur.fetchall()
    db_conn.commit()
    cur.close()
    return type_list

def get_sensor_categories(db_conn):
    """returns the list of the sensor categories"""
    sql_str = "SELECT \
                    sensor_category.id, \
                    sensor_category.description \
               FROM  \
                    public.sensor_category"

    cur = db_conn.cursor()
    cur.execute(sql_str)
    list_of_categories = cur.fetchall()
    db_conn.commit()
    cur.close()
    return list_of_categories

def get_sensor_list(db_conn, device_type, device_category):
    """returns the list of the sensor devices"""
    sql_str = "SELECT id, location FROM sensor_device WHERE \
               sensor_device.device_type = %s AND \
               sensor_device.device_category = %s"

    cur = db_conn.cursor()
    cur.execute(sql_str, [device_type, device_category])
    config_values = cur.fetchall()
    db_conn.commit()
    cur.close()
    return config_values

def get_sensor_values(db_conn, device_type, device_category):
    """returns the list of the sensor types"""
    sql_str = "SELECT device_id, log_time, log_value \
               FROM ( \
                     SELECT *, \
                     row_number() over (partition by sensor_values.device_id order by sensor_values.log_time desc) as row_number \
               FROM sensor_values, sensor_device \
               WHERE \
	           sensor_values.device_id = sensor_device.id AND \
	           sensor_device.device_type = %s AND \
               sensor_device.device_category = %s \
               ) as rows \
               where row_number = 1"

    cur = db_conn.cursor()
    cur.execute(sql_str, [device_type, device_category])
    sensor_values = cur.fetchall()
    db_conn.commit()
    cur.close()
    return sensor_values

def main():
    """Main function to read and return sensor values"""
    config = read_config_file()
    db_config = config["psql"]
    conn = open_db(db_config["db"], db_config["user"], db_config["host"], db_config["prt"], db_config["pwd"])
    types = get_sensor_types(conn)
    categories = get_sensor_categories(conn)

    arg_dict = get_args(types, categories, sys.argv[1:])

    if arg_dict["config"]:
        sensor_list = get_sensor_list(conn, arg_dict["type_id"], arg_dict["category_id"])
        for sensor in sensor_list:
            print("{}{}.label {}".format(arg_dict["type_name"], sensor[0], sensor[1]))
    else:
        sensor_values = get_sensor_values(conn, arg_dict["type_id"], arg_dict["category_id"])
        for sensor in sensor_values:
            val = sensor[2]
            time_diff = datetime.datetime.now() - sensor[1]
            if time_diff.total_seconds() > 360:
                val = ''
            print("{}{}.value {}".format(arg_dict["type_name"], sensor[0], val))

    conn.close()


if __name__ == '__main__':
    main()