# Bruker 2-Photon Video Utils
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters

###############################################################################
# Import Packages
###############################################################################

# Teledyne DALSA Genie Nano Interface: Harvesters
from harvesters.core import Harvester

# Other Packages
# Import OpenCV2 to write images/videos to file + previews
import cv2

# Static cti file location
cti_filepath = "C:/Program Files/MATRIX VISION/mvIMPACT Acquire/bin/x64/mvGENTLProducer.cti"

###############################################################################
# Camera Control
###############################################################################

# -----------------------------------------------------------------------------
# Initiate Preview Camera
# -----------------------------------------------------------------------------


def init_camera_preview():
    camera = None

    # Setup Harvester
    # Create harvester object as h
    h = Harvester()

    # Give path to GENTL producer
    cti_file = cti_filepath

    # Add GENTL producer to Harvester object
    h.add_file(cti_file)

    # Update Harvester object
    h.update()

    # Print device list to make sure camera is present
    print("Connected to Camera: \n", h.device_info_list)

    # Grab Camera, Change Settings
    # Create image_acquirer object for Harvester, grab first (only) device
    camera = h.create_image_acquirer(0)

    # Gather node map to camera properties
    n = camera.remote_device.node_map

    # Save camera width and height parameters
    width = n.Width.value
    height = n.Height.value

    # Change camera properties for continuous recording, no triggers needed
    n.AcquisitionMode.value = "Continuous"
    n.TriggerMode.value = "Off"

    print("Preview Mode: ", n.AcquisitionMode.value)

    # Start the acquisition, return camera and harvester for buffer
    print("Starting Preview")
    camera.start_acquisition()

    return h, camera, width, height


# -----------------------------------------------------------------------------
# Capture Preview of Camera
# -----------------------------------------------------------------------------


def capture_preview():
    h, camera, width, height = init_camera_preview()
    preview_status = True
    print("To stop preview, hit 'Esc' key")
    while preview_status is True:
        try:
            with camera.fetch_buffer() as buffer:
                # Define frame content with buffer.payload
                content = buffer.payload.components[0].data.reshape(height,
                                                                    width)

                # Provide preview for camera contents:
                cv2.imshow("Preview", content)
                c = cv2.waitKey(1) % 0x100
                if c == 27:
                    preview_status = False
        except:
            print("Frame Dropped/Packet Loss")
            pass

    cv2.destroyAllWindows()

    # Shutdown the camera
    shutdown_camera(camera, h)


# -----------------------------------------------------------------------------
# Initialize Camera for Recording
# -----------------------------------------------------------------------------


def init_camera_recording():
    camera = None

    # Setup Harvester
    # Create harvester object as h
    h = Harvester()

    # Give path to GENTL producer
    cti_file = cti_filepath

    # Add GENTL producer to Harvester object
    h.add_file(cti_file)

    # Update Harvester object
    h.update()

    # Print device list to make sure camera is present
    print("Connected to Camera: \n", h.device_info_list)

    # Grab Camera, Change Settings
    # Create image_acquirer object for Harvester, grab first (only) device
    camera = h.create_image_acquirer(0)

    # Gather node map to camera properties
    n = camera.remote_device.node_map

    # Set and then save camera width and height parameters
    width = n.Width.value  # width = 1280
    height = n.Height.value  # height = 1024

    # Change camera properties to listen for Bruker TTL triggers
    # Record continuously
    n.AcquisitionMode.value = "Continuous"

    # Enable triggers
    n.TriggerMode.value = "On"

    # Trigger camera on rising edge of input signal
    n.TriggerActivation.value = "RisingEdge"

    # Select Line 2 as the Trigger Source and Input Source
    n.TriggerSource.value = "Line2"
    n.LineSelector.value = "Line2"

    # Print in terminal which acquisition mode is enabled
    print("Acquisition Mode: ", n.AcquisitionMode.value)

    # Start the acquisition, return camera and harvester for buffer
    print("Starting Acquisition")
    camera.start_acquisition()

    # Return Harvester, camera, and frame dimensions
    return h, camera, width, height


# -----------------------------------------------------------------------------
# Capture Camera Recording
# -----------------------------------------------------------------------------


def capture_recording(number_frames, video_list, plane_number):

    # Assign video name as the config_filename for readability
    video_name = video_list[1] + "_" + plane_number + ".avi"

    # Give basepath for video using supplied project name
    video_basepath = "E:/studies/" + video_list[0] + "/video/"

    # Create full video path
    video_fullpath = video_basepath + video_name

    # Define number of frames to record
    # TODO: Number of frames: Make this an input/from setup
    num_frames = number_frames

    # Define video codec for writing images
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')

    # Start the Camera
    h, camera, width, height = init_camera_recording()

    # Write file to disk
    # Create VideoWriter object: file, codec, framerate, dims, color value
    out = cv2.VideoWriter(video_fullpath, fourcc, 30, (width, height),
                          isColor=False)
    print("VideoWriter created")

    frame_number_list = []
    frame_number = 1
    for i in range(num_frames):

        # Introduce try/except block in case of dropped frames
        # More elegant solution for packet loss is necessary...
        try:

            # Use with statement to acquire buffer, payload, an data
            # Payload is 1D numpy array, RESHAPE WITH HEIGHT THEN WIDTH
            # Numpy is backwards, reshaping as heightxwidth writes correctly
            with camera.fetch_buffer() as buffer:

                # Define frame content with buffer.payload
                content = buffer.payload.components[0].data.reshape(height,
                                                                    width)

                # Debugging statment, print content shape and frame number
                out.write(content)
                print(content.shape)
                cv2.imshow("Live", content)
                cv2.waitKey(1)
                frame_number_list.append(frame_number)
                print(frame_number)
                frame_number += 1

        # TODO What is exception for dropped frame? How to make an exception?
        # Except block for if/when frames are dropped
        except:
            frame_number_list.append(frame_number)
            print(frame_number)
            print("Frame Dropped/Packet Loss")
            frame_number += 1
            pass

    # Once recording is done, let user know
    print("Video Complete")

    # Release VideoWriter object
    out.release()

    # Destroy camera window
    cv2.destroyAllWindows()

    # Shutdown the camera
    shutdown_camera(camera, h)

# -----------------------------------------------------------------------------
# Shutdown Camera
# -----------------------------------------------------------------------------


def shutdown_camera(image_acquirer, harvester):
    # Stop the camera's acquisition
    print("Stopping Acquisition")
    image_acquirer.stop_acquisition()

    # Destroy the camera object, release the resource
    print("Camera Destroyed")
    image_acquirer.destroy()

    # Reset Harvester object
    print("Resetting Harvester")
    harvester.reset()
