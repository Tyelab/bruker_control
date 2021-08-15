# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty, Aaron Huffman May 2021

###############################################################################
# Import Packages
###############################################################################
# Import numpy for trial array generation/manipulation
import numpy as np

# Import numpy, default_rng for random trial generation
from numpy.random import default_rng

from operator import itemgetter

###############################################################################
# Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray(config_template):
    """
    Creates pseudorandom trial structure for binary discrimination task.

    Generates array of stimuli and catch trials from configuration file the
    user provides.  1s and 0s encode stimuli where 1 is reward and 0 is
    punishment. 2s and 3s encode catch trials where 2 is aversive catch and
    3 is reward catch.

    Args:

        Configuration template value dictionary gathered from team's
        configuration .json file.

    Returns:

        ndarray: Trial array with user specified trial structure.
    """

    # Create trial array that's all reward trials, to be flipped randomly
    fresh_array = np.ones(config_template["metadata"]["totalNumberOfTrials"],
                         dtype=int)

    # Calculate the number of punishment trials to deliver
    num_punish = round(config_template["metadata"]["percentPunish"]
                       * len(fresh_array))

    # Generate potential flip positions for punish trials
    potential_flips = np.arange(config_template["metadata"]["startingReward"],
                                len(fresh_array))

    punish_check = True
    catch_check = True

    while punish_check + catch_check != 0:

        tmp_array = fresh_array.copy()

        trialArray, punish_check = flip_punishments(tmp_array, potential_flips,
                                                    num_punish)

        trialArray, catch_check = flip_catch(trialArray,
                                             config_template)

    return trialArray


def flip_catch(trialArray, config_template):

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Get number of reward catch trials to deliver
    num_catch_reward = config_template["metadata"]["numCatchReward"]

    # Get number of punishment catch trials
    num_catch_punish = config_template["metadata"]["numCatchPunish"]

    # Get position for where catch trials are to start for session
    catch_offset = config_template["metadata"]["catchOffset"]

    # Get position to start flipping catch trials
    catch_index_start = round(len(trialArray) -
                              (len(trialArray) * catch_offset))

    # Get indexes for the possible catch trials
    catch_idxs = [idx for idx in range(catch_index_start, len(trialArray))]

    # Get values of possible catch trials
    catch_values = list(itemgetter(*catch_idxs)(trialArray))

    # Make dictionary of values for punish trials
    catch_dict = {catch_idxs[i]: catch_values[i] for i in range(len(catch_idxs))}

    # Make list of punish trial indexes
    punish_trials = [key for key in catch_dict if catch_dict[key] == 0]

    # Make list of reward trial indexes
    reward_trials = [key for key in catch_dict if catch_dict[key] == 1]

    if len(punish_trials) < num_catch_punish:
        print("Not enough punish trials to flip into catch trials! Reshuffling...")
        return trialArray, catch_check

    elif len(reward_trials) < num_catch_reward:
        print("Not enough reward trials to flip into catch trials! Reshuffling...")
        return trialArray, catch_check

    else:
        catch_check = False

    punish_catch_list = punish_catch_sample(punish_trials, num_catch_punish)

    for index in punish_catch_list:
        trialArray[index] = 2

    reward_catch_list = reward_catch_sample(reward_trials, num_catch_reward)

    for index in reward_catch_list:
        trialArray[index] = 3

    return trialArray, catch_check


def reward_catch_sample(reward_trials, num_catch_reward):

    rng = default_rng()

    reward_catch_list = rng.choice(reward_trials, size=num_catch_reward).tolist()

    return reward_catch_list


def punish_catch_sample(punish_trials, num_catch_punish):

    rng = default_rng()

    punish_catch_list = rng.choice(punish_trials, size=num_catch_punish).tolist()

    return punish_catch_list


def check_trial_punishments(trialArray):

    zeros = 0

    punish_check = False

    for trial in trialArray:
        if trial == 1:
            zeros = 0
        elif zeros == 3:
            punish_check = True
            break
        else:
            zeros += 1

    return punish_check

def flip_punishments(tmp_array, potential_flips, num_punish):

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    punish_flips = rng.choice(potential_flips, size=num_punish,
                              replace=False)

    for index in punish_flips:
        tmp_array[index] = 0

    # Select flip positions for punish trials by random sample
    punish_status = check_trial_punishments(tmp_array)

    return tmp_array, punish_status


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
