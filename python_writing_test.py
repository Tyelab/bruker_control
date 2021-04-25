import random
import scipy
from scipy.stats import truncnorm
import numpy
from numpy.random import default_rng
from pySerialTransfer import pySerialTransfer as txfer

#### Trials ####
# Define Total Number of Trials
totalNumberOfTrials = 10
# Initialize trial number 1
trialNumber = 1

# TODO: Send these experiment variables over Serial Comms
#### Sound ####
# Define Noise Duration
noiseDuration = 2000 # 2s
# Define Punish Tone in Hz
punishTone = 2000
# Define Reward Tone
rewardTone = 18000

#### Sucrose ####
# Define Sucrose Delivery Time
USDeliveryTime_Sucrose = 5 # 5ms
# Define Sucrose Consumption Time
USConsumptionTime_Sucrose = 1000 # 1s

#### Airpuff ####
# Define Airpuff Delivery Time
USDeliveryTime_Air = 10 # 10ms

#### Trial Functions ####
# Random Trials Array Generation
def gen_trial_array(totalNumberOfTrials):
    # Always initialize trial array with 3 reward trials
    trial_array = [1,1,1]
    # Define number of samples needed from generator
    num_samples = totalNumberOfTrials - 3
    # Define probability that the animal will receive sucrose 60% of the time
    sucrose_prob = 0.60
    # Initialize random number generator with default_rng
    rng = np.random.default_rng()
    # Generate a random trial array with Generator.binomial
    # Use n=1 to pull one sample at a time, p=.5 as probability of sucrose
    # Use num_samples to fill out accurate number of trials
    # Use .tolist() to convert random_trials from np.array to list
    random_trials = rng.binomial(
    n=1, p=sucrose_prob, size=num_samples
    ).tolist()
    # Append the two arrays together
    for i in random_trials:
        trial_array.append(i)

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

    return ITIArray







print("Trial List Created")

if __name__ == '__main__':
    try:
        link = txfer.SerialTransfer('COM12', 115200, debug=True)
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
