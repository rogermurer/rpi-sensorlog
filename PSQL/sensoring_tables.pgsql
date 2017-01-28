CREATE TABLE sensor_type (
    id INTEGER PRIMARY KEY NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE sensor_category (
    id INTEGER PRIMARY KEY NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE sensor_device (
    id INTEGER NOT NULL PRIMARY KEY,
    description TEXT NOT NULL,
    serial_no TEXT,
    device_type INTEGER REFERENCES sensor_device(id) NOT NULL,
    device_category INTEGER REFERENCES sensor_category(id) NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE sensor_values (
    device_id INTEGER REFERENCES sensor_type(id) NOT NULL,
    log_time TIMESTAMP NOT NULL,
    log_value REAL NOT NULL,
    PRIMARY KEY (device_id,log_time)
)

INSERT INTO sensor_type (id,description)
    VALUES (1,'temp');

INSERT INTO sensor_type (id,description)
    VALUES (2,'pressure');

INSERT INTO sensor_type (id,description)
    VALUES (3,'humid');

INSERT INTO sensor_type (id,description)
    VALUES (4,'wind');

INSERT INTO sensor_category (id,description)
    VALUES (1,'Environment Sensors')

INSERT INTO sensor_category (id,description)
    VALUES (2,'System Sensors')