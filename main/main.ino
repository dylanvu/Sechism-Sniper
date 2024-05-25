#include <ESP32Servo.h>
#include <Arduino_JSON.h>

const int HORIZONTAL_SERVO = 40;
const int VERTICAL_SERVO = 39;    // for now
const int LASER_PIN = 38;         // for now

Servo horizontalServo; 
Servo verticalServo;

// declare functions
void followCoordinates(const int x, const int y, const int camHeight, const int camWidth, const int horizontalFOV, const int verticalFOV);

void setup() {
  Serial.begin(115200);
  horizontalServo.attach(HORIZONTAL_SERVO);
  verticalServo.attach(VERTICAL_SERVO);
}

void loop() {
  // Use a buffer for incoming data (adjust size if needed)
  static char buffer[64];
  static size_t bufferIndex = 0;

  // read the serial data to obtain
  while (Serial.available() > 0) {
    char incomingByte = Serial.read();

    // Look for a newline character as the delimiter
    if (incomingByte == '\n') { 
      buffer[bufferIndex] = '\0'; // Null-terminate the string
      bufferIndex = 0; 

      // Process the received JSON object
      JSONVar myObject = JSON.parse(buffer);

      if (JSON.typeof(myObject) == "undefined") {
        Serial.println("Parsing input failed!");
      } else {
        int x = myObject["x"];
        int y = myObject["y"];

        // Camera parameters (make these configurable if possible)
        const int camHeight = 1080;
        const int camWidth = 1920;
        const int horizontalFOV = 54;
        const int verticalFOV = 54;

        followCoordinates(x, y, camHeight, camWidth, horizontalFOV, verticalFOV);
      } 
    } else if (bufferIndex < sizeof(buffer) - 1) { 
      buffer[bufferIndex++] = incomingByte; 
    } else {
      Serial.println("Buffer overflow!"); // Handle buffer overflow
      bufferIndex = 0;  // Reset buffer
    }
  }
}

void followCoordinates(const int x, const int y, const int camHeight, const int camWidth, const int horizontalFOV, const int verticalFOV) {
  Serial.println("Moving to (" + String(x) + ", " + String(y) + ")");
  // calculate offset from the center
  int x_offset = x - camWidth / 2;
  int y_offset = y - camHeight / 2;
  
  // convert the offset into angles
  int angle_horizontal = x_offset * horizontalFOV / camWidth;
  int angle_vertical = y_offset * verticalFOV / camHeight;

  // now, move the laser
  horizontalServo.write(angle_horizontal);
  verticalServo.write(angle_vertical);

  delay(15); // a small delay to allow servos to move properly to the position 
}