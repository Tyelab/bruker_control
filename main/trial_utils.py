# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty, Aaron Huffman, Deryn LeDuke May 2021
# Much of the functionality in this module initially existed as part of Arduino
# scripts implemented by Deryn LeDuke and Dr. Kyle Fischer. They were reimplemented
# using Python to generate the arrays so the system would output precise values
# to file both for documentation purposes as well as reproducibility purposes.
# Other labs or users can literally run the same exact experiment using the
# configuration file's contents with the Arduino scripts that are used in
# production without any post-processing of datasets being necessary.

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
# Functions: No stimulation
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray_nostim(config_template: dict) -> np.ndarray:
    """
    Creates pseudorandom trial structure for binary discrimination task without stimulation.

    Generates array of stimuli and catch trials from configuration file the
    user provides.  1 and 0 encode stimuli where 1 is reward and 0 is
    punishment. 2 and 3 encode catch trials where 2 is aversive catch and
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
    fresh_array = np.ones(
        config_template["beh_metadata"]["totalNumberOfTrials"],
        dtype=int
        )

    # Calculate the number of punishment trials to deliver
    num_punish = round(
        config_template["beh_metadata"]["percentPunish"] * len(fresh_array)
        )

    # Get maximum number of punishment trials that can occur in a row
    max_seq_punish = config_template["beh_metadata"]["maxSequentialPunish"]

    # Get maximum number of reward trials that can occur in a row
    max_seq_reward = config_template["beh_metadata"]["maxSequentialReward"]

    # Generate potential flip positions for punish trials by making array of
    # trial indexes starting just after the starting rewards until the end
    # of the experimental session.
    potential_flips = np.arange(
        config_template["beh_metadata"]["startingReward"],
        len(fresh_array)
        )

    # Create punish, reward, and catch trial statuses for checking after
    # flipping trial types in the next step
    punish_check = True
    reward_check = True
    catch_check = True

    # While the punish and catch checks are not BOTH False (or zero)
    while sum([punish_check, catch_check, reward_check]) != 0:

        # Create temporary array that's a fresh copy of starting array
        tmp_array = fresh_array.copy()

        # Perform the flips for punish trials upon the tmp_array using
        # list of potential flips and the number of punish trials specified
        trialArray, punish_check = flip_punishments(
            tmp_array,
            potential_flips,
            num_punish,
            max_seq_punish
            )

        # If the number of punish trials is less than half, getting a valid
        # trial set is unlikely if the number of rewards in a row is
        # restricted.  Therefore, sest the reward_check to False.

        if config_template["beh_metadata"]["percentPunish"] < 0.50:
            reward_check = False

        # Otherwise use check_session_rewards to ensure trial structure is
        # compliant with study's rules.
        else:
            reward_check = check_session_rewards(
                trialArray,
                max_seq_reward
                )

        # Check if the user specified having catch trials for their experiment
        if config_template["beh_metadata"]["catchTrials"]:

            # Use generated trialArray and config_template values to perform
            # catch trial flips only if they want catch trials
            trialArray, catch_check = flip_catch(
                trialArray,
                config_template,
                catch_check
                )

        # If the user doesn't want catch trials, the catch_check passes, setting
        # the value to False, and therefore passes the check.
        else:

            catch_check = False

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
    num_catch_reward = config_template["beh_metadata"]["numCatchReward"]

    # Get number of punishment catch trials
    num_catch_punish = config_template["beh_metadata"]["numCatchPunish"]

    # Get position for where catch trials are to start for session
    catch_offset = config_template["beh_metadata"]["catchOffset"]

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
    for index in punish_catch_list:
        trialArray[index] = 2

    # Get random sample of available catch indexes for reward trials past
    # offset
    reward_catch_list = reward_catch_sample(reward_trials, num_catch_reward)

    # For each index in the chosen punish_catch_list, change the trial's value
    # to 3.
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
    reward_catch_list = rng.choice(
        reward_trials,
        size=num_catch_reward
        ).tolist()

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
    punish_catch_list = rng.choice(
        punish_trials,
        size=num_catch_punish,
        replace=False
        ).tolist()

    return punish_catch_list


def check_session_punishments(trialArray: np.ndarray, max_seq_punish: int) -> bool:
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

    # This list defines all trial types that are not punishment trials
    # across all availble trial types in the system
    non_punishment_trials = [1, 3, 5, 6]

    # Set punish check to False.  If successful, a False status is returned
    # which allows system to move forward.
    punish_check = False

    # Loop over the trialArray
    for trial in trialArray:

        # If the number of punishments in a row reaches max number of allowed
        # punishment trials from configuration, set punish_check as True and
        # break the loop.
        if punishments > max_seq_punish:
            punish_check = True
            break

        # TODO: Is this really the best I can do? There's gotta be a cleaner way...
        # If the trial is anything other than a punish trial, stimulation or not,
        # set number of punishments in a row to zero
        elif trial in non_punishment_trials:
            punishments = 0

        # If the trial is a punish trial and the number of
        # specified punishment trials haven't happened in a row yet,
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

    # This list defines all trial types that are not reward trials
    # across all available trial types in the system.
    non_reward_trials = [0, 2, 4, 6]

    # Set reward_check to False.  If successful, a False status is returned
    # which allows system to move forward.
    reward_check = False

    # Loop over the trialArray
    for trial in trialArray:

        # If the trial is a punishment trial (0), set number of rewards in a
        # row to 0.
        if trial in non_reward_trials:
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
                     num_punish: int, max_seq_punish: int) -> Tuple[np.ndarray, bool]:
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
        tmp_array:
            Modified array containing flipped values, to be saved as trialArray

        punish_check:
            Boolean status of whether the array meets experimenter defined
            criteria. False if successful, True if failed.
    """

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Perform random sample with rng.choice from punish_trials list for the
    # number of punish catch trials specified and finally convert it to a list.
    punish_flips = rng.choice(potential_flips, size=num_punish, replace=False)

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
    num_trials = config_template["beh_metadata"]["totalNumberOfTrials"]

    # Get minimum ITI value from configuration and multiply by 1000 to convert
    # to milliseconds
    iti_lower = config_template["beh_metadata"]["minITI"]*1000

    # Get maximum ITI value from configuation and mulitply by 1000 to convert
    # to milliseconds.
    iti_upper = config_template["beh_metadata"]["maxITI"]*1000

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
    num_trials = config_template["beh_metadata"]["totalNumberOfTrials"]

    # Get the base ITI to use for the session and multiply by 1000 to convert
    # to milliseconds.
    iti_duration = config_template["beh_metadata"]["baseITI"]*1000

    # Build ITIArray into a list of values
    ITIArray = [iti_duration] * num_trials

    return ITIArray


# -----------------------------------------------------------------------------
# Tone Array Generation
# -----------------------------------------------------------------------------


def gen_jitter_toneArray(config_template: dict) -> list:
    """
    Generate jittered toneArray for given experiment from user specified bounds.

    Generates array of tones from configuration the user provides.  Uses a
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
    num_trials = config_template["beh_metadata"]["totalNumberOfTrials"]

    # Get minimum tone time value from configuration and multiply by 1000 to
    # convert to milliseconds
    tone_lower = config_template["beh_metadata"]["minTone"]*1000

    # Get maximum tone time value from configuration and multiply by 1000 to
    # convert to milliseconds
    tone_upper = config_template["beh_metadata"]["maxTone"]*1000

    # Initialize random number generator with default_rng
    rng = default_rng()

    # Generate array by sampling from uniform distribution
    tone_array = rng.uniform(low=tone_lower, high=tone_upper, size=num_trials)

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
    num_trials = config_template["beh_metadata"]["totalNumberOfTrials"]

    # Get the tone duration to use for the session and multiply by 1000 so
    # its in millisecond format
    tone_duration = config_template["beh_metadata"]["baseTone"]*1000

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
    iti_jitter = config_template["beh_metadata"]["ITIJitter"]

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
    static or jittered tones depending on user's selection.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        toneArray
    """

    # Gather tone_jitter status from configuraiton
    tone_jitter = config_template["beh_metadata"]["toneJitter"]

    # If the tone_jitter status is true, create a jittered tone array
    if tone_jitter:
        toneArray = gen_jitter_toneArray(config_template)

    # If the tone_jitter status is False, create a static tone array
    else:
        toneArray = gen_static_toneArray(config_template)

    return toneArray

###############################################################################
# Session Length Calculations
###############################################################################


def calculate_session_length(experiment_arrays: list) -> int:
    """
    Calculates number of imaging frames to collect for experimental session.

    Iterates through experiment runtime arrays to calculate amount of time and,
    therefore, the total number of frames that the microscope and camera should
    collect for the experiment.

    Args:
        experiment_arrays:
            List of experiment runtime arrays generated from generate_arrays().

    Returns:
        Session length in seconds.
    """

    # Make session_length_s variable and add to it as values are calculated
    session_len_s = 0

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


###############################################################################
# Generate Arrays function to unite aboves functions
###############################################################################


def generate_arrays(config_template: dict) -> list:
    """
    Generates all necessary arrays for Bruker experimental runtime.

    Creates arrays as specified by user's configuration file.  Builds the
    trialArray, ITIArray, toneArray, and LEDArray according to user defined rules.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file

    Returns:
        experiment_arrays
            List of experimental arrays to be sent via pySerialTransfer
    """

    # Generate trialArray using template configuration values and convert it to
    # to a list pySerialTransfer. If the experiment requires stimulation, use
    # gen_trialArray_stim. Otherwise, use gen_trialArray_nostim.
    if config_template["beh_metadata"]["stim"]:
        trialArray = gen_trialArray_stim(config_template).tolist()
    else:
        trialArray = gen_trialArray_nostim(config_template).tolist()

    # Generate ITIArray using template configuration values.  This is already
    # converted to a list during generation.
    ITIArray = gen_ITIArray(config_template)

    # Generate toneArray using template configuration values.  This is already
    # converted to a list during generation.
    toneArray = gen_toneArray(config_template)

    # Generate LEDArray using template configuration values, trialArray, and
    # ITI array.
    LEDArray = gen_LEDArray(config_template, trialArray, ITIArray)

    # Put arrays together in a list
    experiment_arrays = [trialArray, ITIArray, toneArray, LEDArray]

    # Return list of arrays to be transferred via pySerialTransfer
    return experiment_arrays


###############################################################################
# Functions: Stimulation
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------

def gen_trialArray_stim(config_template: dict) -> np.ndarray:
    """
    Creates pseudorandom trial structure for binary discrimination task with LED stimulation.

    Generates array of stimuli and catch trials from configuration file the
    user provides.  1 and 0 encode stimuli where 1 is reward and 0 is
    punishment. 2 and 3 encode catch trials where 2 is aversive catch and
    3 is reward catch. 4, 5, and 6 encode LED stimulation where 4 is aversive
    stim, 5 is reward stim, and 6 is stim alone.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        trialArray
            Trial array with user specified trial structure using LED stimulation.
    """

    # Create trial array that's all reward trials, to be flipped randomly
    fresh_array = np.ones(
        config_template["beh_metadata"]["totalNumberOfTrials"],
        dtype=int
    )

    # TODO: Again, all of this should just be part of a stimulation class
    # or something, but I haven't done that refactor yet...
    # Get maximum number of punishment trials that can occur in a row
    max_seq_punish = config_template["beh_metadata"]["maxSequentialPunish"]

    # Get maximum number of reward trials that can occur in a row
    max_seq_reward = config_template["beh_metadata"]["maxSequentialReward"]

    # Get number of positive stimulation trials
    num_stim_reward = config_template["beh_metadata"]["numStimReward"]

    # Get number of aversive stimulation trials
    num_stim_punish = config_template["beh_metadata"]["numStimPunish"]

    # Get number of stimulation alone trials
    num_stim_alone = config_template["beh_metadata"]["numStimAlone"]

    # Get position where stimulation trials will start
    stim_start_position = config_template["beh_metadata"]["stimStartPosition"]

    # Calculate total number of stimulation trials
    total_stim_trials = sum([num_stim_reward, num_stim_punish, num_stim_alone])

    # Build the array containing stimulation trials
    stimulated_array = flip_stim_trials(
        fresh_array,
        total_stim_trials,
        num_stim_punish,
        num_stim_alone,
        stim_start_position,
        max_seq_punish
    )

    # Calculate the number of punishment trials to deliver outside stimulation epochs
    # which is the total number of punish trials minus the ones already allocated
    num_punish_nostim = round(
        (config_template["beh_metadata"]["percentPunish"] * len(fresh_array)) -
        num_stim_punish
        )

    # Define which trials can be flipped before the stimulation epoch
    potential_pre_stim_flips = np.arange(
        config_template["beh_metadata"]["startingReward"],
        stim_start_position
    )

    # Define which trials can be flipped after the stimulation epoch
    potential_post_stim_flips = np.arange(
        stim_start_position + total_stim_trials,
        len(stimulated_array)
    )

    # Combine pre/post stimulation positions into one array
    potential_nostim_flips = np.concatenate(
        (potential_pre_stim_flips, potential_post_stim_flips),
        axis=None
    )

    # Create punish, reward, and catch trial statuses for checking after
    # flipping trial types in the next step
    punish_check = True
    reward_check = True
    catch_check = True

    # At some point, this should be made into a function of it's own probably
    # While the punish, catch, and reward cheks are not all false (or zero)
    while sum([punish_check, catch_check, reward_check]) != 0:

        # Create temporary array that's a copy of stimulated array
        tmp_array = stimulated_array.copy()

        # Perform the flips for punish trials upon the tmp_array using
        # list of potential nos stimulation flips and the number of punish
        # trials remaining

        trialArray, punish_check = flip_punishments(
            tmp_array,
            potential_nostim_flips,
            num_punish_nostim,
            max_seq_punish
            )

        # If the number of punish trials is less than half, getting a valid
        # trial set is unlikely if the number of rewards in a row is
        # restricted.  Therefore, sest the reward_check to False.
        if config_template["beh_metadata"]["percentPunish"] < 0.50:
            reward_check = False

        # Otherwise use check_session_rewards to ensure trial structure is
        # compliant with study's rules.
        else:
            reward_check = check_session_rewards(
                trialArray,
                max_seq_reward
                )

        # Use generated trialArray and config_template values to perform
        # catch trial flips
        trialArray, catch_check = flip_catch(
            trialArray,
            config_template,
            catch_check
            )

    return trialArray


def flip_stim_trials(fresh_array: np.ndarray, total_stim_trials: int, num_stim_punish: int,
                     num_stim_alone: int, stim_start_position: int, max_seq_punish: int) -> np.ndarray:
    """
    Flips fresh array of all reward trials into stimulation trials for both reward and punish trials.

    Stimulation trials are defined by the user as part of the configuration template file.
    The fresh array containing all reward trials has a subset of trials flipped to stimulation
    trial types (4, 5, or 6) that starts at the specified position in the trial structure.
    It first flips the subset of trials to reward, punish, and stimulation alone trials and then
    performs multiple shuffles of the subset. A check for sequential punish trials is conducted
    next and, if it fails, it will reshuffle until it succeeds. Returns a trialArray that has
    stimulation trials.

    Args:
        fresh_array:
            Array composed entirely of reward trials to be flipped pseudo-randomly
        total_stim_trials:
            Total number of photo-stimulation trials (reward, punish, and stim only)
        num_stim_punish:
            User specified number of photo-stimulation trials with airpuff
        num_stim_alone:
            User specified number of trials with only photo-stimulation
        stim_start_position:
            User specified position for where photo-stimulation block starts
        max_seq_punish:
            Maximum number of punishment trials permitted in a row

    Returns:
        stimulated_array:
            Intermediate Trial Array that contains stimulation trials per user's rules

    """

    # Specify the stimulation indexes that will be used that may be flipped
    # to punish trials
    potential_stim_flips = np.arange(
        stim_start_position,
        stim_start_position + total_stim_trials
    )

    # Create a punishment check flag to ensure no more than the specified
    # maximum number of sequential punish trials will occur.
    punish_check = True

    while punish_check:

        stimulated_array, punish_check = flip_punishments(
            fresh_array,
            potential_stim_flips,
            num_stim_punish,
            max_seq_punish
        )

    # TODO: This block of getting dict keys will one day be solved
    # through the use of classes and, at some point, a function that
    # generally performs this list(itemgetter()) procedure to output
    # necessary values. Today, 10/22/21, is not that day.
    # A remaining set of potential flips must be determined for the
    # stimulation only trials. First evaluate which indexes were
    # flipped by flip_punishments
    punish_stims = [index for index in stimulated_array if index == 0]

    # Convert potential_stim_flips to list for use with set function
    stim_idxs = potential_stim_flips.tolist()

    # Use itemgetter to gather the union between stim_idxs and stimulated_array
    punish_stim_values = list(itemgetter(*stim_idxs)(stimulated_array))

    # Create a dictionary of stim indexes and values to iterate over
    punish_stim_dict = {stim_idxs[i]: punish_stim_values[i] for i in range(len(stim_idxs))}

    # Get punish stimluation indexes, or where the value is 0
    punish_stims = [key for key in punish_stim_dict if punish_stim_dict[key] == 0]

    # Use the set function to get only unique indexes that are remaining
    # from the potential_flips
    remaining_stim_flips = list(set(stim_idxs) - set(punish_stims))

    # flip_punishments flips trials to 0, or punishment trials. LED Stimulation
    # trials for punishments are encoded by 4. Therefore, change the
    # punish trials in the stimulation block to 4. At this point in the
    # generation of stimuli, the only punishments in the trial set are
    # in the stimulation indexes.
    for trial_type in range(len(stimulated_array)):
        if stimulated_array[trial_type] == 0:
            stimulated_array[trial_type] = 4

    # Create stimulation only check flag to ensure that no more than
    # 2 stim trials occur in a row. For now, this is a hardcoded value.
    # TODO: Expand configuration to include this value
    stim_only_check = True

    while stim_only_check:

        tmp_array = stimulated_array.copy()

        stimulated_array, stim_only_check = flip_stim_only(
            tmp_array,
            remaining_stim_flips,
            num_stim_alone
        )

    # Lastly, turn the appropriate remaining reward trials into
    # LED Stimulation reward trials
    for trial_type in range(stim_start_position, stim_start_position + total_stim_trials):
        if stimulated_array[trial_type] == 1:
            stimulated_array[trial_type] = 5

    return stimulated_array


def flip_stim_only(tmp_array: np.ndarray, remaining_flips: np.ndarray, num_stim_alone: int) -> Tuple[np.ndarray, bool]:
    """
    Flips user specified number of trials to stimulation only trials.

    Args:
        tmp_array:
            trialArray consisting of trials that have had flips performed for punishment stimulation.
        remaining_flips:
            Array of indexes that can be switched to stimulation only trials
        num_stim_alone:
            Number of trials where only LED stimulation occurs

    Returns:
        trialArray

        stim_only_check

    """

    # Initialize new random number generator with default_rng()
    rng = default_rng()

    # Perform random sample with rng.choice from punish_trials list for the
    # number of punish catch trials specified and finally convert it to a list.
    stim_only_flips = rng.choice(remaining_flips, size=num_stim_alone, replace=False)

    # For each index in the chosen stim_only_flips, change the trial's value
    # to 6.
    for index in stim_only_flips:
        tmp_array[index] = 6

    # Check flip positions for stim_only trials to make sure no more than 2
    # occur in a row.
    stim_only_status = check_session_stim_only(tmp_array, 2)

    # Return the tmp_array to be saved as trialArray and the punish_status
    return tmp_array, stim_only_status


def check_session_stim_only(tmp_array: np.ndarray, max_seq_stim_only=2) -> bool:
    """
    Checks if there are more than 2 stimulation only trials that occur in a row.

    Args:
        tmp_array:
            Trial array containing newly flipped stimulation only trials.
        max_seq_stim_only:
            Maximim number of stimulation only trials allowed to occur in order.

    Returns:
        stim_only_status:
            Boolean value encoding if the check passed or failed.
    """

     # Start stim_only count at zero
    stim_only = 0

    # Set stim_only_check check to False.  If successful, a False status is returned
    # which allows system to move forward.
    stim_only_check = False

    # Loop over the trialArray
    for trial in tmp_array:

        # If the trial is a reward trial or a stimulation punishment trial, set number of
        # stim_only in a row to zero
        if trial == 1 or 4:
            stim_only = 0

        # If the number of stim_only in a row reaches max number of allowed, set stim_only_check
        # as True and break the loop.
        elif stim_only == max_seq_stim_only:
            stim_only_check = True
            break

        # If the trial is a stim_only trial and the max number of sequential stim_only trials
        # hasn't occured yet, increment stim_only by 1
        else:
            stim_only += 1

    return stim_only_check


def gen_LEDArray(config_template: dict, trialArray: np.ndarray, ITIArray: np.ndarray) -> list:
    """
    Generates LED stimulation timepoints if necessary.

    Stimulation arrays have been incorporated into the Arduino scripts by default to avoid
    having several scripts per team to maintain. Therefore, for now at least, LEDArray is
    is a required part of array generation. This may change in the future where stimulation and
    no-stimulation experiments have their own Arduino scripts that are used.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file
        trialArray:
            Completed trial array containing trial types
        ITIArray:
            Array of ITIs for the experiment

    Returns:
        LEDArray
    """

    # If the experiment isn't using stimulation, then all the values for the LEDArray will be
    # zeroes.
    if not config_template["beh_metadata"]["stim"]:
        LEDArray = [0]

    # If the experiment is using stimulation, then calculate the times to send stimulation TTL
    # triggers to Prairie View
    else:

        # Gather when the stimulation should start pre-CS
        precs_delay = config_template["beh_metadata"]["stimDeliveryTime_PreCS"]

        # Get number of positive stimulation trials
        num_stim_reward = config_template["beh_metadata"]["numStimReward"]

        # Get number of aversive stimulation trials
        num_stim_punish = config_template["beh_metadata"]["numStimPunish"]

        # Get number of stimulation alone trials
        num_stim_alone = config_template["beh_metadata"]["numStimAlone"]

        # Calculate total number of stimulation trials
        total_stim_trials = sum([num_stim_reward, num_stim_punish, num_stim_alone])

        # Get position where stimulation trials will start
        stim_start_position = config_template["beh_metadata"]["stimStartPosition"]

        # TODO: Stim start and stim end position will be member of StimMetadata class
        # Create array of stimulation indexes for timing calculation as a list
        stim_positions = np.arange(
            stim_start_position,
            stim_start_position + total_stim_trials
        )

        # Convert stim_positions np.ndarray to list
        stim_idxs = stim_positions.tolist()

        # Use itemgetter to gather the union between stim_idxs and stimulated_array
        iti_stim_values = list(itemgetter(*stim_idxs)(ITIArray))

        # Create a dictionary of stim indexes and values to iterate over
        iti_stim_dict = {stim_idxs[i]: iti_stim_values[i] for i in range(len(stim_idxs))}

        # Create stimulation array of only relevant stimulation positions
        LEDArray = [iti_stim_dict[value] for value in iti_stim_dict]

        # Calculate when to send the LED stimulation trigger to Prairie View.
        # Above we simply copied the ITI values into LEDArray, now we subtract
        # by when we need to provide the LED stimulus before hand.
        LEDArray = np.subtract(LEDArray, precs_delay).astype(int).tolist()

    return LEDArray
