// Use package SerialTransfer.h from PowerBroker2 https://github.com/PowerBroker2/SerialTransfer
#include "SerialTransfer.h"

// Rename SerialTransfer to myTransfer
SerialTransfer myTransfer;


int trialArray[20]; // create array that is 20 integers long
byte arrayIndex = 0; // create index to track bit mapping in received packet


// Create setup
void setup()
{
  Serial.begin(115200); // SerialTransfer uses a baud of 115200 by default
  Serial1.begin(115200);
  myTransfer.begin(Serial1); // Begin serial comms over USB
}

// Per SerialTransfer documentation, this is how I'm supposed to read in what's transmitted to the Arduino
// I'm still working on confirming data was received and sending that confirmation back to Python script.
int rxObjTransfer()
{
  if(myTransfer.available())
  {
    uint16_t recSize = 0;
    recSize = myTransfer.rxObj(trialArray, recSize);
  }
  return trialArray;
}

void txObjTransfer()
{
  if (myTransfer.available())
  {
    uint16_t sendSize = 0;
    sendSize = myTransfer.txObj(trialArray, sendSize);
    myTransfer.sendData(sendSize);
    delay(1000);
  }
}



void loop() {
  rxObjTransfer();
  Serial.print(trialArray[1]);
//  txObjTransfer();
//  testFx();
//  bitTransfer();
}

// This code currently accepts list from python and transmits list back to computer; this is from an example that PowerBroker2 has on his GitHub
// Challenge is to store the list and return it as trial list used for experiment
//int bitTransfer() {
//  if(myTransfer.available())
//  {
//    int trialArray[20];
//    for (uint16_t i=0; i < myTransfer.bytesRead; i++)
//      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
//      for (int i=0; i < 21; i++)
//        trialArray[arrayIndex] = myTransfer.packet.txBuff[i];
//
//    myTransfer.sendData(myTransfer.bytesRead);
//
//    return trialArray[20];
//  }
//}

// My (Jeremy) attempt at saving the array correctly using the package, still testing...
// Arduino IDE also complains that I'm performing an invalid conversion from 'int*' to 'int' when compiling, learning what that means...
//int testFx() {
//  if (myTransfer.available())
//  {
//    int trialArray[20];
//    for (uint16_t i=0; i < myTransfer.bytesRead; i++)
//      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
//      for (int i=0; i < 21; i++)
//        trialArray[arrayIndex] = myTransfer.packet.txBuff[i];
//
//    myTransfer.sendData(myTransfer.bytesRead);
//    return trialArray[20];
////    Serial.print(trialArray[1]);
//  }
//}
