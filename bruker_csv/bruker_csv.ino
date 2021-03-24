long randNumber;

#include "SerialTransfer.h"

SerialTransfer myTransfer;

int anArray[20];
byte arrayIndex = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  myTransfer.begin(Serial);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(myTransfer.available())
  {
    for (uint16_t i=0; i < myTransfer.bytesRead; i++)
      myTransfer.packet.txBuff[i] = myTransfer.packet.rxBuff[i];
      for (int i=0; i < 21; i++)
        anArray[arrayIndex] = myTransfer.packet.txBuff[i];
      
    myTransfer.sendData(myTransfer.bytesRead);
  }
}
