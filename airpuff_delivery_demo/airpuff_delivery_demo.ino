// Control code for Arduino management of Bruker 2P Air Demo
// Jeremy Delahanty Mar. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019

//// PACKAGES ////
#include <digitalWriteFast.h> // Speeds up communication for digital serial writing
#include <Wire.h> // Further enhance comms


//// PIN ASSIGNMENT: Stimuli and Solenoid ////
const int solPin_air = 22; // solenoid for airpuff control
const int speakerPin = 12; // speaker control pin
const int sessionRunning = 8;

//// PIN ASSIGNMENT: NIDAQ ////
const int airDeliveryPin = 25;
const int speakerDeliveryPin = 14;

//// VARIABLE ASSIGNEMNT ////
long ms;
// flags
boolean newTrial = false;
boolean ITI = false;
boolean newUSDelivery = false;
boolean solenoidOn = false;
boolean airpuff = false;
boolean noise = false;

//// EXPERIMENT VARIABLES ////
const int totalNumberOfTrials = 5;
const int percentNegativeTrials = 100;
const int baseITI = 5000;
const int USDeliveryTime_Air = 20;

// stop times
long ITIend;
long airDelayMS;
long USDeliveryMS_Air;
long USDeliveryMS;

// trial variables (0 negative [air]): This demo introduces air ONLY
int trialType;
int currentTrial = 0;

// arrays
int trialTypeArray[totalNumberOfTrials];
int ITIArray[totalNumberOfTrials];
byte trialIndex = 0;



void setup() {
  // -- DEFINE BITRTE -- //
  Serial.begin(9600);

  // -- DEFINE PINS -- //
  // input
  // none
  // output
  pinMode(solPin_air, OUTPUT);
  pinMode(speakerPin, OUTPUT);
  pinMode(speakerDeliveryPin, OUTPUT);
  pinMode(sessionRunning, OUTPUT);

  digitalWriteFast(solPin_air, LOW);
  digitalWriteFast(airDeliveryPin, LOW);

  // -- INITIALIZE TRIAL TYPES -- //
  defineTrialTypes(totalNumberOfTrials, percentNegativeTrials);

  // -- POPULATE DELAY TIME ARRAYS -- //
  fillDelayArray(ITIArray, totalNumberOfTrials, baseITI, 0, 0);

  // -- delay to allow start of T-Series -- //
  Serial.println("Delay...");
  delay(10000);

  // Notify of start...
  Serial.println("Starting...");
  newTrial = true;
  newUSDelivery = false;
  digitalWriteFast(sessionRunning,HIGH);
}

void loop() {
  if (currentTrial <= totalNumberOfTrials) {
    ms = millis();
    startITI(ms);
    //tonePlayer(ms);
    USDelivery(ms);
    onSolenoid(ms);
  }

}

void startITI(long ms) {
  if (newTrial) {                                 // start new ITI
    Serial.print("staring trial ");
    Serial.println(currentTrial);
    trialType = trialTypeArray[currentTrial];     // assign trial type
    newTrial = false;
    ITI = true;
    noise = true;
    int thisITI = ITIArray[currentTrial];         // get ITI for this trial
    if (currentTrial == totalNumberOfTrials) {
      thisITI = baseITI;
    }
    Serial.println(thisITI);
    ITIend = ms + thisITI;
    // turn off when done
  } else if (ITI && (ms >= ITIend)) {             // ITI is over
    ITI = false;
    newUSDelivery = true;
    if (currentTrial == totalNumberOfTrials) {
      ITI = true;
      newUSDelivery = false;
      digitalWriteFast(sessionRunning,LOW);
      }
    }
}

void tonePlayer(long ms) {
  if (noise) {
    Serial.println("playing tone");
    switch (trialType) {
      case 0:
        Serial.println("playing air tone");
        tone(speakerPin, 2000, 2000);
        noise = false;
        break;
    }
  }
}

void USDelivery(long ms) {
  if (newUSDelivery) {
    Serial.print("delivering us type ");
    Serial.println(trialType);
    switch (trialType) {
      case 0: 
        Serial.println("delivering airpuff");
        newUSDelivery = false;
        solenoidOn = true;
        USDeliveryMS = (ms + USDeliveryTime_Air);
        digitalWriteFast(solPin_air, HIGH);
        digitalWriteFast(airDeliveryPin, HIGH);
        break;
    }
  }
}

void onSolenoid(long ms) {
  if (solenoidOn && (ms >= USDeliveryMS)) {
    switch (trialType) {
      case 0:
        Serial.println("air solenoid off");
        solenoidOn = false;
        digitalWriteFast(solPin_air, LOW);
        digitalWriteFast(airDeliveryPin, LOW);
        newTrial = true;
        currentTrial++;
        break;
    }
  }
}

////// ARRAY FUNCTIONS ////
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
