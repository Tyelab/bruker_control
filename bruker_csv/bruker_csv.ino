// Use package SerialTransfer.h from PowerBroker2 https://github.com/PowerBroker2/SerialTransfer
#include "SerialTransfer.h"

// Rename SerialTransfer to myTransfer
SerialTransfer myTransfer;

const int MAX_NUM_TRIALS = 46; // maximum number of trials possible; much larger than needed but smaller than max value of metadata.totalNumberOfTrials




struct __attribute__((__packed__)) metadata_struct {
  uint8_t totalNumberOfTrials;              // total number of trials for experiment
  uint16_t punishTone;                      // airpuff frequency tone in Hz
  uint16_t rewardTone;                      // sucrose frequency tone in Hz
  uint8_t USDeliveryTime_Sucrose;           // amount of time to open sucrose solenoid
  uint8_t USDeliveryTime_Air;               // amount of time to open air solenoid
  uint16_t USConsumptionTime_Sucrose;       // amount of time to wait for sucrose consumption
} metadata;

int32_t trialArray[MAX_NUM_TRIALS]; // create trial array
int32_t ITIArray[MAX_NUM_TRIALS]; // create ITI array
int32_t noiseArray[MAX_NUM_TRIALS]; // create noise array

boolean acquireMetaData = true;
boolean acquireTrials = true;
boolean acquireITI = false;
boolean acquireNoise = false;

void setup()
{
  Serial.begin(115200);
  Serial1.begin(115200);

  myTransfer.begin(Serial1, true);
}


void loop(){
//  metadata_rx();
  trials_rx();
  iti_rx();
  noise_rx();
}


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

int trials_rx() {
  if (acquireTrials) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(trialArray);
      Serial.println("Received Trial Array");

      myTransfer.sendDatum(trialArray);
      Serial.println("Sent Trial Array");

      acquireTrials = false;
      acquireITI = true;
    }
  }
}

int iti_rx() {
  if (acquireITI) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(ITIArray);
      Serial.println("Received ITI Array");

      myTransfer.sendDatum(ITIArray);
      Serial.println("Sent ITI Array");
      acquireITI = false;
      acquireNoise = true;
    }
  }
}

int noise_rx() {
  if (acquireNoise) {
    if (myTransfer.available())
    {
      myTransfer.rxObj(noiseArray);
      Serial.println("Received Noise Array");

      myTransfer.sendDatum(noiseArray);
      Serial.println("Sent Noise Array");
      acquireNoise = true;
    }
  }
}
