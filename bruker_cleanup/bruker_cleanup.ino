/*
  
  Cleanup script for liquid solenoids.

  Opens liquid solenoid for 10 seconds, then closes for 500ms.

  To make sure the solenoids are cleaned through, clean the sucrose
  and lines and solenoid by first emptying the line of sucrose,
  then clean with ethanol, and finally rinse with water.

  Collect the waste in a 50mL conical tube from the spout.

*/

const int solPin_liquid = 26;

void setup() {
  // Initialize liquid solenoid pin for cleaning
  pinMode(solPin_liquid, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  // Open solenoid for 10 seconds
  digitalWrite(solPin_liquid, HIGH);
  delay(10000);

  // Close solenoid for 500ms
  digitalWrite(solPin_liquid, LOW);
  delay(500);
}
