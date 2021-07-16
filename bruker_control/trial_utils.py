# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty, Aaron Huffman May 2021

###############################################################################
# Import Packages
###############################################################################
# Import numpy for trial array generation/manipulation
import numpy as np

# Import numpy, default_rng for random trial generation
from numpy.random import default_rng

# Import json for writing trial data to config file
import json

# Dictionary for the percent of trials that should be flipped to zero
# TODO: Should be moved to be part of the configuration file for a project
percent_zeros_dict = {"food_dep": 0.50,
                      "specialk": 0.25}


###############################################################################
# Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray(trials, config_fullpath, project_name, sucrose_only_flag):

    # First, check if sucrose_only_flag is True
    if sucrose_only_flag is True:

        # Tell the user that it was supplied
        print("Generating ONLY sucrose trials...")

        # Create trial array of only sucrose trials
        trialArray = [1]*trials

        # Checking trial array is unnecessary, write to config file.
        # Open config file to write array to file
        with open(config_fullpath, 'r') as inFile:

            # Dump config file into function
            data = json.load(inFile)

        # Assign json variable to trialArray data
        data["trialArray"] = trialArray

        # Write trialArray to file
        with open(config_fullpath, 'w') as outFile:

            # Add trialArray into config file
            json.dump(data, outFile)

    # If the sucrose_only flag is not supplied with a value or is false
    else:

        # Collect correct proportion of zeros with percent_zeros_dict
        percent_zeros = percent_zeros_dict[project_name]

        # Collect number of trials to convert to 0
        num_zeros = round(trials*percent_zeros)

        # Initialize random number generator with default_rng()
        rng = default_rng()

        # Create list of potential flip positions from 3 to the last trial
        # number
        potential_flips = np.arange(3, trials)

        # Make check trials flag to continuously check if trial list is
        # acceptable
        check_trials = True

        while check_trials is True:

            # Create a trial array that's all sucrose trials, to be flipped
            # randomly
            trialArray = [1]*trials

            # Randomly sample positions for flipping using rng.choice from
            # potential flips generated earlier
            flip_positions = rng.choice(potential_flips, size=num_zeros,
                                        replace=False)

            # For each position in the randomly selected flip positions, flip
            # the value from one to zero
            for position in flip_positions:
                trialArray[position] = 0

            # Check if the trials are acceptable
            check_trials = check_trial_structure(trialArray, project_name)

        # Open config file to write array to file
        with open(config_fullpath, 'r') as inFile:

            # Dump config file into function
            data = json.load(inFile)

        # Assign json variable to trialArray data
        data["trialArray"] = trialArray

        # Write trialArray to file
        with open(config_fullpath, 'w') as outFile:

            # Add trialArray into config file
            json.dump(data, outFile)

    # Return trialArray
    return trialArray

# -----------------------------------------------------------------------------
# ITI Array Generation
# -----------------------------------------------------------------------------


def gen_ITIArray(trials, config_fullpath, demo_flag):

    # Initialize empty iti array
    iti_array = []

    if demo_flag is True:

        # Define lower and upper limits on ITI values in ms with small values
        iti_lower, iti_upper = 1000, 3000

    else:

        # Define lower and upper limits on ITI values in ms
        iti_lower, iti_upper = 15000, 30000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from unfiorm distribution
    iti_array = rng.uniform(low=iti_lower, high=iti_upper, size=trials)

    # ITI Array generated will have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    iti_array = np.round(iti_array).astype(int)

    # Finally, generate ITIArray as a list for pySerialTransfer
    ITIArray = iti_array.tolist()

    # Open config file to write array to file
    with open(config_fullpath, 'r') as inFile:

        # Dump config file into function
        data = json.load(inFile)

    # Assign json variable to ITIArray data
    data["ITIArray"] = ITIArray

    # Write ITIArray to file
    with open(config_fullpath, 'w') as outFile:

        # Add ITIArray into config file
        json.dump(data, outFile)

    # Return ITI Array
    return ITIArray


# -----------------------------------------------------------------------------
# Noise Array Generation
# -----------------------------------------------------------------------------


def gen_noiseArray(trials, config_fullpath):

    # Initialize empty noise array
    noise_array = []

    # Define lower and upper limits on ITI values in ms
    noise_lower, noise_upper = 1000, 5000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from uniform distribution
    noise_array = rng.uniform(low=noise_lower, high=noise_upper, size=trials)

    # Noise Array generated will have decimals in it and be float type.
    # Use np.round() to round the elements in the array and type them as int.
    noise_array = np.round(noise_array).astype(int)

    # Finally, generate noiseArray as a list for pySerialTransfer.
    noiseArray = noise_array.tolist()

    # Open config file to write array to file
    with open(config_fullpath, 'r') as inFile:

        # Dump config file into function
        data = json.load(inFile)

    # Assign json variable to noiseArray data
    data["noiseArray"] = noiseArray

    # Write noiseArray to file
    with open(config_fullpath, 'w') as outFile:

        # Add noiseArray into config file
        json.dump(data, outFile)

    # Return the noiseArray
    return noiseArray


###############################################################################
# Trial Check Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Check Function: Zeros and Ones United
# -----------------------------------------------------------------------------


def check_trial_structure(trialArray, project_name):

    print("Checking Trials...")

    if project_name == "specialk":
        check_trials = check_trial_zeros(trialArray)

        return check_trials

    elif project_name == "food_dep":

        check_zeros = check_trial_zeros(trialArray)

        check_ones = check_trial_ones(trialArray)

    if check_zeros + check_ones == 0:

        print("Trials Acceptable")

        print(trialArray)

        check_trials = False

    else:
        print("Array unusable. Reshuffling...")
        check_trials = True

    return check_trials


# -----------------------------------------------------------------------------
# Trial Check Function: Zeros
# -----------------------------------------------------------------------------


def check_trial_zeros(trialArray):

    zeros = 0

    for trial in trialArray:
        if trial == 1:
            zeros = 0
        elif zeros == 3:
            check_zeros = True
            return check_zeros
        else:
            zeros += 1

    check_zeros = False

    return check_zeros


# -----------------------------------------------------------------------------
# Trial Check Function: Ones
# -----------------------------------------------------------------------------


def check_trial_ones(trialArray):

    ones = 0

    for trial in trialArray:
        if trial == 0:
            ones = 0
        elif ones == 3:
            check_ones = True
            return check_ones
        else:
            ones += 1

    check_ones = False

    return check_ones


# -----------------------------------------------------------------------------
# Generate Arrays function to unite these functions
# -----------------------------------------------------------------------------


def generate_arrays(trials, config_fullpath, demo_flag, sucrose_only_flag,
                    project_name):

    # Create Trial Array
    trialArray = gen_trialArray(trials, config_fullpath, project_name,
                                sucrose_only_flag)

    # Create ITI Array
    ITIArray = gen_ITIArray(trials, config_fullpath, demo_flag)

    # Create Noise Array
    noiseArray = gen_noiseArray(trials, config_fullpath)

    # Calculate how long the imaging session for one session will run for
    # without a vacuum being used
    trials_length = (sum(ITIArray) + sum(noiseArray))/1000

    # Currently, vacuum is only used by the specialk project. Check if
    # the project is being used here
    if project_name == "specialk":

        # Vacuum duration is set at a constant 500msec. Calculate seconds the
        # vacuum will be engaged
        vacuum_duration = (500*trials)/1000

        # Consumption duration is set according to the config file
        # TODO: Gather what the consumption duration is from the config file
        consumption_duration = (3000*trials)/1000

        # BUG: Timing for vacuum trials is still incorect despite fix morning
        # of 6/3/21. Re-opening Issue 23

    else:

        # If the project isn't specialk, the project doesn't use the vacuum.
        # Set the vacuum duration and consumption duration to zero
        vacuum_duration = 0

        consumption_duration = 0

    # Session length is the sum of the time needed for the trials, consumption
    # duration, and vacuum duration
    session_length = vacuum_duration + consumption_duration + trials_length

    # Calculate number of video frames by multiplying number of seconds by 30
    # frames per second. Add a buffer of 300 frames to make sure all
    # data is captured
    video_frames = round((session_length * 30) + 360)

    # Open config file to write total number of frames
    with open(config_fullpath, 'r') as inFile:

        # Load the config file
        data = json.load(inFile)

    # Assign json variable to video_frames data
    data["video_frames"] = video_frames

    # Write video_frames to file
    with open(config_fullpath, 'w') as outFile:

        # Add video_frames to to config file
        json.dump(data, outFile)

    # Put arrays together in a list
    array_list = [trialArray, ITIArray, noiseArray]

    # Return list of arrays to be transferred and number of video frames to
    # collect
    return array_list, video_frames
