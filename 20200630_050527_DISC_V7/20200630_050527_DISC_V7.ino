// Discrimination Task
// Mauri van der Huevel, Kyle Fischer, Oct. 2019
// Updated for two vacuum solenoids Jun. 2020 

#include <Adafruit_MPR121.h>
#include <digitalWriteFast.h>
#include <Wire.h> //enhances communication with MPR121

#ifndef _BV
#define _BV(bit) (1 << (bit)) // capacitance detection using bitshift operations
#endif

//// PIN ASSIGNMENT ////
// input
const int lickPin = 2;      // unused
//output
const int solPinPos = 4;    // right spout
const int solPinNeg = 5;    // left spout
const int vacPinPos = 22;
const int vacPinNeg = 24;

// NIDAQ input
const int NIDAQ_READY = 9;
// NIDAQ output
const int USDeliveryPos = 10;
const int USDeliveryNeg = 11;
const int lickDetectPinPos = 12;
const int lickDetectPinNeg = 13;


//// VARIABLE ASSIGNMENT ////
long ms;
// flags
boolean needVariables = true;
boolean newTrial = false;
boolean ITI = false;
boolean newUSDelivery = false;
boolean solenoidOn = false;
boolean vacOn = false;
boolean consume = false;
boolean cleanIt = false;

//// -- MATLAB ENTERED VARIABLES -- ////

const int totalNumberOfTrials = 20;
const int percentNegativeTrials = 50;
const int baseITI = 10000;


const int USDeliveryTime = 50;
const int USConsumptionTime = 1000;
const int minITIJitter = 0;
const int maxITIJitter = 0;






///////////////////////////////////////

int MATLAB_VALUE = 0;
// stop times
long ITIend;
long rewardDelayMS;
long USDelayMS;
long USDeliveryMS;
long USConsumptionMS;
long vacTime;
// trial variables (0 negative, 1 positive);
int trialType;
int currentTrial = 0;
// lick variables
Adafruit_MPR121 cap = Adafruit_MPR121();
uint16_t currtouched = 0;
uint16_t lasttouched = 0;

// vac variables
const int vacDelay = 500;

// arrays
int trialTypeArray[totalNumberOfTrials];
int ITIArray[totalNumberOfTrials];

//////////////////////////////////////////////////////////////////////////////////////////////////////

//// SETUP ////
void setup() {
  Serial.begin(9600);

  // -- INITIALIZE TOUCH SENSOR -- //
  Serial.println("MPR121 capacitive touch sensor check");
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);                                                  // turn off for debugging
  }
  Serial.println("MPR121 found!");

  //  // -- INCREASE TOUCH SENSITIVITY -- //
  //  cap.setThresholds(3,3);

  // -- INITIALIZE PINS -- //
  pinMode(NIDAQ_READY, INPUT);
  pinMode(solPinNeg, OUTPUT);
  pinMode(solPinPos, OUTPUT);
  pinMode(USDeliveryPos, OUTPUT);
  pinMode(USDeliveryNeg, OUTPUT);
  pinMode(lickDetectPinPos, OUTPUT);
  pinMode(lickDetectPinNeg, OUTPUT);

  // -- INITIALIZE TRIAL TYPES -- //
  defineTrialTypes(totalNumberOfTrials, percentNegativeTrials);

  // -- POPULATE DELAY TIME ARRAYS -- //
  fillDelayArray(ITIArray, totalNumberOfTrials, baseITI, minITIJitter, maxITIJitter);

  // -- WAIT FOR MATLAB SIGNAL THAT DAQ IS ONLINE-- //
  MATLAB_VALUE = digitalRead(NIDAQ_READY);
  while (MATLAB_VALUE == LOW) {
    MATLAB_VALUE = digitalRead(NIDAQ_READY);
  }

  // -- FIRE IT UP! -- //
  delay(5000);                                   // allow time for matlab to catch up
  newTrial = true;
  Serial.println("Starting!");
}

//// THE BIZ ////
void loop() {
  if (currentTrial < totalNumberOfTrials) {
    ms = millis();
    lickDetect();                                 // Measures capacitance on spouts to detect licking
    startITI(ms);
    USDelivery(ms);
    vacuum(ms);
  }
}

//// TRIAL FUNCTIONS ////
void lickDetect() {
  currtouched = cap.touched(); // Get the currently touched pads
  // it if *is* touched and *wasnt* touched before, alert!
  if ((currtouched & _BV(1)) && !(lasttouched & _BV(1)) ) {
    digitalWriteFast(lickDetectPinPos, HIGH);
  }
  if ((currtouched & _BV(2)) && !(lasttouched & _BV(2)) ) {
    digitalWriteFast(lickDetectPinNeg, HIGH);
  }
  // if it *was* touched and now *isnt*, alert!
  if (!(currtouched & _BV(1)) && (lasttouched & _BV(1)) ) {
    digitalWriteFast(lickDetectPinPos, LOW);
  }
  if (!(currtouched & _BV(2)) && (lasttouched & _BV(2)) ) {
    digitalWriteFast(lickDetectPinNeg, LOW);
  }
  lasttouched = currtouched;
}

void startITI(long ms) {
  if (newTrial) {                               // start new ITI
    trialType = trialTypeArray[currentTrial];   // assign trial type
    newTrial = false;
    ITI = true;
    int thisITI = ITIArray[currentTrial];       // get ITI for this trial
    ITIend = ms + thisITI;
    // turn off when done
  } else if (ITI && (ms  >= ITIend)) {          // ITI is over
    ITI = false;
    newUSDelivery = true;
  }
}

void USDelivery(long ms) {
  if (newUSDelivery) {                                // start US delivery
    newUSDelivery = false;
    solenoidOn = true;
    USDeliveryMS = (ms + USDeliveryTime);
    switch (trialType) {
      case 0:                                         // negative US
        digitalWriteFast(solPinNeg, HIGH);
        digitalWriteFast(USDeliveryNeg, HIGH);
        break;
      case 1:                                         // positive US
        digitalWriteFast(solPinPos, HIGH);
        digitalWriteFast(USDeliveryPos, HIGH);
        break;
    }
  } else if (solenoidOn && (ms >= USDeliveryMS)) {    // turn off when done
    solenoidOn = false;
    consume = true;
    USConsumptionMS = (ms + USConsumptionTime);
    digitalWriteFast(solPinNeg, LOW);
    digitalWriteFast(solPinPos, LOW);
    digitalWriteFast(USDeliveryNeg, LOW);
    digitalWriteFast(USDeliveryPos, LOW);
  } else if (consume && (ms >= USConsumptionMS)) {            // move on after allowed to consume
    consume = false;
    cleanIt = true;
  }
}

void vacuum(long ms) {
  if (cleanIt) {                                // start US delivery
    cleanIt = false;
    vacOn = true;
    vacTime = ms + vacDelay;
    switch (trialType) {
      case 0:                                         // negative US
        digitalWriteFast(vacPinNeg, HIGH);
        break;
      case 1:                                         // positive US
        digitalWriteFast(vacPinPos, HIGH);
        break;
    }
  } else if (vacOn && (ms >= vacTime)) {    // turn off when done
    vacOn = false;
    digitalWriteFast(vacPinPos, LOW);
    digitalWriteFast(vacPinNeg, LOW);
    newTrial = true;
    currentTrial++;
  }
}

//// ARRAY FUNCTIONS ////
void defineTrialTypes(int trialNumber, float percentNeg) {
  // initialize array with all positive (1) trials
  for (int i = 0; i < trialNumber; i++) {
    trialTypeArray[i] = 1;
  }
  if (percentNeg > 0) {
    randomSeed(analogRead(0));
    int negTrialNum = round(trialNumber * (percentNeg / 100));
    // randomly choose negTrialNum indexs to make negative (0) trials
    int indexCount = 0;
    while (indexCount < negTrialNum) {
      int negIndex = random(trialNumber);
      // only make negative if it isn't already
      if (trialTypeArray[negIndex]) {
        trialTypeArray[negIndex] = 0;
        indexCount++;
      }
    }
  }
}

void fillDelayArray(int delayArray[], int trialNumber, int baseLength, int minJitter, int maxJitter) {
  randomSeed(analogRead(0));
  // initialize array with all positive (1) trials
  for (int i = 0; i < trialNumber; i++) {
    delayArray[i] = baseLength + random(minJitter, maxJitter);
  }
}
