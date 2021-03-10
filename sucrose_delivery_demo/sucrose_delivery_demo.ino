// Testing code for Arduino control of Bruker 2P Set up for Team Specialk
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
// NOTE 5/8/21: Testing is being done with water.


//// PIN ASSIGNMENT ////
// input
// none established yet
// plan on adding lick sensing and pressure sensing for airpuff
// output
// const int solPin_air = 13; // solenoid for air puff control
const int solPin_liquid = 12; // solenoid for liquid control: sucrose, water, EtOH
const int vacPin = 11; // solenoid for vacuum control

// NIDAQ input
// none established yet
// using template from DISC_V7, credited above
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
   Sucrose Demo
   Turns on solenoid for sucrose quickly, activate vacuum, and do so repeatedly.
*/
   
// -- INITIALIZE PINS -- //
//    pinMode(solPin_air, OUTPUT);
   pinMode(solPin_liquid, OUTPUT);
   pinMode(vacPin, OUTPUT);
}


void loop() {
//    digitalWrite(solPin_air, HIGH); // turn the LED on (HIGH is the voltage level)
   digitalWrite(solPin_liquid, HIGH); // open solenoid for liquid
   delay(5); // wait 5 ms, any longer the water droplet falls, any shorter the solenoid doesn't open
   digitalWrite(solPin_liquid, LOW); // close solenoid for liquid
   delay(800); // wait 800 ms, any longer the droplet falls
   digitalWrite(vacPin, HIGH); // open solenoid for vacuum
   delay(3000); //wait 3 seconds
   digitalWrite(vacPin, LOW); // close solenoid for vacuum
   delay(5000); // wait for a second

}
