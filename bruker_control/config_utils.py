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

# Import sys for exiting program safely
import sys

# Import datetime for generating config file names correctly
from datetime import datetime

# Configuration directories are within project directories.  The server is
# mounted to the X: volume on the machine BRUKER.
config_dir = Path("X:/")

###############################################################################
# Functions
###############################################################################

# Functions expect metadata_args as found in bruker_control.py


def config_parser(metadata_args, plane):

    # Gather project name for use in each case
    project_name = metadata_args['project']

    # Gather status of template flag
    template_flag = metadata_args['template']

    # TODO: Reimplement num_planes properly
    # Gather number of imaging planes to be collected
    # num_planes = metadata_args['imaging_planes']

    # Gather mouse id for naming files
    mouse_id = metadata_args['mouse']

    # If the user doesn't submit a configuration file, but does submit the
    # template flag
    if metadata_args['config'] is None and template_flag is True:

        # Tell the user the program is building from template for their project
        print("Building metadata using template from", project_name)

        config_file, config_filename, config_fullpath = build_config(project_name,
                                                                     template_flag,
                                                                     mouse_id,
                                                                     plane)

        # Get configuration with read_config()
        config = read_config(config_file)

        # Create configuration and video lists
        config_list = [config, config_filename, config_fullpath]
        video_list = [project_name, config_filename, plane]

        # Return the config object for use in next steps
        return config_list, video_list

    # elif metadata_args['config'] is not None and metadata_args['modify'] is True:
    #     Modify configuration function in development...
    #     # TODO: Write config modification functions

    # If the name of a metadata file is given and the user doesn't want to
    # modify it, confirm the file is present.  If the file is present, load
    # its contents.
    elif metadata_args['config'] is not None and metadata_args['modify'] is False:

        # Let user know that the program is looking for the file
        print("Trying to find file...")

        # Use the correct base path for configuration files for the
        # project
        config_basepath = "E:/studies/" + project_name + "/config/"

        # Gather the configuration file name from the config argument
        config_filename = metadata_args['config']

        # Combine the basepath, filename, and extension
        # TODO: Interpret other file types like .csv and then save them as
        # a json file.
        # TODO: Create new argument that allows some other absolute
        # path to import the config file.  This should be discouraged...
        config_fullpath = Path(config_basepath + config_filename + '.json')

        # If there is a file with this name in the correct directory
        if Path.exists(config_fullpath) is True:

            # Tell the user the config file was found
            print("Found config file!")

            # Save the configuration variables as config
            config = read_config(config_fullpath)

        else:
            print("No config found...")
            print("Exiting")
            sys.exit()

        config_list = [config, config_filename, config_fullpath]
        video_list = [project_name, config_filename]

        # Return the config object for use in next steps
        return config_list, video_list

    # If something can't be interpreted in the configuration file,
    # tell the user
    else:
        print("Invalid Configuration File Supplied")


def read_config(config_file):
    with open(config_file, 'r') as inFile:
        contents = inFile.read()

        # Use json.loads to gather metadata and save them in an
        # ordered dictionary for checking if contents are correct
        # during transmission later
        config_contents = json.loads(contents,
                            object_pairs_hook=OrderedDict)

    # Return the config object for use in next steps
    return config_contents


def build_from_template(config_fullpath, project_name):

    # Tell user that they're using template values for the experiment
    print("Using template values for experiment")

    # Gather which configuration to use for the provided project using
    # the configuraiton dictionary above
    project_config = config_dict[project_name]

    # Load config file with template values
    with open(project_config, 'r') as inFile:
        contents = inFile.read()

        # Save template configuration
        template_config = json.loads(contents,
                                     object_pairs_hook=OrderedDict)

    # Write out new config file using the template information
    with open(config_fullpath, 'w') as outFile:

        # Dump template config contents into new config file
        json.dump(template_config, outFile)

    # Return the config file for use in the experiment
    return config_fullpath


def build_from_user(config_fullpath):

    # Ask user for metadata values and force them to be integers
    totalNumberOfTrials = int(input("How many trials do you want to run? "))
    punishTone = int(input("What tone should airpuff stimuli use? (kHz) ")) * 1000
    rewardTone = int(input("What tone should sucrose stimuli use? (kHz) ")) * 1000
    USConsumptionTime_Sucrose = int(input("How long should sucrose be present? (s) ")) * 1000

    # Load config file with empty values
    with open(empty_config_file, 'r') as inFile:
        contents = inFile.read()

        # Save empty configuration
        empty_config = json.loads(contents,
                                  object_pairs_hook=OrderedDict)

        # Update keys in the configuration using user's inputs
        empty_config["metadata"]["totalNumberOfTrials"]["value"] = totalNumberOfTrials
        empty_config["metadata"]["punishTone"]["value"] = punishTone
        empty_config["metadata"]["rewardTone"]["value"] = rewardTone
        empty_config["metadata"]["USConsumptionTime_Sucrose"]["value"] = USConsumptionTime_Sucrose

    # Write config file for session
    with open(config_fullpath, 'w') as outFile:

        # Dump customized template into new config file
        json.dump(empty_config, outFile)

    # Return config file for use in the experiment
    return config_fullpath


def build_config(project_name, template_flag, mouse_id, plane):

    # Create status for duplicate filename.  For now, overwriting is not
    # allowed.  Assume duplicate is occuring unless proven otherwise...
    # TODO: Incorporate a flag or question that lets you overwrite a file
    duplicate_config = True

    # Perform check with while true loop
    while duplicate_config is True:

        # Get todays date with datetime
        session_date = datetime.today().strftime("%Y%m%d")

        # State base path for config file
        config_basepath = "E:/studies/" + project_name + "/config/"

        # Convert num_planes to a string
        plane = str(plane)

        # Assign config file name
        config_filename = session_date + "_" + mouse_id + "_plane" + plane + "_config"

        # Make full filepath for config file
        config_fullpath = Path(config_basepath + config_filename + ".json")

        # Check if there's a file that exists with this name already
        # If there's no file with this name already
        if config_fullpath.exists() is False:

            # Tell the user
            print("Unique filename given")

            # Move on by setting duplicate_config to false
            duplicate_config = False

        # If there's already a file with the same name
        elif config_fullpath.exists() is True:

            # Tell the user and ask for unique filename
            print("File already exists!")
            print("Unique filename is required. Please provide one.")
            print("Exiting...")
            sys.exit()

    # Start building the configuration values.  The user may not know about
    # template flag which might make this section redundant.  Print a help
    # message that informs them about the flag.  Let them customize the
    # different values for the experiment.
    if template_flag is False:
        # Print help message
        print("Note: You can use template values by using the --template flag")

        # Use build_from_user()
        config_file = build_from_user(config_fullpath)

    # If the user did use the --template flag, write a template config file
    elif template_flag is True:

        # Use build_from_template()
        config_file = build_from_template(config_fullpath, project_name)

    return config_file, config_filename, config_fullpath
