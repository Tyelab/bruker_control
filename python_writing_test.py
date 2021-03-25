import time
import random
from numpy.random import default_rng
from pySerialTransfer import pySerialTransfer as txfer

# Define trial types: 0 = airpuff, 1 = sucrose, 2 = ambiguous
trial_types = [0,1,2]
# Define probabilities for each value: 40%, 40%, 20%
probs = [0.4, 0.4, 0.2]

# Per numpy documentation, use default_rng() as generator
rng = default_rng(20)
# Create trials_array using .choice method, 20 instances, allow replacement,
# use linked probabilities
trials_array = rng.choice(trial_types, 20, replace=True, p=probs)
# print(type(trials_array))
# print(trials_array)

# default_rng.choice() creates numpy.ndarray; must be list for txfer
trials_array = trials_array.tolist()

print("Trial List Created")

if __name__ == '__main__':
    # print("Starting tx")
    try:
        link = txfer.SerialTransfer("COM13", 115200)

        link.open()
        # print("Comms Opened")
        time.sleep(2) # give time for Arudino to reset
        # print("Arduino Reset")

        while True:
            send_size = 0

            ###################################################################
            # Send a list
            ###################################################################
            list_ = trials_array
            print(type(trials_array))
            print(type(list_))
            list_size = link.tx_obj(list_)
            send_size += list_size
            link.send(send_size)
            print("Data Sent")

            while not link.available():
                if link.status <0:
                    if link.status == txfer.CRC_ERROR:
                        print("ERROR: CRC_ERROR")
                    elif link.status == txfer.PAYLOAD_ERROR:
                        print("ERROR: PAYLOAD_ERROR")
                    elif link.status == txfer.STOP_BYTE_ERROR:
                        print("ERROR: STOP_BYTE_ERROR")
                    else:
                        print("ERROR: {}".format(link.status))
            ###################################################################
            # Parse response list
            ###################################################################
            print("Receiving Response")
            rec_list_  = link.rx_obj(obj_type=type(list_),
                                     obj_byte_size=list_size,
                                     list_format='i')
            ###################################################################
            # Display the received data
            ###################################################################
            print('SENT: {}'.format(list_))
            print('RCVD: {}'.format(rec_list_))
            print(' ')

            if list_ == rec_list_:
                print("Confirmed!")
                try:
                    link.close()
                except:
                    print("Error!")
                    break
            # TODO: Add packet checking and retry if there's an error in comms


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
