// Demo code for Arduino control of Bruker 2P Set up for Team Specialk
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
// NOTE 5/8/21: Testing is being done with water.


//// PIN ASSIGNMENT ////
// input
// none
// output
const int solPin_air = 13; // solenoid for air puff control
const int solPin_liquid = 12; // solenoid for liquid control: sucrose, water, EtOH
const int vacPin = 11; // solenoid for vacuum control
const int speakerPin = 10; // pin for using tone() function


/// SETUP ////

void setup() {
/*
   Stimulation Demo
   Turns on solenoid for air puff, sucrose, and vacuum after a tone. Do so repeatedly.
*/
   
// -- INITIALIZE PINS -- //
   pinMode(solPin_air, OUTPUT);
   pinMode(solPin_liquid, OUTPUT);
   pinMode(vacPin, OUTPUT);
   pinMode(speakerPin, OUTPUT);
}


void loop() {
  delay(1000); // wait 1s
  tone(speakerPin, 1000, 500); // play 1kHz tone for 0.5s
  delay(500); // wait 0.5s
  digitalWrite(solPin_air, HIGH); // open air solenoid
  delay(25); // wait 25 ms
  digitalWrite(solPin_air, LOW); // close air solenoid
  delay(2000); // wait 2s
  tone(speakerPin, 3000, 500); // play 3kHz tone for 0.5s
  digitalWrite(solPin_liquid, HIGH); // open liquid solenoid
  delay(5); // wait 5 ms, any longer the water droplet falls, any shorter the solenoid doesn't open
  digitalWrite(solPin_liquid, LOW); // close solenoid for liquid
  delay(800); // wait 800 ms, any longer the droplet falls
  digitalWrite(vacPin, HIGH); // open vacuum solenoid
  delay(3000); //wait 3 seconds
  digitalWrite(vacPin, LOW); // close vacuum solenoid
  delay(5000); // wait for five seconds

}
