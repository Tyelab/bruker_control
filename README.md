# headfix_control
Repository for Arduino code controlled by MATLAB and Python used to control behavior experiments in the Headfix room and 2P Room.

Substantial cleanup of the repository and many updates to the code are forthcoming.

Currently, the code is functional for the Bruker 2P microscope.

On the Python side:
There are numerous hacks involved, some problems with timing the programs correctly, a lack of file naming and writing capabilities that is automatically formatted and stored in the correct location for a given animal, and usability issues that should be handled with the following future implementations (among others...):

- [ x ]  Multithreading: Preview camera, show live feed, send/receive Arduino information while starting camera
- [ ] Code for recording from camera should be stopped by external trigger, automatically generated from Arduino or Bruker
- [ ] Users should be able to use custom made trial arrays in Excel/CSV and change configurations on the fly as needed
- [ ] Write randomly generated trial array and ITI array to `config.json`
- [ ] Create standard naming convention for configuration JSON files using NWB formats
- [ ] The max number of trials needs to be increased to at least 90 trials. The trial array and ITI array must be converted to multipacket transmissions.
- [ ] Error checking for transmission problems must be implemented and, if an error occurs, the packets should be resent to the Arduino.
- [ ] Automatically poll COM ports for Arduinos and select them
- [ ] Error codes should be created and standardized for the software so useful tracebacks are available
- [ ] Due to timing inconsistency, outputs from Camera should be recorded on the Bruker's DAQ to ensure synced frames are in fact synced.
- [ ] More thorough testing for edge cases/user error/packet loss/camera error/timeout errors/etc...
- [ ] Must have conda environment `bruker_control` installed for all users on the machine
- [ ] Prairie View configuration for a given experiment should be saved
- [ ] Profile resource requirements, timing for each function and step
- [ ] Ensure code is generalized for different cameras and check if camera is compliant to GenIcam standard
- [ ] A GUI so users can avoid having to activate conda environments and typing terminal commands
- [ ] Sphinx documentation development

On the Arduino side:
Things appear to be functioning correctly. Further testing for there to be at least 90 trials for a given animal controlled by Arduino is necessary. Storing two 90 element arrays as well as the compiled code may be too large for an Arduino to handle. If this is the case, continuous transmission must be implemented. In the meantime, there are still several improvements that can be made:
- [ ] The code still requires uploading the `Bruker_DISCV8` sketch before initiating each experiment. Arduino should be reinitialized the moment the experiment is over and simply wait for new transmissions. Sketches should only be sent when the Arduino code needs an update.
- [ ] Error checking is nearly non-existent except in the case of the `lick_detect` function which Arduino provided
- [ ] Profiling speed of the program should be performed
- [ ] Documentation development for C++

Finally, documentation and examples:
I (@jmdelahanty) have done my best to document what the code is up to inside the various files and functions contained here. However, the documentation is not consistently created for every file in this repository. Several files/folders should be outright deleted as they are no longer useful. and the ReadMe is completely insufficient. There is also no current set of documentation that explains how the code works independent of the code itself. If this code is to be usable by others, I should also create examples that illustrate how to use each of the different functions I've created independently for the camera, Arduino, and Prairie View communication. This should be solved with the following:
- [ ] Clean up repository
- [ ] Rewrite ReadMe
- [ ] Create examples for using each function/library developed here
- [ ] Develop independent documentation
- [ ] Have users completely unfamiliar with the software test it for themselves
- [ ] Create video demos using screen captures to illustrate how to use functions
