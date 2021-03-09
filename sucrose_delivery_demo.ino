// Testing code for Arduino control of Bruker 2P Set up for Team Specialk
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019

//// PIN ASSIGNMENT ////
// input
// none established yet
// plan on adding lick sensing and pressure sensing for airpuff
// output
const int solPinPos_air = 13; // solenoid for air puff control
const int solPinPos_sucrose = 12; // solenoid for sucrose control
const int vacPinPos = 11; // solenoid for vacuum control

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
   Testing
   Turns on solenoids briefly, then off for one second, repeatedly.
*/
   
// -- INITIALIZE PINS -- //
   pinMode(solPinPos_air, OUTPUT);
   pinMode(vacPinPos, OUTPUT);
}


void loop() {
   digitalWrite(solPinPos_air, HIGH); // turn the LED on (HIGH is the voltage level)
   digitalWrite(vacPinPos, HIGH);
   delay(30); // wait 30ms
   digitalWrite(solPinPos_air, LOW); // turn the LED off by making the voltage LOW
   digitalWrite(vacPinPos, LOW);
   delay(1000); // wait for a second

}
