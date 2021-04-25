// Use package SerialTransfer.h from PowerBroker2 https://github.com/PowerBroker2/SerialTransfer
#include "SerialTransfer.h"

// Rename SerialTransfer to myTransfer
SerialTransfer myTransfer;

const int MAX_NUM_TRIALS = 100; // maximum number of trials possible; much larger than needed but smaller than max value of metadata.totalNumberOfTrials




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

int32_t trialArray[MAX_NUM_TRIALS]; // create trial array
int32_t ITIArray[MAX_NUM_TRIALS]; // create ITI array

void setup()
{
  Serial.begin(9600);
  Serial1.begin(115200);
  
  myTransfer.begin(Serial1, true);
}


void loop(){
  Serial.println(sizeof(metadata));
}


//int trials_rx() {
//  if (acquireTrials) {
//    if (myTransfer.available())
//    { 
//      myTransfer.rxObj(list);
//      Serial.println("Received");
//
//      myTransfer.sendDatum(list);
//      Serial.println("Sent");
//      acquireTrials = false;
//    }
//  }
//}
////
