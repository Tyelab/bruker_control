# Bruker 2-Photon Serial Transfer Utils
# Jeremy Delahanty May 2021
# pySerialTransfer written by PowerBroker2
# https://github.com/PowerBroker2/pySerialTransfer

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

# Import Tuple for appropriate typehinting of functions
from typing import Tuple

###############################################################################
# Functions
###############################################################################


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
            0th index is trialArray, 1st is ITIArray, 2nd is toneArray.

    """

    try:
        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

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


def transfer_experiment_arrays(experiment_arrays: list, link: txfer):
    """
    Transfers experimental arrays to Arduino via pySerialTransfer.

    Determines what type of packet transfer is required (single or multi) for
    the generated trials.  If the number of trials is greater than 60, then
    multiple packets are required for transferring each array.  If less, then
    only one packet is required for each array.

    Args:
        experiment_arrays:
            List of arrays generated for a given microscopy session's behavior.
            0th index is trialArray, 1st is ITIArray, 2nd is toneArray.
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

        # Tell the user the transfer was successful
        print("Successful Transfer")

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


def transfer_packet(array: list, packet_id: int, link: txfer):
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
def transfer_metadata(arduino_metadata: str, link: txfer):
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
        metaData_size = link.tx_obj(arduino_metadata['metadata']['totalNumberOfTrials'],       metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(arduino_metadata['metadata']['punishTone'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['metadata']['rewardTone'],                metaData_size, val_type_override='H')
        metaData_size = link.tx_obj(arduino_metadata['metadata']['USDeliveryTime_Sucrose'],    metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(arduino_metadata['metadata']['USDeliveryTime_Air'],        metaData_size, val_type_override='B')
        metaData_size = link.tx_obj(arduino_metadata['metadata']['USConsumptionTime_Sucrose'], metaData_size, val_type_override='H')

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

        print(rxmetaData)

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


def onepacket_transfer(experiment_arrays: list, link: txfer):
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
    update_python_status(packet_id)


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


def update_python_status(packet_id: int, link: txfer):
    """
    Updates python side of program as ready to continue post serial transfer.

    Once the packets have all been transmitted to the Arduino, this final step
    is performed to ensure that all information has made it across the link.
    Once this check is passed, the experiment will start!

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
