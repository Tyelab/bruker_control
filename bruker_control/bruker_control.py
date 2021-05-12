# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

###############################################################################
# Import Packages
###############################################################################
# File Types
# Import JSON for configuration file
import json
# Import ordered dictionary to ensure order in json file
from collections import OrderedDict
# Import argparse if you want to create a configuration on the fly
import argparse

# Trial Array Generation
# Import scipy.stats truncated normal distribution for ITI Array
from scipy.stats import truncnorm
# Import numpy for trial array generation/manipulation and Harvesters
import numpy as np
# Import numpy default_rng
from numpy.random import default_rng

# Serial Transfer
# Import pySerialTransfer for serial comms with Arduino
from pySerialTransfer import pySerialTransfer as txfer

# Teledyne DALSA Genie Nano Interface: Harvesters
from harvesters.core import Harvester
# TODO: Is mono8 necessary to import?
# Import mono8 location format, our Genie Nano uses mono8 or mono10
# from harvesters.util.pfnc import mono_location_formats

# Other Packages
# Import OpenCV2 to write images/videos to file + previews
import cv2
# Import os and os.path to change directories and write files to disk
import os
from os import path
# Import sys for exiting program safely
import sys

# NOTE Prairie View Interface
# win32com client installation: Do NOT use pip install, use conda.
# conda install pywin32
import win32com.client
pl = win32com.client.Dispatch("PrairieLink.Application")


###############################################################################
# Functions
###############################################################################

###############################################################################
# Random Array Generation: One Packet
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation: One Packet
# -----------------------------------------------------------------------------


def gen_trialArray_onepacket(totalNumberOfTrials):

    # Always initialize trial array with 3 reward trials
    trialArray = [1, 1, 1]

    # Define number of samples needed from generator
    num_samples = totalNumberOfTrials - len(trialArray)

    # Define probability that the animal will receive sucrose 50% of the time
    sucrose_prob = 0.5

    # Initialize random number generator with default_rng
    rng = default_rng(2)

    # Generate a random trial array with Generator.binomial.  Use n=1 to pull
    # one sample at a time and p=0.5 as probability of sucrose.  Use
    # num_samples to generate the correct number of trials.  Finally, use
    # tolist() to convert random_trials from an np.array to a list.
    random_trials = rng.binomial(
                                 n=1, p=sucrose_prob, size=num_samples
                                ).tolist()

    # Append the two arrays together
    for i in random_trials:
        trialArray.append(i)

    # If the total number of trials is larger than 45, which is the max size
    # that can be transmitted in one packet, a different function will be used
    # to send that information.

    # TODO: Write out the trial array into JSON as part of experiment config

    # Return trialArray
    return trialArray

# -----------------------------------------------------------------------------
# ITI Array Generation: One Packet
# -----------------------------------------------------------------------------


def gen_ITIArray_onepacket(totalNumberOfTrials):

    # Initialize empty iti array
    iti_array = []

    # Define lower and upper limits on ITI values in ms
    iti_lower, iti_upper = 2500, 3500

    # Define mean and variance for ITI values
    mu, sigma = 3000, 1000

    # Upper bound calculation
    upper_bound = (iti_upper - mu)/sigma

    # Lower bound calculation
    lower_bound = (iti_lower - mu)/sigma

    # Generate array by sampling from truncated normal distribution w/scipy
    iti_array = truncnorm.rvs(
                              lower_bound, upper_bound, loc=mu, scale=sigma,
                              size=totalNumberOfTrials
                             )

    # ITI Array generated will have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    iti_array = np.round(iti_array).astype(int)

    # Finally, generate ITIArray as a list for pySerialTransfer
    ITIArray = iti_array.tolist()

    # Return ITI Array
    return ITIArray


# -----------------------------------------------------------------------------
# Noise Array Generation: One Packet
# -----------------------------------------------------------------------------


def gen_noiseArray_onepacket(totalNumberOfTrials):

    # Initialize empty noise array
    noise_array = []

    # Define lower and upper limits on ITI values in ms
    noise_lower, noise_upper = 2500, 3500

    # Define mean and variance for ITI values
    mu, sigma = 3000, 1000

    # Upper bound calculation
    upper_bound = (noise_upper - mu)/sigma

    # Lower bound calculation
    lower_bound = (noise_lower - mu)/sigma

    # Generate array by sampling from truncated normal distribution w/scipy
    noise_array = truncnorm.rvs(
                                lower_bound, upper_bound, loc=mu, scale=sigma,
                                size=totalNumberOfTrials
                                )

    # Noise Array generated will have decimals in it and be float type.
    # Use np.round() to round the elements in the array and type them as int.
    noise_array = np.round(noise_array).astype(int)

    # Finally, generate noiseArray as a list for pySerialTransfer.
    noiseArray = noise_array.tolist()

    # Return the noiseArray
    return noiseArray


###############################################################################
# Random Array Generation: Multi-packet
###############################################################################

# -----------------------------------------------------------------------------
# Trial Array Generation: Multi-packet
# -----------------------------------------------------------------------------


def gen_trialArray_multipacket(totalNumberOfTrials):

    # Always initialize trial array with 3 reward trials
    trialArray = [1, 1, 1]

    # Define number of samples needed from generator
    num_samples = totalNumberOfTrials - len(trialArray)

    # Define probability that the animal will receive sucrose 50% of the time
    sucrose_prob = 0.5

    # Initialize random number generator with default_rng
    rng = default_rng(2)

    # Generate a random trial array with Generator.binomial.  Use n=1 to pull
    # one sample at a time and p=0.5 as probability of sucrose.  Use
    # num_samples to generate the correct number of trials.  Finally, use
    # tolist() to convert random_trials from an np.array to a list.
    random_trials = rng.binomial(
                                 n=1, p=sucrose_prob,
                                 size=num_samples
                                ).tolist()

    # Append the two arrays together
    for i in random_trials:
        trialArray.append(i)

    # Use np.array_split() to divide list into smaller sizes
    split_array = np.array_split(trialArray, 2)

    # First index of split array is content of first packet
    first_trialArray = split_array[0].tolist()

    # Second index of split array is content of second packet
    second_trialArray = split_array[1].tolist()

    # TODO: Write out the trial array into JSON as part of experiment config

    # Return trial arrays
    return first_trialArray, second_trialArray


# -----------------------------------------------------------------------------
# ITI Array Generation: Multi-packet
# -----------------------------------------------------------------------------


def gen_ITIArray_multipacket(totalNumberOfTrials):

    # Initialize empty iti array
    iti_array = []

    # Define lower and upper limits on ITI values in ms
    iti_lower, iti_upper = 2500, 3500

    # Define mean and variance for ITI values
    mu, sigma = 3000, 1000

    # Upper bound calculation
    upper_bound = (iti_upper - mu)/sigma

    # Lower bound calculation
    lower_bound = (iti_lower - mu)/sigma

    # Generate array by sampling from truncated normal distribution w/scipy
    iti_array = truncnorm.rvs(
                              lower_bound, upper_bound, loc=mu, scale=sigma,
                              size=totalNumberOfTrials
                             )

    # ITI Array generated will have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    iti_array = np.round(iti_array).astype(int)

    split_array = np.array_split(iti_array, 2)
    first_ITIArray = split_array[0].tolist()
    second_ITIArray = split_array[1].tolist()

    # TODO: Write out the ITI array into JSON as part of experiment config

    # Return first and second ITI Arrays
    return first_ITIArray, second_ITIArray


# -----------------------------------------------------------------------------
# Noise Array Generation: Multi-packet
# -----------------------------------------------------------------------------


def gen_noiseArray_multipacket(totalNumberOfTrials):

    # Initialize empty noise array
    noise_array = []

    # Define lower and upper limits on ITI values in ms
    noise_lower, noise_upper = 2500, 3500

    # Define mean and variance for ITI values
    mu, sigma = 3000, 1000

    # Upper bound calculation
    upper_bound = (noise_upper - mu)/sigma

    # Lower bound calculation
    lower_bound = (noise_lower - mu)/sigma

    # Generate array by sampling from truncated normal distribution w/scipy
    noise_array = truncnorm.rvs(
                                lower_bound, upper_bound, loc=mu, scale=sigma,
                                size=totalNumberOfTrials
                                )

    # Noise Array generated will have decimals in it and be float type.
    # Use np.round() to round the elements in the array and type them as int.
    noise_array = np.round(noise_array).astype(int)

    split_array = np.array_split(noise_array, 2)
    first_noiseArray = split_array[0].tolist()
    second_noiseArray = split_array[1].tolist()

    # TODO:  Write out the noise array into JSON as part of experiment config

    # Return the first and second noise arrays
    return first_noiseArray, second_noiseArray

###############################################################################
# Serial Transfer to Arduino: One Packet
###############################################################################

# -----------------------------------------------------------------------------
# Configuration/Metadata File Transfer
# -----------------------------------------------------------------------------


def serialtransfer_metadata(config):

    try:
        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # stuff TX buffer (https://docs.python.org/3/library/struct.html#format-characters)
        metaData_size = 0
        metaData_size = link.tx_obj(config['metadata']['totalNumberOfTrials']['value'],       metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(config['metadata']['punishTone']['value'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(config['metadata']['rewardTone']['value'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(config['metadata']['USDeliveryTime_Sucrose']['value'],    metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(config['metadata']['USDeliveryTime_Air']['value'],        metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(config['metadata']['USConsumptionTime_Sucrose']['value'], metaData_size, val_type_override='H')

        link.open()

        link.send(metaData_size, packet_id=0)

        while not link.available():
            pass

        # Receive packet from Arduino
        # Create rxmetaData dictionary
        rxmetaData = {}
        rxmetaData_size = 0

        rxmetaData['totalNumberOfTrials'] = link.rx_obj(obj_type='B', start_pos=rxmetaData_size)
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['B']
        rxmetaData['punishTone'] = link.rx_obj(obj_type='H', start_pos=rxmetaData_size)
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['H']
        rxmetaData['rewardTone'] = link.rx_obj(obj_type='H', start_pos=rxmetaData_size)
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['H']
        rxmetaData['USDeliveryTime_Sucrose'] = link.rx_obj(obj_type='B', start_pos=rxmetaData_size)
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['B']
        rxmetaData['USDeliveryTime_Air'] = link.rx_obj(obj_type='B', start_pos=rxmetaData_size)
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['B']
        rxmetaData['USConsumptionTime_Sucrose'] = link.rx_obj(obj_type='H', start_pos=rxmetaData_size)

        print(rxmetaData)

        # TODO: Put error checking outside the function
        # Check if metaData was sent correctly:
        # if config == rxmetaData:
        #     print("Confirmed Metadata!")
        #     metaData_status = True
        # else:
        #     print("Metadata error! Exiting...")
        #     sys.exit()

        link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass
    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


# -----------------------------------------------------------------------------
# Trial Array Transfer: One Packet
# -----------------------------------------------------------------------------


def serialtransfer_trialArray_onepacket(trialArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize trialArray_size of 0
        trialArray_size = 0

        # Stuff packet with size of trialArray
        trialArray_size = link.tx_obj(trialArray)

        # Open communication link
        link.open()

        # Send array
        link.send(trialArray_size, packet_id=0)

        print("Sent Trial Array")
        print(trialArray)

        while not link.available():
            pass

        # Receive trial array:
        rxtrialArray = link.rx_obj(obj_type=type(trialArray),
                                   obj_byte_size=trialArray_size,
                                   list_format='i')

        print("Received Trial Array")
        print(rxtrialArray)

        # TODO: Move error handling outside of function; need to learn how...

        # if trialArray == rxtrialArray:
        #     print("Trial Array transfer successful!")
        #
        # else:
        #     link.close()
        #     print("Trial Array error! Exiting...")
        #     sys.exit()

        # Close the communication link
        link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


# -----------------------------------------------------------------------------
# ITI Array Transfer: One Packet
# -----------------------------------------------------------------------------


def serialtransfer_ITIArray_onepacket(ITIArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Send ITI array:
        ITIArray_size = 0
        ITIArray_size = link.tx_obj(ITIArray)
        link.open()
        link.send(ITIArray_size, packet_id=0)

        print(ITIArray)

        while not link.available():
            pass

        # Receive ITI Array
        rxITIArray = link.rx_obj(obj_type=type(ITIArray),
                                 obj_byte_size=ITIArray_size,
                                 list_format='i')

        print(rxITIArray)

        # TODO: Move error checking outside function
        # Confirm data was sent/received properly:
        # if ITIArray == rxITIArray:
        #     print("Confrimed ITI Array!")
        # else:
        #     link.close()
        #     print("ITI Array error! Exiting...")
        #     sys.exit()
        #
        # link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass
    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


# -----------------------------------------------------------------------------
# Noise Array Transfer: One Packet
# -----------------------------------------------------------------------------


def serialtransfer_noiseArray_onepacket(noiseArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)
        noiseArray_size = 0
        noiseArray_size = link.tx_obj(noiseArray)
        link.open()
        link.send(noiseArray_size, packet_id=0)

        print(noiseArray)

        while not link.available():
            pass

        # Receive Noise Duration Array
        rxnoiseArray = link.rx_obj(obj_type=type(noiseArray),
                                   obj_byte_size=noiseArray_size,
                                   list_format='i')

        print(rxnoiseArray)

        if noiseArray == rxnoiseArray:
            print("Noise Array transfer successful")
        else:
            link.close()
            print("Noise Array transfer failure")
            print("Exiting...")
            sys.exit()

        link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass
    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


###############################################################################
# Serial Transfer to Arduino: Multi-packet
###############################################################################

# -----------------------------------------------------------------------------
# Trial Array Transfer: Multi-packet
# -----------------------------------------------------------------------------


def serialtransfer_trialArray_multipacket(first_trialArray, second_trialArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize first packet size of 0
        first_trialArray_size = 0

        # Stuff the packet with the first trial array
        first_trialArray_size = link.tx_obj(first_trialArray)

        # Open the communication link
        link.open()

        # Send the first packet with a packet_id of 0
        link.send(first_trialArray_size, packet_id=0)

        print("First Half of Trials Sent")
        print(first_trialArray)

        while not link.available():
            pass

        # Receive the first half of trials from Arduino
        rxfirst_trialArray = link.rx_obj(obj_type=type(first_trialArray),
                                         obj_byte_size=first_trialArray_size,
                                         list_format='i')

        print("First Half of Trials Received")
        print(rxfirst_trialArray)

        # TODO Move error checking outside this function

        # # Confirm packet was sent correctly
        # if first_trialArray == rxfirst_trialArray:
        #     print("First Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("First Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()

        # Initialize second packet size of 0
        second_trialArray_size = 0

        # Stuff the packet with second trial array
        second_trialArray_size = link.tx_obj(second_trialArray)

        # Send the second packet with a packet_id of 1
        link.send(second_trialArray_size, packet_id=1)

        print("Second Half of Trials Sent")
        print(second_trialArray)

        # Receive second half of trials from Arduino
        rxsecond_trialArray = link.rx_obj(obj_type=type(second_trialArray),
                                          obj_byte_size=second_trialArray_size,
                                          list_format='i')

        print("Second Half of Trials Received")
        print(rxsecond_trialArray)

        # TODO Put error checking outside this function
        # if second_trialArray == rxsecond_trialArray:
        #     print("Second Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("Second Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()
        #
        # link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


def serialtransfer_ITIArray_multipacket(first_ITIArray, second_ITIArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize first packet size of 0
        first_ITIArray_size = 0

        # Stuff the packet with the first trial array
        first_ITIArray_size = link.tx_obj(first_ITIArray)

        # Open the communication link
        link.open()

        # Send the first packet with a packet_id of 0
        link.send(first_ITIArray_size, packet_id=0)

        print("First Half of ITIs Sent")
        print(first_ITIArray)

        while not link.available():
            pass

        # Receive the first half of trials from Arduino
        rxfirst_ITIArray = link.rx_obj(obj_type=type(first_ITIArray),
                                       obj_byte_size=first_ITIArray_size,
                                       list_format='i')

        print("First Half of ITIs Received")
        print(rxfirst_ITIArray)

        # TODO Move error checking outside this function

        # # Confirm packet was sent correctly
        # if first_ITIArray == rxfirst_ITIArray:
        #     print("First Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("First Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()

        # Initialize second packet size of 0
        second_ITIArray_size = 0

        # Stuff the packet with second trial array
        second_ITIArray_size = link.tx_obj(second_ITIArray)

        # Send the second packet with a packet_id of 1
        link.send(second_ITIArray_size, packet_id=1)

        print("Second Half of ITIs Sent")
        print(second_ITIArray)

        # Receive second half of trials from Arduino
        rxsecond_ITIArray = link.rx_obj(obj_type=type(second_ITIArray),
                                        obj_byte_size=second_ITIArray_size,
                                        list_format='i')

        print("Second Half of ITIs Received")
        print(rxsecond_ITIArray)

        # TODO Put error checking outside this function
        # if second_ITIArray == rxsecond_ITIArray:
        #     print("Second Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("Second Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()
        #
        # link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


def serialtransfer_noiseArray_multipacket(first_noiseArray, second_noiseArray):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize first packet size of 0
        first_noiseArray_size = 0

        # Stuff the packet with the first trial array
        first_noiseArray_size = link.tx_obj(first_noiseArray)

        # Open the communication link
        link.open()

        # Send the first packet with a packet_id of 0
        link.send(first_noiseArray_size, packet_id=0)

        print("First Half of Noises Sent")
        print(first_noiseArray)

        while not link.available():
            pass

        # Receive the first half of trials from Arduino
        rxfirst_noiseArray = link.rx_obj(obj_type=type(first_noiseArray),
                                       obj_byte_size=first_noiseArray_size,
                                       list_format='i')

        print("First Half of Noises Received")
        print(rxfirst_noiseArray)

        # TODO Move error checking outside this function

        # # Confirm packet was sent correctly
        # if first_noiseArray == rxfirst_noiseArray:
        #     print("First Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("First Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()

        # Initialize second packet size of 0
        second_noiseArray_size = 0

        # Stuff the packet with second trial array
        second_noiseArray_size = link.tx_obj(second_noiseArray)

        # Send the second packet with a packet_id of 1
        link.send(second_noiseArray_size, packet_id=1)

        print("Second Half of Noises Sent")
        print(second_noiseArray)

        # Receive second half of trials from Arduino
        rxsecond_noiseArray = link.rx_obj(obj_type=type(second_noiseArray),
                                          obj_byte_size=second_noiseArray_size,
                                          list_format='i')

        print("Second Half of Noises Received")
        print(rxsecond_noiseArray)

        # TODO Put error checking outside this function
        # if second_noiseArray == rxsecond_noiseArray:
        #     print("Second Half Trial Array Transfer Successful!")
        # else:
        #     link.close()
        #     print("Second Half Trial Array Transfer Failure!")
        #     print("Exiting...")
        #     sys.exit()
        #
        # link.close()

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass


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
    cti_file = "C:/Program Files/MATRIX VISION/mvIMPACT Acquire/bin/x64/mvGENTLProducer.cti"

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
    while preview_status:
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
    cti_file = "C:/Program Files/MATRIX VISION/mvIMPACT Acquire/bin/x64/mvGENTLProducer.cti"

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


def capture_recording(number_frames):
    # Get filename
    # TODO: Filename: make this an imput from setup
    filename = 'testvid.avi'

    # Define filepath for video
    directory = r"C:\Users\jdelahanty\Documents\genie_nano_videos"

    # Change to directory for writing the video
    os.chdir(directory)

    # Define number of frames to record
    # TODO: Number of frames: Make this an input/from setup
    num_frames = number_frames

    # Define video codec for writing images
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')

    # Start the Camera
    h, camera, width, height = init_camera_recording()

    # Write file to disk
    # Create VideoWriter object: file, codec, framerate, dims, color value
    out = cv2.VideoWriter(filename, fourcc, 30, (width, height), isColor=False)
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

    # Release VideoWriter object
    out.release()
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


###############################################################################
# Prairie View Control
###############################################################################


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------

def prairie_abort():
    print("Connected to Prairie View")
    pl.Connect()
    pl.SendScriptCommands("-Abort")
    pl.Disconnect()
    print("Disconnected from Prairie View")


###############################################################################
# Main Function
###############################################################################


if __name__ == "__main__":

    # TODO: Use argparser for config file
    # TODO: Let user change configurations/create them on the fly with parser

    # TODO: Get relative paths working using os.path
    # Give config file name
    config_file = r"C:\\Users\\jdelahanty\\Documents\\gitrepos\\headfix_control\\bruker_control\\config.json"
    # read JSON config file
    with open(config_file, 'r') as inFile:
        contents = inFile.read()
        # Convert from JSON to Dictionary
        config = json.loads(contents)

    # Gather total number of trials
    trials = config["metadata"]["totalNumberOfTrials"]["value"]

    # Preview video for headfixed mouse placement
    capture_preview()

    # If only one packet is required, use single packet generation and
    # transfer.  Single packets are all that's needed for sizes less than 45.
    if trials <= 45:

        # Send configuration file
        serialtransfer_metadata(config_file)

        # Generate single packet arrays
        trialArray = gen_trialArray_onepacket(trials)
        ITIArray = gen_ITIArray_onepacket(trials)
        noiseArray = gen_noiseArray_onepacket(trials)

        # Use single packet serial transfer for arrays
        serialtransfer_trialArray_onepacket(trialArray)
        serialtransfer_ITIArray_onepacket(ITIArray)
        serialtransfer_noiseArray_onepacket(noiseArray)

        # TODO Gather number of frames expected from microscope for num_frames
        # Now that the packets have been sent, the Arduino will start soon.  We
        # now start the camera for recording the experiment!
        capture_recording(600)

        print("Video Complete")
        print("Connected to Prairie View")
        pl.Connect()
        pl.SendScriptCommands("-Abort")
        pl.Disconnect()
        print("Disconnected from Prairie View")
        print("Experiment Over!")
        print("Exiting...")
        sys.exit()

    # If there's multiple packets required, use multipacket generation and
    # transfer.  Multiple packets are required for sizes greater than 45.
    elif trials > 45:

        # Send configuration file
        serialtransfer_metadata(config_file)

        # Generate multipacket arrays
        first_trialArray, second_trialArray = gen_trialArray_multipacket(trials)
        first_ITIArray, second_ITIArray = gen_ITIArray_multipacket(trials)
        first_noiseArray, second_noiseArray = gen_noiseArray_multipacket(trials)

        # Use multipacket serial transfer for arrays
        serialtransfer_trialArray_multipacket(first_trialArray,
                                              second_trialArray)
        serialtransfer_ITIArray_multipacket(first_ITIArray,
                                            second_ITIArray)
        serialtransfer_noiseArray_multipacket(first_noiseArray,
                                              second_noiseArray)

        # Now that the packets have been sent, the Arduino will start soon.  We
        # now start the camera for recording the experiment!
        capture_recording(600)

        # Once recording is done, let user know
        print("Video Complete")

        # End Prairie View's imaging session with abort command
        prairie_abort()

        # Now that the microscopy session has ended, let user know
        print("Experiment Over!")

        # Exit the program
        print("Exiting...")
        sys.exit()

    # If some other value that doesn't fit in these categories is given, there
    # is something wrong. Let the user know and exit the program.
else:
    print("Something is wrong with the config file...")
    print("Exiting...")
    sys.exit()
