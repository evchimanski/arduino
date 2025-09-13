import serial
import time
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

SERIAL_PORT = '/dev/ttyACM0'  # Change if needed
BAUD_RATE = 9600
FILENAME = 'datalog.csv'
PLOT_FILENAME = 'datalog_plot.png'
STOP_FILE = 'STOP'

def save_to_csv(timestamps, elapsed_mins, temps, hums):
    df = pd.DataFrame({
        'timestamp': timestamps,
        'elapsed_time_min': elapsed_mins,
        'temperature_degC': temps,
        'humidity_percent': hums
    })
    df.to_csv(FILENAME, index=False)

def plot_data(elapsed_mins, temps, hums):
    plt.figure(figsize=(8,5), dpi=300)
    plt.scatter(elapsed_mins, temps, label='Temperature (°C)', color='tab:red')
    plt.scatter(elapsed_mins, hums, label='Humidity (%)', color='tab:blue')
    plt.xlabel('Elapsed Time (minutes)', fontsize=12)
    plt.ylabel('Measurement', fontsize=12)
    plt.title('DHT11 Temperature and Humidity over Time', fontsize=14, weight='bold')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(PLOT_FILENAME)
    plt.close()

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)  # Wait for serial connection to settle

    timestamps = []
    elapsed_mins = []
    temps = []
    hums = []

    start_time = time.time()
    count = 0
    save_interval = 5

    print(f"Logging data to {FILENAME}... Create '{STOP_FILE}' file to stop.\n")

    try:
        while True:
            if os.path.isfile(STOP_FILE):
                print(f"\nDetected '{STOP_FILE}'. Stopping...")
                break

            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            # Only print and parse lines containing both 'T =' and 'H ='
            if "T =" in line and "H =" in line:
                print(f"Received: '{line}'")
                try:
                    temp_part, hum_part = line.split(',')
                    temp_str = temp_part.split('=')[1].strip().split(' ')[0]
                    temp = float(temp_str)
                    hum_str = hum_part.split('=')[1].strip().replace('%','')
                    hum = float(hum_str)
                except Exception as e:
                    print(f"Parse error: {e} in line: {line}")
                    continue

                elapsed_sec = time.time() - start_time
                elapsed_min = elapsed_sec / 60
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                timestamps.append(timestamp_str)
                elapsed_mins.append(elapsed_min)
                temps.append(temp)
                hums.append(hum)

                print(f"[{timestamp_str}] Elapsed: {elapsed_min:.2f} min, Temp: {temp} °C, Humidity: {hum} %")

                count += 1
                if count % save_interval == 0:
                    save_to_csv(timestamps, elapsed_mins, temps, hums)
                    plot_data(elapsed_mins, temps, hums)

            else:
                # Ignore any lines without full temperature and humidity info
                continue

    except KeyboardInterrupt:
        print("\nKeyboard interrupt, stopping...")

    finally:
        ser.close()
        save_to_csv(timestamps, elapsed_mins, temps, hums)
        plot_data(elapsed_mins, temps, hums)
        print(f"Serial closed. Final plot saved as {PLOT_FILENAME}")

if __name__ == "__main__":
    main()
