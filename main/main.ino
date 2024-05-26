// ESP32S3

// this code is for ESP32C3 Dev Module
// #include <ESP32Servo.h>
// #include <Arduino_JSON.h>

// const int HORIZONTAL_SERVO = 40;
// const int VERTICAL_SERVO = 39;    // for now
// const int LASER_PIN = 38;         // for now

const int FLYWHEEL_GPIO = 4;
const int TRIGGER_GPIO = 5;

int incomingByte = 52; // for incoming serial data

// Servo horizontalServo; 
// Servo verticalServo;

// declare functions
// void followCoordinates(const int x, const int y, const int camHeight, const int camWidth, const int horizontalFOV, const int verticalFOV);

void fire() {
  Serial.println("Ramping up FlyWheel");
  // allow flywheel to ramp up for 3 seconds
  digitalWrite(FLYWHEEL_GPIO, HIGH);
  delay(2000);

  // pulse the trigger
  Serial.println("Fire!");
  digitalWrite(TRIGGER_GPIO, HIGH); // retract
  delay(500);
  digitalWrite(TRIGGER_GPIO, LOW); // extend

  Serial.println("Shutting off Flywheel!");
  // allow flywheel to ramp down for 3 seconds
  digitalWrite(FLYWHEEL_GPIO, LOW);
  delay(2000);
  Serial.println("Done!");
}

void setup() {
  Serial.begin(115200);
  // horizontalServo.attach(HORIZONTAL_SERVO);
  // verticalServo.attach(VERTICAL_SERVO);

  // set pinmodes
  pinMode(FLYWHEEL_GPIO, OUTPUT);
  pinMode(TRIGGER_GPIO, OUTPUT);
  Serial.println("Ready to loop");
}


void loop() {
  // Use a buffer for incoming data (adjust size if needed)
  // static char buffer[64];
  // static size_t bufferIndex = 0;

  // read the serial data to obtain
  // while (Serial.available() > 0) {
  //   char incomingByte = Serial.read();

  //   // Look for a newline character as the delimiter
  //   if (incomingByte == '\n') { 
  //     buffer[bufferIndex] = '\0'; // Null-terminate the string
  //     bufferIndex = 0; 

  //     // Process the received JSON object
  //     JSONVar myObject = JSON.parse(buffer);

  //     if (JSON.typeof(myObject) == "undefined") {
  //       Serial.println("Parsing input failed!");
  //     } else {
  //       int x = myObject["x"];
  //       int y = myObject["y"];

  //       // Camera parameters (make these configurable if possible)
  //       const int camHeight = 1080;
  //       const int camWidth = 1920;
  //       const int horizontalFOV = 54;
  //       const int verticalFOV = 54;

  //       followCoordinates(x, y, camHeight, camWidth, horizontalFOV, verticalFOV);
  //     } 
  //   } else if (bufferIndex < sizeof(buffer) - 1) { 
  //     buffer[bufferIndex++] = incomingByte; 
  //   } else {
  //     Serial.println("Buffer overflow!"); // Handle buffer overflow
  //     bufferIndex = 0;  // Reset buffer
  //   }
  // }

  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();

    // filter out the newline
    if (incomingByte == 10)
    {
        return;
    }

    Serial.print("I received: ");
    Serial.println(incomingByte);

    // check if the incoming byte is character 0
    // fire if so
    if (incomingByte == 48) {
      Serial.println("Firing sequence initiated!");
      // fire
      fire();
    }
  }

  // loop through firing for testing
  fire();
}

// void followCoordinates(const int x, const int y, const int camHeight, const int camWidth, const int horizontalFOV, const int verticalFOV) {
//   Serial.println("Moving to (" + String(x) + ", " + String(y) + ")");
//   // calculate offset from the center
//   int x_offset = x - camWidth / 2;
//   int y_offset = y - camHeight / 2;
  
//   // convert the offset into angles
//   int angle_horizontal = x_offset * horizontalFOV / camWidth;
//   int angle_vertical = y_offset * verticalFOV / camHeight;

//   // now, move the laser
//   horizontalServo.write(angle_horizontal);
//   verticalServo.write(angle_vertical);

//   delay(15); // a small delay to allow servos to move properly to the position 
// }