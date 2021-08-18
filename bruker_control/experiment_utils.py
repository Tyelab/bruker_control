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


def run_imaging_experiment(metadata_args):

    # Gather subject_id
    subject_id = metadata_args["subject_id"]

    # Gather team information
    team = metadata_args["team"]

    # Gather number of planes to image
    requested_planes = metadata_args["imaging_planes"]

    # Create experiment running flag
    exp_running = True

    # Initialize current plane at value of 0, to be incremented later
    current_plane = 0

    # Initialize number of completed imaging planes at value of 1, to be
    # incremented later if necessary
    completed_planes = 1

    while exp_running is True:

        # Get configuration template with config_utils.get_template
        config_template = config_utils.get_template(team)

        # Get metadata that the Arduino requires
        arduino_metadata = config_utils.get_arduino_metadata(config_template)

        # Create experiment runtime arrays
        experiment_arrays = trial_utils.generate_arrays(config_template)

        # Calculate session length in seconds
        session_len_s = trial_utils.calculate_session_length(experiment_arrays,
                                                             config_template)

        # Calculate number of frames
        num_frames = video_utils.calculate_frames(session_len_s)

        # Start preview of animal's face and then zero microscope over lens
        # video_utils.capture_preview()

        # Once the preview is escaped, start the microscopy session.
        # imaging_plane = prairieview_utils.start_microscopy_session(team,
        #                                                            subject_id)
        imaging_plane = 280
        # Now that the Bruker scope is ready and waiting, send the data to
        # the Arduino through pySerialTransfer!
        # serialtransfer_utils.transfer_data(arduino_metadata, experiment_arrays)

        # Now that the packets have been sent, the Arduino will start soon.
        # We now start the camera for recording the experiment!
        dropped_frames = video_utils.capture_recording(num_frames,
                                                       imaging_plane,
                                                       team, subject_id)

        break


        #     # Send configuration file
        #     serialtransfer_utils.transfer_metadata(config_list[0])
        #
        #     # Use single packet serial transfer for arrays
        #     serialtransfer_utils.onepacket_transfers(array_list)
        #
        #     # Send update that python is done sending data
        #     serialtransfer_utils.update_python_status()
        #
        #     video_utils.capture_recording(video_frames, video_list)
        #     # video_utils.capture_recording(60, video_list)
        #
        #     # Now that the microscopy session has ended, let user know
        #     # the plane is complete!
        #     print("Plane Completed!")
        #
        #     # Abort this plane's recording
        #     prairieview_utils.prairie_abort()
        #
        #     # TODO: Move to next plane, create mouse configuration
        #     # that defines planes of interest and distance between them
        #
        #     if completed_planes == requested_planes:
        #
        #         # Experiment completed! Tell the user that this mouse
        #         # is done.
        #         print("Experiment Completed for",
        #               metadata_args['mouse'])
        #
        #         # Tell the user the program is finished and exit
        #         print("Exiting...")
        #         sys.exit()
        #
        #     else:
        #         completed_planes += 1
