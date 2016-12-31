CREATE TABLE sensor_type (
    id INTEGER PRIMARY KEY NOT NULL,
    description TEXT NOT NULL,
);

CREATE TABLE sensor_device (
    id INTEGER NOT NULL PRIMARY KEY,
    description TEXT NOT NULL,
    serial_no TEXT,
    device_type INTEGER REFERENCES sensor_device(id),
    location TEXT NOT NULL
);

CREATE TABLE sensor_values (
    device_id INTEGER REFERENCES sensor_type(id) NOT NULL,
    log_time TIMESTAMP NOT NULL,
    log_value REAL NOT NULL,
    PRIMARY KEY (device_id,log_time)
)

INSERT INTO sensor_type (id,description)
    VALUES (1,'Temperature');

INSERT INTO sensor_type (id,description)
    VALUES (2,'Air Pressure');

INSERT INTO sensor_type (id,description)
    VALUES (3,'Humidity');

INSERT INTO sensor_type (id,description)
    VALUES (4,'Wind Speed');