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


start_time = time.time()


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
    print() 

    if os.path.exists('STOP'):
        print("STOP file detected, exiting...")
        break


    # Wait before taking the next measurement
    time.sleep(measurement_interval)

