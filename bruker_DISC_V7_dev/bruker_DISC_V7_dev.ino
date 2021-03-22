// Control code for Arduino management of Bruker 2P setup for Team Specialk
// Purpose is to slowly develop each portion one by one as each function as currently written fails spectacularly!
// Jeremy Delahanty Mar. 2021

//// PACKAGES ////
// 3/19/21: Using Volume.h and digitalWriteFast.h
#include <digitalWriteFast.h>
#include <Volume.h>

// Volume package settings
Volume vol; // rename Volume to vol

//// PIN ASSIGNMENT: Stimuli and Solenoids ////
//output
const int speakerPin = 4; //

void setup() {
  vol.begin();
  
}

void loop() {
  // put your main code here, to run repeatedly:
  vol.tone(2000, 255);
  vol.millis(1000);
  vol.end()
}
