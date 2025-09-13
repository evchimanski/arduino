// www.elegoo.com
// 2016.12.9
// EVC added to that

#include <LiquidCrystal.h>
#include <math.h>

// LCD pin setup: (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

int tempPin = A0;

// Stats
float tempSum = 0;
float tempSqSum = 0;
unsigned long readingCount = 0;
unsigned long startMillis;

void setup() {
  lcd.begin(16, 2);
  startMillis = millis();
  lcd.print("Starting...");
  delay(1000);
  lcd.clear();
}

void loop() {
  // Read temperature
  int tempReading = analogRead(tempPin);
  double tempK = log(10000.0 * ((1024.0 / tempReading - 1)));
  tempK = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK * tempK)) * tempK);
  float tempC = tempK - 273.15;

  // Update stats
  tempSum += tempC;
  tempSqSum += tempC * tempC;
  readingCount++;

  // Calculate average and std dev
  float avg = tempSum / readingCount;
  float variance = (tempSqSum / readingCount) - (avg * avg);
  float stddev = sqrt(variance);

  // Elapsed time in millis
  unsigned long elapsedMillis = millis() - startMillis;
  unsigned long totalSeconds = elapsedMillis / 1000;

  int hours = totalSeconds / 3600;
  int minutes = (totalSeconds % 3600) / 60;
  int seconds = totalSeconds % 60;

  // Display on LCD
  lcd.clear();

  // First line: A:24.3°C S:0.5
  lcd.setCursor(0, 0);
  lcd.print("A:");
  lcd.print(avg, 1);
  lcd.print((char)223); // Degree symbol
  lcd.print("C S:");
  lcd.print(stddev, 1);

  // Second line: T:hh:mm:ss
  lcd.setCursor(0, 1);
  lcd.print("T:");
  if (hours < 10) lcd.print("0");
  lcd.print(hours);
  lcd.print(":");
  if (minutes < 10) lcd.print("0");
  lcd.print(minutes);
  lcd.print(":");
  if (seconds < 10) lcd.print("0");
  lcd.print(seconds);

  delay(2000); // Update every 2 seconds
}
