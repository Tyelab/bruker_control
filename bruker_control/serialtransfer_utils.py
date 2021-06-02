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

###############################################################################
# Functions
###############################################################################


###############################################################################
# Serial Transfer to Arduino: Error Checking
###############################################################################


def array_error_check(transmitted_array, received_array):

    # If the transmitted array and received array are equal
    if transmitted_array == received_array:

        # Tell the user the transfer was successful
        print("Successful Transfer")

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


# TODO: Open connection once per experiment instead of once per packet transfer
def transfer_packet(array, packet_id):

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize array_size of 0
        array_size = 0

        # Stuff packet with size of trialArray
        array_size = link.tx_obj(array)

        # Open communication link
        link.open()

        # Send array
        link.send(array_size, packet_id=packet_id)

        print("Sent Array")
        print(array)

        while not link.available():
            pass

        # Receive trial array:
        rxarray = link.rx_obj(obj_type=type(array),
                              obj_byte_size=array_size,
                              list_format='i')

        print("Received Array")
        print(rxarray)

        # Close the communication link
        link.close()

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
def transfer_metadata(config):

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

        # Open comms to Arudino
        link.open()

        # Send the metadata to the Arduino
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

        # Close comms to the Arduino
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
# Trial Array Transfers: One Packet
# -----------------------------------------------------------------------------


def onepacket_transfers(array_list):

    # Give each new packet an ID of 0.  The link is closed per packet
    # transmission.
    packet_id = 0

    # For each array in the list of arrays defining trial data
    for array in array_list:

        # Transfer the packet
        transfer_packet(array, packet_id)


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

    packet_id = 0
    # For each array in the list of trial arrays
    for array in array_list:

        # Split the array into packets small enough to transfer
        split_array = split_multipacket_array(array)

        # Transfer the arrays as multiple packets
        transfer_arrays_multipacket(split_array, packet_id)
        # multipacket_dev(split_array, packet_id)

        packet_id = 0


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
        obj_byte_size=second_array_size, list_format='i')

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


def update_python_status():

    try:

        # Initialize COM Port for Serial Transfer
        link = txfer.SerialTransfer('COM12', 115200, debug=True)

        # Initialize array_size of 0
        array_size = 0

        array = 1

        # Stuff packet with size of trialArray
        array_size = link.tx_obj(array)

        # Open communication link
        link.open()

        # Send array
        link.send(array_size, packet_id=0)

        print("Sent END OF TRANSMISSION Status")

        while not link.available():
            pass

        # Receive trial array:
        rxarray = link.rx_obj(obj_type=type(array),
                              obj_byte_size=array_size,
                              list_format='i')

        print("Received END OF TRANSMISSION Status")

        array_error_check(array, rxarray)

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
