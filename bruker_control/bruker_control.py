# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021, Deryn LeDuke July 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

# Version Number
__version__ = "0.74"

###############################################################################
# Import Packages
###############################################################################

# -----------------------------------------------------------------------------
# Custom Modules: Bruker Control
# -----------------------------------------------------------------------------
# Import experiment utils to run different experiments
import experiment_utils


# -----------------------------------------------------------------------------
# Python Libraries
# -----------------------------------------------------------------------------
# Import argparse for runtime control
import argparse

# Import pathlib for creating valid choices list for project
from pathlib import Path

#  TODO Use ctrl+c to kill entire program from __main__ if needed
# Import sys for exiting program safely
# import sys


###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # Dynamically generate available projects by globbing raw data study
    # directory.
    team_choices = [team for team in Path("E:/").glob("*") if team.is_dir()]

    project_choices = [project for project in team_choices.glob("*") if
                       project.is_dir()]

    # Create argument parser for metadata configuration
    metadata_parser = argparse.ArgumentParser(description='Set Metadata',
                                              epilog="Good luck on your work!",
                                              prog='Bruker Experiment Control')

    # Add configuration file argument [DEPRECATED]
    # Will use provided project choice for finding appropriate config file
    # metadata_parser.add_argument('-c', '--config_file',
    #                              type=str,
    #                              action='store',
    #                              dest='config',
    #                              help='Config Filename (yyyymmdd_animalid)',
    #                              default=None,
    #                              required=False)

    # Add modify configuration file argument [DEPRECATED]
    # metadata_parser.add_argument('-m', '--modify',
    #                              action='store_true',
    #                              dest='modify',
    #                              help='Modify given config file (bool flag)',
    #                              required=False)

    # Add template configuration file argument [DEPRECATED]
    # Using template for a given experiment is done by default
    # metadata_parser.add_argument('-t', '--template',
    #                              action='store_true',
    #                              dest='template',
    #                              help='Use template config file (bool flag)',
    #                              required=False)

    # Add project name argument
    metadata_parser.add_argument('-p', '--project',
                                 type=str,
                                 action='store',
                                 dest='project',
                                 help='Project Name (required)',
                                 choices=project_choices,
                                 required=True)

    # Add number of imaging planes argument
    metadata_parser.add_argument('-i', '--imaging_planes',
                                 type=int,
                                 action='store',
                                 dest='imaging_planes',
                                 help='Number of Imaging Planes',
                                 default=None,
                                 required=True)

    # Add mouse id argument
    metadata_parser.add_argument('-m', '--mouse_id',
                                 type=str,
                                 action='store',
                                 dest='mouse',
                                 help='Mouse ID (required)',
                                 required=True)

    # Add demo flag
    metadata_parser.add_argument('-d', '--demo',
                                 action='store_true',
                                 dest='demo',
                                 help='Use Demonstration Values (bool flag)',
                                 required=False)

    # Add behavior_only flag [DEPRECATED]
    # People should NOT be using the behavior only flag
    # metadata_parser.add_argument('-b', '--behavior',
    #                              action='store_true',
    #                              dest='behavior',
    #                              help='Perform behavior ONLY (bool flag)',
    #                              required=False)

    # Add sucrose_only flag [DEPRECATED]
    # Handled now with more descriptive configuration file
    # metadata_parser.add_argument('-s', '--sucrose',
    #                              action='store_true',
    #                              dest='sucrose',
    #                              help='Give ONLY sucrose trials (bool flag)',
    #                              required=False)

    # Add program version argument
    metadata_parser.add_argument('--version',
                                 action='version',
                                 version='%(prog)s v. ' + __version__)

    # Parse the arguments given by the user
    metadata_args = vars(metadata_parser.parse_args())

    # Run an imaging experiment using the provided arguments by the user
    experiment_utils.imaging_experiment_onepacket(metadata_args)

                # # If there's multiple packets required, use multipacket generation and
                # # transfer.  Multiple packets are required for sizes greater than 60.
                # elif trials > 60:
                #
                #     # Send configuration file
                #     serialtransfer_utils.transfer_metadata(config_list[0])
                #
                #     # Use multipacket serial transfer for arrays
                #     serialtransfer_utils.multipacket_transfer(array_list)
                #
                #     # Send update that python is done sending data
                #     serialtransfer_utils.update_python_status()
                #
                #     # Now that the packets have been sent, the Arduino will start soon.  We
                #     # now start the camera for recording the experiment!
                #     # video_utils.capture_recording(60, project_name, config_filename)
                #
                #     # End Prairie View's imaging session with abort command
                #     # prairieview_utils.prairie_abort()
                #
                #     # Now that the microscopy session has ended, let user know the
                #     # experiment is complete!
                #     print("Experiment Over!")
                #
                #     # Exit the program
                #     print("Exiting...")
                #     sys.exit()

                # If some other value that doesn't fit in these categories is
                # given, there is something wrong with the configuration file.
                # Let the user know and exit the program.
