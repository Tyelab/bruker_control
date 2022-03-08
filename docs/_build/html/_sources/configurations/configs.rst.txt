Configurations
==============

The use of ``bruker_control`` requires an experimental configuration file held inside a ``JSON`` format. These were created as a means of doing the
following:

- Create files that act as documentation which precisely describe the exact parameters used for an experiment for every subject
- Have a reproducible experiment that can be executed using completed configuration files
- Have a standard set of parameters for performing experiments with the system that is flexible for several use cases and simpler to modify and add to
- Avoid generating copies of Arduino sketches at runtime as occured in the first iterations of running headfixed behavior experiments
- Have a file format that can be programmatically accessed when running analysis scripts or searching for particular experiments
- Have templates that can be easily called upon and updated programatically at runtime without requiring user input

Many of these fields were present in the initial Arduino and MATLAB code, but the Arduino scripts had these values hard coded into the sketch itself.
Having a configuration file allows for there to be just one sketch for each team/project as needed that can stand ready for a session without needing to reupload
a new sketch in between running individual animals.

.. _config-values:

********************************
Example Project Config: Behavior
********************************

Below is an example of what such a configuration looks like:

.. literalinclude:: ../../configs/project_config.json
    :language: JSON


------------------------------------
Config Values Key: Behavior Metadata
------------------------------------

Many of the fields were written as to be self explanatory. Below you can find an explainer for each field:
    
- **totalNumberOfTrials**: Total number of trials for an experiment
- **startingReward**: Total number of sucrose trials to deliver in the beginnin
- **maxSequentialReward**: Maximum number of reward trials to allow in a row
- **maxSequentialPunish**: Maximum number of punishment trials to allow in a row
- **punishTone**: Tone in Hertz (Hz) to play through a speaker for the subject
- **rewardTone**: Tone in Hertz (Hz) to play through a speaker for the subject
- **USDeliveryTime_Sucrose**: Time in milliseconds (ms) to open sucrose solenoid
- **USDeliveryTime_Air**: Time in milliseconds (ms) to open the air solenoid
- **USConsumptionTime_Sucrose**: Time in milliseconds (ms) to allow subject to consume sucrose droplet
- **vacuum**: Whether or not a vacuum is enabled for use in the experiment. Either ``True`` or ``False``
- **ITIJitter**: Whether or not to have jitter in inter-trial-interval (ITI) timings
- **baseITI**: Inter-trial-interval (ITI) to use if *no* ``ITIJitter`` is ``False``
- **minITI**: Minimum inter-trial-interval (ITI) value in seconds. Defines lower bound for sampling ITI values
- **maxITI**: Maximum inter-trial-interval (ITI) value in seconds. Defines upper bound for sampling ITI values
- **toneJitter**: Whether or not to have jitter in the duration of tones that are played for the subject. Either ``True`` or ``False``
- **baseTone**: Time to play tone in seconds (s) for subject if ``toneJitter`` is ``False``.
- **minTone**: Minimum time to play tone in seconds (s). Defines lower bound for sampling tone values
- **maxTone**: Maximum time to play tone in seconds (s). Defines upper bound for sampling tone values
- **catchTrials**: Whether or not to have catch trials occur during an experiment. Either ``True`` or ``False``
- **numCatchReward**: Number of reward catch trials to present to the subject
- **numCatchPunish**: Number of punish catch trials to present to the subject
- **catchOffset**: Where in the ``trialArray`` catch trials should be presented. This is defined as the proportion of remaining trials that should be eligible for delivering catch trials.
- **percentPunish**: The proportion of trials that will be punishment trials.
- **stim**: Whether or not to have stimulation trials occur during an experiment. Currently only valid for whole field LED stimulation.
- **shutterOnly**: Whether or not the stimulation trials did not activate LED and only activated PMT shutters.
- **stimFrequency**: Frequency of stimulation in Hertz (Hz) that the whole field LED will perform
- **stimLambda**: Wavelength of stimulating LED in nanometers (nm). This is assumed to be constant for a given project and is for documentation purposes alone
- **stimDeliveryTime_PreCS**: Time in milliseconds (ms) to start LED output *before* presentation of conditioned stimulus
- **stimDeliveryTime_Total**: Total time in milliseconds (ms) that the LED ouptut will be delivered. This is assumed to be constant for a given project and is for documentation purposes alone.
- **stimStartPosition**: ``1-Indexed`` position where LED stimulation should begin. ``trial_utils.py`` will decrement this by 1 so it is ``0-indexed`` for Python/Arduino iterations.
- **numStimReward**: Number of trials to give LED stimulation with a reward
- **numStimPunish**:  Number of trials to give LED stimulation with a punishment
- **numStimAlone**: Number of trials to give LED stimulation alone
- **yoked**: *(NEW)* Whether or not to generate/check for ``yoked`` trial settings
- **trialArray**: Array of integers for trials that the Arduino will iterate through. Valid numbers are 0-6
- **ITIArray**: Array of inter-trial-intervals (ITIs) that the Arduino will iterate through
- **toneArray**: Array of tone durations to deliver to the subject
- **LEDArray**: Array of times for delivering LED stimulation. Calculated by ``trial_utils.py`` by taking the ITI for the appropriate trial and subtracting the ``stimDeliveryTime_PreCS`` value
- **dropped_frames**: List of video frames that are dropped when transferring data from the Genie Nano to the computer during an experiment. Packet loss is rare, but has occured previously.
  
------------------------------------
Config Values Key: Z-Stack Metadata
------------------------------------

If users want to have a z-stack performed for their imaging session before the experiment, they can use this metadata to define parameters used for imaging.

- **zstack**: Whether or not to perform a z-stack for a given recording
- **stack_number**: Number of z-stacks to perform
- **zdelta**: Distance in micrometers (um) to move above and below the selected imaging plane for the z-stack.
- **zstep**: Distance in micrometeres (um)  the scope will move between images.

--------------------------------
Config Values Key: Miscellaneous
--------------------------------

Some users need to make sure a weight has been recorded for the subject being imaged. To ensure that users remember to have weights recorded for their mice, there's
an option to perform a weight check. If the weight check fails, the experiment won't go forward. It is likely that this will be removed in the near future.

************************
Example Subject Metadata
************************

In an effort to make metadata about the subject programmatically available for use in generating Neurodata Without Borders compliant datasets as well as programmatically
update laser power and wavelength for instances where z-stacks required multiple wavelengths for imaging different fluorophores. Below is an example of what the subject
metdata looks like:

.. literalinclude:: ../../configs/mouseid.yml
    :language: YAML

Not every project has this metadata available and no project is required to have it to use the system. Only some of these fields are used by ``bruker_control`` while
a majority of them are used for NWB compliance. ``bruker_control`` does not currently implement NWB files at runtime as it did previously. The module ``nwb_utils.py``
may be reimplemented in the future.

There is currently only 1 field that is used by ``bruker_control``:

- **fluorophore_excition_lambda**: Wavelength in nanometers (nm) that the injected indicator uses for imaging. Value is multiplied by 2 at runtime to change the laser wavelength

The remaining fields are used for documentation of the subject and NWB compliance.

*********************************
Example Subject Metadata: Weights
*********************************

The NWB standard asks for weights to be recorded for a given recording. While they're not required, users typically are weighing subjects before imaging sessions.
In order to programatically add weights to the NWB File and access them later, a weights file was added to store subjects' measurements. The files are very simple and consist
of date/weight pairs. The date format is stored as ``YYYYMMDD`` as with all other dates stored in this system. Weights are stored in kilograms (kg) per the NWB standard's
documentation.

.. literalinclude:: ../../configs/mouseid_weights.yml
    :language: YAML
