# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty May 2021

###############################################################################
# Import Packages
###############################################################################

# Trial Array Generation
# Import scipy.stats truncated normal distribution for ITI Array
# from scipy.stats import truncnorm

# Import numpy for trial array generation/manipulation and Harvesters
import numpy as np

# Import numpy, default_rng for random trial generation
import numpy
from numpy.random import default_rng

# Import json for writing trial data to config file
import json

###############################################################################
# Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray(trials, config_fullpath):

    # Always initialize trial array with 3 reward trials
    trialArray = [1, 1]

    #TODO Implement automatic checking for trial complying with rules
    # Check out https://en.wikipedia.org/wiki/Derangement and stack overflow...
    # Define number of samples needed from generator
    # num_samples = trials - len(trialArray)

    # Initialize random number generator with default_rng
    rng = default_rng()

    shuff_trialArray = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]

    check_trials = True

    while check_trials is True:

        rng.shuffle(shuff_trialArray)
        for i in shuff_trialArray:
            trialArray.append(i)
        print(trialArray)
        trial_check = str(input("Are these trials acceptable? y/n"))

        if trial_check == 'y':
            print("Accepted trials")
            check_trials = False

        else:
            print("reshuffling...")
            trialArray = [1, 1]

    # Generate a random trial array with Generator.integers.  The function is
    # inclusive of the low value and exclusive of the high value.  Therefore,
    # use a low of 0 and high of 2 which will sample from a discrete uniform
    # distribution for either ones or zeros.  Use num_samples to generate the
    # correct number of trials.  Finally, use tolist() to convert random_trials
    # from an np.array to a list.
    # random_trials = rng.integers(
    #                             low=0, high=2, size=num_samples
    #                             ).tolist()
    #
    # # Append the two arrays together
    # for i in random_trials:
    #     trialArray.append(i)

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

        # Define lower and upper limits on ITI values in ms
        iti_lower, iti_upper = 1000, 3000

    else:

        # Define lower and upper limits on ITI values in ms
        iti_lower, iti_upper = 15000, 30000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from unfiorm distribution
    iti_array = rng.uniform(
                            low=iti_lower, high=iti_upper,
                            size=trials
                            )

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
    noise_array = rng.uniform(
                                 low=noise_lower, high=noise_upper,
                                 size=trials
                                )

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


# -----------------------------------------------------------------------------
# Generate Arrays function to unite these functions
# -----------------------------------------------------------------------------


def generate_arrays(trials, config_fullpath, demo_flag):

    # Create Trial Array
    trialArray = gen_trialArray(trials, config_fullpath)

    # Create ITI Array
    ITIArray = gen_ITIArray(trials, config_fullpath, demo_flag)

    # Create Noise Array
    noiseArray = gen_noiseArray(trials, config_fullpath)

    # Calculate how long the experiment will run for
    session_length = (sum(ITIArray) + sum(noiseArray))/1000

    # Calculate number of video frames by multiplying number of seconds by 30
    # frames per second. Add a buffer of 300 frames to make sure all
    # data is captured
    video_frames = round((session_length * 30) + 300)

    print("Number of video frames to be collected:", video_frames)

    # Put arrays together in a list
    array_list = [trialArray, ITIArray, noiseArray]

    # Return list of arrays to be transferred and number of video frames
    return array_list, video_frames
