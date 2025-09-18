#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;  // Use this for the 16-bit version

float Voltage = 0.0;

void setup(void) {
  Serial.begin(9600);
  ads.begin();  // Initialize the ADS1115
}

void loop(void) {
  int16_t adc0 = ads.readADC_SingleEnded(0);  // Read from channel 0
  Voltage = (adc0 * 0.1875) / 1000;  // Convert ADC value to voltage

  Serial.print("AIN0: ");
  Serial.print(adc0);
  Serial.print("\tVoltage: ");
  Serial.println(Voltage, 7);
  Serial.println();

  delay(1000);  // Wait 1 second before reading again
}



