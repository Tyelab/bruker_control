======================================
Bruker Control's Functions and Classes
======================================

**************
video_utils.py
**************

Module contains functions for configuring GenICam compliant cameras as well as
grabbing, displaying, and writing video frames the cameras acquire. It has
been written with flexibility of number of cameras in mind, but has only been
tested using one camera so far.

.. currentmodule:: video_utils

.. automodule:: video_utils
  :members:

**************
trial_utils.py
**************

Module contains functions for interpreting configuration file parameters and
using them for generating pseudorandom trial arrays following user defined
rules with the capability of producing catch trials in given subsets of the
trial order, for generating ITIs from a uniform random distribution between
bounds defined by the user, and tone durations that vary between user
defined bounds.

.. currentmodule:: trial_utils

.. automodule:: trial_utils
  :members:

***************
config_utils.py
***************

Module contains functions for reading, writing, and passing configuration
information to different modules or files including NWB files.

.. currentmodule:: config_utils

.. automodule:: config_utils
  :members:

********************
prairieview_utils.py
********************

Module contains functions for interacting with Prairie View's API to set data
directories, filenames, and gathering imaging plane information. Also sets
microscope laser values according to user presets and initiates image acquisition.

.. currentmodule:: prairieview_utils

.. automodule:: prairieview_utils
  :members:

***********************
serialtransfer_utils.py
***********************

Module contains functions for sending, receiving, and checking trial information
to the Arduino delivering stimuli via pySerialTransfer.

.. currentmodule:: main/serialtransfer_utils

.. automodule:: serialtransfer_utils
  :members:

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
