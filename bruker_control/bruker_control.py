# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021, Deryn LeDuke July 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

__version__ = "0.50"

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

# Import datetime for generating config file names correctly
# from datetime import datetime
# from dateutil.tz import tzlocal

#  TODO Use ctrl+c to kill entire program from __main__ if needed
# Import sys for exiting program safely
# import sys

# Static Directory for teams directory in Raw Data, drive E:
teams_path = Path("Y:/bruker_refactor_testing")

# Generate valid team choices for argparser variable "team" by checking the
# directories on the server
team_choices = [team.name for team in teams_path.glob("*")]

###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # Create argument parser for metadata configuration
    metadata_parser = argparse.ArgumentParser(description='Set Metadata',
                                              epilog="Good luck on your work!",
                                              prog='Bruker Experiment Control')

    # Add team name argument
    metadata_parser.add_argument('-t', '--team',
                                 type=str,
                                 action='store',
                                 dest='team',
                                 help='Team Name (required)',
                                 choices=team_choices,
                                 required=True)

    # Add number of imaging planes argument
    metadata_parser.add_argument('-i', '--imaging_planes',
                                 type=int,
                                 action='store',
                                 dest='imaging_planes',
                                 help='Number of Imaging Planes (required)',
                                 default=None,
                                 required=True)

    # Add mouse id argument
    metadata_parser.add_argument('-s', '--subject_id',
                                 type=str,
                                 action='store',
                                 dest='subject_id',
                                 help='Subject ID (required)',
                                 required=True)

    # Add demo flag
    metadata_parser.add_argument('-d', '--demo',
                                 action='store_true',
                                 dest='demo',
                                 help='Use Demonstration Values (bool flag)',
                                 required=False)

    # Add program version argument
    metadata_parser.add_argument('--version',
                                 action='version',
                                 version='%(prog)s v. ' + __version__)

    # Parse the arguments given by the user
    metadata_args = vars(metadata_parser.parse_args())

    # Run an imaging experiment using the provided arguments by the user
    experiment_utils.run_imaging_experiment(metadata_args)
