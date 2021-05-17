# Bruker 2-Photon Trial Generation Utils
# Jeremy Delahanty May 2021

###############################################################################
# Import Packages
###############################################################################

# Trial Array Generation
# Import scipy.stats truncated normal distribution for ITI Array
from scipy.stats import truncnorm

# Import numpy for trial array generation/manipulation and Harvesters
import numpy as np

# Import numpy default_rng
from numpy.random import default_rng


###############################################################################
# Functions
###############################################################################


# -----------------------------------------------------------------------------
# Trial Array Generation
# -----------------------------------------------------------------------------


def gen_trialArray(trials):

    # Always initialize trial array with 3 reward trials
    trialArray = [1, 1, 1]

    # Define number of samples needed from generator
    num_samples = trials - len(trialArray)

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

    # TODO: Write out the trial array into JSON as part of experiment config

    # Return trialArray
    return trialArray

# -----------------------------------------------------------------------------
# ITI Array Generation
# -----------------------------------------------------------------------------


def gen_ITIArray(trials):

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
                              size=trials
                             )

    # ITI Array generated will have decimals in it and be float type
    # Use np.round() to round the elements in the array and type them as int
    iti_array = np.round(iti_array).astype(int)

    # Finally, generate ITIArray as a list for pySerialTransfer
    ITIArray = iti_array.tolist()

    # Return ITI Array
    return ITIArray


# -----------------------------------------------------------------------------
# Noise Array Generation
# -----------------------------------------------------------------------------


def gen_noiseArray(trials):

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
                                size=trials
                                )

    # Noise Array generated will have decimals in it and be float type.
    # Use np.round() to round the elements in the array and type them as int.
    noise_array = np.round(noise_array).astype(int)

    # Finally, generate noiseArray as a list for pySerialTransfer.
    noiseArray = noise_array.tolist()

    # Return the noiseArray
    return noiseArray


# -----------------------------------------------------------------------------
# Generate Arrays function to unite these functions
# -----------------------------------------------------------------------------


def generate_arrays(trials):

    # Create Trial Array
    trialArray = gen_trialArray(trials)

    # Create ITI Array
    ITIArray = gen_ITIArray(trials)

    # Create Noise Array
    noiseArray = gen_noiseArray(trials)

    # Put them together in a list
    array_list = [trialArray, ITIArray, noiseArray]

    # Return list of arrays to be transferred
    return array_list
