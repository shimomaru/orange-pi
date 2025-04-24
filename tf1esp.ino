#include <HardwareSerial.h>
#include <ESP32Servo.h>

// Create serial port for TF-Luna
HardwareSerial tfSerial(1);  // UART1

// Servo objects
Servo servoPan;   // SG90 - horizontal
Servo servoTilt;  // MG996R - vertical

// Pins
const int panPin = 18;
const int tiltPin = 19;

// Scan angles (adjust as needed)
const int panMin = 0;
const int panMax = 180;
const int tiltMin = 45;
const int tiltMax = 135;
const int stepSize = 5;

// UART TF-Luna
const int tfRx = 16;  // ESP32 RX
const int tfTx = 17;  // ESP32 TX

// Read distance from TF-Luna
int readLidarDistance() {
  uint8_t buf[9];
  if (tfSerial.available() >= 9) {
    tfSerial.readBytes(buf, 9);
    if (buf[0] == 0x59 && buf[1] == 0x59) {
      int dist = buf[2] + buf[3] * 256;
      return dist;
    }
  }
  return -1;
}

void setup() {
  Serial.begin(115200);
  tfSerial.begin(115200, SERIAL_8N1, tfRx, tfTx);
  servoPan.attach(panPin);
  servoTilt.attach(tiltPin);
  Serial.println("Starting LiDAR scan...");
}

void loop() {
  for (int tilt = tiltMin; tilt <= tiltMax; tilt += stepSize) {
    servoTilt.write(tilt);
    delay(300);

    for (int pan = panMin; pan <= panMax; pan += stepSize) {
      servoPan.write(pan);
      delay(200);

      int dist = readLidarDistance();
      if (dist > 0) {
        Serial.printf("Tilt: %d, Pan: %d, Distance: %d\n", tilt, pan, dist);
      } else {
        Serial.printf("Tilt: %d, Pan: %d, No reading\n", tilt, pan);
      }
    }
  }

  Serial.println("Scan complete.\n");
  delay(2000);
}
