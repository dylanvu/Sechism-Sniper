#include <ESP32Servo.h>

const int SOLENOID_GPIO = 40;
Servo myServo;  // Create a Servo object

void setup() {
  Serial.begin(115200);
  myServo.attach(SOLENOID_GPIO);  // Attach the servo to pin 9
}

void loop() {
  // Move the servo to 0 degrees
  myServo.write(0);
  delay(1000);  // Wait for 1 second

  // Move the servo to 90 degrees
  myServo.write(90);
  delay(1000);  // Wait for 1 second

  // Move the servo to 180 degrees
  myServo.write(180);
  delay(1000);  // Wait for 1 second
}
