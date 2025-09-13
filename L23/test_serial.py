import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
time.sleep(2)

print("Starting to read lines:")
while True:
    line = ser.readline()
    if line:
        try:
            print(line.decode('utf-8').strip())
        except UnicodeDecodeError:
            print("[ERROR] Could not decode line")
    else:
        print("[DEBUG] No data received")
