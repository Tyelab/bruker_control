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

# Get current working directory for above paths to work
current_dir = Path.cwd()

# Static template file location
template_config_file = current_dir.joinpath("Documents/gitrepos/headfix_control/configs/templatevalues.json")

# Static empty json file location
empty_config_file = current_dir.joinpath("Documents/gitrepos/headfix_control/configs/templateempty.json")

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


def build_config(project_name, template_flag):

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

        # Ask user for mouse ID and convert it to a string
        mouse_id = str(input("Mouse ID: "))

        # Assign config file name
        config_filename = session_date + "_" + mouse_id

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

    # Start building the configuration values.  The user may not know about
    # template flag which might make this section redundant.  Print a help
    # message that informs them about the flag.  Let them customize the
    # different values for the experiment.
    if template_flag is False:

        # Use build_from_user()
        config_file = build_from_user(config_fullpath)

    # If the user did use the --template flag, write a template config file
    elif template_flag is True:

        # Use build_from_template()
        config_file = build_from_template(config_fullpath)

    return config_file, config_filename


def config_parser(metadata_args):

    # Gather project name for use in each case
    project_name = metadata_args['project']

    # Gather status of template flag
    template_flag = metadata_args['template']

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
                config_file, config_filename = build_config(project_name,
                                                            template_flag)
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

        return config, project_name, config_filename

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

        # Return the config object for use in next steps
        return config, project_name, config_filename

        # If something can't be interpreted, tell the user
    else:
        print("Invalid Configuration File Supplied")
