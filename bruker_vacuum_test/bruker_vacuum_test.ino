/*
  
  Testing script for vacuum use for headfixed behavior solenoids.

  Opens liquid solenoid for 150ms, then closes.
  Waits 1 second to activate vacuum, vacuum active for 500ms

  Do this repeatedly until position of needles is correct

*/

const int solPin_liquid = 26;
const int vacPin = 24;

void setup() {
  // Initialize liquid solenoid pin for cleaning
  pinMode(solPin_liquid, OUTPUT);
  pinMode(vacPin, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  // Open solenoid for 150msec to deliver fluid
  digitalWrite(solPin_liquid, HIGH);
  delay(150);

  // Close solenoid, wait 1 second
  digitalWrite(solPin_liquid, LOW);
  delay(1000);

  // Open vacuum for 500ms
  digitalWrite(vacPin, HIGH);
  delay(500);
  digitalWrite(vacPin, LOW);

  // Delay for a couple seconds in between tests...
  delay(2000);
}
