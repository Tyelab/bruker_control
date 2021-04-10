// Use package SerialTransfer.h from PowerBroker2 https://github.com/PowerBroker2/SerialTransfer
#include "SerialTransfer.h"

// Rename SerialTransfer to myTransfer
SerialTransfer myTransfer;

int32_t list[20];
boolean acquireTrials = true;

void setup()
{
  Serial.begin(115200);
  Serial1.begin(115200);

  myTransfer.begin(Serial1, true);
}

int trials_rx() {
  if (acquireTrials) {
    if (myTransfer.available())
    { 
      myTransfer.rxObj(list);
      Serial.println("Received");

      myTransfer.sendDatum(list);
      Serial.println("Sent");
      acquireTrials = false;
    }
  }
}
//
void loop()
{
  trials_rx();
}
//
//void loop()
//{
//  if(myTransfer.available())
//  {
//    myTransfer.rxObj(list);
//    Serial.println("Received:");
//    Serial.print("[");
//    Serial.print(list[0]);
//    Serial.print(", ");
//    Serial.print(list[1]);
//    Serial.println("]");
//    Serial.println();
//    
//    myTransfer.sendDatum(list);
//    Serial.println("Sent");
//    Serial.print("[");
//    Serial.print(list[0]);
//    Serial.print(", ");
//    Serial.print(list[1]);
//    Serial.println("]");
//    Serial.println();
//  }
//}
