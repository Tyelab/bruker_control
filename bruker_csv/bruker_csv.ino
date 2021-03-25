#include "SerialTransfer.h"

SerialTransfer myTransfer;


struct trialStruct {
  int x[20];
} tester; // structure for containing received trial type array

int trialArray[20]; // create array that is 20 integers long

void setup()
{
  Serial.begin(115200);
  myTransfer.begin(Serial);
}

void loop()
{
  if(myTransfer.available())
  {   
  // used to track how many bytes we've processed from the receive buffer
   uint16_t recSize = 0;
   recSize = myTransfer.rxObj(tester, recSize);
//   Serial.println(trialStruct.x);
   recSize = myTransfer.rxObj(trialArray, recSize);
  }
}
