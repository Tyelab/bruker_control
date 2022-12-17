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

# Import sys to safely exit
import sys

def testing():
    
    config_template = config_utils.get_template("test")

    experiment_arrays = trial_utils.generate_arrays(config_template)

    # Get metadata that the Arduino requires
    arduino_metadata = config_utils.get_arduino_metadata(config_template)

    # Now that the Bruker scope is ready and waiting, send the data to
    # the Arduino through pySerialTransfer
    serialtransfer_utils.transfer_data(
        arduino_metadata,
        experiment_arrays
        )
    
    sys.exit()
