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
  myTransfer.begin(Serial); // Begin serial comms over USB
}

// This code currently accepts list from python and transmits list back to computer; this is from an example that PowerBroker2 has on his GitHub
// Challenge is to store the list and return it as trial list used for experiment
void bitTransfer() {
  if(myTransfer.available())
  {
    for (uint16_t i=0; i < myTransfer.bytesRead; i++)
      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
      for (int i=0; i < 21; i++)
        trialArray[arrayIndex] = myTransfer.packet.txBuff[i];

    myTransfer.sendData(myTransfer.bytesRead);
  }
}

// My (Jeremy) attempt at saving the array correctly using the package, still testing...
// Arduino IDE also complains that I'm performing an invalid conversion from 'int*' to 'int' when compiling, learning what that means...
int testFx() {
  if (myTransfer.available())
  {
    for (uint16_t i=0; i < myTransfer.bytesRead; i++)
      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
      for (int i=0; i < 21; i++)
        trialArray[arrayIndex] = myTransfer.packet.txBuff[i];
  }
  return trialArray;
}

void loop() {
  bitTransfer();
}

// Per SerialTransfer documentation, this is how I'm supposed to read in what's transmitted to the Arduino
// I'm still working on confirming data was received and sending that confirmation back to Python script.
//void rxObjTransfer()
//{
//  if(myTransfer.available())
//  {   
//  // used to track how many bytes we've processed from the receive buffer
//   uint16_t recSize = 0;
//   recSize = myTransfer.rxObj(trialArray, recSize);
//  }
//}
