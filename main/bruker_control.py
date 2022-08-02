# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

__version__ = "1.10.4 Get Yoked"

# Import experiment utils to run different experiments
import experiment_utils

# Import argparse for runtime control
import argparse

# Import pathlib for creating valid choices list for project
from pathlib import Path

#  TODO Use ctrl+c to kill entire program from __main__ if needed
# Import sys for exiting program safely
# import sys

# TODO: Paths to different teams/projects must be static on the machine until
# a better way of polling this is completed. Should try polling the
# file system for available mounted paths or something at some point
# TEAM_PATHS = Path("")

# Static Directory for teams found in SNLKT Server. Until doing this via
# class methods is implemented, having a dictionary for these values is
# necessary... this isn't a great way to do this I don't think...
# VALID_CHOICES = {"specialk_cs": Path("V:/specialk_cs"),
#                 "specialk_lh": Path("U:/specialk_lh")}

# Generate valid team choices for argparser variable project by checking the server for
# valid project names
PROJECT_CHOICES = ["specialk_cs", "specialk_lh", "deryn_fd"]

###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # Create argument parser for metadata configuration
    metadata_parser = argparse.ArgumentParser(
        description='Set Metadata',
        epilog="Good luck on your work!",
        prog='Bruker Experiment Control'
    )

    # Add number of imaging planes argument
    metadata_parser.add_argument(
        '-i', '--imaging_planes',
        type=int,
        action='store',
        dest='imaging_planes',
        help='Number of Imaging Planes (required)',
        required=True
    )

    # Add subject ID argument
    metadata_parser.add_argument(
        '-s', '--subject_id',
        type=str,
        action='store',
        dest='subject_id',
        help='Subject ID (required)',
        required=True
    )

    # Add project flag
    metadata_parser.add_argument(
        '-p', '--project',
        type=str,
        action='store',
        dest='project',
        choices=PROJECT_CHOICES,
        help="Team & Project Name i.e. specialk_cs (required)",
        required=True
    )

    # Add Experimental Condition flag
    # Until there is consistent adoption of subject metadata files,
    # users wishing to use the "yoked" trial settings will have to add
    # this argument to their command line.
    metadata_parser.add_argument(
        '-g', '--group',
        type=str,
        action='store',
        dest='group',
        choices=["exp", "con"],
        help="Subject Group: Experimental vs Control (optional)",
        default=None,
        required=False
    )

    # Add demo flag
    metadata_parser.add_argument(
        '-d', '--demo',
        action='store_true',
        dest='demo',
        help='Use Demonstration Values (bool flag)',
        required=False
        )

    # Add program version argument
    metadata_parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s v. ' + __version__
        )

    # Parse the arguments given by the user
    metadata_args = vars(metadata_parser.parse_args())

    # Run an imaging experiment using the provided arguments by the user
    experiment_utils.run_imaging_experiment(metadata_args)
