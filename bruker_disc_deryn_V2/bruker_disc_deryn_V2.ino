/**
Tye Lab Headfixed Discrimination Task: Bruker 2P Microscope
Name: bruker_disc_deryn
Purpose: Present stimuli to headfixed subject and send signals to DAQ for Tye Lab Team specialk

@author Deryn LeDuke, Kyle Fischer PhD, Dexter Tsin, Jeremy Delahanty
@version 1.9.0 9/22
-Deryn (Sept 2022): This version has been edited to reflect new trial structure and updated controls between bruker/python code. 
The config file has been similarly edited. Changes are pushed to github with corresponding notes.

Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
digitalWriteFast.h written by Watterott Electronic https://github.com/watterott/Arduino-Libs/tree/master/digitalWriteFast
SerialTransfer.h written by PowerBroker2 https://github.com/PowerBroker2/SerialTransfer

The program operates using these steps:
  1. Open communications to Python on Bruker PC
  2. Receive metadata, trial type array, ITI array, and tone duration array
  3. Confirm Python has finished sending data
  4. Delay program for 5 seconds to allow Teledyne Genie Nano to start up
  5. Send trigger to the Bruker DAQ to start the microscopy session
  6. Run through the trials specified in totalNumberOfTrials
  7. Reset the Arduino

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
  uint16_t stimDeliveryTime_Total;          // amount of time LED is scheduled to run
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
// The timepoints for stimulating the subject via LED are transmitted from Python to Arduino
int32_t LEDArray[MAX_NUM_TRIALS];

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
boolean acquireLED = false;
boolean rx = true;
boolean pythonGoSignal = false;
boolean arduinoGoSignal = false;
// Experiment State Flags (These have been changed to reflect the new flags)
boolean cameraDelay = false;
boolean brukerTrigger = false;
// Arduino Loop Flags
// Trial type
boolean Air=false;
boolean Sucrose=false;
boolean Catch=false;
boolean newTrial=true;
// ITI booleans
boolean ITIReady=false;
boolean ITIRunning=false;
// Stimulus booleans
boolean StimulusReady=false;
// CS booleans
boolean SpeakerRunning=false;
// US booleans
boolean USRunning=false;
boolean USReady=false;
// Vacuum booleans
boolean VacuumReady=false;
boolean VacuumRunning=false;
// Lick contingency variables
boolean LickDetected=false;
//int LickDetected;
boolean contcurrent = false; // for lick contingency
boolean WindowFlag=false;

//// TIMING VARIABLES ////
// Time is measured in milliseconds for this program
// Things that don't change but need to be specified anyways
const int VacuumDelay=100;
const int USDelay=500; // Hard codes the US Delay because it doesn't seem like its there on the config
long ms; // milliseconds
// Each experimental condition has a time parameter
// Things that change depending on trial no.
int CurrentType;
int CurrentTrial;
int CurrentITI;
int CurrentNoise;
// Things that change depending on ms no.
long VacuumEnd;
long ITIEnd;
long NoiseEnd;
long Noisestart;
long USstart;
long USend;
long USbegin;

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
const int lickPin = 2;                        // input from MPR121
//const int airPin = 3; // measure delay from solenoid to mouse
// output
const int vacPin=24;
const int sol_air = 22;                    // solenoid for air puff control
const int sol_sucrose = 26;                 // solenoid for liquid control: sucrose, water, EtOH
const int speaker = 12;                    // speaker control pin
const int bruker2PTriggerPin = 11;            // trigger to start Bruker 2P Recording on Prairie View

//// PIN ASSIGNMENT: NIDAQ ////
// NIDAQ input
// none
// NIDAQ output
const int ITInewTrial = 31;                // ITI Timestamp
const int lickDetectPin = 41;                 // detect sucrose licks
const int speakerDeliveryPin_Airpuff = 50;    // tone delivery for airpuff trials
const int speakerDeliveryPin_Liquid = 51;     // tone delivery for sucrose trials

//// PIN ASSIGNMENT: RESET ////
const int resetPin = 0;                       // reset Arduino by driving this pin LOW

// Metadata and flow-control functions
/**
   Receives, parses, and sends back Arduino Metadata to PC. Increments the
   transmissionStatus by 1.
*/
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

/**
   Receives, parses, and sends back array of trial types to be performed
   for given experiment. Increments transmission status by 1 if totalNumber
   OfTrials is greater than 60, by 2 if less than 60.
*/
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

/**
   Receives, parses, and sends back array of Inter Trial Intervals (ITIs)
   to be performed for given experiment. Increments transmission status by
   1 if totalNumberOfTrials is greater than 60, by 2 if less than 60.
*/
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

/**
   Receives, parses, and sends back array of Tone Durations to be performed
   for given experiment. Increments transmission status by 1 if
   totalNumberOfTrials is greater than 60, by 2 if less than 60.
*/
int tone_rx() {
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
      acquireLED = true;
    }
  }
}

/**
 * Receives, parses, and sends back array of Stim Durations to be performed
 * for a given experiment. Increments transmission status by 1 if
 * totalNumberOfTrials is greater than 60, by 2 if less than 60.
 */
int led_rx() {
  if (acquireLED && transmissionStatus >= 7 && transmissionStatus < 9) {
    acquireTone = false;
    if (myTransfer.available())
    {
      myTransfer.rxObj(LEDArray);
      Serial.println("Received LED Stim Array");

      myTransfer.sendDatum(LEDArray);
      Serial.println("Sent LED Stim Array");
      Serial.println(transmissionStatus);
      if (metadata.totalNumberOfTrials > 60) {
        transmissionStatus++;
      }
      else {
        transmissionStatus++;
        transmissionStatus++;
        Serial.println(transmissionStatus);
      }
      acquireLED = false;
      pythonGoSignal = true;
    }
  }
}

/**
   Unites receiving functions for serial comms of Python generated trial
   values. Proceeds at the start of the experiment to set Arduino trials
   up successfully. ALWAYS proceeds in the following order:
    1. Metadata transmission
    2. Trial type transmission
    3. ITI duration transmission
    4. Tone duration transmission
    5. LED Stimulation time transmission
*/
void rx_function() {
  if (rx) {
    metadata_rx();
    trials_rx();
    iti_rx();
    tone_rx();
    led_rx();
  }
}

/**
   Confirms that Python has finished sending data for the session and
   increments the current trial from -1 to 0, meaning the first element
   of the trialArray received from Python. Starts the delay for the
   Genie Nano so it can start up.
*/
int pythonGo_rx() {
  if (pythonGoSignal && transmissionStatus == 9) {
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

/**
   Sends notification to user that experiment will start and
   signals script to send TTL to Bruker's DAQ to start recording.
*/
void go_signal() {
  if (arduinoGoSignal) {
    arduinoGoSignal = false;
    Serial.println("GO!");
    brukerTrigger = true;
  }
}

/**
   Delays script for 5 seconds (5000 ms) allowing for the Genie Nano
   to start up.
*/
void camera_delay() {
  if (cameraDelay) {
    Serial.println("Delaying Bruker Trigger for Camera Startup...");
    cameraDelay = false;
    delay(5000);
    arduinoGoSignal = true;
  }
}

/**
   Sends TTL to Bruker's DAQ to start the experimental session.
*/
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

/**
   Resets the Arduino's flags to starting values.
*/
void reset_board() {
  transmissionStatus = 0;
  currentTrial = -1;
  acquireMetaData = true;
  acquireTrials = false;
  acquireITI = false;
  acquireTone = false;
  acquireLED = false;
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

// Lick Detection Function
/**
   Standard MPR121 capacitance board script monitoring for touches
   to the sucrose delivery needle. Uses pin 2 on the board for
   monitoring the capacitance touching.
*/
void lickDetect() {
  currtouched = cap.touched(); // Get currently touched contacts
  // if it is *currently* touched and *wasn't* touched before, alert!
  if ((currtouched & _BV(2)) && !(lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, HIGH);
    contcurrent=true;
  }
  // if it *was* touched and now *isn't*, alert!
  if (!(currtouched & _BV(2)) && (lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, LOW);
    contcurrent=false;
  }
  lasttouched = currtouched;
}

/** The following functions are edited to reflect the new trial structure (lick contingency)
 *  The edited trial structure comes from DISC_LC_V3.2. 
*/
// Determine Trial Type

void DetermineTrialType(long ms) {
  if (newTrial) {
      Serial.println("Starting trial ");
      Serial.println(CurrentTrial);
      Serial.println("Trial Type is:");
      CurrentType=TrialTypes[CurrentTrial];
      switch (CurrentType){
        case 0:
        Serial.println("Air");
        Air=true;
        break;
        case 1:
        Serial.println("Sucrose");  
        Sucrose=true;
        break;
        case 3:
        Serial.println("Catch");
        Catch=true;
        break;
      }
     newTrial=false;
     ITIReady=true;
  }
}
// ITI Function
/**
   Starts ITI for new trials and continues the ITI for duration
   specified by trial's index in the ITIARray. Gathers the trial
   type selected and defines it for the next sessions. Sends
   ITI signal to DAQ.

   @param ms Current time in milliseconds (ms)
*/
void startITI(long ms) {
  if (ITIReady) {
    ITIReady=false;
    Serial.println("Starting ITI");
    digitalWriteFast(ITInewTrial, HIGH); // Report to NIDAQ
    CurrentITI=ITIArray[CurrentTrial];
    ITIEnd=ms+CurrentITI;
    Serial.println(CurrentITI);
    ITIRunning=true;
  }
  else if (ITIRunning && (ms >=ITIEnd)){
    Serial.println("Ending ITI");
    digitalWriteFast(ITInewTrial, LOW); // Report to NIDAQ
    ITIRunning=false;
    StimulusReady=true;
  }
}
// Stimulus Functions
// Air Functions 
void AirStimulus (long ms) {
  if (Air){
  if (StimulusReady){
    CurrentNoise=NoiseArray[CurrentTrial];
    StimulusReady=false;
    NoiseEnd=ms+CurrentNoise;
    USstart=ms+USDelayTime;
    USend=USstart+USDeliveryTime_Air;
    Serial.println("Playing tone for Air"); 
    Serial.println(CurrentNoise);
    tone(speaker, toneNeg, CurrentNoise); //Start Speaker
    digitalWriteFast(speakerDeliveryPin_Airpuff, HIGH); // Report to NIDAQ
    USReady=true;
  }  
  else if (USReady && (ms >=USstart)){
    USReady=false;
    Serial.println("Airpuff On"); 
    Serial.println(USDeliveryTime_Air);
    digitalWriteFast(sol_air, HIGH); // Start Airpuff
    USRunning=true;
  }
  else if (USRunning && (ms >=USend)){
    USRunning=false;
    Serial.println("Airpuff Off");
    digitalWriteFast(sol_air, LOW); // Turn off Airpuff
    SpeakerRunning=true;
  }
  else if (SpeakerRunning && (ms >=NoiseEnd)){
    SpeakerRunning=false;
    Air=false;
    noTone(speaker); // Turn off tone
    Serial.println("Speaker Off");
    digitalWriteFast(speakerDeliveryPin_Airpuff, LOW); // Report to NIDAQ    
    newTrial=true;
    CurrentTrial++;    
   }
  }
}

// Sucrose Stimulus (NOTE: This is for LICK CONTINGENCY-> WITH US DELAY)

void SucroseStimulus (long ms) {
  if (Sucrose){
    if (StimulusReady){
      // start the tone- regardless of lick/no lick
      CurrentNoise=NoiseArray[CurrentTrial];
      StimulusReady=false;
      NoiseEnd=ms+CurrentNoise;
      USbegin=ms+USDelayTime;
      Serial.println("Playing tone for Sucrose");
      tone(speaker, tonePos, CurrentNoise);// Start speaker
      digitalWriteFast(speakerDeliveryPin_Liquid, HIGH); // Report to NIDAQ
      Serial.println(CurrentNoise);
      // now tell the arduino to run a lick window for the time of the current noise:
      USReady=true;
      }
      while (USReady && ms <=NoiseEnd){
        ms=millis(); //redeclare ms for timing
        lickDetect(); //redeclare lick detect for background info
        SpeakerRunning=true;
        Serial.println("Lick Window Open- waiting for licks");
      if (contcurrent){ 
        Serial.println("Lick Detected!");
        WindowFlag=true;
      }
      else if (WindowFlag && ms>=USbegin){
        WindowFlag=false;
        USReady=false;
        SpeakerRunning=false;
        Serial.println("Dispensing Sucrose");
        USstart=ms;               //establish US start 
        USend=USstart+USDeliveryTime_Sucrose; //establish US end  
        LickDetected=true;
      }
      else if (SpeakerRunning && ms>=NoiseEnd){
        USReady=false;
        noTone(speaker); // turn off speaker
        Serial.println("Speaker Off");
        digitalWriteFast(speakerDeliveryPin_Liquid,LOW); // Report to NIDAQ
        Serial.println(ms);
        Sucrose=false;
        VacuumReady=true;
      }
    }
    if (LickDetected && (ms >=USstart)){
      LickDetected=false;
      Serial.println("Sucrose On");
      digitalWriteFast(sol_sucrose, HIGH); //Start sucrose
      USRunning=true;
    }
    else if (USRunning && (ms >= USend)){
      USRunning=false;
      Serial.println("Sucrose Off");
      digitalWriteFast(sol_sucrose, LOW); //Turn off sucrose
      SpeakerRunning=true;
    }
    else if (SpeakerRunning && ms>=NoiseEnd){
      SpeakerRunning=false;      
      noNewTone(speaker); // turn off speaker
      Serial.println("Speaker Off");
      digitalWriteFast(speakerDeliveryPin_Liquid,LOW); // Report to NIDAQ
      Serial.println(ms);
      Sucrose=false;
      VacuumReady=true;
    }
  }
}

// Catch Trial Functions

void CatchTrial (long ms) {
  if (Catch) {
   if (StimulusReady){
    CurrentNoise=NoiseArray[CurrentTrial];
    StimulusReady=false;
    NoiseEnd=ms+CurrentNoise;
    Serial.println("Playing tone for Sucrose (catch)"); 
    Serial.println(CurrentNoise);
    NewTone(speaker, tonePos, CurrentNoise); //Start Speaker
    digitalWriteFast(speakerDeliveryPin_Liquid, HIGH); // Report to NIDAQ
    SpeakerRunning=true;
   }
  else if (SpeakerRunning && (ms >=NoiseEnd)){
    SpeakerRunning=false;
    Catch=false;
    noNewTone(speaker); // Turn off tone
    Serial.println("Speaker Off");
    digitalWriteFast(speakerDeliveryPin_Liquid, LOW); // Report to NIDAQ    
    newTrial=true;
    CurrentTrial++;    
  }
  }
}
// Vacuum Delivery

void VacuumDelivery (long ms){
  if (VacuumReady){
    Serial.println("Vacuum On");
    digitalWriteFast(vacpin, HIGH); // Start vacuum
    digitalWriteFast(vacuumDeliveryPin, HIGH); // Report to NIDAQ
    VacuumEnd=ms+VacuumDelay;
    VacuumReady=false;
    VacuumRunning=true;
  }
  else if (VacuumRunning && (ms >=VacuumEnd)){
    VacuumRunning=false;
    Serial.println("Vacuum Off");
    digitalWriteFast(vacpin, LOW); // End vacuum
    digitalWriteFast(vacuumDeliveryPin, LOW); // Report to NIDAQ
    newTrial=true;
    CurrentTrial++;
  }
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
  //output (arduino)
  pinMode(sol_air, OUTPUT);
  pinMode(sol_sucrose, OUTPUT);
  pinMode(vacpin, OUTPUT);
  pinMode(speaker, OUTPUT);
  //daq output
  pinMode(speakerDeliveryPin_Airpuff, OUTPUT);
  pinMode(speakerDeliveryPin_Liquid, OUTPUT);
  pinMode(ITInewTrial, OUTPUT);
  pinMode(bruker2PTriggerPin, OUTPUT);
  pinMode(lickDetectPin, OUTPUT);
  //internal pins
  pinMode(resetPin, OUTPUT);

  // -- INITIALIZE TOUCH SENSOR -- //
  Serial.println("MPR121 check...");
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);
  } // need to learn what value 0x5A represents - JD
  Serial.println("MPR121 found!");
  // Set thresholds for capactiance
  cap.setThresholds(1,1);
  Serial.println("Capacitance Thresholds Set (touched:released):(1,1)");
}

//// THE BIZ ////
void loop() {
  rx_function();
  pythonGo_rx();
  go_signal();
  camera_delay();
  bruker_trigger();
  if (CurrentTrial < metadata.totalNumberOfTrials) { // See updated functions (9/22)
    ms = millis();
    lickDetect();
    DetermineTrialType(ms);
    startITI(ms);
    switch(CurrentType){
      case 0:
      AirStimulus(ms);
      break;
      case 1:
      SucroseStimulus(ms);
      VacuumDelivery(ms);
      break;
      case 2:
      CatchTrial(ms);
      break;
      }
     }
  else if (CurrentTrial == metadata.totalNumberOfTrials) {
    reset_board();
  }
}
