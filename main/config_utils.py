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

# Template configuration directories are within project directories. Teams
# have started merging into their own project volumes, making a dictionary
# for each project:project_dir dictionary pairing.
# TODO Part of the second refactor should be to have class object for server
# directories built, a method of which would be gathering the appropriate
# Path object for each volume. That way the config utils can just have a class
# that's dedicated to grepping this information and passing it to the relevant
# parts of the program.
SERVER_PATHS = {"specialk_cs": Path("V:"),
                "specialk_lh": Path("U:"),
                }

# Experimental configuration directories are in the Raw Data volume on the
# machine BRUKER which is mounted to E:. This is where configs will be written
# TODO: Convert DATA_PATH to Path object w/pathlib, unsure why I didn't do this
# in the first place
DATA_PATH = "E:/"

###############################################################################
# Exceptions
###############################################################################

class TemplateError(Exception):
    """
    Exception for when there's an error when parsing templates.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "TemplateError: " + "{0}".format(self.message)
        else:
            return "TEMPLATE ERROR"

class SubjectError(Exception):
    """
    Exception for when there's an error when parsing information for a subject.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "SubjectError: " + "{0}".format(self.message)
        else:
            return "SUBJECT ERROR"

###############################################################################
# Metadata Classes: In development
###############################################################################

# class ConfigTemplate:
#     """
#     Class containing configuration values from project's .JSON file.
#     """

# class StimMetadata(ConfigTemplate):
#     """
#     Metadata class describing information related to stimulation parameters
#     """

# class IndicatorMetadata(ConfigTemplate):
#     """
#     Metadata class describing imaging indicators' properties.
#     """

# class SubjectMetadata(ConfigTemplate):
#     """
#     Metadata class describing information related to the subject being imaged
#     """

# class SurgeryMetadata(ConfigTemplate):
#     """
#     Metadata class describing information related to subject's surgeries
#     """
# class ZStackMetadata(ConfigTemplate):
#     """
#     Metadata class describing information related to the Z-stack functionality
#     """

###############################################################################
# Functions
###############################################################################


def get_template(project: str) -> dict:
    """
    Grab team's template configuration file for experiment runtime.

    Uses the metadata_args values "team" and "project" found in bruker_control to select the
    specific 2-Photon configuration file that will run the experiment for a session.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)

    Returns:
        template_config
    """

    # Determine which path to use by grabbing appropriate key/value pair from static dir
    # on the machine
    server_location = SERVER_PATHS[project]

    # Append base directory with selected team and project
    template_dir = server_location / "2p" / "config"

    # Glob the configuration directory for the .json file and convert it to a list
    template_config_path = list(template_dir.glob("*.json"))

    # If the length of the list for the template file is great than 1,
    # something is wrong. Raise an exception.
    if len(template_config_path) > 1:
        raise TemplateError(
            "Project has multiple template files! Check your 2p/config folder for your project."
            )

    # Otherwise, try to load the one present file. If it's not there,
    # an index error occurs and an exception is raised.
    else:
        try:
            template_config = template_config_path[0]
            config_template = read_config(template_config)


        except IndexError:
            raise TemplateError(
                "Project Template is missing! Check your 2p/config folder for your project."
                )

    return config_template


def read_config(config_path: Path) -> dict:
    """
    Utility function for reading config files

    General purpose function for reading .json files containing configuration
    values for an experiment.

    Args:
        config_path:
            Pathlib path to the template configuration file.

    Returns:
        Dictionary of contents inside the configuration .json file
    """

    with open(config_path, 'r') as inFile:

        contents = inFile.read()

        # Use json.loads to gather metadata and save them in an
        # ordered dictionary
        config_values = json.loads(
            contents,
            object_pairs_hook=OrderedDict
        )

    return config_values


def write_experiment_config(config_template: dict, experiment_arrays: list,
                            dropped_frames: list, project: str, subject_id: str,
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
            [1] is ITIArray, [2] is toneArray, [3] is LEDArray. These must
            always be in this order.
        dropped_frames:
            List of dropped frames from the camera during the experiment
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
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
    config_dir = DATA_PATH + project + "/config/"

    # Generate the filename
    config_filename = "_".join([session_name, "config"])

    # Append .json for the file
    config_filename += ".json"

    # Complete the fullpath for the config file to be written
    config_fullpath = config_dir + config_filename

    # Assign trialArray key to trialArray data.  The 0th index of the list is
    # always the the trialArray
    config_template["beh_metadata"]["trialArray"] = experiment_arrays[0]

    # Assign ITIArray key to ITIArray data.  The 1st index of the list is
    # always the ITIArray
    config_template["beh_metadata"]["ITIArray"] = experiment_arrays[1]

    # Assign toneArray key the toneArray data.  The 2nd index of the list is
    # always the toneArray.
    config_template["beh_metadata"]["toneArray"] = experiment_arrays[2]

    # Assign LEDArray key the LEDArray data. The 3rd index of the list is
    # always the LEDArray.
    config_template["beh_metadata"]["LEDArray"] = experiment_arrays[3]

    # Assign dropped_frames key the dropped_frames data.
    config_template["beh_metadata"]["dropped_frames"] = dropped_frames

    # Write the completed configuration file
    with open(config_fullpath, 'w') as outFile:

        json.dump(
            config_template,
            outFile,
            indent=4
            )

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
                             "USConsumptionTime_Sucrose", "stimDeliveryTime_Total"]

    # Generate Dictionary of relevant Arduino metadata
    arduino_metadata = {key: value for (key, value) in
                        config_template["beh_metadata"].items() if
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


def get_subject_metadata(project: str, subject_id: str) -> dict:
    """
    Parses imaging subject's .yml metadata file for NWB fields

    Locates and then uses ruamel.yaml to parse the metadata fields with safe
    loading. Gathers yaml data and places it into a dictionary for use later
    in the NWB file.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Subject ID from metadata_args["subject"]

    Returns:
        subject_metadata
    """

    # Define YAML object parser with safe loading
    yaml = YAML(typ='safe')

    # Grab appropriate server volume location
    server_location = SERVER_PATHS[project]

    # Construct the base path for the subject's YAML file
    subject_path = server_location / "subjects" / subject_id

    # Generate a glob object for finding the yaml file and turn it into a list.
    subject_metadata = list(subject_path.glob(f"{subject_id}.yml"))

    # Check if there's multiple metadata files present for a subject.
    if len(subject_metadata) > 1:
        raise SubjectError("Multiple subject files found! Check your project's subjects directory (ie U:/subjects/subjectid/)")

    # Otherwise, try to load the one present file. If it's not there,
    # an index error occurs and an exception is raised.
    else:
        try:
            subject_metadata = yaml.load(subject_metadata[0])

        except IndexError:
            raise SubjectError("No subject metadata found! Check your project's subjects directory (ie U:/subjects/subjectid/)")

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

    # For now, only the first surgery present in the metadata file
    # is usable and it is assumed that the relevant procedures were
    # conducted for this surgery (GRIN implant, gCaMP injection, etc)
    surgery_metadata = surgery_metadata[next(iter(surgery_metadata))]

    return surgery_metadata


def build_server_directory(project: str, subject_id: str, config_template: dict):
    """
    Builds directories for copying files to server at the end of the day.

    Directories are not automatically built for different subjects on different days
    because dates and times might change. Therefore, they're built during runtime.
    The directory for a given animal in the 2P folder for a given project will already
    exist, so this function creates the appropriate structure.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Subject ID value from metadata_args["project"]
        config_template:
            Configuration template gathered for the project by get_template()

    Returns:
        session_path:
            Path that files should be written to after experiment is finished.
    """
    # Gather the date of the day's session
    session_date = datetime.today().strftime("%Y%m%d")

    # Grab appropriate server volume location
    server_location = SERVER_PATHS[project]

    # Create list of elements that compose the session path
    session_elements = ["2p", "raw", subject_id, session_date]

    # Build the session's name and convert to a Pathlib object
    session_path = server_location / Path("/".join(session_elements))

    # Build the session path to the server
    session_path.mkdir(parents=True, exist_ok=True)

    # If a z-stack is scheduled to run, build that directory to the full path
    if config_template["zstack_metadata"]["zstack"]:
        (session_path / "zstacks").mkdir(parents=True, exist_ok=True)

    return session_path


def weight_check(project: str, subject_id: str):
    '''
    Checks subject's weight file for current measurement.

    Some teams want to ensure that their recordings have a weight gathered that
    day. In practice, it can be something that users could forget to do accidentally
    and then be left without that data when they need it. If the project's configuration
    requires users to gather a weight for that day, this function will search for the
    subject's weight file and check if a measurement has been taken.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            Subject ID value from metadata_args["project"]
    '''

    yaml = YAML(typ='safe')

    # Grab appropriate server volume location
    server_location = SERVER_PATHS[project]

    weight_dir = server_location / "subjects" / subject_id

    subject_weight_file = list(weight_dir.glob(f"{subject_id}_weights.yml"))

    # Check to see if the subject has a weight that has been
    # collected on the day of the experiment
    session_date = datetime.today().strftime("%Y%m%d")

    # Check if there's multiple metadata files present for a subject.
    if len(subject_weight_file) > 1:
        raise SubjectError("Multiple weight files found! Check _DATA/project/subjects/subject_id")

    # Otherwise, try to load the one present file. If it's not there,
    # an index error occurs and an exception is raised.
    else:
        try:
            subject_weights = yaml.load(subject_weight_file[0])

        except IndexError:
            raise SubjectError("No subject weight file found! Check _DATA/project/subjects/subject_id")

        # Once it's confirmed there aren't multiple weight files, check that subject has weight
        # recorded for that day. If there's no weight measured, then a KeyError occurs and an
        # exception is raised.
        try:
            weight = subject_weights[session_date]

        # Stating that the exception is raised from 'None' essentially tells Python to ignore
        # previous context of any other exceptions. This behavior makes the error messages in
        # the terminal a little cleaner than before.
        except KeyError:
            raise SubjectError("Subject has no weight recorded! Measure subject's weight before continuing.") from None


def write_yoked_config(subject_type: str, current_plane: int, project: str, experiment_arrays: list):
    """
    Write out yoked configurations for unique plane/subject combinations.

    Yoked trial sets indicate that an entire experimental group will receive the same
    pseudorandom trials. This generates sessions that are far easier to compare between
    mice and also larger N for each dataset for statistical analysis of neural activity
    later. These are written to the local filesystem first and will be copied to the server
    at the end of the day.

    Args:
        subject_type:
            Type of group the subject is a part of, either "experimental" or "control".
        current_plane:
            Which plane number is being currently imaged (i.e. 1, 2, 3)
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        experiment_arrays:
            List of experimental arrays to be sent via pySerialTransfer

    """

    yoked_config = {"beh_metadata": {"trialArray": []}}

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Generate the yoked dataset name
    yoked_name = "_".join([session_date, subject_type,
                        "plane{}".format(current_plane)])

    # Generate Experiment Configuration Directory Path
    yoked_dir = DATA_PATH + project + "/yoked/"

    # Generate the filename
    yoked_filename = "_".join([yoked_name, "yoked"])

    # Append .json for the file
    yoked_filename += ".json"

    # Complete the fullpath for the config file to be written
    yoked_fullpath = yoked_dir + yoked_filename

    # The yoked configuration file will follow the same structure as the
    # configuration file that's output. Although it may seem unnecessary,
    # I decided that consistency between the output .json file for the
    # individual session and the version for the yoked trial sets
    # would make it so it's easy to load either one without having to
    # specify different loading parameters for these different filetypes.
    # Until everyone adopts specialk style metadata format, this duplication
    # of datasets will have to continue.

    # Assign trialArray key to trialArray data.  The 0th index of the list is
    # always the the trialArray
    yoked_config["beh_metadata"]["trialArray"] = experiment_arrays[0]

    # Assign ITIArray key to ITIArray data.  The 1st index of the list is
    # always the ITIArray
    yoked_config["beh_metadata"]["ITIArray"] = experiment_arrays[1]

    # Assign toneArray key the toneArray data.  The 2nd index of the list is
    # always the toneArray.
    yoked_config["beh_metadata"]["toneArray"] = experiment_arrays[2]

    # Assign LEDArray key the LEDArray data. The 3rd index of the list is
    # always the LEDArray.
    yoked_config["beh_metadata"]["LEDArray"] = experiment_arrays[3]

    # Write the completed configuration file
    with open(yoked_fullpath, 'w') as outFile:

        json.dump(yoked_config, outFile)


def check_yoked_config(subject_type: str, current_plane: int, project: str) -> list:
    """
    Checks to see if a yoked trialset already exists for a session.

    If a user wants yoked trial sessions, a check is performed to see if a trial set
    for the given experimental group and given plane has been generated yet. If no
    file is available, a None object is returned and trialsets are generated with
    trial_utils as normal. If a file is available, those experimental arrays are
    loaded and saved as the expeirment_arrays.

    Args:
        subject_type:
            Type of group the subject is a part of, either "experimental" or "control".
        current_plane:
            Which plane number is being currently imaged (i.e. 1, 2, 3)
        project:
            The team and project conducting the experiment (ie teamname_projectname)

    Returns:
        experiment_arrays

    """

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Generate the yoked dataset name
    yoked_name = "_".join([session_date, subject_type,
                        "plane{}".format(current_plane)])

    # Generate Experiment Configuration Directory Path
    yoked_dir = Path(DATA_PATH + project + "/yoked/")

    # Generate the filename
    yoked_filename = "_".join([yoked_name, "yoked"])

    # Append .json for the file
    yoked_filename += ".json"


    yoked_files = list(yoked_dir.glob(yoked_filename))

    # TODO: Explicit checks should be made here to ensure the correct file
    # has been found.
    # If a yoked file is not present, pass None as the experiment arrays
    # so the next step knows to generate them and write them to disk
    if len(yoked_files) != 1:

        experiment_arrays = None

    # If a file is found, load the values into the experiment arrays
    else:

        experiment_arrays = []

        yoked_file = yoked_files[0]

        yoked_config = read_config(yoked_file)

        for key in yoked_config["beh_metadata"].keys():
            experiment_arrays.append(yoked_config["beh_metadata"][key])

    return experiment_arrays
