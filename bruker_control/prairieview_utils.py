# Bruker 2-Photon Prairie View Utils
# Jeremy Delahanty, Dexter Tsin May 2021
# Written with assistance from Michael Fox, Sr Software Engineer Bruker

###############################################################################
# Import Packages
###############################################################################

# Import Prairie View Application
# NOTE Prairie View Interface Installation:  Do NOT use pip install, use conda.
# conda install pywin32
# import win32com.client as client

# Import datetime for folder naming
from datetime import datetime

# Save the Praire View application as pl
# pl = client.Dispatch("PrairieLink.Application")

# Define microscopy basebath for where raw files are written to.  This is onto
# the E: drive on machine BRUKER.  Set it as a string to be joined later.
basepath = "E:/teams/"

###############################################################################
# Functions
###############################################################################

# -----------------------------------------------------------------------------
# PrairieLink Connect Function
# -----------------------------------------------------------------------------


def pv_connect():
    """
    Connect to Prairie View

    Used to connect to Prairie View at the beginning of each session with their
    API.  This function takes no arguments and returns nothing.
    """

    # pl.Connect()
    print("Connected to Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Disconnect Function
# -----------------------------------------------------------------------------


def pv_disconnect():
    """
    Disconnect from Prairie View

    Used to disconnect from Prairie View at the end of each session with their
    API.  This function takes no arguments and returns nothing.
    """

    # pl.Disconnect()
    print("Disconnected from Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------


def abort_recording():
    """
    Aborts T-Series Microscopy recording

    Once the number of frames specified is collected, a signal to abort the
    microscopy session is sent to Prairie View.  Once aborted, Python will
    disconnect from Prairie View.  This function takes no arguments and returns
    nothing.
    """

    # Tell user recording is being stopped using abort command
    print("Aborting Recording...")

    # Tell user abort command is being sent, send the command, and finally
    # tell user that the command has been executed.
    # pl.SendScriptCommands("-Abort")
    print("Abort Command Sent")

    # Disconnect from Prairie View
    pv_disconnect()


# -----------------------------------------------------------------------------
# PrairieLink Set Directory and Filename Function
# -----------------------------------------------------------------------------


def set_filename(team: str, subject_id: str, current_plane: int) -> str:
    """
    Sets Microscopy and Behavior recording filenames and directories.

    Gathers what plane is being imaged for the session generates appropriately
    named imaging and behavior directories and filenames for data coming off
    the microscope.

    Args:
        team:
            The team performing the experiment
        subject_id:
            The subject being recorded
        current_plane:
            The plane being imaged as in 1st, 2nd, 3rd, etc

    Returns:
        imaging_plane
    """

    # Get Z Axis Imaging plane from Prairie View
    # imaging_plane = str(pl.GetMotorPosition("Z"))

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session's path
    imaging_dir = basepath + team + "/microscopy/"

    # Set Prairie View path for saving files
    # pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    # session_name = "_".join([session_date, subject_id,
    #                          "plane{}".format(current_plane),
    #                          imaging_plane, "raw"])

    # # Set behavior filename
    # behavior_filename = "_".join([session_name, "behavior"])
    #
    # pl.SendScriptCommands("-SetState directory {} VoltageRecording"
    #                       .format(behavior_filename))

    # Set imaging filename by adding 2p to session_name
    # Until 5.6 Update, having 2P in the name is redundant.  This will just
    # assign imaging_filename to session_name until then.
    # imaging_filename = "_".join([session_name, "2p"])
    # imaging_filename = session_name

    # pl.SendScriptCommands("-SetFileName Tseries {}".format(imaging_filename))

    # Not usable until PV 5.6 release
    # Set behavior session basepath
    # behavior_dir = basepath + team + "/behavior/"
    #
    # pl.SendScriptCommands("-SetState directory {} VoltageRecording"
    #                       .format(behavior_dir))

    # return imaging_plane


# -----------------------------------------------------------------------------
# PrairieLink Start T-Series Function
# -----------------------------------------------------------------------------


def start_tseries():
    """
    Starts Prairie View T-Series 2P Recording

    Connects to Prairie View and starts the T-Series which will wait for an
    input trigger.  Waiting for an input trigger is done within Prairie View's
    GUI.  It also ensures that the microscope's setting is put to Resonant
    Galvo in case the user forgot.  This argument takes no arguments and
    returns nothing.
    """

    # Tell user that the T-Series is starting and waiting for trigger
    print("Starting T-Series: Waiting for Input Trigger")

    # Make sure that the acquisition mode is in Resonant Galvo
    # pl.SendScriptCommands("-SetAcquisitionMode 'Resonant Galvo'")

    # Send T-Series command
    # pl.SendScriptCommands("-TSeries")


def start_microscopy_session(project: str, subject_id: str,
                             current_plane: int) -> str:
    """
    Readies the Bruker 2-Photon microscope for an experiment

    Sets directories, filenames, and initializes Bruker T-Series for imaging
    and Voltage Recording for behavior data. Returns the current imaging_plane
    as found in Prairie View.

    Args:
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc

    Returns:
        imaging_plane
    """

    pv_connect()

    imaging_plane = set_filename(project, subject_id, current_plane)

    start_tseries()

    return imaging_plane


def end_microscopy_session() -> datetime:
    """
    Aborts the microscopy session and disconnects from Prairie View.

    Used when the data for the given experiment has been collected and written
    to disk.  Invokes the abort command and disconnects from Prarie View with
    their API.  This function takes no arguments and returns nothing.
    """

    abort_recording()
