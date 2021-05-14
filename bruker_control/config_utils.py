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

# Import glob for searching for files and grabbing relevant configs
import glob

# Import sys for exiting program safely
import sys

# Import datetime for generating config file names correctly
from datetime import datetime

# Static template file location
template_config_file = r"../configs/templatevalues.json"

# Static empty json file location
empty_config_file = r"../configs/templateempty.json"

###############################################################################
# Functions
###############################################################################
# Functions expect metadata_args as found in bruker_control.py


def read_config(config_file):
    with open(config_file, 'r') as inFile:
        contents = inFile.read()

        # Use json.loads to gather metadata and save them in an
        # ordered dictionary for checking if contents are correct
        # during transmission later
        config = json.loads(contents,
                            object_pairs_hook=OrderedDict)

    # Return the config object for use in next steps
    return config


def build_from_template(config_fullpath):

    # Tell user that they're using template values for the experiment
    print("Using template values for experiment")

    # Load config file with template values
    with open(template_config_file, 'r') as inFile:
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
    # Print help message
    print("Note: You can use template values by using the --template flag")

    # Ask user for metadata values
    totalNumberOfTrials = input("How many trials do you want to run? ")
    punishTone = input("What tone should airpuff stimuli use? (kHz) ") * 1000
    rewardTone = input("What tone should sucrose stimuli use? (kHz) ") * 1000
    USConsumptionTime_Sucrose = input("How long should sucrose be present? (s) ") * 1000

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


def build_config(metadata_args):

    # Get todays date with datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Get the project name from user's input
    project_name = metadata_args['project']

    # State base path for config file
    config_basepath = "E:/studies/" + project_name + "/config/"

    # Ask user for mouse ID and convert it to a string
    mouse_id = str(input("Mouse ID: "))

    # Assign config file name
    config_filename = session_date + "_" + mouse_id

    # Make full filepath for config file
    config_fullpath = config_basepath + config_filename + ".json"

    # Start building the configuration values.  The user may not know about
    # template flag which might make this section redundant.  Print a help
    # message that informs them about the flag.  Let them customize the
    # different values for the experiment.
    if metadata_args['template'] is False:

        # Use build_from_user()
        config_file = build_from_user(config_fullpath)

    # If the user did use the --template flag, write a template config file
    elif metadata_args['template'] is True:

        # Use build_from_template()
        config_file = build_from_template(config_fullpath)

    return config_file


def config_parser(metadata_args):

    # If the user doesn't submit a configuration file
    if metadata_args['config'] is None:

        # Tell the user there was not metadata file provided
        print("No metadata file provided")

        # By default, it will be assumed the user would like to make a config.
        # Set a make_metadata status as true.  However, just in case, let the
        # user confirm if they want to.
        make_metadata = True

        # Use a while loop to ask for user input
        while make_metadata is True:

            # Ask the user if they want to make the file with input()
            user_choice = input("Do you want to create a metadata file? y/n ")

            # If the user replies with 'y', enter new_metadata() function
            if user_choice == 'y':
                config_file = build_config(metadata_args)
                config = read_config(config_file)

                make_metadata = False

            # If the user replies with 'n', tell user metadata is needed and
            # then exit the program
            elif user_choice == 'n':
                print("Experiment requires metadata to run.")
                print("Exiting...")
                sys.exit()

            # If the user doesn't give appropriate response, tell them and
            # let them try again.
            else:
                print("Only 'y' and 'n' are acceptable options.")

        return config

    # elif metadata_args['config'] is not None and metadata_args['modify'] is True:
    #     Modify configuration function in development...
    #     # TODO: Write config modification functions

    # If the name of a metadata file is given and the user doesn't want to
    # modify it, confirm the file is present.  If the file is present, load
    # its contents.
    elif metadata_args['config'] is not None and metadata_args['modify'] is False:

        # Let user know that the program is looking for the file
        print("Trying to find file...")

        # If the project argument is in list of known projects, here specialk
        project_name = metadata_args['project']

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
        config_fullpath = config_basepath + config_filename + '.json'

        # If there is a file with this name in the correct directory
        if glob.glob(config_fullpath) is not None:

            config = read_config(config_fullpath)

            # Return the config object for use in next steps
            return config

        # If something can't be interpreted, tell the user
    else:
        print("Invalid Configuration File Supplied")