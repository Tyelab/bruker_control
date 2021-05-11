// Control code for Arduino and Matlab integration of headfix-room training boxes
// Discrimination task with liquid delivery as positive and air puff as negative
// Jeremy Delahanty Mar. 2021, Dexter Tsin Apr. 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
// digitalWriteFast.h written by Watterott Electronic https://github.com/watterott/Arduino-Libs/tree/master/digitalWriteFast
// SerialTransfer.h written by PowerBroker2 https://github.com/PowerBroker2/SerialTransfer

//// PACKAGES ////
#include <Adafruit_MPR121.h> // Adafruit MPR121 capicitance board recording
#include <digitalWriteFast.h> // Speeds up communication for digital srite
#include <Wire.h> // Enhances comms with MPR121
//#include <SerialTransfer.h> // Enables serial comms between Python config and Arduino
// rename SerialTransfer to myTransfer
//SerialTransfer myTransfer;

//// BITSHIFT OPERATIONS DEF: CAPACITANCE ////
#ifndef _BV
#define _BV(bit) (1 << (bit)) // capacitance detection using bitshift operations, need to learn about what these are - JD
#endif

//// PIN ASSIGNMENT: Stimuli and Solenoids ////
// input
const int lickPin = 2; // input from MPR121
//const int airPin = 3; // measure delay from solenoid to mouse
// output
const int LEDpin = 11; // output for camera
const int solPin_air = 31; // solenoid for air puff control
const int vacPin = 24; // solenoid for vacuum control
const int solPin_liquid = 33; // solenoid for liquid control: sucrose, water, EtOH
const int speakerPin = 12; // speaker control pin
const int imageTrigger = 13;

//// PIN ASSIGNMENT: NIDAQ ////
const int NIDAQ_READY = 35; // how do we do this with Bruker?
// NIDAQ output
const int airDeliveryPin = 37; // airpuff delivery
const int sucroseDeliveryPin = 39; // sucrose delivery
const int lickDetectPin = 41; // detect sucrose licks
const int speakerDeliveryPin = 43; // noise delivery


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
boolean sucrose = false;
boolean airpuff = false;
boolean noise = false;
boolean noiseDAQ = false;
boolean trigWait = false;

//// -- MATLAB ENTERED VARIABLES -- ////

// <*/VAR TARGET\*> //

///////////////////////////////////////

//// EXPERIMENT VARIABLES ////
//// For Manual Input ////
//const int totalNumberOfTrials = 30;
//const int baseITI = 3000; // 3 inter-trial interval
//const int baseNoiseDuration = 500;
//const int USDeliveryTime_Sucrose = 200; // opens Sucrose solenoid for 50 ms, currently 5ms b/c using water 3-30-21
//const int USDeliveryTime_Air = 10; // opens airpuff solenoid for 10 ms
//const int USConsumptionTime_Sucrose = 1000; // wait 1s for animal to consume, currently 800ms b/c using water 3-30-21
//const int minITIJitter = 500; // min inter-trial jitter
//const int maxITIJitter = 1000; // max inter-trial jitter
//const int minNoiseJitter = 0; // min inter-trial jitter
//const int maxNoiseJitter = 2000; // max inter-trial jitter
//const int percentNegativeTrials = 50;


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
long noiseDeliveryMS;
long noiseListeningMS;
long noiseDAQMS;

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
int ITIArray[totalNumberOfTrials];
int noiseDurationArray[totalNumberOfTrials];
int trialTypeArray[totalNumberOfTrials];


//// SETUP ////
void setup() {
  // -- DEFINE BITRATE -- //
  // Serial debugging on COM13, use Ctrl+Shift+M
  Serial.begin(9600);

  while (!Serial) { // needed to keep leonardo/micro from starting too fast!
    delay(10);
  }
  
  // -- DEFINE PINS -- //
  // input
  pinMode(lickPin, INPUT);
  //output
  pinMode(LEDpin, OUTPUT);
  pinMode(solPin_air, OUTPUT);
  pinMode(solPin_liquid, OUTPUT);
  pinMode(vacPin, OUTPUT);
  pinMode(speakerPin, OUTPUT);
  pinMode(speakerDeliveryPin, OUTPUT);
  pinMode(imageTrigger, OUTPUT);
  pinMode(lickDetectPin, OUTPUT);

  // -- INITIALIZE TOUCH SENSOR -- //
  Serial.println("MPR121 check...");
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);
  } // need to learn what value 0x5A represents - JD
  Serial.println("MPR121 found!");

  // -- POPULATE DELAY TIME ARRAYS -- //
  fillDelayArray(ITIArray, totalNumberOfTrials, baseITI, minITIJitter, maxITIJitter);
  fillDelayArray(noiseDurationArray, totalNumberOfTrials, baseNoiseDuration, minNoiseJitter, maxNoiseJitter);

  // -- INITIALIZE TRIAL TYPES -- //
  defineTrialTypes(totalNumberOfTrials, percentNegativeTrials);

  // -- WAIT FOR SIGNAL THAT DAQ IS ONLINE -- //
  //MATLAB_VALUE = digitalRead(NIDAQ_READY);
  //while (MATLAB_VALUE == LOW) {
  //  MATLAB_VALUE = digitalRead(NIDAQ_READY);
  //}

  newTrial = true;
}

//// THE BIZ ////
void loop() {
  if (currentTrial < totalNumberOfTrials) {
    ms = millis();
    lickDetect();
    startITI(ms);
    tonePlayer(ms);
    onTone(ms);
    USDelivery(ms);
    offSolenoid(ms);
  }
}

//// TRIAL FUNCTIONS ////
void lickDetect() {
  currtouched = cap.touched(); // Get currently touched contacts
  // if it is *currently* touched and *wasn't* touched before, alert!
  if ((currtouched & _BV(2)) && !(lasttouched & _BV(2))) {            ///// CHANGED PIN LATER!!
    digitalWriteFast(lickDetectPin, HIGH);
  }
  // if it *was* touched and now *isn't*, alert!
  if (!(currtouched & _BV(2)) && (lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, LOW);
  }
  lasttouched = currtouched;
}

void startITI(long ms) {
  if (newTrial) {                                 // start new ITI
    Serial.print("staring trial ");
    Serial.println(currentTrial);
    trialType = trialTypeArray[currentTrial];     // assign trial type
    newTrial = false;
    ITI = true;
    int thisITI = ITIArray[currentTrial];         // get ITI for this trial
    ITIend = ms + thisITI;
    trigWait = true;
    // turn off when done
  } else if (trigWait && (ms >= ITIend - baseline) && (ms <= ITIend)) {
    // tell Bruker to start imaging
    digitalWriteFast(imageTrigger, HIGH);
    Serial.println("imaging trigger fired!");
    trigWait = false;    
  } else if (ITI && (ms >= ITIend)) {             // ITI is over
    // turn off imaging trigger
    digitalWriteFast(imageTrigger, LOW);
    ITI = false;
    noise = true;
  }
}

void tonePlayer(long ms) {
  if (noise) {
    Serial.println("Playing Tone");
    int thisNoiseDuration = noiseDurationArray[currentTrial];
    noise = false;
    noiseDAQ = true;
    noiseListeningMS = ms + thisNoiseDuration;
    digitalWriteFast(speakerDeliveryPin, HIGH);
    switch (trialType) {
      case 0:
        Serial.println("AIR");
        LED(50);
        tone(speakerPin, 2000, thisNoiseDuration);
        break;
      case 1:
        Serial.println("SUCROSE");
        LED(50);
        tone(speakerPin, 9000, thisNoiseDuration);
        break;
    }
  }
}

void onTone(long ms) {
  if (noiseDAQ && (ms >= noiseListeningMS)){
    noiseDAQ = false;
    digitalWriteFast(speakerDeliveryPin, LOW);
    newUSDelivery = true;
  }
}

void USDelivery(long ms) {
  if (newUSDelivery) {
    Serial.println("Delivering US");
    Serial.println(trialType);
    newUSDelivery = false;
    solenoidOn = true;
    switch (trialType) {
      case 0: 
        Serial.println("Delivering Airpuff");
        USDeliveryMS = (ms + USDeliveryTime_Air);
        digitalWriteFast(airDeliveryPin, HIGH);
        digitalWriteFast(solPin_air, HIGH);
        delay(50);
        break;
      case 1:
        Serial.println("Delivering Sucrose");
        USDeliveryMS = (ms + USDeliveryTime_Sucrose);
        digitalWriteFast(solPin_liquid, HIGH);
        digitalWriteFast(sucroseDeliveryPin, HIGH);
        break;
    }
  }
}

void offSolenoid(long ms) {
  if (solenoidOn && (ms >= USDeliveryMS)) {
    solenoidOn = false;
    newTrial = true;
    currentTrial++;
    switch (trialType) {
      case 0:
        Serial.println("air solenoid off");
        digitalWriteFast(airDeliveryPin, LOW);
        digitalWriteFast(solPin_air, LOW);
        delay(30);
        break;
      case 1:
        Serial.println("liquid solenoid off");
        sucroseConsumptionMS = (ms + USConsumptionTime_Sucrose);
        digitalWriteFast(solPin_liquid, LOW);
        digitalWriteFast(sucroseDeliveryPin, LOW);
        break;
    }
  }
}
