/*
 * Control code for Arduino using Python integration for headfixed behavior
 * Discrimination task: Liquid Sucrose = Positive, Airpuff = Negative
 * 
 * Deryn LeDuke 2019, Jeremy Delahanty Mar. 2021, Dexter Tsin Apr. 2021
 * Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
 * digitalWriteFast.h written by Watterott Electronic
 * https://github.com/watterott/Arduino-Libs/tree/master/digitalWriteFast
 * SerialTransfer.h written by PowerBroker2
 * https://github.com/PowerBroker2/SerialTransfer
 * 
 * This program is intended to run vacuumless discrimination tasks for head-fixed 
 * behavior using Python for trial structures, metadata, and timing arrays.
 * 
 * The program operates following these steps:
 *    1. Open communications to Python on Bruker PC
 *    2. Receive metadata, trial type array, ITI array, and tone duration array
 *    3. Confirm Python has finished sending data
 *    4. Delay the program for 5 seconds to allow Teledyne Genie Nano to start up
 *    5. Send a start trigger to the Bruker DAQ to start microscopy/voltage recording
 *    6. Run through trials until finished
*/

//// PACKAGES ////
#include <Adafruit_MPR121.h>              // Adafruit MPR121 capicitance board recording
#include <digitalWriteFast.h>             // Speeds up communication for digital srite
#include <Wire.h>                         // Enhances comms with MPR121
#include <SerialTransfer.h>               // Enables serial comms between Python config and Arduino

// rename SerialTransfer to myTransfer
SerialTransfer myTransfer;

//// EXPERIMENT METADATA ////
// The maximum number of trials that can be run for a given experiment is 60
const int MAX_NUM_TRIALS = 60;
// Metadata is received as a struct and then renamed metadata
// Struct allows for different datatypes of different sizes to be stored in an array
struct __attribute__((__packed__)) metadata_struct {
  uint8_t totalNumberOfTrials;              // total number of trials for experiment
  uint16_t punishTone;                      // airpuff frequency tone in Hz
  uint16_t rewardTone;                      // sucrose frequency tone in Hz
  uint8_t USDeliveryTime_Sucrose;           // amount of time to open sucrose solenoid
  uint8_t USDeliveryTime_Air;               // amount of time to open air solenoid
  uint16_t USConsumptionTime_Sucrose;       // amount of time to wait for sucrose consumption
} metadata;

//// EXPERIMENT ARRAYS ////
// The order of stimuli to deliver is stored in the trial array
// This is transmitted from Python to the Arduino
// Uses int32_t as Python ints are stored as 32bit integers
int32_t trialArray[MAX_NUM_TRIALS];
// The ITI for each trial is transmitted from Python to the Arduino
int32_t ITIArray[MAX_NUM_TRIALS];
// The amount of time a tone is transmitted from Python to the Arudino
int32_t toneArray[MAX_NUM_TRIALS];

//// PYTHON TRANSMISSION STATUS ////
// Additional control is required for running the experiment correctly.
// Python will send a final transmission that states the program is done
// sending all the relevant metadata. This will initiate the Bruker's
// imaging trigger and start the experiment.
int32_t pythonGo;
int transmissionStatus = 0;

//// TRIAL TYPES ////
// trial variables are encoded as 0 and 1
// 0 is negative stimulus [air], 1 is  positive stimulus [sucrose]
// Initialize the trial type as an integer
int trialType;
// Initialize the current trial number as -1 before experiment begins
// Use -1 so 0 indexed trial is first trial in the set
// Allows for the iteration of max(totalNumberOfTrials) to reset board
int currentTrial = -1;

//// FLAG ASSIGNMENT ////
// In this version, the vacuum has been removed from the setup.
// Therefore, vacuum related flags have been commented out.
// Flags can be categorized by purpose:
// Serial Transfer Flags
boolean acquireMetaData = true;
boolean acquireTrials = false;
boolean acquireITI = false;
boolean acquireTone = false;
boolean rx = true;
boolean pythonGoSignal = false;
boolean arduinoGoSignal = false;
// Experiment State Flags
boolean cameraDelay = false;
boolean brukerTrigger = false;
boolean newTrial = false;
boolean ITI = false;
boolean giveStim = false;
boolean newUSDelivery = false;
boolean solenoidOn = false;
boolean noise = false; // can't use tone as it's protected in Arduino
boolean toneDAQ = false;

//// TIMING VARIABLES ////
// Time is measured in milliseconds for this program
long ms; // milliseconds
// Each experimental condition has a time parameter
long ITIend;
long rewardDelayMS;
long sucroseDelayMS;
long USDeliveryMS_Sucrose;
long sucroseConsumptionMS;
long airDelayMS;
long USDeliveryMS_Air;
long USDeliveryMS;
long noiseDeliveryMS;
long toneListeningMS;
long toneDAQMS;


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
// In this version, the vacuum has been removed from the setup.
// Therefore, vacuum related pins have been commented out.
// input
const int lickPin = 2;                        // input from MPR121
//const int airPin = 3; // measure delay from solenoid to mouse
// output
const int solPin_air = 22;                    // solenoid for air puff control
const int solPin_liquid = 26;                 // solenoid for liquid control: sucrose, water, EtOH
const int speakerPin = 12;                    // speaker control pin
const int bruker2PTriggerPin = 11;            // trigger to start Bruker 2P Recording on Prairie View

//// PIN ASSIGNMENT: NIDAQ ////
// NIDAQ input
// none
// NIDAQ output
const int itiDeliveryPin = 31;                // ITI Timestamp
const int lickDetectPin = 41;                 // detect sucrose licks
const int speakerDeliveryPin_Airpuff = 50;    // tone delivery for airpuff trials
const int speakerDeliveryPin_Liquid = 51;     // tone delivery for sucrose trials

//// PIN ASSIGNMENT: RESET ////
const int resetPin = 0;                       // reset Arduino by driving this pin LOW

//// RECIEVE METADATA FUNCTIONS ////
// These three functions will be run in order.
// The metadata is first received to initialize correct sizes for arrays
int metadata_rx() {
  if (acquireMetaData && transmissionStatus == 0) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(metadata);
      Serial.println("Received Metadata");

      myTransfer.sendDatum(metadata);
      Serial.println("Sent Metadata");
      
      acquireMetaData = false;
      transmissionStatus++;
      acquireTrials = true;
    }
  }
}

// Next, an array of trials to run is received and stored.
int trials_rx() {
  if (acquireTrials && transmissionStatus >= 1 && transmissionStatus < 3) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(trialArray);
      Serial.println("Received Trial Array");

      myTransfer.sendDatum(trialArray);
      Serial.println("Sent Trial Array");
      if (metadata.totalNumberOfTrials > 60) {
        transmissionStatus++;
      }
      else {
        transmissionStatus++;
        transmissionStatus++;
      }
      acquireITI = true;
    }
  }
}

// Next, an array of ITI values are received and stored.
int iti_rx() {
  if (acquireITI && transmissionStatus >= 3 && transmissionStatus < 5) {
    acquireTrials = false;
    if (myTransfer.available())
    {
      myTransfer.rxObj(ITIArray);
      Serial.println("Received ITI Array");

      myTransfer.sendDatum(ITIArray);
      Serial.println("Sent ITI Array");
      if (metadata.totalNumberOfTrials > 60) {
        transmissionStatus++;
      }
      else {
        transmissionStatus++;
        transmissionStatus++;
      }
      acquireTone = true;
    }
  }
}

// Finally, an array of noise duration values are received and stored.
int noise_rx() {
  if (acquireTone && transmissionStatus >= 5 && transmissionStatus < 7) {
    acquireITI = false;
    if (myTransfer.available())
    {
      myTransfer.rxObj(toneArray);
      Serial.println("Received Noise Array");

      myTransfer.sendDatum(toneArray);
      Serial.println("Sent Noise Array");
      if (metadata.totalNumberOfTrials > 60) {
        transmissionStatus++;
      }
      else {
        transmissionStatus++;
        transmissionStatus++;
      }
      pythonGoSignal = true;
    }
  }
}

// Unite array reception functions into one function for better control
void rx_function() {
  if (rx) {
    metadata_rx();
    trials_rx();
    iti_rx();
    noise_rx();
  }
}

//// PYTHON STATUS FUNCTION ////
int pythonGo_rx() {
  if (pythonGoSignal && transmissionStatus == 7) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(pythonGo);
      Serial.println("Received Python Status");
  
      myTransfer.sendDatum(pythonGo);
      Serial.println("Sent Python Status");

      currentTrial++;
      
      cameraDelay = true;
    }
  }
}

// Arduino go signal for flow control
void go_signal() {
  if (arduinoGoSignal) {
    arduinoGoSignal = false;
    Serial.println("GO!");
    brukerTrigger = true;
  }
}

//// CAMERA WAIT FUNCTION ////
void camera_delay() {
  if (cameraDelay) {
    Serial.println("Delaying Bruker Trigger for Camera Startup...");
    cameraDelay = false;
    delay(5000);
    arduinoGoSignal = true;
  }
}

//// BRUKER TRIGGER FUNCTION ////
void bruker_trigger() {
  if (brukerTrigger) {
    Serial.println("Sending Bruker Trigger");
    digitalWriteFast(bruker2PTriggerPin, HIGH);
    Serial.println("Bruker Trigger Sent!");
    digitalWriteFast(bruker2PTriggerPin, LOW);
    brukerTrigger = false;

    newTrial = true;
  }
}


//// TRIAL FUNCTIONS ////
// Lick Function
void lickDetect() {
  currtouched = cap.touched(); // Get currently touched contacts
  // if it is *currently* touched and *wasn't* touched before, alert!
  if ((currtouched & _BV(2)) && !(lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, HIGH);
  }
  // if it *was* touched and now *isn't*, alert!
  if (!(currtouched & _BV(2)) && (lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, LOW);
  }
  lasttouched = currtouched;
}

// ITI Function
void startITI(long ms) {
  if (newTrial) {                                 // start new ITI
    digitalWriteFast(itiDeliveryPin, HIGH);
    Serial.print("Starting New Trial: ");
    Serial.println(currentTrial + 1);
    trialType = trialArray[currentTrial];         // gather trial type
    newTrial = false;
    ITI = true;
    int thisITI = ITIArray[currentTrial];         // get ITI for this trial
    ITIend = ms + thisITI;
    // turn off when done
  } else if (ITI && (ms >= ITIend)) {             // ITI is over
    digitalWriteFast(itiDeliveryPin, LOW);
    ITI = false;
    noise = true;
  }
}


//// NOISE FUNCTIONS ////
// Play tone function
void tonePlayer(long ms) {
  if (noise) {
    Serial.println("Playing Tone");
    int thisNoiseDuration = toneArray[currentTrial];
    noise = false;
    toneDAQ = true;
    toneListeningMS = ms + thisNoiseDuration;
    switch (trialType) {
      case 0:
        Serial.println("Air");
        tone(speakerPin, metadata.punishTone, thisNoiseDuration);
        digitalWriteFast(speakerDeliveryPin_Airpuff, HIGH);
        giveStim = true;
        break;
      case 1:
        Serial.println("Sucrose");
        tone(speakerPin, metadata.rewardTone, thisNoiseDuration);
        digitalWriteFast(speakerDeliveryPin_Liquid, HIGH);
        giveStim = true;
        break;
    }
  }
}

// Send noise signal to DAQ function
void onTone(long ms) {
  if (toneDAQ && (ms >= toneListeningMS)){
    toneDAQ = false;
    switch (trialType) {
      case 0:
        digitalWriteFast(speakerDeliveryPin_Airpuff, LOW);
        break;
      case 1:
        digitalWriteFast(speakerDeliveryPin_Liquid, LOW);
        break;
    }
  }
}

//// STIMULUS DELIVERY FUNCTIONS ////

void presentStimulus(long ms) {
  switch (trialType) {
    case 0:
      if (giveStim && (ms >= toneListeningMS - metadata.USDeliveryTime_Air)) {
        newUSDelivery = true;
        break;
      }
    case 1:
      if (giveStim && (ms >= toneListeningMS - metadata.USDeliveryTime_Sucrose)) {
        newUSDelivery = true;
        break;
      }
  }
}
// Stimulus Delivery: 0 is airpuff, 1 is sucrose
void USDelivery(long ms) {
  if (newUSDelivery) {
    Serial.println("Delivering US");
    newUSDelivery = false;
    giveStim = false;
    solenoidOn = true;
    switch (trialType) {
      case 0:
        Serial.println("Delivering Airpuff");
        USDeliveryMS = ms + metadata.USDeliveryTime_Air;
        digitalWriteFast(solPin_air, HIGH);
        break;
      case 1:
        Serial.println("Delivering Sucrose");
        USDeliveryMS = ms + metadata.USDeliveryTime_Sucrose;
        digitalWriteFast(solPin_liquid, HIGH);
        break;
    }
  }
}

// Turn off Solenoid
void offSolenoid(long ms) {
  if (solenoidOn && (toneDAQ == false)) {
    switch (trialType) {
      case 0:
        Serial.println("Air Solenoid Off");
        solenoidOn = false;
        digitalWriteFast(solPin_air, LOW);
        newTrial = true;
        currentTrial++;
        break;
      case 1:
        Serial.println("Liquid Solenoid Off");
        solenoidOn = false;
        digitalWriteFast(solPin_liquid, LOW);
        newTrial = true;
        currentTrial++;
        break;
    }
  }
}

//// RESET ARDUINO FUNCTION ////
void reset_board() {
  transmissionStatus = 0;
  currentTrial = -1;
  acquireMetaData = true;
  acquireTrials = false;
  acquireITI = false;
  acquireTone = false;
  rx = true;
  pythonGoSignal = false;
  arduinoGoSignal = false;
  cameraDelay = false;
  brukerTrigger = false;
  newTrial = false;
  ITI = false;
  giveStim = false;
  newUSDelivery = false;
  solenoidOn = false;
  noise = false;
  toneDAQ = false;
  Serial.println("Resetting Arduino after 3 seconds...");
  delay(3000);
  Serial.println("RESETTING");
  digitalWriteFast(resetPin, LOW);
}

//// SETUP ////
void setup() {
  // -- DEFINE BITRATE -- //
  // Serial debugging from Arduino, use Ctrl+Shift+M
  Serial.begin(115200);

  // Serial transfer of trials on UART Converter COM port
  Serial1.begin(115200);
  myTransfer.begin(Serial1, true);
  
  // -- DEFINE PINS -- //
  digitalWriteFast(resetPin, HIGH);
  // input
  pinMode(lickPin, INPUT);
  //output
  pinMode(solPin_air, OUTPUT);
  pinMode(solPin_liquid, OUTPUT);
  pinMode(speakerPin, OUTPUT);
  pinMode(speakerDeliveryPin_Airpuff, OUTPUT);
  pinMode(speakerDeliveryPin_Liquid, OUTPUT);
  pinMode(itiDeliveryPin, OUTPUT);
  pinMode(bruker2PTriggerPin, OUTPUT);
  pinMode(lickDetectPin, OUTPUT);
  pinMode(resetPin, OUTPUT);

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
  rx_function();
  pythonGo_rx();
  go_signal();
  camera_delay();
  bruker_trigger();
  if (currentTrial < metadata.totalNumberOfTrials) {
    ms = millis();
    lickDetect();
    startITI(ms);
    tonePlayer(ms);
    onTone(ms);
    presentStimulus(ms);
    USDelivery(ms);
    offSolenoid(ms);
  }
  else if (currentTrial == metadata.totalNumberOfTrials) {
    reset_board();
  }
}
