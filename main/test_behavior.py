# Import config_utils functions for manipulating config files
import config_utils

# Import video_utils functions for using Harvesters for camera
import video_utils

# Import serialtransfer_utils for transmitting information to Arduino
import serialtransfer_utils

# Import trial_utils for generating random trials
import trial_utils

# Import prairieview_utils for interacting with Bruker
import prairieview_utils

# Import the Flight Manifest GUI
import flight_manifest

# Import pytest for testing functions and modules
import pytest

# Import sys to safely exit
import sys

def test_reward_check():
    
    trialArray = [1,1,1,0,1,1,1,1,1]

    max_seq_reward = 3

    assert trial_utils.check_session_rewards(trialArray, max_seq_reward) == 1

    trialArray = [1,1,1,0,1,2,3,5,1,1]

    max_seq_reward = 3

    assert trial_utils.check_session_rewards(trialArray, max_seq_reward) == 1

def test_punish_check():

    trialArray = [1,1,1,0,0,1,0,0,0,0]

    max_seq_punish = 3

    assert trial_utils.check_session_punishments(trialArray, max_seq_punish) == 1

    # experiment_arrays = trial_utils.generate_arrays(config_template)

    # # Get metadata that the Arduino requires
    # arduino_metadata = config_utils.get_arduino_metadata(config_template)

    # # Now that the Bruker scope is ready and waiting, send the data to
    # # the Arduino through pySerialTransfer
    # serialtransfer_utils.transfer_data(
    #     arduino_metadata,
    #     experiment_arrays
    #     )
