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

# Import nwb_utils for writing out base level NWB File
import nwb_utils

# Import sys to safely exit
import sys

###############################################################################
# Functions
###############################################################################

# TODO: Move to next plane, create mouse configuration that defines planes of
# interest and distance between them


def run_imaging_experiment(metadata_args):

    # Gather subject_id
    subject_id = metadata_args["subject_id"]

    # Gather team information
    team = metadata_args["team"]

    # Gather experimenter information
    experimenter = metadata_args["experimenter"]

    # Gather number of planes to image
    requested_planes = metadata_args["imaging_planes"]

    # Create experiment running flag
    exp_running = True

    # Initialize number of completed imaging planes at value of 1, to be
    # incremented later if necessary
    current_plane = 1

    while exp_running is True:

        print("Gathering metadata...")
        # TODO: Unite all these functions into one call and build a
        # metadata Class that contains each of these things in it.  This will
        # require a significant refactor to transition everything into using
        # class objects throughout the system.
        # Get configuration template with config_utils.get_template
        config_template = config_utils.get_template(team)

        if team == "specialk":
            # Get project metadata
            project_metadata = config_utils.get_project_metadata(team, subject_id)

            # Get subject metadata
            subject_metadata = config_utils.get_subject_metadata(team, subject_id)

            # Get surgery metadata
            surgery_metadata = config_utils.get_surgery_metadata(subject_metadata)

            # Get Z-Stack metadata
            zstack_metadata = config_utils.get_zstack_metadata(config_template)

        # Get metadata that the Arduino requires
        arduino_metadata = config_utils.get_arduino_metadata(config_template)

        print("Metadata collected!")

        # Create experiment runtime arrays
        experiment_arrays = trial_utils.generate_arrays(config_template)

        # Calculate session length in seconds
        session_len_s = trial_utils.calculate_session_length(
            experiment_arrays,
            config_template
        )

        # Calculate number of frames
        num_frames = video_utils.calculate_frames(session_len_s)

        # Connect to Prairie View
        prairieview_utils.pv_connect()

        # Start preview of animal's face.  Zero microscope over lens here.
        video_utils.capture_preview()

        imaging_plane = prairieview_utils.get_imaging_plane()

        if zstack_metadata["zstack"]:
            prairieview_utils.zstack(
                zstack_metadata,
                team,
                subject_id,
                current_plane,
                imaging_plane,
                surgery_metadata
            )

        # Once the Z-Stack is collected (if requested), start the T-Series
        prairieview_utils.tseries(
            team,
            subject_id,
            current_plane,
            imaging_plane,
            surgery_metadata
       )

        # Now that the Bruker scope is ready and waiting, send the data to
        # the Arduino through pySerialTransfer
        serialtransfer_utils.transfer_data(arduino_metadata, experiment_arrays)

        # Now that the packets have been sent, the Arduino will start soon.
        # We now start the camera for recording the experiment!
        dropped_frames = video_utils.capture_recording(
                            num_frames,
                            current_plane,
                            str(imaging_plane),
                            team,
                            subject_id
                            )

        config_utils.write_experiment_config(
            config_template,
            experiment_arrays,
            dropped_frames,
            team,
            subject_id,
            imaging_plane,
            current_plane
            )

        prairieview_utils.end_tseries()

        if current_plane == requested_planes:

            print("Experiment Completed for", subject_id)

            # Disconnect from Prairie View
            prairieview_utils.pv_disconnect()
            exp_running = False

        else:
            current_plane += 1

    if team == "specialk":

        nwb_utils.build_nwb_file(
            experimenter,
            team,
            subject_id,
            imaging_plane,
            subject_metadata,
            project_metadata,
            surgery_metadata
        )

        print("Exiting...")
        sys.exit()

    else:
        print("Exiting...")
        sys.exit()
