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

### The Future
There's numerous updates in the works on both the hardware and software side. I include a timeline for how long I think it could take
to implement these things, but it should not be considered a promise that it won't take longer or that it can happen faster. The numbered
lists below do not indicate any particuar priority/order. As each of these things are worked on, new `Issues` will be created and updated
as development proceedes.

**NOTE:** Everything in the `main` repository will stay functional while all these things are added. No developing enhancements for the project
will cause downtime for the system. The `main` branch will _**ALWAYS**_ work as specified in the documentation. Any new functionality will only
be merged into `main` after it's been reviewed by **`Team 2P`** and thoroughly tested for typical use cases.

#### Software
1. _NWB Extensions_

After some discussion with [Ryan Ly](https://github.com/rly), a data engineer with NWB, he suggested including as much metadata about our experiments
as possible including the following (in no particular order):
- Experimental Configuration Parameters (from config files)
- PMT Values set during the acquisition
- Explicit surgical information
- Program versions (Prairie View, Arduino Sketches, and Python)
- Microscope objective type
- Basically whatever else we can think of that's relevant to our setup
- Face recording raw data and processed data integration

_**Timeline**_
For basic metadata extension writing: 1-2 weeks.

For facial recording extension: 4-5 months. There's many things needing investigation using data acquired with the
Bruker setup. The facial recording analysis codebase will be separate from `headfix_control` probably, but I'll include
potential issues here that will inform how `bruker_control` operates.

These issues include:
- Laser lighting up the eyes and interfering with recognition code (loss of pupil information)
- Lighting conditions' influence upon data
- Airpuff interfering with HOG matrices
- Is the animal's facial expression the same bilaterally for airpuff stimuli?
- How should facial recording NWB structure be designed? This datatype is not currently supported...
- Other?

2. _Containerizing RAW data converstion to HDF5 files onto SNL Cluster_

Kay has expressed the need for file conversion and processing to be done on the SNL cluster instead of locally on the machine.
The [Deisseroth Lab](https://github.com/deisseroth-lab/two-photon) has a version of Prairie View's utilities that are containerized into
a [Docker Image](https://www.docker.com/). Jorge recently gave me access to the SNL machines with Docker installed as well as permissions to
build images on the server. The goal here will be to process Prairie View's RAW data formats first into TIFFs and, instead of writing them to disk - 
which would create approx. 18,000 individual files -, append each image into an HDF5 file that is appended to a recording's NWB file. Ideally,
this could be established as a service which will poll approved 2P teams' directories looking for new raw files and, the moment they are present,
start converting them on the very fast SNL hardware into NWB files immediately.

The steps for this happening are as follows:
- Build the container with Docker Compose using the Deisseroth's Lab's codebase by integrating their work with ours
- Thoroughly test conversion: Not certain that we can immediately access TIFF file before it's written to disk. It may be necessary to write an
individual file to disk or batch of files to disk before appending them to the NWB HDF5 file which would slow things down some...
- Place the 2P recording into the NWB file in accordance with their requirements into the correct directories
- Reproduce our Docker image onto every machine with Docker installed
- Develop a script that checks if the Docker enabled machines are available
- Write script that initiates such a search
- Develop automatic polling of directories for new files **(Lowest priority)**

_**Timeline**_
For containerization, testing, and reproducing the image on multiple machines: 3-4 weeks. For initiating the search and checking if machines
are busy/waiting if they are: 1-2 weeks.

3. _GUI Development_

The system would benefit from the development of a GUI, or Graphical User Interface, so it's easier to interact with. I have looked into a couple
different frameworks including `Tkinter`, `PyQt5/6`, and `Gooey`.

The steps for this happening are as follows:
- Choose GUI framework
- Design GUI itself
- Incorporate and test functionality with the GUI

_**Timeline**_
To build and test a simple GUI shouldn't (hopefully) be too difficult, but there could be some additional refactoring that's necessary: 2-3 weeks.

4. _Automated Plane Searching in Prairie View_

Prairie View has no functionality for automatically searching for the reference plane that was imaged when finding cells unlike the NLW scope.
A project like this one is likely not particularly necessary and is not something I will work on unless we explicitly need it. It would be
incredibly fun and cool though if it worked. 👀

It would require purchasing a couple things:
- CMOS Camera for the scope that interfaces with Prairie View
- GPU for the machine BRUKER so it could perform image recognition without crashing the CPU

The steps for this happening are as follows:
- Assemble training data
- Perform labeling for individual planes for each animal
- Build networks for each animal (unlikely that one network could generalize to all planes)
- Grab images off of Prairie View with the Prairie Link application
- Use network to classify image and move microscope until reference image is found

_**Timeline**_
This would likely take quite a long time to get into a production ready place...

5. _Z-Stacks and Overlaying Different Images Together_

For Austin's project at least, we will need to take a Z-stack for each animal's reference plane for both GCaMP and DLIGHT.

The steps for accomplishing this are as follows:
- Interface with Prairie View Z-Stack functionality and incorporate into experimental runtime in `bruker_control.py`
- Determine how to incorporate this into NWB standard, unsure if Z-stacks are supported

_**Timeline**_
1-2 Weeks

#### Hardware
1. Optimize lighting conditions
2. Optimize camera position
3. Get filter for camera lens that blocks laser wavelengths
4. Create a "sight" for airpuff alignment

## Contributing
If there's anything broken, anything you'd like to help develop, or anything you'd like us to add, please feel free to open up an Issue and describe your needs and desires! Should you make any updates to the codebase, do so on a new branch and then initiate a pull request so it can be reviewed and added to the system!

Good luck with your work!

Check out the first iteration of developer documentation online [here](https://bruker-control.readthedocs.io/en/latest/)!
