# Bruker 2-Photon Serial Transfer Utils
# Jeremy Delahanty May 2021
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer
# Uploading sketches through CLI inspired by Deryn LeDuke's use of the it in MATLAB

###############################################################################
# Import Packages
###############################################################################

# Serial Transfer
# Import pySerialTransfer for serial comms with Arduino
from pySerialTransfer import pySerialTransfer as txfer

# Import Numpy for splitting arrays
import numpy as np

# Import sys for exiting program safely
import sys

# Import subprocess for uploading team's sketch the first time the program is
# run
import subprocess as sp

# Import pathlib for gathering team's arduino sketch
from pathlib import Path

# Import typing for type hints
from typing import List

# Import os for gathering which user is currently running the experiment
import os

# Import json for decoding ascii strings into dictionaries, ensure that
# experiment can find the Arduino being used before running the session
import json

# Gather username of whoever is signed into the computer that day for
# grepping the appropriate sketches
# For appropriate RTD autodoc functionality, check to see if
# this is being run in a readthedocs workflow.
# See:
# https://docs.readthedocs.io/en/stable/faq.html#how-do-i-change-behavior-when-building-with-read-the-docs
on_rtd = os.environ.get('READTHEDOCS') == 'True'

# If this is being read by readthedocs, give it a fake fun username
if on_rtd:
    USERNAME = "pockel"
# Otherwise, get the real username running the experiment.
else:
    USERNAME = os.getlogin()

# Until something like Autopilot is used, hardcoding sketch paths
# in this manner is how things like this will have to be done...
SKETCH_PATHS = Path(f"C:/Users/{USERNAME}/Documents/gitrepos/bruker_control/")


###############################################################################
# Classes
###############################################################################


class Arduino:
    """
    Generic Arduino class for interacting with arbitrary Arduino boards.

    Class for discovering boards available on the system with ability
    to select arbitrary Arduino boards discovered on the machine. Compiles
    and uploads sketches to the board before the experiment starts.
    """

    def __init__(self, sketch_path:Path, idx:int=0):
        self.sketch_path = sketch_path

        properties = self.list_boards()

        if idx > len(properties):
            raise ValueError(f"Requested board with index {idx}, but {len(properties)} boards found")
        
        self.board_name = properties[idx][0]
        self.fqbn = properties[idx][1]
        self.board_com = properties[idx][2]


    @classmethod
    def list_boards(cls) -> List[tuple]:
        """
        Query CLI for finding available Arduinos on the machine.
        """

        print("Determining Board Properties...")

        # Query the CLI with a subprocess
        com_list = sp.run(
            [
                "arduino-cli",
                "board",
                "list",
                "--format",
                "json"
            ],
            capture_output=True
        ).stdout.decode("ascii")

        # Load json formatted output for parsing
        decoded_com_list = json.loads(com_list)

        # For each address found in the com_list (the CLI)
        # will report all noted COM addresses even if its
        # not sure what it is), find its name, fully-qualified
        # board name (fqbn) and the COM ports associated with it
        for address in decoded_com_list:
            if "matching_boards" in address:
                matching_boards = address["matching_boards"]
                # If only one board is found, having the port
                # addresses in a list makes list comprehension
                # easier later...
                addresses = [address["port"]]
                break

        # Create list of tuples with the name, fqbn, and port
        # that will be used to update the class properties
        boards = [
            (
                matching_boards[board]["name"], 
                matching_boards[board]["fqbn"],
                addresses[board]["address"]) for board in range(0, len(matching_boards)
            )
        ]

        return boards

    def compile_sketch(self):
        """
        Use the CLI to compile the project's Arduino sketch
        """

        print("Compiling Sketch...")

        compile_sketch = sp.run(
            [
                "arduino-cli",
                "compile",
                "--fqbn",
                self.fqbn,
                str(self.sketch_path),
                "-v",
                "--format",
                "json"
            ],
            capture_output=True
        )

        compile_output = json.loads(compile_sketch.stdout.decode())

        if compile_output["success"]:
            print("Sketch compiled successfully!")
        
        # TODO: Things like this should be logged...
        else:
            print("COMPILATION ERROR!!! Error in Arduino Script!")
            print(compile_output)
            print(compile_sketch.stderr.decode())   
            sys.exit()

    def upload_sketch(self):
        """
        Use the CLI to upload the sketch to the Arduino.
        """

        print("Uploading Sketch...")

        upload_sketch = sp.run(
            [
                "arduino-cli",
                "upload",
                "-p",
                self.board_com,
                "--fqbn",
                self.fqbn,
                str(self.sketch_path),
                "--format",
                "json",
                "--verbose"
            ],
            capture_output=True
        )

        # TODO: Another thing that should be logged
        if upload_sketch.returncode:
            print("UPLOAD FAILURE! Serial Monitor Open Elsewhere?")
            print(upload_sketch.stdout.decode())
            print(upload_sketch.stderr.decode())
            sys.exit()
        else:
            print("Upload successful!")


###############################################################################
# Exceptions
###############################################################################


class SketchError(Exception):
    """
    Exception for when there's an error finding or using an Arduino sketch.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "SketchError: " + "{0}".format(self.message)
        else:
            return "SKETCH ERROR"


###############################################################################
# Functions
###############################################################################


def upload_arduino_sketch(project: Path):
    """
    Takes project name running experiment and finds sketch, uploads to board.

    Uses project name to grab .ino file for given team, compiles it, and
    finally sends it to the Arduino using the arduino-cli.

    Args:
        project:
            The team and project conducting the experiment (ie teamname_projectname)
    """

    # Currently teams that have separate projects use just one sketch (by design for now...)
    # The teamname is just the first part of the project name separated by an "_".
    team_name = project.split("_")[0]

    # Assemble what should be the full path of the Arduino sketch in use
    project_sketch = SKETCH_PATHS / ("bruker_disc_" + team_name)

    # Glob whatever sketch is found inside the directory
    arduino_sketches = [sketch for sketch in project_sketch.glob("*.ino")]

    # If the length of the list for the sketch is greater than 1,
    # something is wrong. Raise an exception.    
    if len(arduino_sketches) > 1:
        raise SketchError(
        "Project has multiple Arduino sketches! Check your local bruker_control repo in your project's sketch folder."
        )

    # Otherwise, try to load the one present file. If it's not there,
    # an index error occurs and an exception is raised.
    else:
        try:
            arduino_sketch = arduino_sketches[0]

        except IndexError:
            raise SketchError(
                "Project Arduino sketch is missing! Check your local bruker_control repo in your project's sketch folder."
                )
    
    # Tell the user that their sketch was found.
    # TODO This should all be piped to a logs file of some sort...
    # and ideally it would all be part of the Arduino object...
    print("Sketch found!")

    # Initialize Arduino object
    arduino = Arduino(arduino_sketch)

    # Use instance method to compile the sketch
    arduino.compile_sketch()

    # # Use instance method to upload to board
    arduino.upload_sketch()


def transfer_data(arduino_metadata: str, experiment_arrays: list):
    """
    Sends metadata and trial information to the Arduino.

    Takes each array assembled for transmission to the Arduino and stuffs it
    into packets to be sent via pySerialTransfer. Unites several functions used
    for transmitting, receiving, and checking data during transfer.

    Args:
        arduino_metadata:
            Metadata gathered from config_template that's relevant for Arduino
            runtime. Formatted as a json string.
        experiment_arrays:
            List of arrays generated for a given microscopy session's behavior.
            0th index is trialArray, 1st is ITIArray, 2nd is toneArray, and 3rd
            is the LEDArray.

    """

    try:
        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Start communicating with the Arduino
        link.open()

        transfer_metadata(arduino_metadata, link)

        transfer_experiment_arrays(experiment_arrays, link)

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


def transfer_experiment_arrays(experiment_arrays: list,
                               link: txfer.SerialTransfer):
    """
    Transfers experimental arrays to Arduino via pySerialTransfer.

    Determines what type of packet transfer is required (single or multi) for
    the generated trials.  If the number of trials is greater than 60, then
    multiple packets are required for transferring each array.  If less, then
    only one packet is required for each array.

    Args:
        experiment_arrays:
            List of arrays generated for a given microscopy session's behavior.
            0th index is trialArray, 1st is ITIArray, 2nd is toneArray, 3rd is
            the LEDArray.
        link:
            pySerialTransfer transmission object
    """

    if len(experiment_arrays[0]) > 60:

        multipacket_transfer(experiment_arrays, link)

    else:

        onepacket_transfer(experiment_arrays, link)


###############################################################################
# Serial Transfer to Arduino: Error Checking
###############################################################################


def array_error_check(transmitted_array: list, received_array: list):
    """
    Performs Python side error checking for array transmission.

    While pySerialTransfer performs error checking for different errors, this
    allows for something simple that is independent of the package for error
    checking.

    Args:
        transmitted_array:
            Array that was sent to the Arduino
        received_array:
            Array that was received by the Arduino
    """

    # If the transmitted array and received array are equal
    if transmitted_array == received_array:

        pass

    # TODO: Raise an exception here that quits the program
    # If the transmission failed
    else:

        # Tell the user an error occured
        print("Transmission Error!")

        # Tell the user the program is exiting
        print("Exiting...")

        # Exit the program
        sys.exit()


###############################################################################
# Serial Transfer to Arduino: One Packet
###############################################################################


# -----------------------------------------------------------------------------
# Send an Individual Packet
# -----------------------------------------------------------------------------


def transfer_packet(array: list, packet_id: int, link: txfer.SerialTransfer):
    """
    Transfers an individual packet to the Arduino.

    Each packet is given a unique ID the Arduino can identify and transmitted
    through the pySerialTransfer link. While the link is unavailable, that is
    there's an active transfer, the function passes. When finished
    transmitting, the function receives what the Arduino encoded and an error
    check is performed. If it passes, the program continues.  If it fails,
    an exception is raised and the program exits.

    Args:
        array:
            Experimental array to be transferred
        packet_id:
            Unique ID for encoding an array
        link:
            pySerialTransfer transmission object
    """

    try:

        # Initialize array_size of 0
        array_size = 0

        # Stuff packet with size of experiental array
        array_size = link.tx_obj(array)

        # Send the array
        link.send(array_size, packet_id=packet_id)

        # While transferring, the link is unavailable.  While this happens,
        # pass.
        while not link.available():
            pass

        # Receive trial array:
        rxarray = link.rx_obj(obj_type=type(array),
                              obj_byte_size=array_size,
                              list_format='i')

        array_error_check(array, rxarray)

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
# Configuration/Metadata File Transfer
# -----------------------------------------------------------------------------


# TODO: Add error checking function for configuration
def transfer_metadata(arduino_metadata: str, link: txfer.SerialTransfer):
    """
    Transfers arduino_metadata to the Arduino.

    Arduino metadata collected from config_template is formatted into a json
    string that the Arduino knows how to interpret.  Each variable is encoded
    according to a specific byte size depending on the variable type.

    Args:
        arduino_metadata:
            Metadata gathered from config_template that's relevant for Arduino
            runtime. Formatted as a json string.
        link:
            pySerialTransfer transmission object
    """

    try:

        # stuff TX buffer (https://docs.python.org/3/library/struct.html#format-characters)
        metaData_size = 0
        metaData_size = link.tx_obj(arduino_metadata['totalNumberOfTrials'],       metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(arduino_metadata['punishTone'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['rewardTone'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['USDeliveryTime_Sucrose'],    metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['USDeliveryTime_Air'],        metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['USConsumptionTime_Sucrose'], metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['stimDeliveryTime_Total'],    metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['USDelay'],                   metaData_size, val_type_override='H')
        # val_type_override not needed because it's a built in Python type (https://github.com/PowerBroker2/pySerialTransfer/issues/64#issuecomment-1272163696)
        metaData_size = link.tx_obj(arduino_metadata['lickContingency'],           metaData_size)

        # Send the metadata to the Arduino.  The metadata is transferred first
        # and therefore receives the packet_id of 0.
        link.send(metaData_size, packet_id=0)

        # While sending the data, the link is unavailable.  Pass this state
        # until done.
        while not link.available():
            pass

        # Receive packet from Arduino
        # Create rxmetaData dictionary
        rxmetaData = {}

        # Start rxmetaData reception size of 0
        rxmetaData_size = 0

        # Receive each field from the Arduino
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
        rxmetaData_size += txfer.ARRAY_FORMAT_LENGTHS['H']
        rxmetaData['stimDeliveryTime_Total'] = link.rx_obj(obj_type='H', start_pos=rxmetaData_size)


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
# Trial Array Transfers: One Packet
# -----------------------------------------------------------------------------


def onepacket_transfer(experiment_arrays: list, link: txfer.SerialTransfer):
    """
    Function for completing experiment arrays one packet transfers to Arduino.

    Iterates over transfer_packet() function for each experiment array and
    invoked if the session length is less than or equal to 60 trials.  Finally
    invokes the update_python_status() function to say transmission is
    complete.

    Args:
        experiment_arrays:
            List of arrays generated for a given microscopy session's behavior.
            0th index is trialArray, 1st is ITIArray, 2nd is toneArray.
        link:
            pySerialTransfer transmission object
    """

    # Start out transmission with packet_id of 1.  The 0th packet is the
    # arduino_metadata variable
    packet_id = 1

    # For each array in the list of arrays defining trial data
    for array in experiment_arrays:

        # Transfer the packet
        transfer_packet(array, packet_id, link)

        packet_id += 1

    # Once all arrays are transferred, send signal that Python is ready to
    # continue!
    update_python_status(packet_id, link)


###############################################################################
# Serial Transfer to Arduino: Multi-packet
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Splitting for Multipacket Transfers
# -----------------------------------------------------------------------------


def split_multipacket_array(array):

    # This function receives a large list of trial variables.  It needs to be
    # split into two arrays using np.array_split.
    split_ndarray = np.array_split(array, 2)

    # Return the split numpy arrays
    return split_ndarray


# -----------------------------------------------------------------------------
# Trial Array Transfers: Multi-packet
# -----------------------------------------------------------------------------


def multipacket_transfer(array_list):

    packet_id = 1
    # For each array in the list of trial arrays
    for array in array_list:

        # Split the array into packets small enough to transfer
        split_array = split_multipacket_array(array)

        # Transfer the arrays as multiple packets
        transfer_arrays_multipacket(split_array, packet_id)
        # multipacket_dev(split_array, packet_id)

        packet_id += 1


def transfer_arrays_multipacket(split_array, packet_id):

    # For each array received by the splitting function
    for array in split_array:

        # Save the array as a list for transfer
        array = array.tolist()

        # Send the array
        transfer_packet(array, packet_id)

        # Increment the packet number for sending next array
        packet_id += 1


def multipacket_dev(split_array, packet_id):

    print(packet_id)
    new_array = []

    for array in split_array:
        new_array.append(array.tolist())

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize array_size of 0
        first_array_size = 0
        second_array_size = 0

        # Stuff packet with size of trialArray
        first_array_size = link.tx_obj(new_array[0])

        # Open communication link
        link.open()

        # Send array
        link.send(first_array_size, packet_id=packet_id)

        # print("Sent Array")
        # print(new_array[0])

        while not link.available():
            pass

        # Receive trial array:
        first_rxarray = link.rx_obj(obj_type=type(new_array[0]),
                                    obj_byte_size=first_array_size,
                                    list_format='i')

        # print("Received Array")
        # print(first_rxarray)

        packet_id += 1

        second_array_size = link.tx_obj(new_array[1])

        link.send(second_array_size, packet_id=packet_id)

        while not link.available():
            pass

        second_rxarray = link.rx_obj(obj_type=type(new_array[1]),
                                     obj_byte_size=second_array_size,
                                     list_format='i')

        # print(second_rxarray)
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


###############################################################################
# Serial Transfer to Arduino: Python Status
###############################################################################


def update_python_status(packet_id: int, link: txfer.SerialTransfer):
    """
    Updates python side of program as ready to continue post serial transfer.

    Once the packets have all been transmitted to the Arduino, this final step
    is performed to ensure that all information has made it across the link.
    Once this check is passed, the connection to the Arduino closes and the
    experiment will start!

    Args:
        packet_id:
            Unique ID for encoding an array
        link:
            pySerialTransfer transmission object
    """

    try:

        status = 1

        # Stuff packet with size of trialArray
        status_size = link.tx_obj(status)

        # Send array
        link.send(status_size, packet_id=packet_id)

        print("Sent END OF TRANSMISSION Status")

        while not link.available():
            pass

        # Receive trial array:
        rxarray = link.rx_obj(obj_type=type(status),
                              obj_byte_size=status_size,
                              list_format='i')

        print("Received END OF TRANSMISSION Status")

        array_error_check(status, rxarray)

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
