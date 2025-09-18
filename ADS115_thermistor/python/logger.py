import time
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os  # For checking the presence of the "STOP" file
import pandas as pd

# Constants (same as the Arduino code)
R_FIXED = 10000.0  # Fixed resistor in the voltage divider (10kΩ)
Vcc = 5.0  # Supply voltage (usually 5V for most Arduino boards)
A = 0.001129148  # Steinhart-Hart coefficient A
B = 0.000234125  # Steinhart-Hart coefficient B
C = 0.0000000876741  # Steinhart-Hart coefficient C
R0 = 10000.0  # Thermistor nominal resistance at T0 (25°C)
T0 = 298.15  # Reference temperature (25°C in Kelvin)
BETA = 3950.0  # Beta constant


# Control parameters
measurement_interval = 1  # seconds between measurements
measurements_per_plot = 5  # Number of measurements before plotting and saving

# CSV File
csv_filename = "thermistor_data.csv"

# Function to simulate sensor reading (replace with actual ADC reading code in production)
def read_sensor():
    # This should interface with your hardware to get a real ADC value
    # For demonstration, simulate a value within an expected range
    return np.random.randint(0, 32767)  # Simulate a 16-bit ADC reading

# Function to calculate voltage from ADC reading
def adc_to_voltage(adc_value):
    return (adc_value * 0.1875) / 1000.0  # Calculate voltage in Volts

# Function to calculate thermistor resistance
def calculate_R_therm(voltage):
    if voltage >= Vcc:
        return float('inf')  # If voltage is equal or greater than supply, resistance is effectively infinity
    return (R_FIXED * voltage) / (Vcc - voltage)

# Function to calculate temperature using Steinhart-Hart equation
def calculate_temp_SH(R_therm):
    if R_therm <= 0:
        print(f"Invalid R_therm value: {R_therm}. Skipping this measurement.")
        return float('nan'), float('nan')  # Return NaN for invalid R_therm
    
    logR = math.log(R_therm)
    inv_T = A + B * logR + C * logR**3
    T_K = 1.0 / inv_T
    T_C = T_K - 273.15
    T_F = T_C * 9.0 / 5.0 + 32.0
    return T_K, T_F, T_C

# Function to calculate temperature using Beta equation
def calculate_temp_Beta(R_therm):
    if R_therm <= 0:
        print(f"Invalid R_therm value: {R_therm}. Skipping this measurement.")
        return float('nan'), float('nan'), float('nan')  # Return NaN for invalid R_therm
    
    T_K = 1.0 / ((1.0 / T0) + (1.0 / BETA) * math.log(R_therm / R0))
    T_C = T_K - 273.15
    T_F = T_C * 9.0 / 5.0 + 32.0
    return T_K, T_F, T_C




# Function to plot the data
def plot_data_from_csv(csv_file):
    # Read the CSV file into a DataFrame
    df_or = pd.read_csv(csv_file)
    df_or = df_or.dropna()
    df = df_or[df_or['Temp_SH (C)'] > 0. ].copy()

    #print(df.columns)
    # Extract the data from the CSV
    time = df['Elapsed Time (min)']  # In minutes
    temp_SH_K = df['Temp_SH (K)']
    temp_Beta_K = df['Temp_Beta (K)']

    col_name = 'Voltage (V)'
    data = df[col_name].to_numpy()

    # Initialize lists for cumulative averages and std
    avg_temp_SH_K = []
    std_temp_SH_K = []
    avg_temp_Beta_K = []
    std_temp_Beta_K = []
    avg_data = []
    std_data = []

    # Cumulative calculations
    for i in range(len(time)):
        # Get the subset of data up to current index (i)
        temp_SH_K_sub = temp_SH_K[:i+1]
        temp_Beta_K_sub = temp_Beta_K[:i+1]
        temp_data_sub = data[:i+1]
        # Cumulative average and std
        avg_temp_SH_K.append(np.mean(temp_SH_K_sub))
        std_temp_SH_K.append(np.std(temp_SH_K_sub))

        avg_temp_Beta_K.append(np.mean(temp_Beta_K_sub))
        std_temp_Beta_K.append(np.std(temp_Beta_K_sub))

        avg_data.append(np.mean(temp_data_sub))
        std_data.append(np.mean(temp_data_sub))


    
    # Plotting
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Plot 1: Temperature in K (both methods) with cumulative average and error bars
    axs[0, 0].errorbar(time, avg_temp_SH_K, yerr=std_temp_SH_K, label="Acc. Ave.", fmt='o', color='blue', alpha = 0.5)
    axs[0, 0].errorbar(time, avg_temp_Beta_K, yerr=std_temp_Beta_K, label="Acc. Ave.", fmt='o', color='green', alpha = 0.5)
    axs[0, 0].plot(time, temp_SH_K, label="Temp(SH) K", linestyle='--', color='blue')
    axs[0, 0].plot(time, temp_Beta_K, label="Temp(Beta) K", linestyle='--', color='green')
    #axs[0, 0].set_title("Cumulative Temperature in K (SH & Beta)")
    axs[0, 0].set_xlabel("Elapsed Time (min)")
    axs[0, 0].set_ylabel("Temperature (K)")
    axs[0, 0].legend()

    # Plot 2: Histogram of instantaneous temperature measurements in K (SH & Beta)
    axs[0, 1].hist(temp_SH_K, bins=20, alpha=0.5, label=f'Temp(SH) K: {np.mean(temp_SH_K):3.2f} +- {np.std(temp_SH_K):3.2f} ', color='blue')
    axs[0, 1].hist(temp_Beta_K, bins=20, alpha=0.5, label=f'Temp(Beta) K: {np.mean(temp_Beta_K):3.2f} +- {np.std(temp_Beta_K):3.2f} ', color='green')
    #axs[0, 1].set_title("Histogram of Instantaneous Temperatures (K)")
    axs[0, 1].set_xlabel("Temperature (K)")
    axs[0, 1].set_ylabel("Frequency")
    axs[0, 1].legend()

    # Plot 3: R_therm with cumulative average and error bars
    axs[1, 0].errorbar(time, avg_data, yerr=std_data, fmt='o', color='purple',alpha =0.5)
    axs[1, 0].plot(time, data, linestyle='--', color='purple')
    #axs[1, 0].set_title("Cumulative R_therm (Ohms)")
    axs[1, 0].set_xlabel("Elapsed Time (min)")
    axs[1, 0].set_ylabel(col_name)

    # Plot 4: Histogram of instantaneous R_therm values

    axs[1, 1].hist(data, bins=20, alpha=0.5, color='purple' ,label = f"{np.mean(data):3.2f} +- {np.std(data):3.2f} ")
    #axs[1, 1].set_title("Histogram of Instantaneous R_therm (Ohms)")
    axs[1, 1].set_xlabel(col_name)
    axs[1, 1].set_ylabel("counts")
    axs[1, 1].legend()

    plt.tight_layout()
    plt.savefig("temperature_plot.png")
    plt.clf();plt.close('all') # Closes all currently open figures
#    plt.show()





# Main loop
measurement_count = 0
start_time = time.time()

csv_header = ['Elapsed Time (min)', 'Date', 'Voltage (V)', 'R_therm (Ohms)', 'Temp_SH (K)', 'Temp_SH (F)', 'Temp_SH (C)', 'Temp_Beta (K)', 'Temp_Beta (F)', 'Temp_Beta (C)']

# Create a new CSV file and write the header
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

buffer_data = []

while True:
    # Get the current elapsed time (convert from seconds to minutes)
    elapsed_time = (time.time() - start_time) / 60.0  # Convert seconds to minutes

    # Read the sensor (ADC value)
    adc_value = read_sensor()

    # Convert the ADC value to voltage
    voltage = adc_to_voltage(adc_value)

    # Calculate the thermistor resistance
    R_therm = calculate_R_therm(voltage)

    # Calculate temperatures using both methods
    temp_SH_K_value, temp_SH_F_value, temp_SH_C_value = calculate_temp_SH(R_therm)
    temp_Beta_K_value, temp_Beta_F_value, temp_Beta_C_value = calculate_temp_Beta(R_therm)


    # Print the current measurements to the screen (including elapsed time in minutes)
    print(f"Time: {elapsed_time:.2f} min | Voltage: {voltage:.4f} V | R_therm: {R_therm:.1f} Ohms")
    print(f"R_therm (Ohms): {R_therm:.1f}")
    print(f"Temp(SH) (K): {temp_SH_K_value:.2f} | Temp(SH) (°F): {temp_SH_F_value:.2f} | Temp(SH) (°C): {temp_SH_C_value:.2f}")
    print(f"Temp(Beta) (K): {temp_Beta_K_value:.2f} | Temp(Beta) (°F): {temp_Beta_F_value:.2f} | Temp(Beta) (°C): {temp_Beta_C_value:.2f}")
    print()  # Empty line for better readability

    # If we've reached the required number of measurements, save to CSV and update the plot
    measurement_count += 1
    buffer_data.append([elapsed_time, datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
    voltage, R_therm,
    temp_SH_K_value, temp_SH_F_value, temp_SH_C_value,
    temp_Beta_K_value, temp_Beta_F_value, temp_Beta_C_value])


    if measurement_count >= measurements_per_plot:

        
        # Write data to CSV
        # with open(csv_filename, mode='a', newline='') as file:
        #     writer = csv.writer(file)
        #
        #     writer.writerow([
        #         round(elapsed_time, 2),
        #         datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
        #         round(voltage, 4),
        #         round(R_therm, 1),
        #         round(temp_SH_K_value, 2),
        #         round(temp_SH_F_value , 2),
        #         round(temp_SH_C_value , 2),
        #         round(temp_Beta_K_value, 2),
        #         round(temp_Beta_F_value, 2),
        #         round(temp_Beta_C_value , 2)
        #     ])
        # Write data to CSV
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for k in range(len(buffer_data)):
                        row = buffer_data[k]
                        writer.writerow([round(row[0],2),row[1],
                        round(row[2],4),round(row[3],4),
                        round(row[4],1),round(row[5],2),round(row[6],2),
                        round(row[7],2),round(row[8],2),round(row[9],2)])

            file.flush()

        # Plot the data
        plot_data_from_csv(csv_filename)

        # Reset the data lists for the next set of measurements
        measurement_count = 0
        buffer_data = []
        if os.path.exists('STOP'):
            print("STOP file detected, exiting...")
            break


    # Wait before taking the next measurement
    time.sleep(measurement_interval)

