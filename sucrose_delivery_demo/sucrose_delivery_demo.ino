// Testing code for Arduino control of Bruker 2P Set up for Team Specialk
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
// NOTE 5/8/21: Testing is being done with water.

//// PACKAGES ////
#include <Adafruit_MPR121.h> // used for capacitive sensors to detect licks
#include <digitalWriteFast.h> // speeds up reading/writing to digital pins
#include <Wire.h> // enhances comms with MPR121


//// PIN ASSIGNMENT ////
// input
const int lickPin = 2; // measure lick responses from mouse, not yet implemented
// const int airPin = 3; // measure delay from solenoid to mouse, not yet implemented.
// output
const int solPin_air = 13; // solenoid for air puff control
const int solPin_liquid = 12; // solenoid for liquid control: sucrose, water, EtOH
const int vacPin = 11; // solenoid for vacuum control

// NIDAQ input
// none established yet
// using template from DISC_V7
// const int NIDAQ_READY = 9;
// // NIDAQ output
// const int USDeliveryPos = 10;
// const int USDeliveryNeg = 11;
// const int lickDetectPinPos = 12;
// const int lickDetectPinNeg = 13;

//// VARIABLE ASSIGNMENT ////
// long ms; // unsure what this does/what it's for - JD
// flags unsure what they're used for - JD
// boolean needVariables = true;
// boolean newTrial = false;
// boolean ITI = false;
// boolean newUSDelivery = false;
// boolean solenoidOn = false;
// boolean vacOn = false;
// boolean consume = false;
// boolean cleanIT = false;

//// MATLAB ENTERED VARIABLES //// unsure what the MATLAB code is here and how it works
// const int totalNumber of Trials = 20;
// const int percentNEgativeTrials = 50;
// const int baseITI = 10000;

// const int USDeliveryTime = 50;
// const int USConsumptionTime = 1000;
// const int minITIJitter = 0;
// const int maxITIJitter = 0;



/// SETUP ////

void setup() {
/*
   Stimulation Demo
   Turns on solenoid for air puff, sucrose, and vacuum. Do so repeatedly.
*/
   
// -- INITIALIZE PINS -- //
   pinMode(solPin_air, OUTPUT);
   pinMode(solPin_liquid, OUTPUT);
   pinMode(vacPin, OUTPUT);
}


void loop() {
   digitalWrite(solPin_air, HIGH); // turn the LED on (HIGH is the voltage level)
   delay(25) // wait 25 ms
   digitalWrite(solPin_air, LOW); // close air solenoid
   digitalWrite(solPin_liquid, HIGH); // open liquid solenoid
   delay(5); // wait 5 ms, any longer the water droplet falls, any shorter the solenoid doesn't open
   digitalWrite(solPin_liquid, LOW); // close solenoid for liquid
   delay(800); // wait 800 ms, any longer the droplet falls
   digitalWrite(vacPin, HIGH); // open vacuum solenoid
   delay(3000); //wait 3 seconds
   digitalWrite(vacPin, LOW); // close vacuum solenoid
   delay(5000); // wait for five seconds

}
