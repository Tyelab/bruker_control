from __future__ import annotations
import json
from pathlib import Path
from collections import OrderedDict
from typing import Any, Dict, Optional, List
from operator import itemgetter

import numpy as np
from numpy.random import default_rng

from pydantic import BaseModel, Field
###############################################################
# Basic class inheritance testing; this works as an example...
# class Base(BaseModel):
#     total_number_of_trials: int

# class TrialArray(Base):
#     percent_punish: int
#     max_seq_punish: int
#     max_seq_reward: int
#     starting_reward: int
#     catch_trials: bool

# class Stim(TrialArray):
#     stim_reward: int
#     stim_punish: int
#     stim_alone: int
#     stim_start_pos: int

# class LED(Stim):
#     stim_delivery_time_precs: int

# class Tone(Base):
#     min_tone: int
#     max_tone: int
#     base_tone: None

# class ITIs(Base):
#     min_iti: int
#     max_iti: int
#     base_tone: None

###########################################################
# Pydantic example


class Led(BaseModel):
    """
    Class describing information related to whole-field LED stimulation.
    """
    stim_delivery_time_precs: int = Field(..., alias='stimDeliveryTimePrecs')
    stim_delivery_time_total: int = Field(..., alias='stimDeliveryTimeTotal')
    stim_frequency: int = Field(..., alias='stimFrequency')
    stim_pulse_time: int = Field(..., alias='stimPulseTime')
    stim_lambda: int = Field(..., alias='stimLambda')


class StimSettings(BaseModel):
    """
    Class describing information related to LED stimulation parameters.
    """
    stim: bool
    shutter_only: bool = Field(..., alias='shutterOnly')
    stim_reward: int = Field(..., alias='stimReward')
    stim_punish: int = Field(..., alias='stimPunish')
    stim_alone: int = Field(..., alias='stimAlone')
    stim_start_position: int = Field(..., alias='stimStartPosition')
    led: Led = Field(..., alias='LED')

class TrialSettings(BaseModel):
    """
    Class describing information related to behavior trial settings.
    """
    percent_punish: float = Field(..., alias='percentPunish')
    max_sequential_reward: Any = Field(..., alias='maxSequentialReward')
    max_sequential_punish: int = Field(..., alias='maxSequentialPunish')
    starting_reward: int = Field(..., alias='startingReward')
    catch_trials: bool = Field(..., alias='catchTrials')
    num_catch_reward: int = Field(..., alias='numCatchReward')
    num_catch_punish: int = Field(..., alias='numCatchPunish')
    catch_offset: float = Field(..., alias='catchOffset')
    stim_settings: StimSettings = Field(..., alias='stimSettings')


class ItiSettings(BaseModel):
    """
    Class describing information related to ITI settings.
    """
    iti_jitter: bool = Field(..., alias='itiJitter')
    base_iti: Any = Field(..., alias='baseITI')
    min_iti: int = Field(..., alias='minITI')
    max_iti: int = Field(..., alias='maxITI')



class ToneSettings(BaseModel):
    """
    Class describing information related to speaker settings.
    """
    tone_jitter: bool = Field(..., alias='toneJitter')
    base_tone: Any = Field(..., alias='baseTone')
    min_tone: int = Field(..., alias='minTone')
    max_tone: int = Field(..., alias='maxTone')


class ArduinoMetadata(BaseModel):
    """
    Class describing metadata used for the Arduino's configuration.
    """
    punish_tone: int = Field(..., alias='punishTone')
    reward_tone: int = Field(..., alias='rewardTone')
    us_delivery_time_sucrose: int = Field(..., alias='USDeliveryTimeSucrose')
    us_delivery_time_air: int = Field(..., alias='USDeliveryTimeAir')
    us_consumption_time_sucrose: int = Field(..., alias='USConsumptionTimeSucrose')


class ZstackMetadata(BaseModel):
    """
    Class containing metadata for running z-stack recordings.
    """
    zstack: bool
    stack_number: int = Field(..., alias='stackNumber')
    z_delta: float = Field(..., alias='zDelta')
    z_step: float = Field(..., alias='zStep')


class Params(BaseModel):
    """
    Metaclass containing all necessary subclasses.
    """
    total_number_of_trials: int = Field(..., alias='totalNumberOfTrials')
    trial_settings: TrialSettings = Field(..., alias='trialSettings')
    iti_settings: ItiSettings = Field(..., alias='itiSettings')
    tone_settings: ToneSettings = Field(..., alias='toneSettings')
    arduino_metadata: ArduinoMetadata = Field(..., alias='arduinoMetadata')
    zstack_metadata: ZstackMetadata = Field(..., alias='zstackMetadata')

class Model(BaseModel):
    """
    Base pydantic model class.
    """
    params: Optional[Params] = Field(None, alias='PARAMS')

    def ITIArray(self.params.iti_settings) -> List[int]:
        
        if self.params.iti_settings.iti_jitter:

            rng = default_rng()

            iti_array = rng.uniform(
                low=self.params.iti_settings.min_iti,
                high=self.params.iti_settings.max_iti,
                size=self.params.total_number_of_trials
            )
            
        else:
            iti_array = [self.params.iti_settings.base_iti] * self.params.total_number_of_trials
        
        iti_array = np.round(iti_array).astype(int).tolist()
        
        return iti_array
    
    def toneArray(self) -> List[int]:
        
        if self.params.tone_settings.tone_jitter:
            
            rng = default_rng()
            
            tone_array = rng.uniform(
                low=self.params.tone_settings.min_tone,
                high=self.params.tone_settings.max_tone,
                size=self.params.total_number_of_trials
            )
        
        else:
            tone_array = [self.params.tone_settings.base_tone] * self.params.total_number_of_trials
        
        tone_array = np.round(tone_array).astype(int).tolist()
        
        return tone_array
    
    def trialArray(self) -> List[int]:
        
        if self.params.trial_settings.stim_settings.stim:
            trial_array = gen_trialArray_stim(self)
        
        else:
            trial_array = gen_trialArray_nostim(self)
        
        return trial_array
    
    
            
    
def gen_trialArray_nostim(config: Params) -> np.ndarray:
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
        config.params.total_number_of_trials,
        dtype=int
        )

    # Calculate the number of punishment trials to deliver
    num_punish = round(
        config.params.trial_settings.percent_punish * len(fresh_array)
        )

    # Get maximum number of reward trials that can occur in a row
    max_seq_reward = config.params.trial_settings.max_sequential_reward

    # Generate potential flip positions for punish trials by making array of
    # trial indexes starting just after the starting rewards until the end
    # of the experimental session.
    potential_flips = np.arange(
        config.params.trial_settings.starting_reward,
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
            config.params.trial_settings.max_sequential_punish
            )

        # If the number of punish trials is less than half, getting a valid
        # trial set is unlikely if the number of rewards in a row is
        # restricted.  Therefore, sest the reward_check to False.

        if config.params.trial_settings.percent_punish < 0.50:
            reward_check = False

        # Otherwise use check_session_rewards to ensure trial structure is
        # compliant with study's rules.
        else:
            reward_check = check_session_rewards(
                trialArray,
                max_seq_reward
                )

        # Check if the user specified having catch trials for their experiment
        if config.params.trial_settings.catch_trials:

            # Use generated trialArray and config_template values to perform
            # catch trial flips only if they want catch trials
            trialArray, catch_check = flip_catch(
                trialArray,
                config.params.trial_settings,
                catch_check
                )
        
        # If the user doesn't want catch trials, the catch_check passes, setting
        # the value to False, and therefore passes the check.
        else:

            catch_check = False

    return trialArray


def flip_catch(trialArray: np.ndarray, config: Params,
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

    # Get length of trialArray
    trialArray_len = len(trialArray)

    # Get position to start flipping catch trials using offset
    catch_index_start = round(trialArray_len - (trialArray_len * config.params.trial_settings.catch_offset))

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

    # If the length of punish trials in subset obtained by offset is less than
    # specified number of punishment trials, there's not enough punish trials
    # available!  Returns the trialArray and a True catch check.  If that's
    # not the case, then we can move forward.
    if len(punish_trials) < config.params.trial_settings.num_catch_punish:
        print("Not enough punish trials to flip into catches! Reshuffling...")
        return trialArray, catch_check

    # If the length of reward trials in subset obtained by offset, there's not
    # enough reward trials available!  Returns the trialArray and a True catch
    # check.  If that's not the case, then we can move forward.
    elif len(reward_trials) < config.params.trial_settings.num_catch_reward:
        print("Not enough reward trials to flip into catches! Reshuffling...")
        return trialArray, catch_check

    # Else, the catch check has passed and its status can be set to False.
    else:
        catch_check = False

    # Get random sample of available catch indexes for punish trials past
    # offset
    punish_catch_list = punish_catch_sample(
        punish_trials,
        config.params.trial_settings.num_catch_punish
        )

    # For each index in the chosen punish_catch_list, change the trial's value
    # to 2.
    for index in punish_catch_list:
        trialArray[index] = 2

    # Get random sample of available catch indexes for reward trials past
    # offset
    reward_catch_list = reward_catch_sample(
        reward_trials,
        config.params.trial_settings.num_catch_reward
        )

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


def read_config(config_path: Path) -> dict:
    """
    Utility function for reading config files

    General purpose function for reading .json files containing configuration
    values for an experiment.

    Args:
        config_path:
            Pathlib path to the template configuration file.

    Returns:
        Dictionary of contents inside the configuration .json file
    """

    with open(config_path, 'r') as inFile:

        contents = inFile.read()

        # Use json.loads to gather metadata and save them in an
        # ordered dictionary
        config_values = json.loads(
            contents,
            object_pairs_hook=OrderedDict
        )

    return config_values

def gen_trialArray_stim(config: Params) -> np.ndarray:
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
        config.params.total_number_of_trials,
        dtype=int
    )


    # Build the array containing stimulation trials
    stimulated_array = flip_stim_trials(
        fresh_array,
        config.params.trial_settings.stim_settings.stim_reward,
        config.params.trial_settings.stim_settings.stim_punish,
        config.params.trial_settings.stim_settings.stim_alone,
        config.params.trial_settings.stim_settings.stim_start_position,
        config.params.trial_settings.max_sequential_punish
    )

    # Calculate the number of punishment trials to deliver outside stimulation epochs
    # which is the total number of punish trials minus the ones already allocated
    num_punish_nostim = round(
        (config.params.trial_settings.percent_punish * len(fresh_array)) -
        config.params.trial_settings.stim_settings.stim_punish
        )

    # Define which trials can be flipped before the stimulation epoch
    potential_pre_stim_flips = np.arange(
        config.params.trial_settings.starting_reward,
        config.params.trial_settings.stim_settings.stim_start_position
    )
    
    # TODO: This is redundant as it's calculated earlier in flip_stim_trials, need to find a way
    # to invoke a different property here maybe of my class?
    total_stim_trials = sum([
        config.params.trial_settings.stim_settings.stim_reward,
        config.params.trial_settings.stim_settings.stim_punish,
        config.params.trial_settings.stim_settings.stim_alone,
    ])

    # Define which trials can be flipped after the stimulation epoch
    potential_post_stim_flips = np.arange(
        config.params.trial_settings.stim_settings.stim_start_position + total_stim_trials,
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
            config.params.trial_settings.max_sequential_punish
            )

        # If the number of punish trials is less than half, getting a valid
        # trial set is unlikely if the number of rewards in a row is
        # restricted.  Therefore, sest the reward_check to False.
        if config.params.trial_settings.percent_punish < 0.50:
            reward_check = False

        # Otherwise use check_session_rewards to ensure trial structure is
        # compliant with study's rules.
        else:
            reward_check = check_session_rewards(
                trialArray,
                config.params.trial_settings.max_sequential_reward
                )

        # Use generated trialArray and config_template values to perform
        # catch trial flips
        trialArray, catch_check = flip_catch(
            trialArray,
            config,
            catch_check
            )

    return trialArray


def flip_stim_trials(fresh_array: np.ndarray, num_stim_reward: int, num_stim_punish: int,
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
    
    total_stim_trials = sum([
        num_stim_reward,
        num_stim_punish,
        num_stim_alone
    ])

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
        LEDArray = np.subtract(LEDArray, precs_delay).tolist()

    return LEDArray

# # config = read_config(Path("C:/Users/jdelahanty.SNL/Desktop/20211126_CSE012_plane1_-304.7_config.json"))

config = Path("C:/Users/jdelahanty.SNL/Desktop/new_config3.json")

y = read_config(config)

x = Model.parse_obj(y)

print(x.trialArray)
