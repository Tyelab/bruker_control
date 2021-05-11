# Bruker 2-Photon Experiment Control
# Jeremy Delahanty May 2021
# Harvesters written by Kazunari Kudo
# https://github.com/genicam/harvesters
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Genie Nano manufactured by Teledyne DALSA

# -----------------------------------------------------------------------------
# Import Packages
# -----------------------------------------------------------------------------
#### File Types ####
# Import JSON for configuration file
import json
# Import ordered dictionary to ensure order in json file
from collections import OrderedDict
# Import argparse if you want to create a configuration on the fly
import argparse

#### Trial Array Generation ####
# Import scipy for statistical distributions
import scipy
# Import scipy.stats truncated normal distribution for ITI Array
from scipy.stats import truncnorm
# Import numpy for trial array generation/manipulation and Harvesters
import numpy as np
# Import numpy default_rng
from numpy.random import default_rng

#### Serial Transfer ####
# Import pySerialTransfer for serial comms with Arduino
from pySerialTransfer import pySerialTransfer as txfer

#### Teledyne DALSA Genie Nano Interface: Harvesters ####
# Harvesters for interfacing with Genie Nano
from harvesters.core import Harvester
# Import mono8 location format, our Genie Nano uses mono8 or mono10
from harvesters.util.pfnc import mono_location_formats

#### Other Packages ####
# Import matplotlib for displaying images
import matplotlib.pyplot as plt
# Import OpenCV2 to write images/videos to file + previews
import cv2
# Import OS to change directories and write files to disk
import os
# Import sys for exiting program safely
import sys
# Import time
import time

#### Prairie View Interface ####
# NOTE:
# win32com client installation: Do NOT use pip install, use conda:
# conda install pywin32
import  win32com.client
pl = win32com.client.Dispatch("PrairieLink.Application")

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
#### Trial Generation ####
# Random Trials Array Generation
def gen_trial_array(totalNumberOfTrials):
    # Always initialize trial array with 3 reward trials
    trialArray = [1,1,1]
    # Define number of samples needed from generator
    num_samples = totalNumberOfTrials - len(trialArray)
    # Define probability that the animal will receive sucrose 60% of the time
    sucrose_prob = 0.5
    # Initialize random number generator with default_rng
    rng = np.random.default_rng(2)
    # Generate a random trial array with Generator.binomial
    # Use n=1 to pull one sample at a time, p=.6 as probability of sucrose
    # Use num_samples to fill out accurate number of trials
    # Use .tolist() to convert random_trials from np.array to list
    random_trials = rng.binomial(
    n=1, p=sucrose_prob, size=num_samples
    ).tolist()
    # Append the two arrays together
    for i in random_trials:
        trialArray.append(i)

    ## TODO: Write out the trial array into JSON as part of experiment config
    # Return trialArray
    return trialArray

# ITI Array Generation
def gen_iti_array(totalNumberOfTrials):
    # Initialize empty iti trial array
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
    lower_bound, upper_bound, loc=mu, scale=sigma, size=totalNumberOfTrials
    )
    # ITI Array generated with have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    iti_array = np.round(iti_array).astype(int)
    # Finally, generate ITIArray as a list for pySerialTransfer
    ITIArray = iti_array.tolist()

    ## TODO: Write out the ITI array into JSON as part of experiment config

    # Return ITIArray
    return ITIArray

# Noise Array Generation
def gen_noise_array(totalNumberOfTrials):
    # Initialize empty iti trial array
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
    lower_bound, upper_bound, loc=mu, scale=sigma, size=totalNumberOfTrials
    )
    # ITI Array generated with have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    noise_array = np.round(noise_array).astype(int)
    # Finally, generate ITIArray as a list for pySerialTransfer
    noiseDurationArray = noise_array.tolist()

    ## TODO: Write out the ITI array into JSON as part of experiment config

    # Return ITIArray
    return noiseDurationArray

#### Camera Control ####
# Initiate Preview Camera
def init_camera_preview():
    camera = None

    #### Setup Harvester ####
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

    #### Grab Camera, Change Settings ####
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

# Capture Preview of Camera
def capture_preview():
    h, camera, width, height = init_camera_preview()
    preview_status = True
    while preview_status == True:
        with camera.fetch_buffer() as buffer:
            # Define frame content with buffer.payload
            content = buffer.payload.components[0].data.reshape(height, width)
            # Provide preview for camera contents:
            cv2.imshow("Preview", content)
            cv2.waitKey(1)
            # if input("To end preview, type 's': ") == "s":
            #     preview_status = False
            # else:
            #     pass

    print("Preview Ending")

    # Shutdown the camera
    shutdown_camera(camera, h)

# Initialize Camera for Recording
def init_camera_recording():
    camera = None

    #### Setup Harvester ####
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

    #### Grab Camera, Change Settings ####
    # Create image_acquirer object for Harvester, grab first (only) device
    camera = h.create_image_acquirer(0)
    # Gather node map to camera properties
    n = camera.remote_device.node_map
    # Set and then save camera width and height parameters
    # n.Width.value = 1280
    width = n.Width.value
    # n.Height.value = 1024
    height = n.Height.value
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

    # Sleep the program for three seconds to let buffer get started...
    time.sleep(3)

    # Return Harvester, camera, and frame dimensions
    return h, camera, width, height

def capture_recording(number_frames):
    # Create filename TODO: make this an input or from setup function
    filename = 'testvid.avi'
    # Define filepath for video
    directory = r"C:\Users\jdelahanty\Documents\genie_nano_videos"
    # Change to directory for writing the video
    os.chdir(directory)
    # Define number of frames to record TODO: Make this an input/from setup
    num_frames = number_frames
    # Define video codec for writing images
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    # Start the Camera
    h, camera, width, height = init_camera_recording()
    # Write file to disk
    # Create VideoWriter object: file, codec, framerate, dims, color value
    out = cv2.VideoWriter(filename, fourcc, 30, (width, height), isColor=False)
    print("VideoWriter created")
    frame_number = 0
    for i in range(num_frames):
        # Introduce try/except block in case of dropped frames
        # More elegant solution for packet loss is necessary...
        try:
            # Use with statement to acquire buffer, payload, an data
            # Payload is 1D numpy array, RESHAPE WITH HEIGHT THEN WIDTH
            # Numpy is backwards, reshaping as heightxwidth writes correctly
            with camera.fetch_buffer() as buffer:
                # Define frame content with buffer.payload
                content = buffer.payload.components[0].data.reshape(height, width)
                # Debugging statment, print content shape and frame number
                out.write(content)
                print(content.shape)
                cv2.imshow("Live", content)
                cv2.waitKey(1)
                number += 1
                print(frame_number)
        except:
            print(frame_number)
            print("Frame Dropped/Packet Loss")
            pass

    # Release VideoWriter object
    out.release()
    # Shutdown the camera
    shutdown_camera(camera, h)

# Shutdown Camera
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

#### Serial Transfer to Arduino ####
def serial_transfer(trialArray, ITIArray, noiseDurationArray):
    try:
        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        #read JSON config file
        with open('C:/Users/jdelahanty/Documents/gitrepos/headfix_control/config.json', 'r') as inFile:
            contents = inFile.read()

        # Convert from JSON to Dictionary
        config = json.loads(contents)

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

        # Check if metaData was sent correctly:
        # if config == rxmetaData:
        #     print("Confirmed Metadata!")
        #     metaData_status = True
        # else:
        #     print("Metadata error! Exiting...")
        #     sys.exit()


        # Now send the trial array:
        trialArray_size = 0
        trialArray_size = link.tx_obj(trialArray)
        link.send(trialArray_size, packet_id=1)

        print(trialArray)

        while not link.available():
            pass

        # Receive trial array:
        rxtrialArray = link.rx_obj(obj_type=type(trialArray),
        obj_byte_size=trialArray_size, list_format='i')

        print(rxtrialArray)
        # else:
        #     print("Trial Array error! Exiting...")
        #     sys.exit()

        # Send ITI array:
        ITIArray_size = 0
        ITIArray_size = link.tx_obj(ITIArray)
        link.send(ITIArray_size, packet_id=2)

        print(ITIArray)

        while not link.available():
            pass

        # Receive ITI Array
        rxITIArray = link.rx_obj(obj_type=type(ITIArray),
        obj_byte_size = ITIArray_size,
        list_format='i')

        print(rxITIArray)

        noiseDurationArray_size = 0
        noiseDurationArray_size = link.tx_obj(noiseDurationArray)
        link.send(noiseDurationArray_size, packet_id=3)

        print(noiseDurationArray)

        while not link.available():
            pass

        # Receive Noise Duration Array
        rxnoiseDurationArray = link.rx_obj(obj_type=type(noiseDurationArray),
        obj_byte_size=noiseDurationArray_size,
        list_format='i')

        print(rxnoiseDurationArray)

        link.close()


        # Confirm data was sent/received properly:
        # if ITIArray == rxITIArray:
        #     print("Confrimed ITI Array!")
        #     ITIArray_status = True
        # else:
        #     print("ITI Array error! Exiting...")
        #     sys.exit()



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

if __name__ == "__main__":
    trialArray = gen_trial_array(10)
    ITIArray = gen_iti_array(10)
    noiseDurationArray = gen_noise_array(10)
    capture_preview()
    # serial_transfer(trialArray, ITIArray, noiseDurationArray)
    # capture_recording(600)
    print("Video Complete")
    # print("Connected to Prairie View")
    # pl.Connect()
    # pl.SendScriptCommands("-Abort")
    # pl.Disconnect()
    # print("Disconnected from Prairie View")
    print("Experiment Over!")
    print("Exiting...")
    sys.exit()
