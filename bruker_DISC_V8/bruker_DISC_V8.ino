// Control code for Arduino Delivery of Stimuli for Bruker 2P Experiments
// Jeremy Delahanty, Kyle Fischer May 2021
// Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
// digitalWriteFast.h written by Watterott Electronic https://github.com/watterott/Arduino-Libs/tree/master/digitalWriteFast
// SerialTransfer.h written by PowerBroker2 https://github.com/PowerBroker2/SerialTransfer

//// PACKAGES ////
#include <Adafruit_MPR121.h> // Adafruit MPR121 capicitance board recording
#include <digitalWriteFast.h> // Speeds up communication for digital write
#include <Wire.h> // Enhances comms with MPR121
#include <SerialTransfer.h> // Enables serial comms between Python config and Arduino
// rename SerialTransfer to myTransfer
SerialTransfer myTransfer;

//// EXPERIMENT METADATA ////
// The maximum number of trials that can be run for a given experiment is 45
// Anything larger requires multiple packets for transmission and also keep
// the animal headfixed for too long.
const int MAX_NUM_TRIALS = 45;
// Metadata is received as a struct and then renamed metadata
struct __attribute__((__packed__)) metadata_struct {
  uint8_t totalNumberOfTrials;              // total number of trials for experiment
  uint32_t trialNumber;                     // set trial number for transmission
  uint16_t noiseDuration;                   // length of tone played by speaker
  uint16_t punishTone;                      // airpuff frequency tone in Hz
  uint16_t rewardTone;                      // sucrose frequency tone in Hz
  uint8_t USDeliveryTime_Sucrose;           // amount of time to open sucrose solenoid
  uint8_t USDeliveryTime_Air;               // amount of time to open air solenoid
  uint16_t USConsumptionTime_Sucrose;       // amount of time to wait for sucrose consumption
} metadata;

//// EXPERIMENT ARRAYS ////
// The order of stimuli to deliver is stored in the trial array
// This is transmitted from Python to the Arduino
int32_t trialArray[MAX_NUM_TRIALS];
// The ITI for each trial is transmitted from Python to the Arduino
int32_t ITIArray[MAX_NUM_TRIALS];
// The amount of time a tone is played is sotred in its own array
int noiseDurationArray[MAX_NUM_TRIALS];

//// TRIAL TYPES ////
// trial variables are encoded as 0 and 1
// 0 is negative stimulus [air], 1 is  positive stimulus [sucrose]
// Initialize the trial type as an integer
int trialType;
// Initialize the current trial number as 0 before experiment begins
int currentTrial = 0;

//// FLAG ASSIGNMENT ////
// Flags can be categorized by purpose:
// Serial Transfer Flags
boolean acquireMetaData = true;
boolean acquireTrials = false;
boolean acquireITI = false;
// Experiment State Flags
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

//// TIMING VARIABLES ////
// Time is measured in milliseconds for this program
long ms; // milliseconds
// Each experimental condition has a time parameter
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
// Vacuum has a set amount of time to be active
const int vacDelay = 500; // vacuum delay


//// ADAFRUIT MPR121 ////
// Lick Sensor Variables
Adafruit_MPR121 cap = Adafruit_MPR121(); // renames MPR121 functions to cap
uint16_t currtouched = 0; // not sure why unsigned 16int used, why not long? - JD
uint16_t lasttouched = 0;

//// BITSHIFT OPERATIONS DEF: CAPACITANCE ////
#ifndef _BV
#define _BV(bit) (1 << (bit)) // capacitance detection using bitshift operations, need to learn about what these are - JD
#endif


//// PIN ASSIGNMENT: Stimuli and Solenoids ////
// input
const int lickPin = 2; // input from MPR121
//const int airPin = 3; // measure delay from solenoid to mouse
// output
const int solPin_air = 22; // solenoid for air puff control
const int vacPin = 24; // solenoid for vacuum control
const int solPin_liquid = 26; // solenoid for liquid control: sucrose, water, EtOH
const int speakerPin = 12; // speaker control pin
const int bruker2PTriggerPin = 11; // trigger to start Bruker 2P Recording on Prairie View

//// PIN ASSIGNMENT: NIDAQ ////
const int NIDAQ_READY = 9; // how do we do this with Bruker?
// NIDAQ output
const int airDeliveryPin = 23; // airpuff delivery
const int sucroseDeliveryPin = 27; // sucrose delivery
const int lickDetectPin = 41; // detect sucrose licks
const int speakerDeliveryPin = 51; // noise delivery

//// RECIEVE METADATA FUNCTIONS ////
// These three functions will be run in order.
// The metadata is first received to initialize correct sizes for arrays
int metadata_rx() {
  if (acquireMetaData) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(metadata);
      Serial.println("Received Metadata");

      myTransfer.sendDatum(metadata);
      Serial.println("Sent Metadata");
      
      acquireMetaData = false;
      acquireTrials = true;
    }
  }
}
// Next, an array of trials to run is received and stored.
int trials_rx() {
  if (acquireTrials) {
    if (myTransfer.available())
    {
      // trialArray = trialArray[metadata.totalNumberOfTrials]; something like this?
      myTransfer.rxObj(trialArray);
      Serial.println("Received Trial Array");

      myTransfer.sendDatum(trialArray);
      Serial.println("Sent Trial Array");

      acquireTrials = false;
      acquireITI = true;
    }
  }
}
// Finally, an array of ITI values are received and stored.
int iti_rx() {
  if (acquireITI) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(ITIArray);
      Serial.println("Received ITI Array");

      myTransfer.sendDatum(ITIArray);
      Serial.println("Sent ITI Array");
      acquireITI = false;
      digitalWriteFast(bruker2PTriggerPin, HIGH);
      Serial.println("Sent Bruker Trigger!");
      digitalWriteFast(bruker2PTriggerPin, LOW)
      newTrial = true;
    }
  }
}

//// TRIAL FUNCTIONS ////
// Lick Function
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
    Serial.print("staring trial ");
    Serial.println(currentTrial);
    trialType = trialArray[currentTrial];     // assign trial type
    newTrial = false;
    ITI = true;
    int thisITI = ITIArray[currentTrial];         // get ITI for this trial
    ITIend = ms + thisITI;
    // turn off when done
  } else if (ITI && (ms >= ITIend)) {             // ITI is over
    ITI = false;
    newUSDelivery = true;
    noise = true;
    noiseDAQ = true;
  }
}

// Noise Functions
// play tone function
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
        tone(speakerPin, 2000, thisNoiseDuration);
        break;
      case 1:
        Serial.println("SUCROSE");
        tone(speakerPin, 9000, thisNoiseDuration);
        break;
    }
  }
}

// tone delivery timer function; removed...
//void toneDelivery(long ms) {
//  if (noiseDAQ && (ms <= noiseListeningMS)) {
//    digitalWriteFast(speakerDeliveryPin, HIGH);
//    noiseDAQMS = ms + noiseDuration;
//  }
//}


void onTone(long ms) {
  if (noiseDAQ && (ms >= noiseListeningMS)){
    digitalWriteFast(speakerDeliveryPin, LOW);
    noiseDAQ = false;
    noise = false;
  }
}


void USDelivery(long ms) {
  if (newUSDelivery && (ms >= noiseListeningMS)) {
    Serial.println("Delivering US");
    Serial.println(trialType);
    switch (trialType) {
      case 0: 
        Serial.println("Delivering Airpuff");
        newUSDelivery = false;
        solenoidOn = true;
        USDeliveryMS = (ms + metadata.USDeliveryTime_Air);
        digitalWriteFast(solPin_air, HIGH);
        digitalWriteFast(airDeliveryPin, HIGH);
        break;
      case 1:
        Serial.println("Delivering Sucrose");
        newUSDelivery = false;
        solenoidOn = true;
        USDeliveryMS = (ms + metadata.USDeliveryTime_Sucrose);    
        digitalWriteFast(solPin_liquid, HIGH);
        digitalWriteFast(sucroseDeliveryPin, HIGH);
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
      case 1:
        Serial.println("liquid solenoid off");
        solenoidOn = false;
        consume = true;
        sucroseConsumptionMS = (ms + metadata.USConsumptionTime_Sucrose);
        digitalWriteFast(solPin_liquid, LOW);
        digitalWriteFast(sucroseDeliveryPin, LOW);
        break;
    }
  }
}

void consuming(long ms){
  if (consume && (ms >= sucroseConsumptionMS)) {         // move on after allowed to consume
    Serial.println("consuming...");
    consume = false;
    cleanIt = true;
  }
}

// Vacuum Control
void vacuum(long ms) {
  if (cleanIt) {
    Serial.println("cleaning...");
    cleanIt = false;
    vacOn = true;
    vacTime = ms + vacDelay;
    digitalWriteFast(vacPin, HIGH);
  }
  else if (vacOn && (ms >= vacTime)) {
    Serial.println("stop cleaning...");
    vacOn = false;
    digitalWriteFast(vacPin, LOW);
    newTrial = true;
    currentTrial++;
  }
}

//// SETUP ////
void setup() {
  // -- DEFINE BITRATE -- //
  // Serial debugging on COM13, use Ctrl+Shift+M
  Serial.begin(115200);

  // Serial transfer of trials on UART Converter COM port
  Serial1.begin(115200);
  myTransfer.begin(Serial1, true);
  
  // -- DEFINE PINS -- //
  // input
  pinMode(lickPin, INPUT);
  //output
  pinMode(solPin_air, OUTPUT);
  pinMode(solPin_liquid, OUTPUT);
  pinMode(vacPin, OUTPUT);
  pinMode(speakerPin, OUTPUT);
  pinMode(speakerDeliveryPin, OUTPUT);
  pinMode(lickDetectPin, OUTPUT);
  pinMode(bruker2PTriggerPin, OUTPUT);

  // -- INITIALIZE TOUCH SENSOR -- //
  Serial.println("MPR121 check...");
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);
  } // need to learn what value 0x5A represents - JD
  Serial.println("MPR121 found!");
}

//// THE BIZ ////
void loop() {
  metadata_rx();
  trials_rx();
  iti_rx();
  if (currentTrial < metadata.totalNumberOfTrials) {
    ms = millis();
    lickDetect();
    startITI(ms);
    tonePlayer(ms);
    onTone(ms);
    USDelivery(ms);
    onSolenoid(ms);
    consuming(ms);
    vacuum(ms);
  }
}
