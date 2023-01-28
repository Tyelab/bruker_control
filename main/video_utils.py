# Bruker 2-Photon Video Utils
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters

###############################################################################
# Import Packages
###############################################################################

# Teledyne DALSA Genie Nano Interface: Harvesters
from harvesters.core import Harvester

# Import OpenCV2 to write images/videos to file + previews
import cv2

# Import datetime for filenaming
from datetime import datetime

# Import Tuple for appropriate typehinting of functions
from typing import Tuple

# Import tqdm for progress bar
from tqdm import tqdm

# Import pathlib Path for directory management
from pathlib import Path

# Import sys for exiting safely
import sys

# Import numpy for drawing lines on preview image
import numpy as np

# Import warnings to ignore deprecation warning from skvideo
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Static cti file location
# CTI stands for "Common Transport Interface" and is a type of acquisition software library
# that interacts with the Windows file system as a DLL, or dynamic link library. The CTI standard
# is used by any GenTL compliant cameras, which the Genie Nano is one of.
CTI_FILEPATH = "C:/Program Files/MATRIX VISION/mvIMPACT Acquire/bin/x64/mvGENTLProducer.cti"

# Define server paths for writing preview images to file
SERVER_PATHS = {"specialk_cs": Path("V:"),
                "specialk_lh": Path("U:")}

# Experiment videos are written to the Raw Data volume on the machine BRUKER
# which is mounted to E:
DATA_PATH = Path("E:/")

# To reduce the size of the video that is presented during a recording, introduce a
# common scaling factor that will reduce the image size shown.
SCALING_FACTOR = 50

# To place the live video feed out of the way, in the bottom right corner by default,
# move the window created to these locations
IMSHOW_X_POS = 1920
IMSHOW_Y_POS = 450

###############################################################################
# Classes
###############################################################################

# class Camera GENI Cam Compliant machines etc

###############################################################################
# Exceptions
###############################################################################


class CameraNotFound(Exception):
    """
    Exception class for if Python cannot find a connected GENTL camera.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "Camera Not Found! {0} ".format(self.message)
        else:
            return "Camera not found! Is it disconnected?"


###############################################################################
# Functions
###############################################################################


def init_camera_preview() -> Tuple[Harvester, Harvester, int, int]:
    """
    Creates, configures, describes, and starts harvesters camera object in
    preview setting.

    Initializes harvester camera, sets camera properties appropriate for
    preview, gathers the camera's width and height in pixels, and starts
    video acquisition. The function takes no arguments.

    Returns:

        Harvester object

        Camera object

        Camera's height (pixels)

        Camera's width (pixels)

    """

    # Create camera variable as None type
    camera = None

    # Create harvester object as h
    h = Harvester()

    # Give path to GENTL producer
    cti_file = CTI_FILEPATH

    # Add GENTL producer to Harvester object
    h.add_file(cti_file)

    # Update Harvester object
    h.update()

    camera_list = h.device_info_list

    # Try printing the camera list
    try:
        print("Connected to camera: ", camera_list[0].model, camera_list[0].user_defined_name)

    # If no devices are detected, the list will have no elements!  Raise an
    # exception to quit the program.
    except IndexError:
        raise CameraNotFound()

    # Grab Camera, Change Settings
    # Create image_acquirer object for Harvester, grab first (only) device
    camera = h.create(0)

    # Gather node map to camera properties
    n = camera.remote_device.node_map

    # Save camera width and height parameters
    width = n.Width.value
    height = n.Height.value

    # Change camera properties for continuous recording, no triggers needed
    n.AcquisitionMode.value = "Continuous"
    n.TriggerMode.value = "Off"

    # Show user the preview acquisition mode
    print("Preview Mode:", n.AcquisitionMode.value)

    # Start the acquisition
    print("Starting Preview")
    camera.start()

    # Return harvester, camera, and width/height in pixels of camera
    return h, camera, width, height


def capture_preview(project, subject_id):
    """
    Capture frames generated by camera object and display them in preview mode.

    Takes values from init_camera_preview() to capture images delivered by
    camera buffer, reshapes the image to appropriate height and width, draws
    a grid upon the preview
    
    When user hits the 'Esc' key, the window closes and the camera object is destroyed.
    Finally, the preview content is saved as an image that is timestamped with the day's
    date and placed into the subject's metadata directory.

    Args:
        project:
            The team and project conducting the experiment
        subject_id:
            The subject being recorded

    """

    h, camera, width, height = init_camera_preview()
    preview_status = True
    
    # Define number of rows and columns to have in the preview grid
    rows, cols = (8, 8)

    # Define the distance between each row and column, dx, dy
    dy, dx = height / rows, width / cols

    # Define preview image show dimensions
    imshow_width = int(width * SCALING_FACTOR / 100)
    imshow_height = int(height * SCALING_FACTOR / 100)
    imshow_dims = (imshow_width, imshow_height)

    print("To stop preview, hit 'Esc' key")

    cv2.namedWindow("Preview")
    cv2.moveWindow("Preview", IMSHOW_X_POS, IMSHOW_Y_POS)
    while preview_status is True:
        try:
            with camera.fetch() as buffer:
                # Define frame content with buffer.payload
                content = buffer.payload.components[0].data.reshape(height,
                                                                    width)
                
                # Draw lines along the rows
                # Start is dx away from 0, stop one dx before the end of the distance
                # num is number of lines to draw
                # From user mathandy at:
                # https://stackoverflow.com/questions/44816682/drawing-grid-lines-across-the-image-using-opencv-python
                for x_position in np.linspace(start=dx, stop = width - dx, num = cols - 1):
                    x = int(round(x_position))
                    cv2.line(content, (x, 0), (x, height), color=(255,0,0), thickness = 2)

                # Draw lines along the columns, same as x_position
                for y_position in np.linspace(start=dy, stop = height - dy, num = rows -1):
                    y = int(round(y_position))
                    cv2.line(content, (0, y), (width, y), color=(255,0,0), thickness = 2)
  
                # resize image
                resized = cv2.resize(content, imshow_dims, interpolation = cv2.INTER_AREA)
                cv2.imshow("Preview", resized)
                c = cv2.waitKey(1) % 0x100
                if c == 27:
                    preview_status = False

        except:
            pass
    
    # Get today's date
    session_date = datetime.today().strftime("%Y%m%d")

    # Define subject's directory for writing preview image.
    preview_directory = Path(SERVER_PATHS[project]) / "subjects" / subject_id
    
    # Define the session that's being done, meaning that day's imaging
    preview_session = "_".join(
        [
            session_date,
            subject_id,
            "preview"
        ])
    
    # Create the full filename
    preview_filename = preview_session + ".png"

    # Define the full path for the preview file
    preview_fullpath = str(preview_directory / preview_filename)

    # Write the image to subject directory
    cv2.imwrite(
        preview_fullpath,
        resized
        )

    cv2.destroyAllWindows()

    # Shutdown the camera
    shutdown_camera(camera, h)


def init_camera_recording() -> Tuple[Harvester, Harvester, int, int]:
    """
    Creates, configures, describes, and starts harvesters camera object in
    recording setting.

    Initializes harvester camera, sets camera properties appropriate for
    behavior recording, gathers the camera's width and height in pixels, and
    starts video acquisition. There are no arguments.

    Returns:

        Harvester object

        Camera object

        Camera's height (pixels)

        Camera's width (pixels)
    """

    camera = None

    # Setup Harvester
    # Create harvester object as h
    h = Harvester()

    # Give path to GENTL producer
    cti_file = CTI_FILEPATH

    # Add GENTL producer to Harvester object
    h.add_file(cti_file)

    # Update Harvester object
    h.update()

    camera_list = h.device_info_list

    # Print device list to make sure camera is present
    print("Connected to Camera: ", camera_list[0].model, camera_list[0].user_defined_name)

    # Grab Camera, Change Settings
    # Create image_acquirer object for Harvester, grab first (only) device
    camera = h.create(0)

    # Gather node map to camera properties
    n = camera.remote_device.node_map

    # Set and then save camera width and height parameters
    width = n.Width.value  # width = 1280
    height = n.Height.value  # height = 1024

    # Change camera properties to listen for Bruker TTL triggers
    # Record continuously
    n.AcquisitionMode.value = "Continuous"

    # Listen for Bruker's TTL triggers
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
    camera.start()

    # Return Harvester, camera, and frame dimensions
    return h, camera, width, height


def capture_recording(framerate: float, num_frames: int, current_plane: int, imaging_plane: str,
                      project: str, subject_id: str) -> list:
    """
    Capture frames generated by camera object, display them in recording mode,
    and write frames to .mp4 file.

    Takes values from init_camera_recording() to capture images delivered by
    camera buffer, reshapes the image to appropriate height and width, displays
    the image to an opencv window, and writes the image to a .mp4 file.
    When the camera acquires the specified number of frames for an experiment,
    the window closes, the camera object is destroyed, and the video is written
    to disk.

    Args:
        framerate:
            Microscope's framerate from prairieview_utils used in the video codec
        number_frames:
            Number of frames specified to collect for the video recording
        current_plane:
            Current plane being imaged as in 1st, 2nd, 3rd, etc
        imaging_plane:
            Plane the 2P image is currently being taken acquired from Prairie
            View
        project:
            The team and project conducting the experiment (ie teamname_projectname)
        subject_id:
            The subject being recorded

    Returns:
        dropped_frames
    """

    # Gather session date using datetime
    session_date = datetime.today().strftime("%Y%m%d")

    # Set video path
    video_dir = DATA_PATH / project / "video"

    # Set session name by joining variables with underscores
    session_name = "_".join(
        [session_date, subject_id, "plane{}".format(current_plane), imaging_plane]
        )

    # Assign video name as the session_name and append .mp4 as the file
    # format.
    video_name = session_name + ".mp4"

    # Create full video path
    video_fullpath = str(video_dir / video_name)

    # Start the Camera
    h, camera, width, height = init_camera_recording()

    out = cv2.VideoWriter(
        video_fullpath,
        cv2.VideoWriter_fourcc(*"avc1"),
        framerate,
        (width, height),
        isColor = False
        )

    dropped_frames = []

    frame_number = 1

    cv2.namedWindow("Live!")
    cv2.moveWindow("Live!", IMSHOW_X_POS, IMSHOW_Y_POS)

    # Experimental progress bar in term
    for frame_number in tqdm(range(num_frames), desc="Experiment Progress", ascii=True):

        # Introduce try/except block in case of dropped frames
        try:

            # Use with statement to acquire buffer, payload, an data
            # Payload is 1D numpy array, RESHAPE WITH HEIGHT THEN WIDTH
            # Numpy is backwards, reshaping as heightxwidth writes correctly
            with camera.fetch() as buffer:

                # Define frame content with buffer.payload
                content = buffer.payload.components[0].data.reshape(
                    height,
                    width
                    )

                # Resize image so it's not taking up the whole screen
                # Define dimensions, width and height
                imshow_width = int(width * SCALING_FACTOR / 100)
                imshow_height = int(height * SCALING_FACTOR / 100)

                imshow_dims = (imshow_width, imshow_height)

                # Write frame to disk
                out.write(content)

                # Resize the image, interpolate to avoid distortion
                resized = cv2.resize(content, imshow_dims, interpolation = cv2.INTER_AREA)
    
                cv2.imshow("Live!", resized)
                c = cv2.waitKey(1)

                frame_number += 1

        # TODO Raise warning for frame drops? What is this error...
        except Exception:
            dropped_frames.append(frame_number)
            frame_number += 1

            pass

    # Release VideoWriter object
    out.release()

    # Destroy camera window
    cv2.destroyAllWindows()

    # Shutdown the camera
    shutdown_camera(camera, h)

    return dropped_frames


def shutdown_camera(camera: Harvester, harvester: Harvester):
    """
    Deactivates and resets both harvester and camera after acquisition.

    Turns off camera, resets its configuration values, and resets the harvester
    object once acquisition is done. The function does not return anything

    Args:
        camera
            Harverster camera object
        harvester
            Haverster object
    """

    print("Stopping Acquisition")
    camera.stop()

    # Destroy the camera object, which releases the resource
    print("Camera Destroyed")
    camera.destroy()

    # Reset Harvester object back to default settings
    print("Resetting Harvester")
    harvester.reset()


def calculate_frames(session_len_s: int, framerate: float) -> int:
    """
    Calculates number of images to collect during the experiment.

    Converts imaging session length into number of frames to collect by
    microscope and, therefore, camera. Currently, the camera takes an
    image each time the microscope does via its TTLs.

    Args:
        session_len_s:
            Experimental session length in seconds
        framerate:
            Framerate of microscope.

    Returns:
        num_frames
    """

    # Generate buffer of 900 images to ensure enough data is captured when
    # session ends.
    imaging_buffer = 900

    # Calculate number of video frames, coerce calculation in to class int for tqdm later
    video_frames = int((round(session_len_s)*framerate) + imaging_buffer)

    return video_frames
