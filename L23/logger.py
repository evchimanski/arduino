#  logger.py
#  
# Based on L22 off Elegoo 
#  
#  should create utils.py and etc

import serial
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from scipy.stats import gaussian_kde

# === Config ===
SERIAL_PORT = '/dev/ttyACM0'  # Adjust to your Arduino's port
BAUD_RATE = 9600
CSV_FILENAME = 'temp_log.csv'
PLOT_FILENAME = 'temp_plot.png'
STOP_FILENAME = 'STOP'
SAVE_INTERVAL = 5  # Save and plot every N readings

def connect_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {port}: {e}")
        return None

def save_data(timestamps, elapsed, temps):
    df = pd.DataFrame({
        'timestamp': timestamps,
        'elapsed_min': elapsed,
        'temperature_F': temps
    })
    df.to_csv(CSV_FILENAME, index=False)
    print(f"[INFO] Data saved to '{CSV_FILENAME}'.")

def plot_data(elapsed, temps):
    if len(temps) == 0:
        return

    avg_temp = np.mean(temps)
    std_temp = np.std(temps)
    num_points = len(temps)

    # Calculate running std dev for error bars at each point (simple moving std or cumulative std)
    # Here we use cumulative std dev up to each point for demonstration
    stds = [np.std(temps[:i+1]) if i>0 else 0 for i in range(num_points)]

    # Set up plot with two subplots: time series with error bars and PDF
    fig, axs = plt.subplots(2, 1, figsize=(8, 8), dpi=300)

    # --- Subplot 1: Temperature vs elapsed time with error bars ---
    axs[0].errorbar(elapsed, temps, yerr=stds, fmt='-o', color='tab:red', ecolor='gray', alpha=0.7, label=f'Temperature (°F)\nN={num_points}')
    axs[0].set_xlabel("Elapsed Time (minutes)")
    axs[0].set_ylabel("Temperature (°F)")
    axs[0].set_title("Temperature Over Time")
    axs[0].grid(True, linestyle="--", alpha=0.5)
    axs[0].legend()

    # --- Subplot 2: PDF (Histogram + KDE) of temperature ---
    # Histogram
    axs[1].hist(temps, bins='auto', density=True, alpha=0.5, color='tab:blue', label='Histogram')

    # KDE (Kernel Density Estimate)
    try:
        kde = gaussian_kde(temps)
        temp_range = np.linspace(min(temps), max(temps), 1000)
        axs[1].plot(temp_range, kde(temp_range), color='tab:orange', label='KDE')
    except Exception as e:
        print(f"[WARN] KDE plot error: {e}")

    axs[1].set_xlabel("Temperature (°F)")
    axs[1].set_ylabel("Density")
    axs[1].set_title("Temperature Distribution (PDF)")
    axs[1].legend()
    axs[1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(PLOT_FILENAME)
    plt.close()
    print(f"[INFO] Plot saved to '{PLOT_FILENAME}'.")

def main():
    ser = connect_serial(SERIAL_PORT, BAUD_RATE)
    if not ser:
        return

    timestamps = []
    elapsed_mins = []
    temps = []
    count = 0

    print(f"\n[LOGGING STARTED] Logging to '{CSV_FILENAME}'... (create file named '{STOP_FILENAME}' to stop)\n")

    try:
        while True:
            if os.path.exists(STOP_FILENAME):
                print(f"\n[STOP] Detected '{STOP_FILENAME}'. Exiting loop...")
                break

            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            print(f"[RAW] {line}")  # Debug: show raw line

            try:
                parts = line.split(',')
                if len(parts) != 2:
                    continue

                elapsed = float(parts[0])
                temp_f = float(parts[1])
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                timestamps.append(timestamp)
                elapsed_mins.append(elapsed)
                temps.append(temp_f)

                avg_temp = np.mean(temps)
                std_temp = np.std(temps)

                print(f"[{timestamp}] {elapsed:.2f} min | {temp_f:.2f} °F | Avg: {avg_temp:.2f} ± {std_temp:.2f}")

                count += 1
                if count % SAVE_INTERVAL == 0:
                    save_data(timestamps, elapsed_mins, temps)
                    plot_data(elapsed_mins, temps)

            except ValueError as e:
                print(f"[WARN] Failed to parse line: {line} | Error: {e}")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] KeyboardInterrupt received. Exiting...")

    finally:
        ser.close()
        save_data(timestamps, elapsed_mins, temps)
        plot_data(elapsed_mins, temps)
        print(f"\n[INFO] Serial closed. Final data and plot saved.")

if __name__ == "__main__":
    main()
