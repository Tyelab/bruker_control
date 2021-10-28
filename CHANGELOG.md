# Changelog
Any changes made by **`Team 2P`** that make it into the `main` branch are logged here.

A changelog for commits and changes before this version will not be added.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## bruker_control.py v1.8.2 Hotfix
Small fix to versioning numbers, longer timing for `set_laser_lambda` as it was too short
when going between laser wavelengths. Changed where Z-stack `tqdm` progress bar occurs
and made timing more representative of actual progress.

## bruker_control.py v.1.8.0 *Stimulate Your Mind* 🔦 🎆 🧠 - 2021-10-27
Welcome to v1.8.0! There's plenty to be thankful for as we move towards November, and
one of those things is optogenetics and big bright LEDs! This update adds a hefty amount,
so eat slowly and try not to stuff yourself like a turkey 🦃 just yet.

There's some enhancements made to the trial structure generation to handle stimulations as well as
more expressive metadata for behavioral experiments that encode how stimulations are to
be performed for the session. There's also some additional exception handling classes for
if/when something is entered incorrectly thought they're not comprehensive. The documentation 
also has a couple changes.

:heart: Jeremy Delahanty

### Added

**_Python_**

New command line parameter: Project
**Required**
- --project, -p:

If you're one of the teams that has more than one project going, this argument requires a
two letter code that references the project's name.

*Stimulation Configuration* - behavior_projectcode_config.json
- stim: true/false Do you want stimulations to happen during the trial?
- stimFrequency: Metadata about pulse rate in Hz
- stimPulseTime: Metadata about how long an individual pulse occurs in ms
- stimLabmda: Frequency of stimluation LED being used in the experiment
- stimDeliveryTime_PreCS: Amount of time before a given trial the stimulation should occur
- stimDeliveryTime_Total: How long the stimulation should occur
- stimStartPosition: 0-indexed position of which trials should be LED stimulation trials
- numStimReward: Number of LED trials where the subject should be given a reward
- numStimPunish: Number of LED trials where the subject should be given a punishment
- numStimAlone: Number of LED trials where the subject will receive only LED stimulation
- LEDArray: Array of timepoints where the LED stimulation should be triggered by the Arduino

*`trial_utils.py`: Stimulation Trial Rules*
A few new functions have been added for handling LED stimulation trial structure generation.

- `gen_trialArray_nostim()`: Builds trial structure according to configuraiton rules without LED
stimulation trials
- `gen_trialArray_stim()`: Builds trial structure according to configuration rules with LED
stimulation trials.
- `gen_LEDArray()`: Generates timestamp array for when LED trials should be triggered.
- `flip_stim_trials()`: Flips non-stimulation trials into LED trials within the range of
requested LED trials. Checks to ensure that no more than user configured number of punish
trials are given in a row.
- `flip_stim_only()`: Flips stimulation trials to LED only trials.
- `check_session_stim_only()`: Performs check that no more than 2 LED Only trials are given
in a row.

*`config_utils.py`: New exception classes and enhanced configuration*
Configuration exception classes that are more helpful for when something is missing/malformed
have been made. There's also new handling for the configuration stimulation fields.
**Classes**

- `ProjectNWBConfigMissing(Exception)`
- `ProjectNWBConfigMultiple(Exception)`
- `ProjectTemplateMissing(Exception)`
- `ProjectTemplateMultiple(Exception)`
- `SubjectMultiple(Exception)`
- `SubjectMissing(Exception)`
- `SubjectMissingWeight(Exception)`

**Functions**

- `build_server_directory()`: Builds directory to `snlkt/data/raw/` for the appropriate
project and subject for that day's imaging. This is where NWBFiles will be written
and where the day's imaging data will be written to.

*`nwb_utils.py`: Determine Sessions for CMS Project and XML Exception Handling*
Due to the use of stimulations and voltage outputs in the new paradigm, the
`xml.etree.ElementTree` parser crashes when reading the `.env` file when it
encounters invalid characters that are produced in v1.0 XML but are not supported
until v1.1. Microsoft's .NET implementation does not yet correct for this, but 
per Michael Fox (Senior Software Engineer at Bruker who has been helping me enormously)
Microsoft has let this (minor) problem persist for decades. The use of `lxml` has been
added to the program should the `xml.etree` module fail as it has an option to escape
badly formed XML with the `recover=True` option.

*`prairieview_utils.py`: Setting Channels and Lasers*
New functions are present for telling Prairie View to use different channels when
appropriate for what functional indicator is being imaged at the time of the
experiment.

- `set_one_channel_zseries`: Sets appropirate channel for imaging a specific
indicator. Uses either Red (Ch1) or Green (Ch2).


**_Arduino_**

The Arduino sketch for team specialk has been updated to handle the new transferring
of LED array, LED Trial types, LED Timings, and LED Triggers. Doc strings have been added
for all these new functions in the source.

- `typeLED()`: Used for determining what kind of LED trial is occuring and prints it to
Serial monitor for the user.
- `setLEDStart()`: Used for calculating when to send an LED trigger
- `brukerTriggerLED()`: Sends signal to Bruker DAQ if an LED is scheduled to occur.

**_Shell Scripting_**

A new script called `bruker_transfer_utility.sh` has been written for automatic transferring
of files to the server. It is currently only usable by team Specialk because it is the only
team that has the directory structure built and ready to use on the file server. It's use is
simple and is outlined in the updated `README` at the end of the document. It uses the tool
`rsync` to conduct the file transfer to the SNL server.

**_Prairie View_**

A new "Mark Points Series" has been incorporated for team specialk as has a new "Voltage
Output" experiment that is synced with "Mark Points" when a Stimulation Experiment is
being conducted.

### Changed

**_Python_**

There are some minor changes associated with how things operate in Python.

*`serialtransfer_utils.py`*
- Introduced new metadata variable for transmission that encodes the stimulation array.

*`prairieview_utils.py`*
- Added a progress bar and increased amount of time for laser changes to 5 seconds in `set_laser_lambda`
- Added a progress bar for z-stacks in `z-stack` so the terminal doesn't look like it's hanging during
operation.

**_Arudino_**

The Serial Monitor is a little less busy now. Far fewer things are printed to the terminal in favor
of a cleaner appearance for just trial type, trial number, and when the stimuli is delivered to the subject.
This has only been done for Specialk because I'm unsure if other teams would want/request this.

**_Prairie View_**

The team specialk Voltage Recording has been changed to include the LED590 stimulations if the session
calls for it.


## bruker_control.py v.1.6.0 *Big Mac* - 2021-10-02

This is v1.6.0!  It might be spooky season, but have no fear! This update isn't so scary.
This update adds automated z-stack functionality to the system as well as some enhanced
`subject_metadata` information parsing for performing z-stack to t-series recordings
seamlessly. Lots of things have been changed so take a bite of the *Big Mac* update by
reading on! 🍔

:heart: Jeremy Delahanty

### Added

Z-stack functions added to `prairieview_utils` with the following functions:
- set_galvo_galvo() Function for gathering Z-stack images
- set_laser_lambda() for changing laser wavelengths according to imaging indicators
- set_zseries_filename() Sets filename and directories for Z-stacks correctly
- set_zseries_parameters() Sets up the Z-series values for step size, start/stop positions
- get_imaging_indicators() Gathers indicator information from surgical metadata in a subject

Configuration Information:
**Required**
- `zstack_metadata`: Whether to perform a z-stack or not in a given experiment as well as
the values required by Prairie View for setting up the acquisition correctly.

**Optional**
- Surgery metadata added to subject metadata files

### Changed
- Moved virus information to subject metadata from project metadata
- Moved `get_subject_metadata()` to `config_utils`
- Set coordinates for `origin_coords` using surgical information for imaging plane in NWB file
per Ryan Ly's advice.


## Configurations- 2021-09-16

### Added
- Example animal configuration .yml file
- Example project NWB file

### Changed
- Updated example Arduino configuration to enhanced version

### Removed
- Old template Arduino configuration files.

## bruker_disc_deryn.ino v1.0.1 - 2021-09-16

### Added

Doc strings for all functions now present that are accurate to project's setup.

### Changed

Corrected some typos in the documentation

## bruker_disc_specialk.ino v1.0.1 - 2021-09-15

### Changed

Start new ITI after presentation of sucrose droplet is complete. Now both Deryn and Austin's projects
start ITIs the moment the tone is complete.

Removed ITI delivery output from specialk Arduino sketch.

## bruker_control.py v1.0.0 - 2021-09-13
This is v1.0! There's been several things added and several things changed after refactoring the code
for a few weeks. Check out the info below!

:heart: Jeremy Delahanty

Each section, if it has a block of text, also has a short `In summary` section in case it's TLDR.

### Added

#### _Arduino_
- Doc strings for functions in Arduino sketches
- Added ITI and tone specific DAQ outputs
- Catch trial functionality
- Automatic resetting of Arduino after experiment is finished
- Semantic versioning for sketches

#### _Prairie View_
- Project specific configurations for Prairie View recordings' data output
- Automated Z-plane acquisition for file naming (ie 20210913_MOUSEID_plane1_**-221.12**_...)
- Automated switching to `Resonant Galvo` mode in case user forgets to select it

#### _Python: bruker_control_
- Doc strings for every function
- More descriptive inline comments in functions
- Read the Docs technical documentation hosted ([found here!](bruker-control.readthedocs.io/en/latest/))
- Semantic versioning
- Exceptions for missing configurations and camera disconnects
- Enhanced configuration and customization for trial structure
- Catch trials added
- Writing out list of missing video frames to configuration file
- **(Optional)** Experimenter argument at command line
- **(Optional)** Automated parsing of Prairie View `.env` files for NWB specific microscope information
- **(Optional)** Automated writing of base NWB files to specific directory on the server for a project.

#### _Directory Structures_
Each team that interfaces with the Bruker system will have a folder on the server named `2p_template_configs`.
This will contain the template configuration file for the team's experiment runtime and, if desired, a project
specific configuration file that can be reused for building NWB files later on.
Another optional addition is if you would like to have your base files written to the server in automatically
generated locations appropriate for your subject's place in the experimental timeline.
For example, if you are recording from an animal for its baseline experiment, the system will correctly identify
the animal as being in the baseline stage, build a location on the server for that subject with the appropriate
names, and write a baseline file for you the moment the recording is finished. Given that the experimenter knows
precisely how many 2P recording sessions will be collected for a given subject, an appropriate automated solution
can be implemented for each new project or team.

In summary:
- **Required** Team specific template configuration directory that is hosted on the server
- **(Optional)** Subject metadata directory that is hosted on the server

#### _Metadata and Configuration Files_
Users can have subject specific and project specific metadata files added to their directories.
An optional addition is to have a set of metadata files for animals that contain NWB specific information.
This information includes the subject's ID, strain, date of birth, genotype, sex, and weight.
These could be used when generating NWB files later or, if desired, at runtime of the experiment.
These files are not part of the repository itself, but can be used with it. Examples of them are present
on the repository in the `configs` directory.

In summary:
- **Required** Project specific template
- **(Optional)** Subject specific metadata files
- **(Optional)** Project specific configuration files

#### _NWB Support_
As described above, if the user would like to build a base NWB file at the end of the recording, `bruker_control.py`
is now capable of doing so. Once the microscopy session is completed, the program will grab relevant metadata for
the subject and project from the files described above as well as parse the Prairie View `.env` file that is generated by
the recording. The program will then build a base NWB file for the subject's recording to which the recording's data
can be added to at a later time. These files are written directly to the server in the subject's appropriate experimental
location as described in the _`Directory Structures`_ section above.

In summary:
- If desired, a base NWB file can be generated once the experiment is finished and would be written to the subject's appropriate
directory on the server automatically.

### Changed
- CLI (Command Line Interface) has different arguments: `-t` for the team - formerly `-p` for project - as in `specialk`, `-i` for number of imaging planes,
`-s` for subject - formerly `-m` for mouse - ID, and `-e` for experimenter if using the NWB functionality.
- Arduino variables that were once called `noise` are now all changed to `tone` **EXCEPT** in the case of the `noise` boolean flag.
This cannot be changed to `tone` as tone is a protected name for the `tone()` function in Arduino's IDE.
- Changed Arduino sketch name for team `specialk` to be more specific for the team.
- Raw data is written to a `team` directory instead of a `studies` directory
- Raw Prairie View data is written into a folder with `_raw` appended to the end of it as in `YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw`.
- README.md updated with (very basic) `bruker_control.py` procedure
- Stimulus presentation now overlaps the end of the tone by default

### Removed
- Unused Arduino sketches and configuration files
- `Behavior only` and its associated functions have been deprecated and removed from the repository
- `Sucrose only` and its associated functions have been deprecated and removed from the repository
- The `behavior` directory for the raw data has been removed as Prairie View does not support having different
directories for placing the raw microscopy and voltage recording files.
