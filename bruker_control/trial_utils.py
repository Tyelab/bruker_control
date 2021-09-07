# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty, Aaron Huffman May 2021

###############################################################################
# Import Packages
###############################################################################
# Import numpy for trial array generation/manipulation
import numpy as np

# Import numpy, default_rng for random trial generation
from numpy.random import default_rng

# Import itemgetter for getting indexes of punish/reward trials for catch
# trials.
from operator import itemgetter

# Import Tuple for appropriate typehinting of functions
from typing import Tuple


###############################################################################
# Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray(config_template: dict) -> np.ndarray:
    """
    Creates pseudorandom trial structure for binary discrimination task.

    Generates array of stimuli and catch trials from configuration file the
    user provides.  1s and 0s encode stimuli where 1 is reward and 0 is
    punishment. 2s and 3s encode catch trials where 2 is aversive catch and
    3 is reward catch.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        trialArray
            Trial array with user specified trial structure.
    """

    # Create trial array that's all reward trials, to be flipped randomly
    fresh_array = np.ones(config_template["metadata"]["totalNumberOfTrials"],
                          dtype=int)

    # Calculate the number of punishment trials to deliver
    num_punish = round(config_template["metadata"]["percentPunish"]
                       * len(fresh_array))

    # Get maximum number of punishment trials that can occur in a row
    max_seq_punish = config_template["metadata"]["maxSequentialPunish"]

    # Get maximum number of reward trials that can occur in a row
    max_seq_reward = config_template["metadata"]["maxSequentialReward"]

    # Generate potential flip positions for punish trials by making array of
    # trial indexes starting just after the starting rewards until the end
    # of the experimental session.
    potential_flips = np.arange(config_template["metadata"]["startingReward"],
                                len(fresh_array))

    # Create punish, reward, and catch trial statuses for checking after
    # flipping trial types in the next step
    punish_check = True
    reward_check = True
    catch_check = True

    # While the punish and catch checks are not BOTH False (or zero)
    while punish_check + catch_check + reward_check != 0:

        # Create temporary array that's a fresh copy of starting array
        tmp_array = fresh_array.copy()

        # Perform the flips for punish trials upon the tmp_array using
        # list of potential flips and the number of punish trials specified
        trialArray, punish_check = flip_punishments(tmp_array, potential_flips,
                                                    num_punish, max_seq_punish)

        # If the number of punish trials is less than half, getting a valid
        # trial set is unlikely if the number of rewards in a row is
        # restricted.  Therefore, sest the reward_check to False.
        if config_template["metadata"]["percentPunish"] < 0.50:
            reward_check = False

        # Otherwise use check_session_rewards to ensure trial structure is
        # compliant with study's rules.
        else:
            reward_check = check_session_rewards(trialArray, max_seq_reward)

        # Use generated trialArray and config_template values to perform
        # catch trial flips
        trialArray, catch_check = flip_catch(trialArray,
                                             config_template,
                                             catch_check)

    return trialArray


def flip_catch(trialArray: np.ndarray, config_template: dict,
               catch_check: bool) -> Tuple[np.ndarray, bool]:
    """
    Flips trials to catches in checked trialArray.

    Flips subset of trials depending on user specified offset and selected
    number of reward/punish catch trials.

    Args:
        trialArray:
            Checked trialArray returned by flip_punishments()
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.
        catch_check:
            Boolean status for catch trials being flipped or not.

    Returns:
        trialArray
            trialArray with catch trials added
        catch_check
            Boolean status for catch trials being flipped or not.
    """

    # Get number of reward catch trials to deliver
    num_catch_reward = config_template["metadata"]["numCatchReward"]

    # Get number of punishment catch trials
    num_catch_punish = config_template["metadata"]["numCatchPunish"]

    # Get position for where catch trials are to start for session
    catch_offset = config_template["metadata"]["catchOffset"]

    # Get length of trialArray
    trialArray_len = len(trialArray)

    # Get position to start flipping catch trials using offset
    catch_index_start = round(trialArray_len - (trialArray_len * catch_offset))

    # Get indexes for the possible catch trials
    catch_idxs = [idx for idx in range(catch_index_start, trialArray_len)]

    # Get values of possible catch trials and convert them to a list using
    # the operator itemgetter
    catch_values = list(itemgetter(*catch_idxs)(trialArray))

    # Make dictionary of values for punish trials
    catch_dict = {catch_idxs[i]: catch_values[i] for i
                  in range(len(catch_idxs))}

    # Make list of punish trial indexes
    punish_trials = [key for key in catch_dict if catch_dict[key] == 0]

    # Make list of reward trial indexes
    reward_trials = [key for key in catch_dict if catch_dict[key] == 1]

    # If the length of punish trials in subset obtained by offset, there's not
    # enough punish trials available!  Returns the trialArray and a True catch
    # check.  If that's not the case, then we can move forward.
    if len(punish_trials) < num_catch_punish:
        print("Not enough punish trials to flip into catches! Reshuffling...")
        return trialArray, catch_check

    # If the length of reward trials in subset obtained by offset, there's not
    # enough reward trials available!  Returns the trialArray and a True catch
    # check.  If that's not the case, then we can move forward.
    elif len(reward_trials) < num_catch_reward:
        print("Not enough reward trials to flip into catches! Reshuffling...")
        return trialArray, catch_check

    # Else, the catch check has passed and its status can be set to False.
    else:
        catch_check = False

    # Get random sample of available catch indexes for punish trials past
    # offset
    punish_catch_list = punish_catch_sample(punish_trials, num_catch_punish)

    # For each index in the chosen punish_catch_list, change the trial's value
    # to 2.
    # TODO: This should be made a function or perhaps a method on array
    for index in punish_catch_list:
        trialArray[index] = 2

    # Get random sample of available catch indexes for reward trials past
    # offset
    reward_catch_list = reward_catch_sample(reward_trials, num_catch_reward)

    # For each index in the chosen punish_catch_list, change the trial's value
    # to 3.
    # TODO: This should be made a function or perhaps a method on array
    for index in reward_catch_list:
        trialArray[index] = 3

    # Return the trialArray with flipped trials as well as the catch_check
    # status.
    return trialArray, catch_check


def reward_catch_sample(reward_trials: list, num_catch_reward: int) -> list:
    """
    Generate random sample of reward trial indexes to flip.

    Randomly select trials out of possible reweard positions to flip to catch
    trials depending on the number of catch trials specified by the user.

    Args:
        reward_trials:
            List of reward trial indexes past specified offset contained in the
            trialArray.
        num_catch_reward:
            Number of reward catch trials to implement as specified by the user

    Returns:
        Sampled reward catch trial index list.
    """

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Perform random sample with rng.choice from reward_trials list for the
    # number of reward catch trials specified and finally convert it to a list.
    reward_catch_list = rng.choice(reward_trials,
                                   size=num_catch_reward).tolist()

    return reward_catch_list


def punish_catch_sample(punish_trials: list, num_catch_punish: int) -> list:
    """
    Generate random sample of punish trial indexes to flip.

    Randomly select trials out of possible punish positions to flip to catch
    trials depending on the number of catch trials specified by the user.

    Args:
        punish_trials:
            List of reward trial indexes past specified offset contained in the
            trialArray.

        num_catch_punish:
            Number of punish catch trials to implement as specified by the user

    Returns:
        Sampled punish catch trial index list.
    """

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Perform random sample with rng.choice from punish_trials list for the
    # number of punish catch trials specified and finally convert it to a list.
    punish_catch_list = rng.choice(punish_trials,
                                   size=num_catch_punish).tolist()

    return punish_catch_list


def check_session_punishments(trialArray: np.ndarray,
                              max_seq_punish: int) -> bool:
    """
    Check if too many punish trials happen sequentially

    Takes in trialArray after punish trial flips and determines if more than
    user defined max number of punish trials occur in a row. If so, the
    punish_check is returned True.

    Args:
        trialArray:
            Trial array post punish trial flips
        max_seq_punish:
            Maximum number of sequential punishment trials from config_template

    Returns:
        punish_check
    """

    # Start punishment count at zero
    punishments = 0

    # Set punish check to False.  If successful, a False status is returned
    # which allows system to move forward.
    punish_check = False

    # Loop over the trialArray
    for trial in trialArray:

        # If the trial is a reward trial (1), set number of punishments in a
        # row to zero
        if trial == 1:
            punishments = 0

        # If the number of punishments in a row reaches max number of allowed
        # punishment trials from configuration, set punish_check as True and
        # break the loop.
        elif punishments == max_seq_punish:
            punish_check = True
            break

        # If the trial is a punish trial and 3 haven't happened in a row yet,
        # increment the number of punishments.
        else:
            punishments += 1

    return punish_check


def check_session_rewards(trialArray: np.ndarray, max_seq_reward: int) -> bool:
    """
    Check if too many reward trials happen sequentially.

    Takes in trialArray after punish trial flips and determines if more than
    user defined max number of reward trials occur in a row. If so, the
    reward_check is returned True.

    Args:
        trialArray:
            Trial array post punish trial flips
        max_seq_reward:
            Maximum number of sequential reward trials from config_template

    Returns:
        punish_check_status
    """

    # Start reward count at 0
    rewards = 0

    # Set reward_check to False.  If successful, a False status is returned
    # which allows system to move forward.
    reward_check = False

    # Loop over the trialArray
    for trial in trialArray:

        # If the trial is a punishment trial (0), set number of rewards in a
        # row to 0.
        if trial == 0:
            rewards = 0

        # If the number of rewards in a row reaches max number of allowed
        # reward trials from configuration, set punish_check as True and break
        # the loop.
        elif rewards == max_seq_reward:
            reward_check = True
            break

        # If the trial is a punish trial and there haven't been too many
        # reward trials in a row, increment the number of punishments.
        else:
            rewards += 1

    return reward_check


def flip_punishments(tmp_array: np.ndarray, potential_flips: np.ndarray,
                     num_punish: int, max_seq_punish: int) -> Tuple[np.ndarray,
                                                                    bool]:
    """
    Flips user specified number of trials to punishments over trialArray copy.

    Takes in a copy of the fresh trialArray called tmp_array, takes a random
    sample of potential flip positions for punishment trials, and flips their
    value from 1, reward, to 0, punishment.

    Args:
        tmp_array:
            Copy of fresh trialArray consisting of all reward trials
        potential_flips:
            Array of potential indexes to flip to punishments
        num_punish:
            Integer of number of punishment trials to flip for session

    Returns:
        tmp_array
            Modified array containing flipped values, to be saved as trialArray

        punish_check
            Boolean status of whether the array meets experimenter defined
            criteria. False if successful, True if failed.
    """

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Perform random sample with rng.choice from punish_trials list for the
    # number of punish catch trials specified and finally convert it to a list.
    punish_flips = rng.choice(potential_flips, size=num_punish,
                              replace=False)

    # For each index in the chosen punish_flips, change the trial's value
    # to 0.
    for index in punish_flips:
        tmp_array[index] = 0

    # Select flip positions for punish trials by random sample
    punish_status = check_session_punishments(tmp_array, max_seq_punish)

    # Return the tmp_array to be saved as trialArray and the punish_status
    return tmp_array, punish_status


# -----------------------------------------------------------------------------
# ITI Array Generation
# -----------------------------------------------------------------------------


def gen_jitter_ITIArray(config_template: dict) -> list:
    """
    Generate jittered ITIArray for given experiment from user specified bounds.

    Generates array of ITIs from configuration the user provides.  Uses a
    random uniform distribution bounded by the lower and upper ITIs as defined
    in the configuration file.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        Jittered ITIArray.
    """

    # Initialize empty iti array
    iti_array = []

    # Get total number of trials
    num_trials = config_template["metadata"]["totalNumberOfTrials"]

    # Get minimum ITI value from configuration and multiply by 1000 to convert
    # to milliseconds
    iti_lower = config_template["metadata"]["minITI"]*1000

    # Get maximum ITI value from configuation and mulitply by 1000 to convert
    # to milliseconds.
    iti_upper = config_template["metadata"]["maxITI"]*1000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from unfiorm distribution bound by the lower
    # and upper ITIs
    iti_array = rng.uniform(low=iti_lower, high=iti_upper, size=num_trials)

    # ITI Array generated will have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int.
    # Finally, convert the array to a list for pySerialTransfer.
    ITIArray = np.round(iti_array).astype(int).tolist()

    return ITIArray


def gen_static_ITIArray(config_template: dict) -> list:
    """
    Generate static, or without jitter, ITIArray.

    Generates array of ITIs using baseITI from configuration file for the
    number of trials specified by the user.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        Static ITIArray
    """

    # Initialize an empty iti_array
    ITIArray = []

    # Get total number of trials for session
    num_trials = config_template["metadata"]["totalNumberOfTrials"]

    # Get the base ITI to use for the session and multiply by 1000 to convert
    # to milliseconds.
    iti_duration = config_template["metadata"]["baseITI"]*1000

    # Build ITIArray into a list of values
    ITIArray = [iti_duration] * num_trials

    return ITIArray


# -----------------------------------------------------------------------------
# Tone Array Generation
# -----------------------------------------------------------------------------


def gen_jitter_toneArray(config_template: dict) -> list:
    """
    Generate jittered ITIArray for given experiment from user specified bounds.

    Generates array of ITIs from configuration the user provides.  Uses a
    random uniform distribution bounded by the lower and upper ITIs as defined
    in the configuration file.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        Jittered toneArray.
    """

    # Initialize empty noise array
    tone_array = []

    # Get total number of trials
    num_trials = config_template["metadata"]["totalNumberOfTrials"]

    # Get minimum tone time value from configuration and multiply by 1000 to
    # convert to milliseconds
    tone_lower = config_template["metadata"]["minTone"]*1000

    # Get maximum tone time value from configuration and multiply by 1000 to
    # convert to milliseconds
    tone_upper = config_template["metadata"]["maxTone"]*1000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from uniform distribution
    tone_array = rng.uniform(low=tone_lower, high=tone_upper,
                             size=num_trials)

    # Tone Array generated will have decimals in it and be float type.
    # Use np.round() to round the elements in the array and type them as int.
    # Finally, convert the array into a list for pySerialTransfer.
    toneArray = np.round(tone_array).astype(int).tolist()

    return toneArray


def gen_static_toneArray(config_template: dict) -> list:
    """
    Generate static, or without jitter, toneArray.

    Generates array of tones durations using baseTone from configuration file
    for the number of trials specified by the user.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        Static toneArray
    """

    # Initialize an empty toneArray
    toneArray = []

    # Get total number of trials for session
    num_trials = config_template["metadata"]["totalNumberOfTrials"]

    # Get the tone duration to use for the session and multiply by 1000 so
    # its in millisecond format
    tone_duration = config_template["metadata"]["baseTone"]*1000

    # Build ITIArray into a list of values
    toneArray = [tone_duration] * num_trials

    return toneArray


def gen_ITIArray(config_template: dict) -> list:
    """
    Generate ITIArray for experimental runtime from configuration.

    Generates ITIArray from users configuration file.  Generates either static
    or jittered ITIs depending on user's selection.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        ITIArray
    """

    # Generate ITIArray from configuration values
    # Gather jitter status for ITIArray from configuration
    iti_jitter = config_template["metadata"]["ITIJitter"]

    # If the iti_jitter status is True, create a jittered ITI
    if iti_jitter:
        ITIArray = gen_jitter_ITIArray(config_template)

    # If the iti_jitter status is False, create a static ITI
    else:
        ITIArray = gen_static_ITIArray(config_template)

    return ITIArray


def gen_toneArray(config_template: dict) -> list:
    """
    Generate toneArray for experimental runtime from configuration.

    Generates toneArray from user's configuration file.  Generates either
    static or jittered ITIs depending on user's selection.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        toneArray
    """

    # Gather tone_jitter status from configuraiton
    tone_jitter = config_template["metadata"]["toneJitter"]

    # If the tone_jitter status is true, create a static tone array
    if tone_jitter:
        toneArray = gen_jitter_toneArray(config_template)

    # If the tone_jitter status is False, create a static tone array
    else:
        toneArray = gen_static_toneArray(config_template)

    return toneArray

###############################################################################
# Session Length Calculations
###############################################################################


def calculate_session_length(experiment_arrays: list,
                             config_template: dict) -> int:
    """
    Calculates number of imaging frames to collect for experimental session.

    Iterates through experiment runtime arrays to calculate amount of time and,
    therefore, the total number of frames that the microscope and camera should
    collect for the experiment.

    Args:
        experiment_arrays:
            List of experiment runtime arrays generated from generate_arrays().
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        Session length in seconds.
    """

    # Get vacuum status for the experiment
    vacuum = config_template["metadata"]["vacuum"]

    # Get amount of milliseconds reward is delivered for
    reward_delivery_ms = config_template["metadata"]["USDeliveryTime_Sucrose"]

    # Get amount of milliseconds rewards are present for
    reward_prsnt_ms = config_template["metadata"]["USConsumptionTime_Sucrose"]

    # Get amount of milliseconds punishments are present for
    punish_delivery_ms = config_template["metadata"]["USDeliveryTime_Air"]

    # Make session_length_s variable and add to it as values are calculated
    session_len_s = 0

    # trialArray is always in index 0 in the experimental array_list
    trialArray = experiment_arrays[0]

    # Calculate reward_seconds and add to session length
    reward_seconds = calculate_reward_seconds(reward_delivery_ms,
                                              reward_prsnt_ms, trialArray,
                                              vacuum)
    session_len_s += reward_seconds

    # Calculate punish seconds
    punish_seconds = calculate_punish_seconds(punish_delivery_ms, trialArray)
    session_len_s += punish_seconds

    # Calculate total number of seconds ITI's occur.  The 1st element in the
    # experimental_array_list is always the ITIArray.  Add to session length.
    iti_seconds = sum(experiment_arrays[1])/1000
    session_len_s += iti_seconds

    # Calculate total number of seconds tones are played.  The 2nd element in
    # the experiment_arrays list is always the toneArray.  Add to session
    # length.
    tone_seconds = sum(experiment_arrays[2])/1000
    session_len_s += tone_seconds

    return session_len_s


def calculate_reward_seconds(reward_delivery_ms: int, reward_prsnt_ms: int,
                             trialArray: list, vacuum: bool) -> int:
    """
    Calculates number of seconds rewards are presented and removed.

    Uses configuration values to calculate how many seconds rewards are present
    for a given session as well as how many seconds the vacuum is active if
    used. Returns number of seconds rewards are present.

    Args:
        reward_delivery_ms:
            Amount of time reward is delivered in milliseconds from the config
            file
        reward_prsnt_ms:
            Amount of time reward is presented to mouse in milliseconds from
            the config file
        trialArray:
            Experimental runtime trial order gathered from the
            experimental_array_list at index 0
        vacuum:
            Status of whether or not the vacuum is being used for a project

    Returns:
        reward_seconds
    """

    # Create list of reward trials from the trialArray
    reward_list = [trial for trial in trialArray if trial == 1 or 3]

    # Calculate the total number of seconds reward stimuli contain including
    # consumption time for sucrose
    reward_seconds = (((reward_delivery_ms * len(reward_list))
                      + (reward_prsnt_ms * len(reward_list)))/1000)

    # If the vacuum is being used, calclulate how many seconds the vacuum
    # is being used for the session through multiplying static value to the
    # reward list.
    if vacuum:
        vacuum_seconds = 0.500 * len(reward_list)

    # If the vacuum is not being used, the number of seconds the vacuum on is
    # 0.
    else:
        vacuum_seconds = 0

    # Update the number of seconds rewards will be presented by adding number
    # of vacuum seconds
    reward_seconds = reward_seconds + vacuum_seconds

    return reward_seconds


def calculate_punish_seconds(punish_delivery_ms: int, trialArray: list) -> int:
    """
    Calculates number of seconds punishments are delivered.

    Uses configuration values to calculate how many seconds rewards are present
    for a given session.

    Args:
        punish_delivery_ms:
            Amount of time punishments are delivered in milliseconds from the
            config file.
        trialArray:
            Experimental runtime trial order gathered from the
            experimental_array_list at index 0

    Returns:
        punish_seconds
    """

    punish_list = [trial for trial in trialArray if trial == 0 or 2]

    punish_seconds = (punish_delivery_ms * len(punish_list))/1000

    return punish_seconds
    #     # BUG: Timing for vacuum trials is still incorect despite fix morning
    #     # of 6/3/21. Re-opening Issue 23


###############################################################################
# Generate Arrays function to unite aboves functions
###############################################################################


def generate_arrays(config_template: dict) -> list:
    """
    Generates all necessary arrays for Bruker experimental runtime.

    Creates arrays as specified by user's configuration file.  Builds the
    trialArray, ITIArray, and noiseArray according to user defined rules.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file

    Returns:
        experiment_arrays
            List of experimental arrays to be sent via pySerialTransfer
    """

    # Generate trialArray using template configuration values and convert it to
    # to a list pySerialTransfer.
    trialArray = gen_trialArray(config_template).tolist()

    # Generate ITIArray using template configuration values.  This is already
    # converted to a list during generation if necessary.
    ITIArray = gen_ITIArray(config_template)

    # Generate toneArray using template configuration values.  This is already
    # converted to a list during generation if necessary.
    toneArray = gen_toneArray(config_template)

    # Put arrays together in a list
    experiment_arrays = [trialArray, ITIArray, toneArray]

    # Return list of arrays to be transferred via pySerialTransfer
    return experiment_arrays
