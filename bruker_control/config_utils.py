# Bruker 2-Photon Config Utils
# Jeremy Delahanty May 2021

###############################################################################
# Import Packages
###############################################################################
# File Types
# Import JSON for configuration file
import json

# Import ordered dictionary to ensure order of in json file
from collections import OrderedDict

# Import pathlib for searching for files and grabbing relevant configs
from pathlib import Path

# Import datetime for folder naming
from datetime import datetime
from dateutil.tz import tzlocal

# Template configuration directories are within project directories.  The snlkt
# server housing these directories is mounted to the X: volume on the machine
# BRUKER.
base_template_config_dir = Path("X:/")

# Experimental configuration directories are in the Raw Data volume on the
# machine BRUKER which is mounted to E:. This is where configs will be written
config_basepath = "E:/teams/"

# Configuration files generated for a team's session are placed in their team's
# directory on drive E:

###############################################################################
# Exceptions
###############################################################################


class ConfigDirEmpty(Exception):
    """
    Exception for when the team's template configuration folder is empty.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "ConfigDirEmpty: " + "{0}".format(self.message)
        else:
            return "Config dir empty! Check your 2p_template_configs folder."

###############################################################################
# Functions
###############################################################################


def get_template(team: str) -> dict:
    """
    Grab team's template configuration file for experiment runtime.

    Uses the metadata_args value "team" found in bruker_control to select the
    specific 2-Photon configuration file that will run the experiment for
    a session.

    Args:
        team:
            Team from metadata_args["team"]

    Returns:
        template_config
    """

    # Append base directory with selected team
    template_dir = base_template_config_dir / team / "2p_template_configs"

    # Until consistent conventions for studies are established, automatically
    # populating different files for a given team's studies is not practical.
    # Therefore, teams must be restricted to a single configuration file.

    # Glob the configuration directory for the .json file, convert it to a list
    # and grab the file itself
    try:
        template_file_path = list(template_dir.glob("*.json"))[0]
        # Grab template configuration values with read_config
        config_template = read_config(template_file_path)

    except IndexError:
        raise ConfigDirEmpty()

    return config_template


def read_config(config_file_path: Path) -> dict:
    """
    Utility function for reading config files

    General purpose function for reading .json files containing configuration
    values for an experiment

    Args:
        config_file_path:
            Pathlib path to the configuration file.

    Returns:
        Dictionary of contents inside the configuration .json file

    """

    with open(config_file_path, 'r') as inFile:

        contents = inFile.read()

        # Use json.loads to gather metadata and save them in an
        # ordered dictionary
        config_values = json.loads(contents,
                                   object_pairs_hook=OrderedDict)

    return config_values


def write_experiment_config(config_template: dict, experiment_arrays: list,
                            dropped_frames: list, team: str, subject_id: str,
                            imaging_plane: str):
    """
    Writes experiental configuration file to Raw Data drive.

    Takes the configuration template and appends on the experimental arrays and
    dropped frames from the experiment. Then writes the configuration to disk.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.
        experiment_arrays:
            List of arrays used for experimental runtime. [0] is trialArray,
            [1] is ITIArray, [2] is toneArray. These will always be in this
            order.
        dropped_frames:
            List of dropped frames from the camera during the experiment
        team:
            Team from metadata_args["team"]
        subject_id
            Subject ID from metadata_args["subject_id"]
        imaging_plane:
            Plane 2P images were acquired at, the Z-axis value
    """

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Generate the session_name
    session_name = "_".join([session_date, subject_id,
                             "plane{}".format(imaging_plane)])

    # Generate Experiment Configuration Directory Path
    config_dir = config_basepath + team + "/config/"

    # Generate the filename
    config_filename = "_".join([session_name, "config"])

    # Append .json for the file
    config_filename += ".json"

    # Complete the fullpath for the config file to be written
    config_fullpath = config_dir + config_filename

    # Assign trialArray key to trialArray data.  The 0th index of the list is
    # always the the trialArray
    config_template["trialArray"] = experiment_arrays[0]

    # Assign ITIArray key to ITIArray data.  The 1st index of the list is
    # always the ITIArray
    config_template["ITIArray"] = experiment_arrays[1]

    # Assign toneArray key the toneArray data.  The 2nd index of the list is
    # always the toneArray.
    config_template["toneArray"] = experiment_arrays[2]

    # Assign dropped_frames key the dropped_frames data.
    config_template["dropped_frames"] = dropped_frames

    # # Write the new configuration file
    with open(config_fullpath, 'w') as outFile:

        # Add ITIArray into config file
        json.dump(config_template, outFile)


def get_arduino_metadata(config_template: dict) -> dict:
    """
    Grabs metadata relevent to Arduino runtime

    Parses the template configuration supplied by the user and grabs only the
    metadata that is relevant for the Arduino's function using dictionary
    comprehension. Finally converts dictionary to json object for transfer.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        arduino_metadata
            Dictionary of relevant Arduino metadata for experiment.
    """

    # Define the variables required for Arduino function
    arduino_metadata_keys = ["totalNumberOfTrials", "punishTone", "rewardTone",
                             "USDeliveryTime_Sucrose", "USDeliveryTime_Air",
                             "USConsumptionTime_Sucrose"]

    # Generate Dictionary of relevant Arduino metadata
    arduino_metadata = {key: value for (key, value) in
                        config_template["metadata"].items() if
                        key in arduino_metadata_keys}

    return arduino_metadata
