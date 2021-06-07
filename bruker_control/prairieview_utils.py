# Bruker 2-Photon Prairie View Utils
# Jeremy Delahanty, Dexter Tsin May 2021
# Written with assistance from Michael Fox, Sr Software Engineer Bruker

###############################################################################
# Import Packages
###############################################################################

# Import Prairie View Application
# NOTE Prairie View Interface Installation:  Do NOT use pip install, use conda.
# conda install pywin32
import win32com.client

# Import pathlib for file manipulation and directory creation
from pathlib import Path

# Import datetime for folder naming
from datetime import datetime

# Save the Praire View application as pl
pl = win32com.client.Dispatch("PrairieLink.Application")

# Get current working directory for above paths to work
current_dir = Path.cwd()

###############################################################################
# Functions
###############################################################################

# -----------------------------------------------------------------------------
# PrairieLink Connect Function
# -----------------------------------------------------------------------------


def prairie_connect():

    # Tell user program is connecting to Prairie View, connect, and finally
    # tell user that the program is connected.
    print("Connecting to Prairie View")
    pl.Connect()
    print("Connected to Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Disconnect Function
# -----------------------------------------------------------------------------


def prairie_disconnect():

    # Tell user program is disconnecting from Prairie View, disconnect, and
    # finally tell user that the program has disconnected.
    print("Disconnecting from Prairie View")
    pl.Disconnect()
    print("Disconnected from Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------


def prairie_abort():

    # Tell user recording is being stopped using abort command
    print("Aborting Recording...")

    # Connect to Prairie View
    prairie_connect()

    # Tell user abort command is being sent, send the command, and finally
    # tell user that the command has been executed.
    print("Sending Abort Command")
    pl.SendScriptCommands("-Abort")
    print("Abort Command Sent")

    # Disconnect from Prairie View
    prairie_disconnect()


# -----------------------------------------------------------------------------
# PrairieLink Set Directory and Filename Function
# -----------------------------------------------------------------------------


def prairie_dir_and_filename(project_name, config_filename, behavior_flag):

    # Tell user that the program is setting up a directory for session
    print("Setting Directory")

    # TODO: All the path names/folder creation should happen outside the fx
    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session basepath
    microscopy_basepath = "E:/studies/" + project_name + "/microscopy/" + session_date + "/"

    # Set microscopy filename
    microscopy_filename = config_filename

    # Set microscopy full path for telling user where session is saved
    microscopy_fullpath = microscopy_basepath + microscopy_filename

    # Not usable until PV 5.6 release
    # Set behavior session basepath
    # behavior_basepath = "E:/studies/" + project_name + "/behavior/" + session_date + "/"

    # Set behavior filename
    behavior_filename = config_filename

    # Not usable until PV 5.6 release
    # Set behavior full path for telling user where session is saved
    # behavior_fullpath = behavior_basepath + behavior_filename

    if behavior_flag is True:

        # Connect to Prairie View
        prairie_connect()

        # Set Voltage Recording (Behavior) Name
        pl.SendScriptCommands("-SetState directory {} VoltageRecording".format(behavior_filename))
        print("Set Prairie View Voltage Recording Filename: ", behavior_filename)

        # Disconnect from Prairie View
        prairie_disconnect()

    else:

        # Connect to Praire View
        prairie_connect()

        # Set Prairie View path for saving files
        pl.SendScriptCommands("-SetSavePath {}".format(microscopy_basepath))
        print("Set 2P Image Path: " + microscopy_fullpath)

        # Set Prairie View filename
        pl.SendScriptCommands("-SetFileName Tseries {}".format(microscopy_filename))

        # BUG: While I can name the voltage recording something new, I can't
        # assign where it goes. This is likely something that will require us
        # waiting for Prairie View 5.6 release in about 1 month (Early July)
        # Set Voltage Recording (Behavior) Name
        # pl.SendScriptCommands("-SetState directory {} VoltageRecording".format(behavior_filename))
        # print("Set VoltageRecording Path: " + behavior_fullpath)

        # pl.SendScriptCommands("-SetFileName VoltageRecording {}".format(behavior_filename))

        # Disconnect from Prairie View
        prairie_disconnect()


# -----------------------------------------------------------------------------
# PrairieLink Start T-Series Function
# -----------------------------------------------------------------------------


def prairie_start_tseries():

    # Connect to Prairie View
    prairie_connect()

    # Tell user that the T-Series is starting and waiting for trigger
    print("Starting T-Series: Waiting for Input Trigger")

    # Send T-Series command
    pl.SendScriptCommands("-TSeries")

    # Disconnect from Prairie View
    prairie_disconnect()
