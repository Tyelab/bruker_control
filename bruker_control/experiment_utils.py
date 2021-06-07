# Bruker 2-Photon Experiment Utils
# Jeremy Delahanty May 2021

###############################################################################
# Import Packages
###############################################################################
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

# Import sys to safely exit
import sys

###############################################################################
# Functions
###############################################################################


def imaging_experiment_onepacket(metadata_args):

    # Collect project name from arguments
    project_name = metadata_args["project"]

    # Collect sucrose_only flag
    sucrose_only_flag = metadata_args["sucrose"]

    # Gather number of planes that will be collected for this mouse
    # If no input argument, ask the user
    if metadata_args["imaging_planes"] is None:
        number_img_planes = int(input("How many planes will you image? "))

    # If they did supply a number of planes to obtain, use the value
    else:
        number_img_planes = metadata_args["imaging_planes"]

    # Create ready flag for whether or not user is ready to move forward with
    # experiment plane
    ready = False

    # Create experiment running flag
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
                                                                       demo_flag,
                                                                       sucrose_only_flag,
                                                                       project_name)

                # Preview video for headfixed mouse placement
                video_utils.capture_preview()

                # Start the T-Series which waits for a trigger from Arduino
                prairieview_utils.prairie_start_tseries()

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
                    video_utils.capture_recording(video_frames, video_list)
                    # video_utils.capture_recording(60, video_list)

                    # Now that the microscopy session has ended, let user know
                    # the plane is complete!
                    print("Plane Completed!")

                    # Abort this plane's recording
                    prairieview_utils.prairie_abort()

                    # TODO: Move to next plane, create mouse configuration
                    # that defines planes of interest and distance between them

                    if completed_planes == number_img_planes:

                        # Experiment completed! Tell the user that this mouse
                        # is done.
                        print("Experiment Completed for",
                              metadata_args['mouse'])

                        # Tell the user the program is finished and exit
                        print("Exiting...")
                        sys.exit()

                    else:
                        completed_planes += 1


def behavior_experiment_onepacket(metadata_args):

    # Gather behavior_only flag
    behavior_flag = metadata_args["behavior"]

    # Gather project name
    project_name = metadata_args["project"]

    # Collect sucrose_only flag
    sucrose_only_flag = metadata_args["sucrose"]

    # Create ready flag for whether or not user is ready to move forward with
    # experiment plane
    ready = False

    # Create experiment running flag
    exp_running = True

    while exp_running is True:

        while ready is False:

            ready_input = str(input("Ready to continue? y/n "))

            current_plane = 0

            if ready_input == "y":
                # Use config_utils module to parse metadata_config
                config_list, video_list = config_utils.config_parser(metadata_args,
                                                                     current_plane)

                # Grab status of template flag for demonstration ITIs
                demo_flag = metadata_args['demo']

                # BUG: Prairie View doesn't yet allow for me to set unique
                # voltage recording directory that's independent from the
                # microscopy filepath. Likely needs Prairie View 5.6 release
                # expected in early July.
                prairieview_utils.prairie_dir_and_filename(video_list[0],
                                                           config_list[1],
                                                           behavior_flag)

                # TODO: Let user change configurations on the fly with parser

                # Gather total number of trials
                trials = config_list[0]["metadata"]["totalNumberOfTrials"]["value"]

                # Generate trial arrays
                array_list, video_frames = trial_utils.generate_arrays(trials,
                                                                       config_list[2],
                                                                       demo_flag,
                                                                       sucrose_only_flag,
                                                                       project_name)

                # Preview video for headfixed mouse placement
                video_utils.capture_preview()

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
                    video_utils.capture_recording(video_frames, video_list,
                                                  behavior_flag)
                    # video_utils.capture_recording(60, video_list)

                    # Abort the voltage recording
                    prairieview_utils.prairie_abort()

                    # Experiment completed! Tell the user that this mouse
                    # is done.
                    print("Experiment Completed for",
                          metadata_args['mouse'])

                    # Tell the user the program is finished and exit
                    print("Exiting...")
                    sys.exit()
