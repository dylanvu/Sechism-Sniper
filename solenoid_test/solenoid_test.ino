const int SOLENOID_GPIO = 12;
void setup() {
  Serial.begin(115200);
  // put your setup code here, to run once:
  pinMode(SOLENOID_GPIO, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("PULL");
  digitalWrite(SOLENOID_GPIO, HIGH);
  delay(1000);
  Serial.println("OFF");
  digitalWrite(SOLENOID_GPIO, LOW);
  delay(5000);
}
