    #!/usr/bin/python3
    # Python Modules
    import serial, sys, time
    from influxdb import InfluxDBClient
    # Configuration
    serialPort='/dev/ttyUSB0'
    db = InfluxDBClient(host='10.11.1.104', port=8086, database='weather')
    measurement = 'Messungen'
    # Open serial port
    try:
        ser = serial.Serial(serialPort,baudrate=9600,timeout=None)
    except:
        sys.exit(1)
    # Main loop
    while True:
        # Wait for data and try error recovery on disconnect
        try:
            serData = ser.readline()
        except serial.SerialException as e:
            try:
                ser.close()
                time.sleep(10)
                ser = serial.Serial(serialPort,baudrate=9600,timeout=None)
            except:
                pass