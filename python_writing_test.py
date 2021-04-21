import time
import random
from numpy.random import default_rng
from pySerialTransfer import pySerialTransfer as txfer

# Define Total Number of Trials
total_number_trials = 10

# TODO: Send these experiment variables over Serial Comms
# Define Noise Duration
noise_duration = 2000 # 2s

# Define Sucrose Delivery Time
sucrose_delivery_time = 5 # 5ms

# Define Airpuff Delivery Time
airpuff_delivery_time = 10 # 10ms

# Define Sucrose Consumption Time
sucrose_consumption_time = 1000 # 1s

# TODO: Generate pseudorandom trials with Aneesh's script
# Define trial types: 0 = airpuff, 1 = sucrose
trial_types = [0,1]
# Define probabilities for each value: 50%, 50%
probs = [0, 1]

# Per numpy documentation, use default_rng() as generator
rng = default_rng(1)
# Create trials_array using .choice method, 20 instances, allow replacement,
# use linked probabilities
trials_array = rng.choice(trial_types, 40, replace=True,  p=probs)

# default_rng.choice() creates numpy.ndarray; must be list for txfer
trials_array = trials_array.tolist()

# Define Base ITI
base_iti = 3000 # 3s

# Define Jitter



print("Trial List Created")

if __name__ == '__main__':
    try:
        link = txfer.SerialTransfer('COM12', 115200, debug=True) ########## replace COM port number ##########
        link.open()

        while True:
            list_ = trials_array

            list_size = link.tx_obj(list_)
            link.send(list_size)
            print("Sent:\t\t{}".format(list_))

            while not link.available():
                pass

            rec_list_ = link.rx_obj(obj_type=type(list_),
                                    obj_byte_size=list_size,
                                    list_format='i')
            print("Received:\t{}".format(rec_list_))
            print("")
            time.sleep(1)

            if list_ == rec_list_:
                print("Confirmed!")
                try:
                    link.close()
                    break
                except:
                    print("Error!")
                    break

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
