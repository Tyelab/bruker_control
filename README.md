[![Documentation Status](https://readthedocs.org/projects/bruker-control/badge/?version=latest)](https://bruker-control.readthedocs.io/en/latest/?badge=latest)

# bruker_control

Repository for Python and Arduino code running behavior experiments for the Tye Lab at the Bruker Ultima Multi-photon Microscope.

## bruker_control.py v1.10.3: Get Yoked! 🏋️ 🏋️‍♂️ 🏋️‍♀️
A (very) basic rundown of the experimental runtime is included below.

![User Execution Graph](https://github.com/Tyelab/headfix_control/blob/main/docs/images/bruker_user_execution_graph.svg)

### User Guide

The user guide has been migrated to readthedocs.org. You can find it [here](https://bruker-control.readthedocs.io/en/latest/?badge=latest)!

### The Future
There's numerous updates in the works on both the hardware and software side. I include a timeline for how long I think it could take
to implement these things, but it should not be considered a promise that it won't take longer or that it cant' happen faster. The numbered
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

**_The first steps of this have been completed! We can now spawn many converters across docker enabled machines. Enabling an automated conversion to H5
is the next step. Automatically initiating this conversion process using CRON is under development. Developments can be found in the `bruker_pipeline`
repository in this organization._**

Kay has expressed the need for file conversion and processing to be done on the SNL cluster instead of locally on the machine.
The [Deisseroth Lab](https://github.com/deisseroth-lab/two-photon) has a version of Prairie View's utilities that are containerized into
a [Docker Image](https://www.docker.com/). Jorge recently gave me access to the SNL machines with Docker installed as well as permissions to
build images on the server. The goal here will be to process Prairie View's RAW data formats first into TIFFs and, instead of writing them to disk - 
which would create approx. 18,000 individual files -, append each image into an HDF5 file that is appended to a recording's NWB file. Ideally,
this could be established as a service which will poll approved 2P teams' directories looking for new raw files and, the moment they are present,
start converting them on the very fast SNL hardware into NWB files immediately.

The steps for this happening are as follows:
- Build the container with Docker Compose using the Deisseroth's Lab's codebase by integrating their work with ours **DONE!**
- Thoroughly test conversion: Not certain that we can immediately access TIFF file before it's written to disk. It may be necessary to write an
individual file to disk or batch of files to disk before appending them to the NWB HDF5 file which would slow things down some... **NOT NECESSARY**
- Place the 2P recording into the NWB file in accordance with their requirements into the correct directories **WILL NOT BE DONE**
- Reproduce our Docker image onto every machine with Docker installed **NOT NECESSARY**
- Develop a script that checks if the Docker enabled machines are available
- Write script that initiates such a search
- Develop automatic polling of directories for new files **(Lowest priority)**

_**Timeline**_
Initiating the search and checking if machines are busy/waiting if they are: 1-2 weeks.

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

#### Hardware
1. Optimize lighting conditions
2. Optimize camera position
3. Get filter for camera lens that blocks laser wavelengths - Purchased 3/8/22!
4. Create a "sight" for airpuff alignment

## Contributing
If there's anything broken, anything you'd like to help develop, or anything you'd like us to add, please feel free to open up an Issue and describe your needs and desires! Should you make any updates to the codebase, do so on a new branch and then initiate a pull request so it can be reviewed and added to the system!

Good luck with your work!

## Authors

[Jeremy Delahanty](https://github.com/jmdelahanty)\
Maintainer\
Research Assistant I\
Tye Lab, Salk Institute for Biological Studies

Deryn LeDuke\
UCSD Neurosciences Graduate Student\
Tye Lab, Salk Institute for Biological Studies

Kyle Fischer PhD\
Gene Therapy Research Scientist\
Gene Therapy Division, Neurocrine

Dexter Tsin\
Incoming Princeton Neuroscience Graduate Student! Congrats Dexter!\
Former Tye Lab, Salk Institute for Biological Studies

Annie Ehler\
Computer Analyst I\
Tye Lab, Salk Institute for Biological Studies
