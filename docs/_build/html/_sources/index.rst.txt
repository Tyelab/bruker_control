.. Bruker Control documentation master file, created by
   sphinx-quickstart on Thu Aug 12 12:03:00 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Bruker Control's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

video_utils.py
==============

Module contains functions for configuring GenICam compliant cameras as well as
grabbing, displaying, and writing video frames the cameras acquire. It has
been written with flexibility of number of cameras in mind, but has only been
tested using one camera so far.

.. currentmodule:: video_utils

init_camera_preview
-------------------

.. autofunction:: init_camera_preview

capture_preview
---------------

.. autofunction:: capture_preview

init_camera_recording
---------------------

.. autofunction:: init_camera_recording

capture_recording
-----------------

.. autofunction:: capture_recording

shutdown_camera
---------------

.. autofunction:: shutdown_camera


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
