const int bruker2PTriggerPin = 11;
boolean sendTrigger = true;

void setup() {
  Serial.begin(9600);
  pinMode(bruker2PTriggerPin, OUTPUT); 

}

void loop() {
  brukerTrigger();

}

void brukerTrigger() {
  if (sendTrigger) {
    Serial.println("Sending Trigger");
    digitalWrite(bruker2PTriggerPin, LOW);
    delay(10000);
    digitalWrite(bruker2PTriggerPin, HIGH);
    delay(5000);
  }
}
