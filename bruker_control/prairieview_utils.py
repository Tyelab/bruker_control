# Bruker 2-Photon Prairie View Utils
# Jeremy Delahanty, Dexter Tsin May 2021
# Written with assistance from Michael Fox, Sr Software Engineer Bruker

###############################################################################
# Import Packages
###############################################################################

# Import Prairie View Application
# NOTE Prairie View Interface Installation:  Do NOT use pip install, use conda.
# conda install pywin32
# import win32com.client

# Import datetime for folder naming
from datetime import datetime

# Save the Praire View application as pl
# pl = win32com.client.Dispatch("PrairieLink.Application")

# Get current working directory for above paths to work
# current_dir = Path.cwd()

# Define microscopy basebath for where raw files are written to.  This is onto
# the E: drive on machine BRUKER.  Set it as a string to be joined later.
basepath = "E:/"

###############################################################################
# Functions
###############################################################################

# -----------------------------------------------------------------------------
# PrairieLink Connect Function
# -----------------------------------------------------------------------------


def pv_connect():

    pl.Connect()
    print("Connected to Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Disconnect Function
# -----------------------------------------------------------------------------


def pv_disconnect():

    pl.Disconnect()
    print("Disconnected from Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------


def abort_recording():

    # Tell user recording is being stopped using abort command
    print("Aborting Recording...")

    # Connect to Prairie View
    pv_connect()

    # Tell user abort command is being sent, send the command, and finally
    # tell user that the command has been executed.
    pl.SendScriptCommands("-Abort")
    print("Abort Command Sent")

    # Disconnect from Prairie View
    pv_disconnect()


# -----------------------------------------------------------------------------
# PrairieLink Set Directory and Filename Function
# -----------------------------------------------------------------------------


def set_filename(team: str, subject_id: str):

    # TODO: Get current imaging location from prairie view
    # imaging_plane = pl.SendScriptCommands("-?GETIMAGINGPLANENUMBER")
    imaging_plane = 289

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session's path
    imaging_dir = basepath + team + "/microscopy/"

    # TODO: Need to see if this with behavior dir change is stable...
    # Set Prairie View path for saving files
    # pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    session_name = "_".join([session_date, subject_id,
                             "plane{}".format(imaging_plane),
                             "raw"])

    # Set imaging filename by adding 2p to session_name
    imaging_filename = "_".join([session_name, "2p"])

    # pl.SendScriptCommands("-SetFileName Tseries {}".format(imaging_filename))

    print(imaging_dir + imaging_filename)

    # Not usable until PV 5.6 release
    # Set behavior session basepath
    behavior_dir = basepath + team + "/behavior/"

    # pl.SendScriptCommands("-SetState directory {} VoltageRecording".format(behavior_dir))

    # Set behavior filename
    behavior_filename = "_".join([session_name, "behavior"])

    # pl.SendScriptCommands("-SetFileName VoltageRecording {}".format(behavior_filename))

    print(behavior_dir + behavior_filename)

    return imaging_plane


# -----------------------------------------------------------------------------
# PrairieLink Start T-Series Function
# -----------------------------------------------------------------------------


def start_tseries():

    # Connect to Prairie View
    # pv_connect()

    # Tell user that the T-Series is starting and waiting for trigger
    print("Starting T-Series: Waiting for Input Trigger")

    # Send T-Series command
    # pl.SendScriptCommands("-TSeries")

    # Disconnect from Prairie View
    # pv_disconnect()


def start_microscopy_session(project: str, subject_id: str):
    """
    Readies the Bruker 2-Photon microscope for an experiment

    Sets directories, filenames, and initializes Bruker T-Series for imaging
    and Voltage Recording for behavior data.

    Args:
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
    """
