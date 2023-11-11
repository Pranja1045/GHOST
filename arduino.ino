#include <Servo.h>

Servo bottom;  // bottom - azimuth
Servo top;  // top - alt

int posx = 0, posy = 0; // variable to store the servo position

int servo_max = 180; // Maximum number of rotation units of servo in one direction
int altservo_offset = 0;

const float degToRad = 0.0174533;  // Degrees to radians conversion factor
const float radToDeg = 57.2958;    // Radians to degrees conversion factor
const float pi = 3.14159265359;    // The value of Pi

// Your location's latitude and time
const float latitude = 76.855297;  // Latitude in degrees
const int currentHour = 14;       // Current hour
const int currentMinute = 31;     // Current minute
const int currentSecond = 20;     // Current second

void setup() {
  top.attach(11);   // top - alt
  bottom.attach(10); // bottom - azimuth
  Serial.begin(9600);
  Serial.println("Enter celestial coordinates (RA and Dec):");

  // Initialize servos to a known position (e.g., pointing to the horizon).
  top.write(0.30);
  bottom.write(0.13);
}

void loop() {
  String receivedData;
  // Read the celestial coordinates (RA and Dec) from the serial monitor.
  float ra, dec;
  if (Serial.available() >= 8) {
    receivedData = Serial.readStringUntil('\n');
    int commaIndex = receivedData.indexOf(",");
    
    if (commaIndex != -1) {
      String raStr = receivedData.substring(0, commaIndex);
      String decStr = receivedData.substring(commaIndex + 1);
      
      ra = raStr.toFloat();
      dec = decStr.toFloat();
      Serial.print(ra, 2); // Send RA with 2 decimal places
      Serial.print(",");
      Serial.println(dec, 2); // Read the string until a newline character.
    
    

      // Calculate the current local sidereal time (LST) in radians.
      float lst = getLST();

      // Convert RA and Dec to alt-az coordinates using the LST.
      float ha = lst - ra * degToRad;  // Hour angle
      float alt = asin(sin(dec * degToRad) * sin(latitude * degToRad) + cos(dec * degToRad) * cos(latitude * degToRad) * cos(ha));
      float az = atan2(-sin(ha), cos(ha) * sin(latitude * degToRad) - tan(dec * degToRad) * cos(latitude * degToRad));

      // Convert alt and az back to degrees.
      int az_deg = int(az * radToDeg);
      int alt_deg = int(alt * radToDeg);

      // Map the degrees to servo positions.
      az_deg = map(ra, 0, 360, 0, servo_max);
      alt_deg = map(dec, -90, 90, 0, servo_max);

      // Move the servos to the calculated positions.
      bottom.write(az_deg);
      top.write(alt_deg);
      delay(10000);
      bottom.write(0.30);
      top.write(0.13);
      

      // Print the servo positions to the serial monitor.
      
    }
  }
}


// Calculate the current local sidereal time (LST).
float getLST() {
  int totalSeconds = currentHour * 3600 + currentMinute * 60 + currentSecond;
  float secondsSinceMidnight = float(totalSeconds);

  // Calculate the number of sidereal seconds since midnight.
  float siderealSeconds = secondsSinceMidnight * 366.25 / 3600;

  // Calculate the LST in radians.
  float lst = (100.46061837 + 360.98564736629 * siderealSeconds) * degToRad;
  return lst;
}
