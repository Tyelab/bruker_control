// Control code for Arduino management of Bruker 2P setup for Team Specialk
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019

//// PACKAGES ////
#include <Adafruit_MPR121.h> // Adafruit MPR121 capicitance board recording
#include <digitalWriteFast.h> // Speeds up communication for digital Write
#include <Wire.h> // enhances comms with MPR121
#include <Volume.h> // hardware free volume control package

// Volume package settings
Volume vol; // rename Volume to vol


//// BITSHIFT OPERATIONS DEF: CAPACITANCE ////
#ifndef _BV
#define _BV(bit) (1 << (bit)) // capacitance detection using bitshift operations, need to learn about what these are - JD
#endif

//// PIN ASSIGNMENT: Stimuli and Solenoids ////
// input
const int lickPin = 2; // input from MPR121
//const int airPin = 3; // measure delay from solenoid to mouse
// output
const int solPin_air = 13; // solenoid for air puff control
const int solPin_liquid = 12; // solenoid for liquid control: sucrose, water, EtOH
const int vacPin = 11; // solenoid for vacuum control
const int speakerPin = 4; // using default Volume package pin


//// PIN ASSIGNMENT: NIDAQ ////
const int NIDAQ_READY = 9; // how do we do this with Bruker?
// NIDAQ output
const int sucroseDeliveryPin = 20; // sucrose delivery
const int airDeliveryPin = 22; // airpuff delivery
const int lickDetectPin = 23; // detect sucrose licks

//// VARIABLE ASSIGNMENT ////
long ms; // is this for milliseconds?
// flags; need to have some of these explained
boolean needVariables = true;
boolean newTrial = false;
boolean ITI = false;
boolean newUSDelivery = false;
boolean solenoidOn = false;
boolean vacOn = false;
boolean consume = false;
boolean cleanIt = false;

//// EXPERIMENT VARIABLES ////
const int totalNumberOfTrials = 20;
const int percentNegativeTrials = 50;
const int baseITI = 10000; // 10s inter-trial interval
const int USDeliveryTime_Sucrose = 50; // opens Sucrose solenoid for 50 ms
const int USDeliveryTime_Air = 10; // opens airpuff solenoid for 10 ms
const int USConsumptionTime_Sucrose = 1000; // wait 1s for animal to consume
const int minITIJitter = 0; // min inter-trial jitter
const int maxITIJitter = 0; // max inter-trial jitter

int BRUKER_VALUE = 0;

// stop times
long ITIend;
long rewardDelayMS;
long sucroseDelayMS;
long USDeliveryMS_Sucrose;
long sucroseConsumptionMS;
long vacTime;
long airDelayMS;
long USDeliveryMS_Air;
long USDeliveryMS;

// trial variables (0 negative [air], 1 positive [sucrose])
int trialType;
int currentTrial = 0;

// lick variables
Adafruit_MPR121 cap = Adafruit_MPR121(); // renames MPR121 functions to cap? - JD
uint16_t currtouched = 0; // not sure why unsigned 16int used, why not long? - JD
uint16_t lasttouched = 0;

// vac variables
const int vacDelay = 500; // vacuum delay

// arrays
int trialTypeArray[totalNumberOfTrials];
int ITIArray[totalNumberOfTrials];



//// SETUP ////
void setup() {
  // define bitrate
  Serial.begin(9600);

//  vol.begin();
//  vol.alternatePin(false); // If true, use pin 13, if false, use pin 4

  // -- INITIALIZE TOUCH SENSOR -- //
  Serial.println("MPR121 capacitive touch sensor check");
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);
  } // need to learn what value 0x5A represents - JD
  Serial.println("MPR121 found!");

  // -- INITIALIZE TRIAL TYPES -- //
  defineTrialTypes(totalNumberOfTrials, percentNegativeTrials);

  // -- POPULATE DELAY TIME ARRAYS -- //
  fillDelayArray(ITIArray, totalNumberOfTrials, baseITI, minITIJitter, maxITIJitter);

  // -- WAIT FOR SIGNAL THAT DAQ IS ONLINE -- //
  BRUKER_VALUE = digitalRead(NIDAQ_READY);
  while (BRUKER_VALUE == LOW) {
    BRUKER_VALUE = digitalRead(NIDAQ_READY);
  } // what does == LOW mean? -JD
}

//// THE BIZ ////
void loop() {
  if (currentTrial < totalNumberOfTrials) {
    ms = millis();
    lickDetect();
    startITI(ms);
    USDelivery(ms);
    vacuum(ms);
  }
}

//// TRIAL FUNCTIONS ////
void lickDetect() {
  currtouched = cap.touched(); // Get currently touched contacts
  // if it is *currently* touched and *wasn't* touched before, alert!
  if ((currtouched & _BV(1)) && !(lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, HIGH);
  }
  // if it *was* touched and now *isn't*, alert!
  if (!(currtouched & _BV(1)) && (lasttouched & _BV(1))) {
    digitalWriteFast(lickDetectPin, LOW);
  }
  lasttouched = currtouched;
}

void startITI(long ms) {
  if (newTrial) {                                 // start new ITI
    trialType = trialTypeArray[currentTrial];     // assign trial type
    newTrial = false;
    ITI = true;
    int thisITI = ITIArray[currentTrial];         // get ITI for this trial
    ITIend = ms + thisITI;
    // turn off when done
  } else if (ITI && (ms >= ITIend)) {             // ITI is over
    ITI = false;
    newUSDelivery = true;
  }
}

void USDelivery(long ms) {
  if (newUSDelivery) {
    switch (trialType) {
      case 0: 
        airpuffDelivery(ms);
        break;
      case 1:
        sucroseDelivery(ms);
        break;
    }
  }
}

void sucroseTone(long ms) {
  vol.begin();
  vol.tone(2000, 255);
  vol.noTone();
  vol.end();
}

void ambiguousTone(long ms) {
  vol.begin();
  vol.tone(5500, 255);
  vol.noTone();
  vol.end();
}

void airpuffTone(long ms) {
  vol.begin();
  vol.tone(9000, 255);
  vol.noTone();
  vol.end();
}

void sucroseDelivery(long ms) {
  if (newUSDelivery) {
    sucroseTone(ms);
    newUSDelivery = false;
    solenoidOn = true;
    USDeliveryMS = (ms + USDeliveryTime_Sucrose);
    digitalWriteFast(solPin_liquid, HIGH);
    digitalWriteFast(sucroseDeliveryPin, HIGH); 
  }
  else if (solenoidOn && (ms >= USDeliveryMS)) {              // turn off when done
    solenoidOn = false;
    consume = true;
    sucroseConsumptionMS = (ms + USConsumptionTime_Sucrose);
    digitalWriteFast(solPin_liquid, LOW);
    digitalWriteFast(sucroseDeliveryPin, LOW);
  } 
  else if (consume && (ms >= USConsumptionTime_Sucrose)) {         // move on after allowed to consume
    consume = false;
    cleanIt = true;
  }
}

void airpuffDelivery(long ms) {
  if (newUSDelivery) {
    airpuffTone(ms);
    newUSDelivery = false;
    solenoidOn = true;
    USDeliveryMS = (ms + USDeliveryTime_Air);
    digitalWriteFast(solPin_air, HIGH);
    digitalWriteFast(airDeliveryPin, HIGH);
  }
  else if (solenoidOn && (ms >= USDeliveryMS_Air)) {
    solenoidOn = false;
    digitalWriteFast(solPin_air, LOW);
    digitalWriteFast(airDeliveryPin, LOW);
  }
}

// TODO: Implement ambiguous trials output with randomization between sucrose/airpuff

// Vacuum Control
void vacuum(long ms) {
  if (cleanIt) {
    cleanIt = false;
    vacOn = true;
    vacTime = ms + vacDelay;
    digitalWriteFast(vacPin, HIGH);
  }
  else if (vacOn && (ms >= vacTime)) {
    vacOn = false;
    digitalWriteFast(vacPin, LOW);
    newTrial = true;
    currentTrial++;
  }
}


//// ARRAY FUNCTIONS ////
void defineTrialTypes(int trialNumber, float percentNeg) { // TODO: generate random trial externally order and store on board?
  // initialize array with all positive (1) trials
  for (int i = 0; i < trialNumber; i++) {
    trialTypeArray[i] = 1;
  }
  if (percentNeg > 0) {
    randomSeed(analogRead(0));
    int negTrialNum = round(trialNumber * (percentNeg/100));
    // randomly choose negTrialNum indexes to make negative (0) trials
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
