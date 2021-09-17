# Bruker 2-Photon Prairie View Utils
# Jeremy Delahanty, Dexter Tsin May 2021
# Written with assistance from Michael Fox, Sr Software Engineer Bruker

###############################################################################
# Import Packages
###############################################################################

# Import Prairie View Application
# NOTE Prairie View Interface Installation:  Do NOT use pip install, use conda.
# conda install pywin32
import win32com.client as client

# Import datetime for folder naming
from datetime import datetime

# Save the Praire View application as pl
pl = client.Dispatch("PrairieLink.Application")

# Import NWB Utility for Grabbing Subject Metadata
from nwb_utils import get_subject_metadata

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

    pl.Connect()
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

    pl.Disconnect()
    print("Disconnected from Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------


def end_tseries():
    """
    Ends T-Series Microscopy recording

    Once the number of frames specified is collected, a signal to abort the
    microscopy session is sent to Prairie View.  This function takes no
    arguments and returns nothing.
    """

    # Tell user recording is being stopped using abort command
    print("Ending T-Series Recording...")

    # Tell user abort command is being sent, send the command, and finally
    # tell user that the command has been executed.
    pl.SendScriptCommands("-Abort")
    print("T-Series Complete")


# -----------------------------------------------------------------------------
# PrairieLink Get Z-Axis Function
# -----------------------------------------------------------------------------


def get_imaging_plane() -> float:
    """
    Gets current position of Z-axis motor from Prairie View

    Gathers what plane is being imaged for the microscopy session for use in
    file naming and Z-Stack movement.

    Returns:
        imaging_plane
    """

    imaging_plane = pl.GetMotorPosition("Z")

    return imaging_plane

# -----------------------------------------------------------------------------
# PrairieLink Set Directory and Filename Function
# -----------------------------------------------------------------------------


def set_tseries_filename(team: str, subject_id: str, current_plane: int,
                         imaging_plane: float):
    """
    Sets T-Series and Behavior recording filenames and directories.

    Generates appropriately named imaging and behavior directories and
    filenames for data coming off the microscope.

    Args:
        team:
            The team performing the experiment
        subject_id:
            The subject being recorded
        current_plane:
            The plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    # Convert imaging plane to string
    imaging_plane = str(imaging_plane)

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session's path
    imaging_dir = basepath + team + "/microscopy/"

    # Set Prairie View path for saving files
    pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    session_name = "_".join([session_date, subject_id,
                             "plane{}".format(current_plane),
                             imaging_plane, "raw"])

    # # Set behavior filename
    # behavior_filename = "_".join([session_name, "behavior"])
    #
    # pl.SendScriptCommands("-SetState directory {} VoltageRecording"
    #                       .format(behavior_filename))

    # Set imaging filename by adding 2p to session_name
    # Until 5.6 Update, having 2P in the name is redundant.  This will just
    # assign imaging_filename to session_name until then.
    imaging_filename = "_".join([session_name, "2p"])
    imaging_filename = session_name

    pl.SendScriptCommands("-SetFileName Tseries {}".format(imaging_filename))

    # Not usable until PV 5.6 release
    # Set behavior session basepath
    # behavior_dir = basepath + team + "/behavior/"

    # pl.SendScriptCommands("-SetState directory {} VoltageRecording"
    #                       .format(behavior_dir))


# -----------------------------------------------------------------------------
# PrairieLink Set Resonant Galvo Mode
# -----------------------------------------------------------------------------


def set_resonant_galvo():
    """
    Sets acquisition mode to Resonant Galvo.

    Not having resonant galvo mode engaged during T-Series recordings gathers
    insufficient data and does not trigger the facial recording camera
    correctly. This ensures that it is enabled before the recording starts.
    This function takes no arguments and returns nothing.
    """

    # Change Acquisition Mode to Resonant Galvo
    pl.SendScriptCommands("-SetAcquisitionMode 'Resonant Galvo'")


def set_galvo_galvo():
    """
    Sets Acquisition Mode to Galvo Galvo.

    Z-Series recordings are performed in Galvo Galvo mode. This ensures that
    the mode is switched before the recording starts. This function takes no
    arguments and returns nothing
    """

    # Change Acqusition Mode to Galvo Galvo
    pl.SendScriptCommands("-SetAcquisitionMode 'Galvo'")


# -----------------------------------------------------------------------------
# PrairieLink Set Laser Wavelength
# -----------------------------------------------------------------------------


def set_laser_lambda(subject_metadata):
    """
    Sets laser lambda to appropriate wavelength
    """

# -----------------------------------------------------------------------------
# PrairieLink Start T-Series Function
# -----------------------------------------------------------------------------


def tseries(project: str, subject_id: str, current_plane: int,
            imaging_plane: float):
    """
    Starts Prairie View 2-P T-Series Experiment

    Function unites t-series preparation function with starting the recording
    with an input trigger. Starting with an input trigger is done within
    the Prairie View GUI.

    Args:
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    # Prepare Prairie View for the T-Series Recording
    prepare_tseries(project, subject_id, current_plane, imaging_plane)

    # Tell user that the T-Series is starting and waiting for trigger
    print("Starting T-Series: Waiting for Input Trigger")

    # Send T-Series command
    pl.SendScriptCommands("-TSeries")


def prepare_tseries(project: str, subject_id: str, current_plane: int,
                    imaging_plane: float, subject_metadata: dict):
    """
    Readies the Bruker 2-Photon microscope for a T-Series experiment

    Sets directories and filenames for recording. Ensures that Resonant Galvo
    mode is selected. and initializes Bruker T-Series for imaging and Voltage
    Recording for behavior data.

    Args:
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    set_tseries_filename(project, subject_id, current_plane, imaging_plane)

    set_resonant_galvo()


# -----------------------------------------------------------------------------
# PrairieLink Start Z-Series Functions
# -----------------------------------------------------------------------------


def prepare_zseries(zstack_metadata, project: str, subject_id: str,
                   current_plane: int, imaging_plane: float):
    """
    Readies the Bruker 2-Photon microscope for a Z-Series

    Sets directories and filenames for Z-stack recording as well as defines
    the distance a z-stack should be taken as well as the step distance for the
    Piezo motor. Transitions Galvo mode to Galvo from Resonant Galvo.

    Args:
        zstack_metadata:
            Information about depth for Z-Stack and step distance
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    # Set the Z-Series to write out specific file names
    set_zseries_filename(team, subject_id, current_plane, imaging_plane)

    # Set Acquisition Mode to Galvo Galvo for Z-Stack
    set_galvo_galvo()

    # Set Z-Stack parameters


def set_zseries_parameters(zstack_metadata):
    """
    Set Z-Series depth and step sizes.

    Sets Prairie View's Z-Series parameters for the depth of the stack as well
    as the step size between imaging planes

    Args:
        zstack_metadata:
            Information about depth for Z-Stack and step distance
    """

    pl.SetZSeriesStart()


def set_zseries_filename(team: str, subject_id: str, current_plane: int,
                         imaging_plane: float):
    """
    Sets Z-Series filename and directory.

    Generates appropriately named Z-Series filenames for data coming off the
    microscope.

    Args:
        team:
            The team performing the experiment
        subject_id:
            The subject being recorded
        current_plane:
            The plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    # Convert imaging plane to string
    imaging_plane = str(imaging_plane)

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session's path
    imaging_dir = basepath + team + "/microscopy/"

    # Set Prairie View path for saving files
    pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    session_name = "_".join([session_date, subject_id,
                             "plane{}".format(current_plane),
                             imaging_plane, "raw"])

    # # Set behavior filename
    # behavior_filename = "_".join([session_name, "behavior"])
    #
    # pl.SendScriptCommands("-SetState directory {} VoltageRecording"
    #                       .format(behavior_filename))

    # Set imaging filename by adding 2p to session_name
    # Until 5.6 Update, having 2P in the name is redundant.  This will just
    # assign imaging_filename to session_name until then.
    imaging_filename = "_".join([session_name, "zseries"])
    imaging_filename = session_name

    pl.SendScriptCommands("-SetFileName Zseries {}".format(imaging_filename))


def zstack(zstack_metadata: dict, project: str, subject_id: str,
           current_plane: int, imaging_plane: float, subject_metadata: dict):
    """
    Starts Prairie View Z-Series 2P Recording

    Starts Z-stack recording at the start of a given session for a subject and
    moves through configuration specific planes with configuration specific
    step sizes.  Writes out the raw stack to team's microscopy folder.

    Args:
        zstack_metadata:
            Information about depth for Z-Stack and step distance
        project:
            Name of project for recording
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
    """

    prepare_zseries()
