# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

# Version Number
__version__ = "0.50"

###############################################################################
# Import Packages
###############################################################################

# -----------------------------------------------------------------------------
# Custom Modules: Bruker Control
# -----------------------------------------------------------------------------
# Import config_utils functions for manipulating config files
import config_utils

# Import video_utils functions for using Harvesters for camera
import video_utils

# Import serialtransfer_utils for transmitting information to Arduino
import serialtransfer_utils

# Import trial_utils for generating random trials
import trial_utils

# -----------------------------------------------------------------------------
# Python Libraries
# -----------------------------------------------------------------------------
# File Types
# Import JSON for configuration file
import json

# Import ordered dictionary to ensure order in json file
from collections import OrderedDict

# Import argparse if you want to create a configuration on the fly
import argparse

# Import os to change directories and write files to disk
import os

# Import glob for searching for files and grabbing relevant configs
import glob

# Import sys for exiting program safely
import sys

# NOTE Prairie View Interface
# win32com client installation: Do NOT use pip install, use conda.
# conda install pywin32
import win32com.client
pl = win32com.client.Dispatch("PrairieLink.Application")


###############################################################################
# Prairie View Control
###############################################################################


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------

def prairie_abort():
    print("Connected to Prairie View")
    pl.Connect()
    pl.SendScriptCommands("-Abort")
    pl.Disconnect()
    print("Disconnected from Prairie View")


###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # Create argument parser for metadata configuration
    metadata_parser = argparse.ArgumentParser(description='Set Metadata',
                                              epilog="Good luck on your work!",
                                              prog='Bruker Experiment Control')

    # Add configuration file argument
    metadata_parser.add_argument('-c', '--config_file',
                                 type=str,
                                 action='store',
                                 dest='config',
                                 help='Config Filename (yyyymmdd_animalid)',
                                 default=None,
                                 required=False)

    # Add modify configuration file argument
    metadata_parser.add_argument('-m', '--modify',
                                 action='store_true',
                                 dest='modify',
                                 help='Modify given config file (bool flag)',
                                 required=False)

    # Add template configuration file argument
    metadata_parser.add_argument('-t', '--template',
                                 action='store_true',
                                 dest='template',
                                 help='Use template config file (bool flag)',
                                 required=False)

    # Add project name argument
    metadata_parser.add_argument('-p', '--project',
                                 type=str,
                                 action='store',
                                 dest='project',
                                 help='Project Name (required)',
                                 choices=['specialk', 'food_dep'],
                                 required=True)

    # Add program version argument
    metadata_parser.add_argument('--version',
                                 action='version',
                                 version='%(prog)s v. ' + __version__)

    # Parse the arguments given by the user
    metadata_args = vars(metadata_parser.parse_args())

    # Use config_utils module to parse metadata_config
    config, project_name, config_filename = config_utils.config_parser(metadata_args)

    # TODO: Let user change configurations/create them on the fly with parser

    # Gather total number of trials
    trials = config["metadata"]["totalNumberOfTrials"]["value"]

    # Preview video for headfixed mouse placement
    # video_utils.capture_preview()

    # Generate trial arrays
    array_list = trial_utils.generate_arrays(trials)

    # If only one packet is required, use single packet generation and
    # transfer.  Single packets are all that's needed for sizes less than 45.
    if trials <= 45:

        # Send configuration file
        serialtransfer_utils.transfer_metadata(config)

        # Use single packet serial transfer for arrays
        serialtransfer_utils.onepacket_transfers(array_list)

        # Send update that python is done sending data
        serialtransfer_utils.update_python_status()

        # TODO Gather number of frames expected from microscope for num_frames
        # Now that the packets have been sent, the Arduino will start soon.  We
        # now start the camera for recording the experiment!
        video_utils.capture_recording(60, project_name, config_filename)

        # End Prairie View's imaging session with abort command
        prairie_abort()

        # Now that the microscopy session has ended, let user know the
        # experiment is complete!
        print("Experiment Over!")

        # Exit the program
        print("Exiting...")
        sys.exit()
    #
    # # If there's multiple packets required, use multipacket generation and
    # # transfer.  Multiple packets are required for sizes greater than 45.
    elif trials > 45:

        # Send configuration file
        serialtransfer_utils.transfer_metadata(config)

        # Use multipacket serial transfer for arrays
        serialtransfer_utils.multipacket_transfer(array_list)

        # Send update that python is done sending data
        serialtransfer_utils.update_python_status()

        # Now that the packets have been sent, the Arduino will start soon.  We
        # now start the camera for recording the experiment!
        # video_utils.capture_recording(60, project_name, config_filename)

        # End Prairie View's imaging session with abort command
        # prairie_abort()

        # Now that the microscopy session has ended, let user know the
        # experiment is complete!
        print("Experiment Over!")

        # Exit the program
        print("Exiting...")
        sys.exit()

    # If some other value that doesn't fit in these categories is given, there
    # is something wrong. Let the user know and exit the program.
    else:
        print("Something is wrong with the config file...")
        print("Exiting...")
        sys.exit()
