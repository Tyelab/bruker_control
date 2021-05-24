# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

# Version Number
__version__ = "0.70"

###############################################################################
# Import Packages
###############################################################################

# -----------------------------------------------------------------------------
# Custom Modules: Bruker Control
# -----------------------------------------------------------------------------
# Import config_utils functions for manipulating config files
import config_utils

# Import video_utils functions for using Harvesters for camera
import video_utils

# Import serialtransfer_utils for transmitting information to Arduino
import serialtransfer_utils

# Import trial_utils for generating random trials
import trial_utils

# Import prairieview_utils for interacting with Bruker
import prairieview_utils

# -----------------------------------------------------------------------------
# Python Libraries
# -----------------------------------------------------------------------------
# Import argparse if you want to create a configuration on the fly
import argparse

# Import sys for exiting program safely
import sys


###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # Create argument parser for metadata configuration
    metadata_parser = argparse.ArgumentParser(description='Set Metadata',
                                              epilog="Good luck on your work!",
                                              prog='Bruker Experiment Control')

    # Add configuration file argument
    metadata_parser.add_argument('-c', '--config_file',
                                 type=str,
                                 action='store',
                                 dest='config',
                                 help='Config Filename (yyyymmdd_animalid)',
                                 default=None,
                                 required=False)

    # Add modify configuration file argument
    # metadata_parser.add_argument('-m', '--modify',
    #                              action='store_true',
    #                              dest='modify',
    #                              help='Modify given config file (bool flag)',
    #                              required=False)

    # Add template configuration file argument
    metadata_parser.add_argument('-t', '--template',
                                 action='store_true',
                                 dest='template',
                                 help='Use template config file (bool flag)',
                                 required=False)

    # Add project name argument
    metadata_parser.add_argument('-p', '--project',
                                 type=str,
                                 action='store',
                                 dest='project',
                                 help='Project Name (required)',
                                 choices=['specialk', 'food_dep'],
                                 required=True)

    # Add number of imaging planes argument
    # metadata_parser.add_argument('-i', '--imaging_planes',
    #                              type=int,
    #                              action='store',
    #                              dest='imaging_planes',
    #                              help='Number of Imaging Planes',
    #                              default=1,
    #                              required=False)

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

    # Add program version argument
    metadata_parser.add_argument('--version',
                                 action='version',
                                 version='%(prog)s v. ' + __version__)

    # Parse the arguments given by the user
    metadata_args = vars(metadata_parser.parse_args())

    # Gather number of planes that will be collected for this mouse, ask user
    number_img_planes = int(input("How many planes will you image? "))

    # Create ready flag for whether or not user is ready to move forward with
    # experiment plane
    ready = False

    # Create experiment running flag to keep experiment session running
    exp_running = True

    # Initialize current plane at value of 0, to be incremented later
    current_plane = 0

    # Initialize number of completed imaging planes at value of 1, to be
    # incremented later if necessary
    completed_planes = 1

    while exp_running is True:

        while ready is False:

            ready_input = str(input("Ready to continue? y/n "))

            if ready_input == "y":
                current_plane += 1

                # Use config_utils module to parse metadata_config
                config_list, video_list = config_utils.config_parser(metadata_args,
                                                                     current_plane)

                # Grab status of template flag for demonstration ITIs
                demo_flag = metadata_args['demo']

                prairieview_utils.prairie_dir_and_filename(video_list[0],
                                                           config_list[1])

                # TODO: Let user change configurations on the fly with parser

                # Gather total number of trials
                trials = config_list[0]["metadata"]["totalNumberOfTrials"]["value"]

                # Generate trial arrays
                array_list, video_frames = trial_utils.generate_arrays(trials,
                                                                       config_list[2],
                                                                       demo_flag)

                # Preview video for headfixed mouse placement
                video_utils.capture_preview()

                prairieview_utils.start_tseries()

                # If only one packet is required, use single packet generation
                # and transfer.  Single packets are all that's needed for sizes
                # less than or equal to 60.
                if trials <= 60:

                    # Send configuration file
                    serialtransfer_utils.transfer_metadata(config_list[0])

                    # Use single packet serial transfer for arrays
                    serialtransfer_utils.onepacket_transfers(array_list)

                    # Send update that python is done sending data
                    serialtransfer_utils.update_python_status()

                    # Now that the packets have been sent, the Arduino will
                    # start soon.  We now start the camera for recording the
                    # experiment!
                    # video_utils.capture_recording(video_frames, video_list)
                    video_utils.capture_recording(60, video_list)

                    # Now that the microscopy session has ended, let user know
                    # the plane is complete!
                    print("Plane Completed!")

                    # Abort this plane's recording
                    prairieview_utils.prairie_abort()

                    if completed_planes == number_img_planes:

                        # Experiment completed! Tell the user that this mouse
                        # is done.
                        print("Experiment Completed for",
                              metadata_args['mouse'])

                        # Tell the user the program is exiting and exit
                        print("Exiting...")
                        sys.exit()

                    else:
                        completed_planes += 1

                # If there's multiple packets required, use multipacket generation and
                # transfer.  Multiple packets are required for sizes greater than 60.
                elif trials > 60:

                    # Send configuration file
                    serialtransfer_utils.transfer_metadata(config_list[0])

                    # Use multipacket serial transfer for arrays
                    serialtransfer_utils.multipacket_transfer(array_list)

                    # Send update that python is done sending data
                    serialtransfer_utils.update_python_status()

                    # Now that the packets have been sent, the Arduino will start soon.  We
                    # now start the camera for recording the experiment!
                    # video_utils.capture_recording(60, project_name, config_filename)

                    # End Prairie View's imaging session with abort command
                    # prairieview_utils.prairie_abort()

                    # Now that the microscopy session has ended, let user know the
                    # experiment is complete!
                    print("Experiment Over!")

                    # Exit the program
                    print("Exiting...")
                    sys.exit()

                # If some other value that doesn't fit in these categories is
                # given, there is something wrong with the configuration file.
                # Let the user know and exit the program.
                else:
                    print("Something is wrong with the config file...")
                    print("Exiting...")
                    sys.exit()
