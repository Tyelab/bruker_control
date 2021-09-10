# headfix_control
## By Deryn LeDuke, Kyle Fischer PhD, Dexter Tsin, and Jeremy Delahanty

Repository for Arduino code controlled by MATLAB and/or Python used to control behavior experiments in the Headfix room and 2P Room.

Currently, the code is functional for the Bruker 2P microscope. Training code is not currently present on the repo. MATLAB's scanbox is not present on the repo.

## bruker_control.py v1.0.0
A (very) basic rundown of the experimental runtime is included below.

![User Execution Graph](https://github.com/Tyelab/headfix_control/blob/main/docs/bruker_user_executiongraph.png)

### User Guide

There are three different softwares used for running experiments with the lab's Bruker Ultima Investigator: __Python, Arduino Sketches, and Bruker's Prairie View__.

#### _Arduino_
First, use __bruker_cleanup.ino__ to backfill the sucrose line. 
1. Comment out all the lines in the `loop` portion of the file with `//` characters at the start of the line _except_ for the `digitalWrite(solPin_liquid, HIGH)` line. Assist the sucrose solution through the line with the syringe plunger until it is flowing continuously through the sucrose delivery needle in the faraday cage. It takes approximately 5mL of solution to backfill the line.
2. Uncomment the rest of the lines in the `loop` to test the vacuum. If the droplet is sucked up properly, you can upload your team's experimental sketch! If it fails, first try drying the sucrose delivery needle and, if that fails, grease the interface between the two needles. Ensure that you don't get any grease where the sucrose droplet forms.

Once you've uploaded your team's Arduino sketch, the Arduino system is ready and waiting for the experiment's trials! The board will reset on its own once the imaging session is complete.

#### _Prairie View_
Prairie View will open several windows when it starts.
1. Primary window
Contains many of the different functions Bruker's software can perform. In the `T-Series` tab, there's a box on the bottom left corner that states `Start with input trigger`. Make sure that this is selected. Once that is done, make sure that you select the `Never` option under the `Preferences/Convert Images` tab.

2. Voltage Recording window
The voltage recording window will have multiple experiments saved for different teams' relevant DAQ channels. Select your team's appropriate experiment.

At this point, Prairie View is ready to start imaging!

#### _Python_
Use the `Anaconda Command Prompt` to start a Python Terminal and then type the following commands in order:
1. conda activate bruker_control
2. python Documents\gitrepos\headfix_control\bruker_control\bruker_control.py -t TEAMNAME -i #IMAGINGPLANES -s SUBJECTID -e "YOUR NAME"

- Activating the conda environment `bruker_control` gives Python access to all the packages it needs to run the experiment.

The different arguments on this command line mean...
- -t The team name that your project belongs to (ie "specialk")
- -i The number of imaging planes that you plan to image for your subject
- -s The subject ID for the animal being imaged
- -e Your first and last name. You __MUST__ put this argument in quotes. This one is only used if you'd like to build an NWB file once the imaging session is over.

When you hit enter with this command line, things will get started right away! The next steps below describe the procedure.

#### The Experiment

There's not too much you need to do at this point! The steps are as follows:
1. A preview video will appear on the screen that shows the subject's face. You may have already lined up the sucrose delivery needle and airpuff needles to their correct positions, but if you haven't now is when you should do that. At this point you should also ensure that the microscope's objective is lined up over the lens and lowered to the plane you wish to image.
2. When you're certain you're ready to go and that the Farraday cage is completely closed, you can hit the `Esc` key. This will start the experiment!
3. Watch the magic happen!

At this point, `bruker_control` takes care of the rest! It will automatically generate trial structures that comply with your rules, transmit them to the Arduino, and tell Prairie View to start the recording session of the animal's face and brain activity! It will write out the experiment's information into the `E:` drive appropriate for your team's raw data automatically in it's raw form so its ready for transferring and combining into your team's project directories later.

If you choose to build NWB files at runtime for your animal's microscopy session, `bruker_control` will build an NWB file appropriate for the given experimental session and place that file onto the server for you automatically! For example, if this is the first time you've done some 2P recordings with behavior on the scope (or if you're about to collect the baseline), it will generate NWB formatted files and place them into a newly built `baseline` folder in your project's directory on the server. In order to use this feature, your project must comply with certain directory structure rules. Talk with Jeremy to learn more if you'd like.

## Contributing
If there's anything broken, anything you'd like to help develop, or anything you'd like us to add, please feel free to open up an Issue and describe your needs and desires! Should you make any updates to the codebase, do so on a new branch and then initiate a pull request so it can be reviewed and added to the system!

Good luck with your work!

Check out the first iteration of developer documentation online [here](https://bruker-control.readthedocs.io/en/latest/)!
