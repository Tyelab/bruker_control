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

# Import sleep to let Prairie View change between Galov and Resonant Galvo
from time import sleep

# Import tqdm for progress bar  
from tqdm import tqdm

# Import pathlib for creating z-stack directory
from pathlib import Path

# Import numpy for rounding framerates
import numpy as np

# Import socket to grab hostname and IP address for PL Connection
import socket

# Import os for getting Username and finding file containing Prairie Link Password
import os

# Import sys for exiting safely
import sys

# Import json for reading/writing password file
import json

# Save the Praire View application as pl
pl = client.Dispatch("PrairieLink64.Application")

# Define microscopy basebath for where raw files are written to.  This is onto
# the E: drive on machine BRUKER.  Set it as a string to be joined later.
# Do NOT use Pathlib for this because Prairie Link does not know how to interpret
# pathlib objects
DATA_PATH = "E:/"

# Define Valid 2P Indicators for setting Z-series sessions correctly
IMAGING_VARIABLES = ["fluorophore", "fluorophore_excitation_lambda"]

# Get the username for finding local password file
# For appropriate RTD autodoc functionality, check to see if
# this is being run in a readthedocs workflow.
# See:
# https://docs.readthedocs.io/en/stable/faq.html#how-do-i-change-behavior-when-building-with-read-the-docs
on_rtd = os.environ.get('READTHEDOCS') == 'True'

# If this is being read by readthedocs, give it a fake fun username
if on_rtd:
    USERNAME = "pockel"
# Otherwise, get the real username running the experiment.
else:
    USERNAME = os.getlogin()

# Define static path for where password file is in the repo:
PRAIRIELINK_PASSWORD_FILE = Path(
    f"C:/Users/{USERNAME}/Documents/gitrepos/bruker_control/configs/prairielink_password.json"
    )

###############################################################################
# Classes
###############################################################################

# class BrukerUltimaInvestigatorLegacy:
    # class stuff one day...


###############################################################################
# Exceptions
###############################################################################

class PrairieLinkPasswordError(Exception):
    """
    Exception for when there's an error when parsing prairelink password.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "PrairieLink Password Error: " + "{0}".format(self.message)
        else:
            return "PRAIRIELINK PASSWORD ERROR"

###############################################################################
# Functions
###############################################################################

# -----------------------------------------------------------------------------
# PrairieLink Comms Functions
# -----------------------------------------------------------------------------


def get_pv_password() -> str:
    """
    Load Prairie View Password from file or obtain it from user.

    Prairie View has placed a password on their API that's unique to each
    user account on the system. Per Michael Fox, this was done not because
    of worries about malicious intent but because sometimes IT systems
    will be HTTP address sniffing (basically looking for computers to talk to)
    and start trying to talk to the scope on accident. This can keep the scope's
    software either busy or, more likely, will raise errors from Bruker's API that
    interferes with the experiment as the API will interpret the communications
    as (malformed) PrairieLink commands.
    
    Since it's different per user, a local file must be stored in the repo that contains
    the correct password. This password is found by going to: 
    Tools -> Scripts -> Edit Scripts ... dialog in the bottom left corner of the window.
    It is 4 characters long, all uppercase. The default password will be the string "0000"
    and must be updated by the user the first time they install bruker_control OR likely when
    there's a Prairie View Update. If the password isn't the default, it's passed onto the
    connect function.

    returns:
        password
    """

    # Load password file
    try:

        print("Reading password file...")

        with open(PRAIRIELINK_PASSWORD_FILE, 'r') as inFile:

            contents = inFile.read()

            # Use json.loads to load file
            passwd = json.loads(
                contents
            )
        
        print("Password file read!")

    except:
        raise PrairieLinkPasswordError(
            "PRAIRIELINK PASSWORD FILE ERROR: Possible file is missing, json corrupted? See local repo's configs folder..."
            )
    
    # Check if the password is still the default password.
    if passwd["prairielink_password"] == "0000":

        print("PrairieLink Password is default password.")
        print("Please find your profile's correct Prairie View password. You can find it in: ")
        print("Tools -> Scripts -> Edit Scripts")

        # Gather password from user
        password = input("Please enter the password: ")

        # Update the password in the file, make sure it's upper case since PrairieLink is
        # probably case sensitive.
        passwd["prairielink_password"] = password.upper()

        try:

            with open(PRAIRIELINK_PASSWORD_FILE, 'w') as outFile:

                # Update the password file with new file.
                json.dump(
                    passwd,
                    outFile
                )

            print("Password updated!")

        except:
            raise PrairieLinkPasswordError(
                "ERROR WRITING NEW PRAIRIELINK PASSWORD: json corrupted?"
            )
        
    else:

        # If it wasn't the default password, the updated password should be there.
        password = passwd["prairielink_password"]

    return password


def pv_connect():
    """
    Connect to Prairie View

    First grabs machin hostname and IP address for connecting to Prairie Link.
    Used to connect to Prairie View at the beginning of each session with their
    API.  This function takes no arguments and returns nothing.
    """

    # Grab hostname using socket
    host_name = socket.gethostname()

    # Grab IP address
    ip_address = socket.gethostbyname(host_name)

    # Check if password is correct/available.
    password = get_pv_password()

    # TODO: This should be a try/except block in case the connection fails for some reason...
    # Use hostname and password from Prairie View
    # Password found in lower left corner ofL
    # Tools -> Scripts -> Edit Scripts ... dialog
    pl.Connect(f"{ip_address}", password)
    print("Connected to Prairie View")


def pv_disconnect():
    """
    Disconnect from Prairie View

    Used to disconnect from Prairie View at the end of each session with their
    API.  This function takes no arguments and returns nothing.
    """

    pl.Disconnect()
    print("Disconnected from Prairie View")


# -----------------------------------------------------------------------------
# Galvo Mode Functions
# -----------------------------------------------------------------------------


def set_resonant_galvo():
    """
    Sets acquisition mode to Resonant Galvo.

    Not having resonant galvo mode engaged during T-Series recordings gathers
    insufficient data and does not trigger the facial recording camera
    correctly.  This ensures that it is enabled before the recording starts.
    Sleeps the program for 1 second to make sure Prairie View has enough time
    to switch.  This function takes no arguments and returns nothing.
    """

    # Change Acquisition Mode to Resonant Galvo
    pl.SendScriptCommands("-SetAcquisitionMode ResonantGalvo")

    # Wait 3 seconds for Prairie View to switch modes
    sleep(3)


def set_galvo_galvo():
    """
    Sets Acquisition Mode to Galvo Galvo.

    Z-Series recordings are performed in Galvo Galvo mode. This ensures that
    the mode is switched before the recording starts.  Sleeps the program for
    1 second to make sure Prairie View has enough tim to switch.  This function
    takes no arguments and returns nothing
    """

    # Change Acqusition Mode to Galvo Galvo
    pl.SendScriptCommands("-SetAcquisitionMode Galvo")

    # Wait 3 seconds for Prairie View to switch modes
    sleep(3)

# -----------------------------------------------------------------------------
# Abort T-Series Function
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
# Get Z-Axis Position Function
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


def set_tseries_filename(project: str, subject_id: str, current_plane: int,
                         imaging_plane: float):
    """
    Sets T-Series and Behavior recording filenames and directories.

    Generates appropriately named imaging and behavior directories and
    filenames for data coming off the microscope.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
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
    imaging_dir = DATA_PATH + project + "/microscopy/"

    # Set Prairie View path for saving files
    pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    session_name = "_".join(
            [session_date, subject_id, "plane{}".format(current_plane), imaging_plane, "raw"]
        )

    # Set behavior filename
    behavior_filename = "_".join([session_name, "behavior"])

    pl.SendScriptCommands("-SetState directory {} VoltageRecording"
                          .format(behavior_filename))

    # Set imaging filename by adding 2p to session_name
    # Until 5.6 Update, having 2P in the name is redundant.  This will just
    # assign imaging_filename to session_name until then.
    imaging_filename = "_".join([session_name, "2p"])
    imaging_filename = session_name

    pl.SendScriptCommands("-SetFileName Tseries {}".format(imaging_filename))


# -----------------------------------------------------------------------------
# Laser Control Functions
# -----------------------------------------------------------------------------


def set_laser_lambda(indicator_lambda: float):
    """
    Sets laser lambda to appropriate wavelength for indicator.

    Each indicator has its own optimal excitation wavelength equal to two times
    the value found in the surgical metadata for the subject.  This update is
    performed in this function before setting the laser wavelength for the
    series of Z-stacks that are being collected.  Sleeps the program for 3
    seconds to ensure switch occurs.

    Args:
        indicator_lambda:
            Excitation wavelength for the indicator being imaged
    """

    indicator_lambda = 2 * indicator_lambda

    # If the optimal lambda for the indicator is greater than the Mai Tai
    # Deep See's max output capabilities (1040nm) printa  warning and set
    # the laser to that maximum value.
    if indicator_lambda > 1040:
        print("Optimal wavelength beyond laser's capabilities! Setting to max.")
        indicator_lambda = 1040

    pl.SendScriptCommands("-SetMultiphotonWavelength '{}' 1".format(indicator_lambda))

    # Give Prairie View some time to actually adjust the wavelength before starting.
    for i in tqdm(range(800), desc="Setting Laser Wavelength", ascii=True):
        sleep(0.01)


# TODO: Set PMT values potentially, need to test without this first to see if
# it is necessary
# def set_laser_gain():
#     """
#     Sets PMT values for the laser before recording
#     """


# -----------------------------------------------------------------------------
# T-Series Functions
# -----------------------------------------------------------------------------


def tseries(project: str, subject_id: str, current_plane: int,
            imaging_plane: float, surgery_metadata=None):
    """
    Starts Prairie View 2-P T-Series Experiment

    Function unites t-series preparation function with starting the recording
    with an input trigger. Starting with an input trigger is done within
    the Prairie View GUI.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
        surgery_metadata:

    """

    # Prepare Prairie View for the T-Series Recording
    prepare_tseries(
        project,
        subject_id,
        current_plane,
        imaging_plane,
        surgery_metadata
        )

    # Tell user that the T-Series is starting and waiting for trigger
    print("Starting T-Series: Waiting for Input Trigger")

    # Send T-Series command
    pl.SendScriptCommands("-TSeries")


def prepare_tseries(project: str, subject_id: str, current_plane: int,
                    imaging_plane: float, surgery_metadata: dict):
    """
    Readies the Bruker 2-Photon microscope for a T-Series experiment

    Sets directories and filenames for recording. Ensures that Resonant Galvo
    mode is selected. Sets Prairie View to only use the gcamp indicator channel
    (Channel 2). Initializes Bruker T-Series for imaging, Voltage Recording for
    behavior data, and Mark Points Series as a work around for stimulation trials.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
        surgery_metadata:
            Surgical information for a given subject including virus data
            describing excitation and emission wavelengths.
    """

    set_tseries_filename(
        project,
        subject_id,
        current_plane,
        imaging_plane)

    set_resonant_galvo()

    # For specialk, there could be an instance where the red channel is
    # acquiring data for the Z-stack collected before this point.
    # To make sure that only the relevant channel is used (the green one),
    # turn Channel 1 off and make sure that Channel 2 is on.
    if "specialk" in project:
        set_tseries_parameters(surgery_metadata)


        # TODO: Make this channel setting its own function in next refactor
        pl.SendScriptCommands("-SetChannel '1' 'Off'")
        pl.SendScriptCommands("-SetChannel '2' 'On'")

        # TODO: Make this part of a configuration and make tseries_stim
        # vs tseries_nostim. Must be done with next refactor...
        # pl.SendScriptCommands("-MarkPoints 'specialk' 'cms_stimulations'")



def set_tseries_parameters(surgery_metadata):
    """
    Changes laser lambda to correct wavelength for t-series.

    The laser may or may not be set to use the appropriate wavelength for
    imaging.  This ensures that the laser is set to the correct wavelength
    for the functional indicator specified in the surgical metadata.
    """

    # Get indicators from the surgery metadata
    indicator_metadata = get_imaging_indicators(surgery_metadata)

    functional_indicator = indicator_metadata["gcamp"]

    functional_lambda = functional_indicator["fluorophore_excitation_lambda"]

    set_laser_lambda(functional_lambda)


# -----------------------------------------------------------------------------
# Z-Series Functions
# -----------------------------------------------------------------------------

def configure_zseries(project: str, subject_id: str, current_plane: int,
                    imaging_plane: float, indicator_name: str, stack: int,
                    zstack_delta: float, zstack_step: float):
    """
    Readies the Bruker 2-Photon microscope for a Z-Series

    Sets directories and filenames for Z-stack recording as well as defines
    the distance a z-stack should be taken as well as the step distance for the
    Piezo motor. Transitions Galvo mode to Galvo from Resonant Galvo.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
        indicator_name:
            Name of the fluorophore being imaged during the Z-series
        stack:
            The current stack number from the total number of stacks requested
        zstack_delta:
            Delta both above and below current imaging plane to collect per
            stack
        zstack_step:
            Step size to go between individual planes
    """

    # Set the Z-Series to write out specific file names
    set_zseries_filename(
        project,
        subject_id,
        current_plane,
        imaging_plane,
        indicator_name,
        stack
    )

    # Set Z-Stack parameters
    set_zseries_parameters(
        imaging_plane,
        zstack_delta,
        zstack_step
        )


def set_zseries_parameters(imaging_plane, zstack_delta, zstack_step):
    """
    Set Z-Series depth and step sizes.

    Sets Prairie View's Z-Series parameters for the depth of the stack as well
    as the step size between imaging planes

    Args:
        imaging_plane:
            Current Z-Motor position for given recording plane
        zstack_delta:
            Z-Stack distance to move above and below imaging_plane
        zstack_step:
            Step size to go between individual planes
    """

    # Start position is higher than current imaging plane
    z_start_position = imaging_plane + zstack_delta

    # End position is lower than the current imaging plane
    z_end_position = imaging_plane - zstack_delta

    pl.SendScriptCommands("-SetMotorPosition 'Z' '{}'".format(z_start_position))

    # Sleeping the program is required after moving the z-axis to different locations
    # If this isn't done, the scope/Prairie Link doesn't successfully go between the
    # start/stop locations for a given z-stack.
    sleep(1)

    pl.SendScriptCommands("-SetZSeriesStepSize '{}'".format(zstack_step))

    sleep(1)

    pl.SendScriptCommands("-SetZSeriesStart 'allSettings'")

    pl.SendScriptCommands("-SetMotorPosition 'Z' '{}'".format(z_end_position))

    sleep(1)

    pl.SendScriptCommands("-SetZSeriesStop 'allSettings")


def set_zseries_filename(project: str, subject_id: str,
                         current_plane: int, imaging_plane: float,
                         indicator_name: str, stack: int):
    """
    Sets Z-Series filename and directory.

    Generates appropriately named Z-Series filenames for data coming off the
    microscope.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            The subject being recorded
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
        indicator_name:
            Name of the fluorophore being imaged during the Z-series
        stack:
            The stack being imaged as in 1st, 2nd, 3rd, etc
    """

    # Convert imaging plane to string
    imaging_plane = str(imaging_plane)

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set microscopy session's path
    imaging_dir = DATA_PATH + project + "/zstacks/"

    # Set Prairie View path for saving files
    pl.SendScriptCommands("-SetSavePath {}".format(imaging_dir))

    # Set session name by joining variables with underscores
    session_name = "_".join(
        [session_date,
        subject_id,
        imaging_plane,
        "plane{}".format(current_plane),
        indicator_name,
        "raw"
        ]
    )

    # Set imaging filename by adding zseries and to session_name
    imaging_filename = "_".join([session_name, "zseries"])
    imaging_filename = session_name

    # Use this file iteration parameter for tracking which stack has been
    # collected for the indicator
    pl.SendScriptCommands("-SetFileIteration Zseries {}".format(stack))

    # Set the filename for the Z-stack
    pl.SendScriptCommands("-SetFileName Zseries {}".format(imaging_filename))


def get_imaging_indicators(surgery_metadata: dict) -> dict:
    """
    Gets imaging indicators from surgery metadata.

    Only a subset of metadata from the surgery information is requried for
    changing laser values and filenames. This builds a dictionary of those
    indicators and relevant values.

    Args:
        surgery_metdata:
            Surgical information for a given subject including virus data
            describing excitation and emission wavelengths.

    Returns:
        indicator_metadata
    """

    indicators = surgery_metadata["brain_injections"]

    indicator_metadata = {}

    for key, value in indicators.items():
        indicator_metadata[key] = value

    return indicator_metadata


def zstack(zstack_metadata: dict, project: str, subject_id: str,
           current_plane: int, imaging_plane: float, surgery_metadata: dict):
    """
    Starts Prairie View Z-Series 2P Recording

    Starts Z-stack recording at the start of a given session for a subject and
    moves through configuration specific planes with configuration specific
    step sizes.  Writes out the raw stack to team's microscopy folder.

    Args:
        zstack_metadata:
            Information about depth for Z-Stack and step distance
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Name of the experimental subject
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Current Z-Motor position for given recording plane
        surgery_metdata:
            Surgical information for a given subject including virus data
            describing excitation and emission wavelengths.
    """

    indicator_metadata = get_imaging_indicators(surgery_metadata)

    total_stacks = zstack_metadata["stack_number"]

    zstack_delta = zstack_metadata["zdelta"]

    zstack_step = zstack_metadata["zstep"]

    set_galvo_galvo()

    for indicator in indicator_metadata.keys():

        indicator_name = indicator_metadata[indicator]["fluorophore"]

        print("Conducting Z-Series for indicator:", indicator_name)

        indicator_lambda = indicator_metadata[indicator]["fluorophore_excitation_lambda"]

        indicator_emission = indicator_metadata[indicator]["fluorophore_emission_lambda"]

        set_laser_lambda(indicator_lambda)

        set_one_channel_zseries(indicator_emission)

        for stack in range(0, total_stacks):

            configure_zseries(
                project,
                subject_id,
                current_plane,
                imaging_plane,
                indicator_name,
                stack,
                zstack_delta,
                zstack_step
            )

            pl.SendScriptCommands("-ZSeries")

            # Make progress bar for z-stack duration
            for second in tqdm(range(0, int(zstack_delta)*2), desc="Z-Stack Progress", ascii=True):

                # Sleep the progress bar. Empirically this looks about how long it takes each frame 
                # to be taken and then move the scope down to take the next image.
                sleep(2.2)


    # Put Z-axis back to imaging plane
    pl.SendScriptCommands("-SetMotorPosition 'Z' {}".format(imaging_plane))

def set_one_channel_zseries(indicator_emission: float):
    """
    Sets proper recording channel to use (1: Red 2: Green) in the z-stack.

    Different indicators have different channels that should be recorded from
    depending on the emission wavelengths of the indicators being imaged.

    Args:
        indicator_emission:
            Wavelength fluorescent indicator emits when cell is active and
            being stimulated by light
    """

    # If the indicator's emission wavelength is above green wavelengths,
    # use only the red channel.
    if indicator_emission >= 570.0:
        pl.SendScriptCommands("-SetChannel '1' 'On'")
        pl.SendScriptCommands("-SetChannel '2' 'Off'")

    # Otherwise, use the green channel
    else:
        pl.SendScriptCommands("-SetChannel '1' 'Off'")
        pl.SendScriptCommands("-SetChannel '2' 'On'")


def get_microscope_framerate() -> float:
    """
    Queries Prairie View for the microscope's framerate before a recording is started.

    The scope appears to have slightly different framerates between starts of Prairie View
    on the orders of 0.01FPS. To ensure that the video codec for the facial recording is
    using the same timescale, getting the scope's state for framerate is necessary. This
    will query Prairie View for the scope's current framerate setting, round the framerate
    UP to the nearest hundreth, and return it so the video codec uses the correct FPS.

    Returns:
        microscope_framerate
    """

    # Ask Prairie Link to get the current framerate setting. The function returns a string,
    # so convert it to a float
    framerate = float(pl.GetState("framerate"))

    # The framerate value is calculated with a precision of 12 decimals. Use just to the
    # hundredths value, or 2 decimal places
    framerate = np.round(framerate, decimals=2)

    return framerate

def get_pmt_gain(channel_number: int):
    """
    Queries Prairie View for the microscope's channel number.

    The function will query Prairie View for the scope's current channel number setting,
    and returns it as the correct value of each PMT's gain.

    Args:
        channel_number:
            channel the software will monitor for data collection

    Returns:
        pmt_gain
    """

    # Ask Prairie Link to get the current channel number. The function returns a string,
    # so convert it to an integer
    pmt_gain = int(pl.GetState("channel_number"))

    return pmt_gain


def get_laser_power() -> int:
    """
    Queries Prairie View for the microscope's current laser power.

    The function will query Prairie View for the scope's current laser power setting.

    Returns:
        laser_power
    """

    # Ask Prairie Link to get the current laser power. The function returns a string,
    # so convert it to an integer

    laser_power = int(pl.GetState("laser_power"))

    return laser_power
