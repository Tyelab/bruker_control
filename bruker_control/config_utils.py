# Bruker 2-Photon Config Utils
# Jeremy Delahanty May 2021

###############################################################################
# Import Packages
###############################################################################

# Import JSON for configuration file
import json

# Import ordered dictionary to ensure order of in json file
from collections import OrderedDict

# Import pathlib for searching for files and grabbing relevant configs
from pathlib import Path

# Import datetime for folder naming
from datetime import datetime

# Import YAML for gathering metadata about project
from ruamel.yaml import YAML

# Template configuration directories are within project directories.  The snlkt
# server housing these directories is mounted to the X: volume on the machine
# BRUKER.
base_template_config_dir = Path("X:/")
server_basepath = "X:/"

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
                            imaging_plane: str, current_plane: int):
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
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
    """

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Generate the session_name
    session_name = "_".join([session_date, subject_id,
                             "plane{}".format(current_plane),
                             imaging_plane])

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
    config_template["behavior_metadata"]["trialArray"] = experiment_arrays[0]

    # Assign ITIArray key to ITIArray data.  The 1st index of the list is
    # always the ITIArray
    config_template["behavior_metadata"]["ITIArray"] = experiment_arrays[1]

    # Assign toneArray key the toneArray data.  The 2nd index of the list is
    # always the toneArray.
    config_template["behavior_metadata"]["toneArray"] = experiment_arrays[2]

    # Assign dropped_frames key the dropped_frames data.
    config_template["behavior_metadata"]["dropped_frames"] = dropped_frames

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
                        config_template["behavior_metadata"].items() if
                        key in arduino_metadata_keys}

    return arduino_metadata


def get_zstack_metadata(config_template: dict) -> dict:
    """
    Grabs metadata relevant for generating Z-stacks

    Parses template configuration supplied by the user and grabs only the
    metadata that is relevant for Prairie View executing a Z-stack.

    Args:
        config_template:
            Configuration template value dictionary gathered from team's
            configuration .json file.

    Returns:
        zstack_metadata
            Dictionary of relevant Prairie View Z-Stack for experiment
    """

    zstack_metadata = config_template["zstack_metadata"]

    return zstack_metadata


def get_subject_metadata(team: str, subject_id: str) -> dict:
    """
    Parses imaging subject's .yml metadata file for NWB fields

    Locates and then uses ruamel.yaml to parse the metadata fields with safe
    loading. Gathers yaml data and places it into a dictionary for use later
    in the NWB file.

    Args:
        team:
            Team value from metadata_args["team"]
        subject_id:
            Subject ID from metadata_args["subject"]

    Returns:
        subject_metadata
    """

    # Define YAML object parser with safe loading
    yaml = YAML(typ='safe')

    # Construct the base path for the subject's YAML file
    base_yaml_path = Path(server_basepath + team + "/animal_metadata/")

    animal_glob = [subject for subject in
                   base_yaml_path.glob(f"{subject_id}.yml")]

    # TODO: Raise warning here if there's more than one animal presented in
    # this glob
    subject_metadata = yaml.load(animal_glob[0])

    return subject_metadata


def get_surgery_metadata(subject_metadata: dict) -> dict:
    """
    Grabs surgery information from subject's metadata file.

    Implant information and virus information for stimulation and recording
    is contained within the subject's metadata file.  This information is used
    for filenaming purposes particularly in the Z-Stack files as well as the
    NWB files' metadata sections.

    Args:
        subject_metadata:
            Metadata obtained from get_subject_metadata()

    Returns:
        surgery_metadata
    """

    surgery_metadata = subject_metadata["surgery"]

    surgery_metadata = surgery_metadata[next(iter(surgery_metadata))]

    return surgery_metadata


def get_project_metadata(team: str, subject_id: str):
    """
    Grabs and parses project metadata yml file for NWB file generation.

    Each project has its own metadata associated with it that NWB uses in its
    standard.  This function grabs the proper file and builds a dictionary that
    is used when populating metadata later.

    Args:
        team:
            Team value from metadata_args["team"]
        subject_id:
            Subject ID from metadata_args["subject"]

    Returns:
        project_metadata
    """

    # Define YAML object parser with safe loading
    yaml = YAML(typ='safe')

    # Construct the base path for the project's YAML file
    base_yaml_path = server_basepath + team + "/2p_template_configs/"

    # Until teams and studies/projects are implemented across all directories,
    # this if/else will have to do
    if "LH" in subject_id:
        project_yaml_path = Path(base_yaml_path + "nwb_lh_base.yml")
    else:
        project_yaml_path = base_yaml_path + "nwb_cs_base.yml"

    # Load the project metadata into a dictionary
    project_metadata = yaml.load(project_yaml_path)

    return project_metadata
