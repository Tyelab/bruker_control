# Bruker 2-Photon Experiment Utils
# Jeremy Delahanty May 2021

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

# Import the Flight Manifest GUI
import flight_manifest

# Import sys to safely exit
import sys

# Import multiprocessing for async writing of video to disk
import multiprocessing

# TODO: Move to next plane, create mouse configuration that defines planes of
# interest and distance between them


def run_imaging_experiment(metadata_args):

    # Gather project information
    project = metadata_args["project"]

    # Gather number of planes to image
    requested_planes = metadata_args["imaging_planes"]

    # Get value of subject's experimental/control type
    group_type = metadata_args["group"]
    
    # Get which mice are being imaged that day
    passengers = flight_manifest.run(project)

    # TODO: Unite all these functions into one call and build a
    # metadata Class that contains each of these things in it.  This will
    # require a significant refactor to transition everything into using
    # class objects throughout the system.
    # Get configuration template with config_utils.get_template
    config_template = config_utils.get_template(project)

    # Use new Arduino class to verify and upload available Arduino sketches
    # automatically
    serialtransfer_utils.upload_arduino_sketch(project)

    # TODO: After updating how weights are represented, this should
    # basically tell the user to input a weight (in kg? maybe just g
    # and conver to NWB for them later...) and then append that to
    # the weights information
    # if config_template["weight_check"]:

    #     config_utils.weight_check(project, subject_id)

    # Get Z-Stack metadata
    zstack_metadata = config_utils.get_zstack_metadata(config_template)

    # Connect to Prairie View
    prairieview_utils.pv_connect()

    # Run experiments for each subject contained on the flight manifest.
    for subject_id in passengers:

        print("Conducting Experiment for Subject: ", subject_id)

        # Build the server directory for this recording
        config_utils.build_server_directory(
            project,
            subject_id,
            config_template
            )

        # Only team specialk has the necessary infrastructure for running
        # z-stacks.  Any user that wants to run a z-stack for their data must
        # comply with Specialk-style metadata which is intended to be required
        # for using bruker_control moving forward.
        if "specialk" in project:
            # Get subject metadata
            subject_metadata = config_utils.get_subject_metadata(
                project,
                subject_id
                )

            # Get surgery metadata
            surgery_metadata = config_utils.get_surgery_metadata(subject_metadata)

        else:
            surgery_metadata = None

        # Get metadata that the Arduino requires
        arduino_metadata = config_utils.get_arduino_metadata(config_template)

        # Create experiment running flag
        exp_running = True

        # Initialize number of completed imaging planes at value of 1, to be
        # incremented later if necessary
        current_plane = 1

        while exp_running:

            # TODO: Make this into one united function contained within config_utils
            # If the user specified using yoked trial sets
            if config_template["beh_metadata"]["yoked"]:

                # Check to see if there is currently a yoked trial set available
                experiment_arrays = config_utils.check_yoked_config(
                    group_type,
                    current_plane,
                    project
                    )

                # If experiment arrays is None, that means there are no yoked trials available for this
                # plane for this experimental condition. Generate the trial arrays and then write them
                # to disk
                if experiment_arrays == None:

                    experiment_arrays = trial_utils.generate_arrays(config_template)

                    config_utils.write_yoked_config(
                        group_type,
                        current_plane,
                        project,
                        experiment_arrays
                        )

            # If the user does not choose to use yoked trials, generate a new trial set
            else:
                # Create experiment runtime arrays
                experiment_arrays = trial_utils.generate_arrays(config_template)
                print(experiment_arrays)

            # Calculate session length in seconds
            session_len_s = trial_utils.calculate_session_length(experiment_arrays)

            # Start preview of animal's face.  Zero microscope over lens here.
            video_utils.capture_preview(
                project,
                subject_id
            )

            imaging_plane = prairieview_utils.get_imaging_plane()

            if zstack_metadata["zstack"]:
                prairieview_utils.zstack(
                    zstack_metadata,
                    project,
                    subject_id,
                    current_plane,
                    imaging_plane,
                    surgery_metadata
                )

            # Once the Z-Stack is collected (if requested), start the T-Series
            prairieview_utils.tseries(
                project,
                subject_id,
                current_plane,
                imaging_plane,
                surgery_metadata
                )

            # Get microscope's framerate:
            framerate = prairieview_utils.get_microscope_framerate()

            # Calculate number of frames
            num_frames = video_utils.calculate_frames(
                session_len_s,
                framerate
                )

            # Now that the Bruker scope is ready and waiting, send the data to
            # the Arduino through pySerialTransfer
            serialtransfer_utils.transfer_data(
                arduino_metadata,
                experiment_arrays
                )

            dropped_frames = video_utils.capture_recording(
                framerate,
                num_frames,
                current_plane,
                str(imaging_plane),
                project,
                subject_id
            )

            prairieview_utils.end_tseries()

            config_utils.write_experiment_config(
                config_template,
                experiment_arrays,
                dropped_frames,
                project,
                subject_id,
                str(imaging_plane),
                current_plane
            )

            if current_plane == requested_planes:

                print("Experiment Completed for", subject_id)

                exp_running = False

            else:
                current_plane += 1

    # Disconnect from Prairie View and end the experiments for the day
    prairieview_utils.pv_disconnect()

    print("Exiting...")
    sys.exit()
