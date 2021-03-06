void setup() {
/*
   Blink
   Turns on an LED on for one second, then off for one second, repeatedly.
*/

// the setup function runs once when you press reset or power the board

// initialize digital pin 13 as an output.
   pinMode(13, OUTPUT);
   pinMode(12, OUTPUT);
}


void loop() {
   digitalWrite(13, HIGH); // turn the LED on (HIGH is the voltage level)
   digitalWrite(12, HIGH);
   delay(30); // wait for a second
   digitalWrite(13, LOW); // turn the LED off by making the voltage LOW
   digitalWrite(12, LOW);
   delay(970); // wait for a second

}
