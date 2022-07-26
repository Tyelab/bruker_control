/*

  Cleanup script for liquid solenoids.

  Opens liquid solenoid for 10 seconds, then closes for 500ms.

  To make sure the solenoids are cleaned through, clean the sucrose
  and lines and solenoid by first emptying the line of sucrose,
  then clean with ethanol, and finally rinse with water.

  Collect the waste in a 50mL conical tube from the spout.

*/

const int solPin_liquid = 26;
const int vacPin = 24;

void setup()
{
  // Initialize liquid solenoid pin for cleaning
  pinMode(solPin_liquid, OUTPUT);
  pinMode(vacPin, OUTPUT);
}

// the loop function runs over and over again forever
void loop()
{
  // Open solenoid for 10 seconds or 150msec if making sure needle is ready
  digitalWrite(solPin_liquid, HIGH);
  delay(200);
  digitalWrite(solPin_liquid, LOW);
  delay(3000);
  digitalWrite(vacPin, HIGH);
  delay(500);
  digitalWrite(vacPin, LOW);
  delay(1000);
}
