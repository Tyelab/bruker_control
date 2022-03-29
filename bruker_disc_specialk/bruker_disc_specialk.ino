/**
   Tye Lab Headfixed Discrimination Task: Bruker 2P Microscope
   Name: bruker_disc_specialk
   Purpose: Present stimuli to headfixed subject and send signals to DAQ for Tye Lab Team specialk

   @author Deryn LeDuke, Kyle Fischer PhD, Dexter Tsin, Jeremy Delahanty
   @version 1.8.0 10/27/21

   Adapted from DISC_V7.ino by Kyle Fischer and Mauri van der Huevel Oct. 2019
   digitalWriteFast.h written by Watterott Electronic https://github.com/watterott/Arduino-Libs/tree/master/digitalWriteFast
   SerialTransfer.h written by PowerBroker2 https://github.com/PowerBroker2/SerialTransfer

   The program operates using these steps:
     1. Open communications to Python on Bruker PC
     2. Receive metadata, trial type array, ITI array, tone duration array, and LED Stim timings array
     3. Confirm Python has finished sending data
     4. Delay program for 5 seconds to allow Teledyne Genie Nano to start up
     5. Send trigger to the Bruker DAQ to start the microscopy sessio
     6. Run through the trials specified in totalNumberOfTrials
     7. Reset the Arduino

*/

//// PACKAGES ////
#include <Adafruit_MPR121.h>            // Adafruit MPR121 capicitance board recording
#include <digitalWriteFast.h>           // Speeds up communication for digital write
#include <Wire.h>                       // Enhances comms with MPR121
#include <SerialTransfer.h>             // Enables serial comms between Python config and Arduino

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
// The amount of time a tone is played is transmitted from Python to the Arudino
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
// trial variables are encoded as 0, 1, 2, 3, 4, 5, 6
// 0 is negative stimulus [air], 1 is  positive stimulus [sucrose]
// 2 is negative catch [air catch], 3 is positive catch [sucrose catch]
// 4 is negative LED stim, 5 is positive LED stim, 6 is stim only
// Initialize the trial type as an integer
int trialType;
// Initialize the current trial number as -1 before experiment begins
// Use -1 so 0 indexed trial is first trial in the set
// Allows for the iteration of max(totalNumberOfTrials) to reset board
int currentTrial = -1;
// Initialize the current LED Stimulation number as 0 before
// experiment begins.
int currentLED = 0;

//// ITIs ////
int thisITI;

//// Tones ////
int thisToneDuration;

//// LED Variables ////
int thisLED;


//// FLAG ASSIGNMENT ////
// Flags are categorized by purpose:
// Serial Transfer Flags
boolean acquireMetaData = true;
boolean acquireTrials = false;
boolean acquireITI = false;
boolean acquireTone = false;
boolean acquireLED = false;
boolean rx = true;
boolean pythonGoSignal = false;
boolean arduinoGoSignal = false;
// Experiment State Flags
boolean cameraDelay = false;
boolean brukerTrigger = false;
boolean newTrial = false;
boolean ITI = false;
boolean giveStim = false;             // Stim here means airpuff or sucrose, not LED stim
boolean giveCatch = false;
boolean giveLED = false;              // Flag for when to send an LED trigger to Prairie View
boolean LEDOn = false;
boolean newUSDelivery = false;
boolean newUSDeliveryCatch = false;
boolean solenoidOn = false;
boolean vacOn = false;
boolean consume = false;
boolean cleanIt = false;
boolean noise = false;                // Can't use tone as it's protected in Arduino
boolean toneDAQ = false;

//// TIMING VARIABLES ////
// Time is measured in milliseconds for this program
long ms; // milliseconds
// Each experimental condition has a time parameter
long ITIend;
long LEDStart;
long LEDEnd;
long rewardDelayMS;
long sucroseDelayMS;
long USDeliveryMS_Sucrose;
long sucroseConsumptionMS;
long vacTime;
long airDelayMS;
long USDeliveryMS_Air;
long USDeliveryMS;
long noiseDeliveryMS;
long toneListeningMS;
long toneDAQMS;
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
const int lickPin = 2;                        // input from MPR121
//const int airPin = 3;                       // measure delay from solenoid to mouse
// output
const int solPin_air = 22;                    // solenoid for air puff control
const int vacPin = 24;                        // solenoid for vacuum control
const int solPin_liquid = 26;                 // solenoid for liquid control: sucrose, water, EtOH
const int speakerPin = 12;                    // speaker control pin
const int bruker2PTriggerPin = 11;            // trigger to start Bruker 2P Recording on Prairie View
const int brukerLEDTriggerPin = 39;           // trigger to initiate an LED Pulse on Prairie View

//// PIN ASSIGNMENT: RESET /////
const int resetPin = 0;                       // Pin driven LOW for resetting the Arduino through software.

//// PIN ASSIGNMENT: NIDAQ ////
// NIDAQ input
// none
// NIDAQ output
const int lickDetectPin = 41;                 // detect sucrose licks
const int speakerDeliveryPin = 51;            // noise delivery

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
      if (metadata.totalNumberOfTrials > 60) {
        transmissionStatus++;
      }
      else {
        transmissionStatus++;
        transmissionStatus++;
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
      Serial.println("Python transmission complete!");

      myTransfer.sendDatum(pythonGo);
      Serial.println("Sent confirmation to Python");

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
    arduinoGoSignal = false;
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
  currentLED = 0;
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
  giveCatch = false;
  giveLED = false;
  LEDOn = false;
  newUSDelivery = false;
  newUSDeliveryCatch = false;
  solenoidOn = false;
  vacOn = false;
  consume = false;
  cleanIt = false;
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
  }
  // if it *was* touched and now *isn't*, alert!
  if (!(currtouched & _BV(2)) && (lasttouched & _BV(2))) {
    digitalWriteFast(lickDetectPin, LOW);
  }
  lasttouched = currtouched;
}

// ITI Function
/**
   Starts ITI for new trials and continues the ITI for duration
   specified by trial's index in the ITIray. Gathers the trial
   type selected and defines it for the next session. Also determines
   when an LED stimulation trigger should be sent if appropriate.
   Finally prints out to the Serial Monitor what the trial type is
   for the user.

   @param ms Current time in milliseconds (ms)
*/
void startITI(long ms) {
  if (newTrial) {                                 // start new ITI
    Serial.print("Starting New Trial: ");
    Serial.println(currentTrial + 1);             // add 1 to current trial so user sees non zero-indexed value
    trialType = trialArray[currentTrial];         // gather trial type
    newTrial = false;
    if (trialType > 3) {
      LEDStart, LEDEnd = typeLED(trialType, ms);
    }
    else {
      typeTrial(trialType);
    }
    ITI = true;
    thisITI = ITIArray[currentTrial];             // get ITI for this trial
    ITIend = ms + thisITI;
  }
  else if (ITI && (ms >= ITIend)) {               // ITI is over, start playing the tone
    ITI = false;
    noise = true;
  }
}

// Trial Type Function
/**
 * Determines which type of trial is coming IFF it's not an LED trial.
 * The output is used to print the trial type to the user right after
 * the trial number is printed out for the user.
 * 
 * @param trialType Type of trial coming into the user.
 */
 void typeTrial (int trialType) {
  switch (trialType) {
    case 0:
      Serial.println("Airpuff");
      break;
    case 1:
      Serial.println("Sucrose");
      break;
    case 2:
      Serial.println("Airpuff Catch");
      break;
    case 3:
      Serial.println("Sucrose Catch");
      break;
  }
 }

// LED Stimulation Functions
/**
 * Determines which type of LED stimulation trial to provide after
 * startITI() initiates an ITI and gathers the trial type. Then
 * establishes when the LED stimulation should start by grabbing
 * the appropriate timing from the LEDArray transmitted by Python
 * 
 * @param trialType Type of trial being conducted (0-6)
 * @param ms Current time in milliseconds (ms)
 */
int typeLED (int trialType, long ms) {
  switch (trialType) {
    case 4:
      Serial.println("Airpuff LED");
      LEDStart, LEDEnd = setLEDStart(ms);
      return LEDStart, LEDEnd;
    case 5:
      Serial.println("Sucrose LED");
      LEDStart, LEDEnd = setLEDStart(ms);
      return LEDStart, LEDEnd;
    case 6:
      Serial.println("LED Only");
      LEDStart, LEDEnd = setLEDStart(ms);
      return LEDStart, LEDEnd;
  }
}

/**
 * Determines when LED stimulation should occur for a given trial.
 * Only called when an LED Trial is scheduled to occur. Takes the
 * LED Stimulation trigger time from the LEDArray and calculates
 * the ms that stimulation should occur. Uses that result to
 * calculate the ms when the LED stimulation is ending.
 * 
 * @param ms Current time in milliseconds (ms)
 * @return LEDStart Time in ms to wait before sending LED Trigger
 * @return LEDEnd Time in ms that LED train will be on after triggering
 */
long setLEDStart(long ms) {
  giveLED = true;
  // Reset LED Values for new calculation to be correct
  // Gives negative values for LEDEnd without this...
  LEDStart = 0;
  LEDEnd = 0;
  thisLED = LEDArray[currentLED];
  LEDStart = ms + thisLED;
  LEDEnd = LEDStart + metadata.stimDeliveryTime_Total;
  
  return LEDStart, LEDEnd;
}

/**
 * Sends TTL to Bruker's DAQ to start an LED pulse train.
 * 
 * @param ms Current time in milliseconds (ms)
 */
void brukerTriggerLED (long ms) {
  if (giveLED && (ms >= LEDStart)) {
    giveLED = false;
    LEDOn = true;
    digitalWriteFast(brukerLEDTriggerPin, HIGH);
    Serial.println("LED Trigger Sent!");
  }
}

/**
 * Sends brukerLEDTriggerPin LOW after 
 */
void offLED (long ms) {
  if (LEDOn && (ms >= LEDEnd)) {
    LEDOn = false;
    digitalWriteFast(brukerLEDTriggerPin, LOW);
  }
}

// Tone Functions
/**
   Plays tone for given trial type for specified duration defined
   in toneArray.  Sends signal to DAQ that speaker is on. If
   non-catch trials, signals script to use giveStim functions. If
   catch trials, signals script to use giveCatch functions.

   @param ms Current time in milliseconds (ms)
*/
void tonePlayer(long ms) {
  if (noise) {
    noise = false;
    thisToneDuration = toneArray[currentTrial];
    toneDAQ = true;
    toneListeningMS = ms + thisToneDuration;
    switch (trialType) {
      case 0:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.punishTone, thisToneDuration);
        giveStim = true;
        break;
      case 1:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.rewardTone, thisToneDuration);
        giveStim = true;
        break;
      case 2:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.punishTone, thisToneDuration);
        giveCatch = true;
        break;
      case 3:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.rewardTone, thisToneDuration);
        giveCatch = true;
        break;
      case 4:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.punishTone, thisToneDuration);
        giveStim = true;
        break;
      case 5:
        digitalWriteFast(speakerDeliveryPin, HIGH);
        tone(speakerPin, metadata.rewardTone, thisToneDuration);
        giveStim = true;
        break;
      case 6:
        giveCatch = true;
        break;
    }
  }
}

/**
   Signals for the speaker to turn off and stop sending signal to DAQ that
   the speaker is active.

   @param ms Current time in milliseconds (ms)
*/
void onTone(long ms) {
  if (toneDAQ && (ms >= toneListeningMS)) {
    toneDAQ = false;
    digitalWriteFast(speakerDeliveryPin, LOW);
  }
}

// Stimuli functions
/**
   Delivers stimuli when trial types are non-catch trials. Delivers the
   stimuli before the end of the tone for how long the solenoid delivering
   it is required to be open.

   @param ms Current time in milliseconds (ms)
*/
void presentStimulus(long ms) {
  switch (trialType) {
    case 0:
      if (giveStim && (ms >=  toneListeningMS - metadata.USDeliveryTime_Air)) {
        newUSDelivery = true;
        break;
      }
    case 1:
      if (giveStim && (ms >= toneListeningMS - metadata.USDeliveryTime_Sucrose)) {
        newUSDelivery = true;
        break;
      }
    case 4:
      if (giveStim && (ms >= toneListeningMS - metadata.USDeliveryTime_Sucrose)) {
        newUSDelivery = true;
        break;
      }
    case 5:
      if (giveStim && (ms >= toneListeningMS - metadata.USDeliveryTime_Air)) {
        newUSDelivery = true;
        break;
      }
  }
}

/**
   Delivers stimuli when trial types are catch trials. Does NOT open solenoids
   for stimuli at any point.

   @param ms Current time in milliseconds (ms)
*/
void presentCatch(long ms) {
  switch (trialType) {
    case 2:
      if (giveCatch && (ms >= toneListeningMS - metadata.USDeliveryTime_Air)) {
        newUSDeliveryCatch = true;
        break;
      }
    case 3:
      if (giveCatch && (ms >= toneListeningMS - metadata.USDeliveryTime_Sucrose)) {
        newUSDeliveryCatch = true;
        break;
      }
    case 6:
      if (giveCatch && (ms >= toneListeningMS - metadata.USDeliveryTime_Sucrose)) {
        newUSDeliveryCatch = true;
        break;
      }
  }
}

/**
   Signals for solenoid activity depending on current trial type. If
   stimuli trials, solenoids are opened. If catch trials, only a
   message indicating that the catch is being "delivered" is displayed.

   @param ms Current time in milliseconds (ms)
*/
void USDelivery(long ms) {
  if (newUSDelivery) {
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
      case 4:
        Serial.println("Delivering Airpuff (LED)");
        USDeliveryMS = ms + metadata.USDeliveryTime_Air;
        digitalWriteFast(solPin_air, HIGH);
        break;
      case 5:
        Serial.println("Delivering Sucrose (LED)");
        USDeliveryMS = ms + metadata.USDeliveryTime_Sucrose;
        digitalWriteFast(solPin_liquid, HIGH);
        break;
    }
  }
  else if (newUSDeliveryCatch) {
    newUSDeliveryCatch = false;
    giveCatch = false;
    solenoidOn = true;
    switch (trialType) {
      case 2:
        Serial.println("Delivering Airpuff Catch");
        USDeliveryMS = ms + metadata.USDeliveryTime_Air;
        break;
      case 3:
        Serial.println("Delivering Sucrose Catch");
        USDeliveryMS = ms + metadata.USDeliveryTime_Sucrose;
        break;
      case 6:
        USDeliveryMS = ms + metadata.USDeliveryTime_Sucrose;
        break;
    }
  }
}


/**
   Turns off solenoids if presenting stimuli and resets the solenoidOn flags.
   If a sucrose trial was presented (catch or not), the consume flag is true.

   @param ms Current time in milliseconds (ms)
*/
void offSolenoid(long ms) {
  if (solenoidOn && (toneDAQ == false)) {
    switch (trialType) {
      case 0:
        solenoidOn = false;
        digitalWriteFast(solPin_air, LOW);
        newTrial = true;
        currentTrial++;
        break;
      case 1:
        solenoidOn = false;
        sucroseConsumptionMS = (ms + metadata.USConsumptionTime_Sucrose);
        consume = true;
        newTrial = true;
        currentTrial++;
        digitalWriteFast(solPin_liquid, LOW);
        break;
      case 2:
        solenoidOn = false;
        newTrial = true;
        currentTrial++;
        break;
      case 3:
        solenoidOn = false;
        sucroseConsumptionMS = (ms + metadata.USConsumptionTime_Sucrose);
        consume = true;
        newTrial = true;
        currentTrial++;
        break;
      case 4:
        solenoidOn = false;
        digitalWriteFast(solPin_air, LOW);
        newTrial = true;
        currentTrial++;
        currentLED++;
        break;
      case 5:
        solenoidOn = false;
        sucroseConsumptionMS = (ms + metadata.USConsumptionTime_Sucrose);
        consume = true;
        newTrial = true;
        currentTrial++;
        currentLED++;
        digitalWriteFast(solPin_liquid, LOW);
        break;
      case 6:
        Serial.println("End of LED Only Trial");
        solenoidOn = false;
        newTrial = true;
        currentTrial++;
        currentLED++;
        break;
    }
  }
}

/**
   Signals to turn on vacuum once specified consumption period is over.

   @param ms Current time in milliseconds (ms)
*/
void consuming(long ms) {
  if (consume && (ms >= sucroseConsumptionMS)) {         // move on after allowed to consume
    consume = false;
    cleanIt = true;
  }
}

/**
   Turns on vacuum for specified vacDelay and turns it off
   once vacuum time has elapsed.

   @param ms Current time in milliseconds (ms)
*/
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
  }
}


void setup() {
  // Define Bitrate for SerialTransfer. Using 115200 is faster/more efficient means of comms.
  Serial.begin(115200);

  // Begin communicating with Bruker PC on specified COM port.
  Serial1.begin(115200);
  myTransfer.begin(Serial1, true);

  // -- DEFINE PINS -- //
  digitalWriteFast(resetPin, HIGH);
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
  pinMode(brukerLEDTriggerPin, OUTPUT);
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
    brukerTriggerLED(ms);
    offLED(ms);
    presentStimulus(ms);
    presentCatch(ms);
    USDelivery(ms);
    offSolenoid(ms);
    consuming(ms);
    vacuum(ms);
  }
  else if (currentTrial == metadata.totalNumberOfTrials) {
    reset_board();
  }
}
