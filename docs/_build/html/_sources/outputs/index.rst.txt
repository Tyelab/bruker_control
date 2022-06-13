##############
System Outputs
##############

.. image:: ../images/bruker_logo.jpg
    :alt: Bruker Microscopy's Logo

**************
Raw File Types
**************

Every 2P experiment generates imaging and voltage recording data, a configuration file for the behavior experiment, and a video recording of the subject's face.
The imaging data is the recording of the neural tissue that's fluorescing after being stimulated by the powerful laser.
The voltage recording data is from Bruker's DAQ box sampling voltage inputs to its many BNC connections that come from the activity of solenoids, stimulating LEDs, PMT shutters,and the animal's licking behavior.
Each of these datasets contain their own file formats.

If a project uses the whole field LED stimulation module for their experiment, additional file formats are generated for the MarkPoints and VoltageOutput functions.

The naming conventions used in Bruker Control are ISO 8601 compliant for date information and descriptive for each data stream recorded.


==============================
2-Photon Experiment File Types
==============================

There are several different files that are made during the multi-photon imaging.

Imaging Files
=============

Raw "Cycle" Files
-----------------
Each recording has an associated "CYCLE" number which is related to the number of different experiments you run in a given 2P experiment.
So far in the lab, every recording uses just one cycle to gather images.

These "Cycle" files are the raw data files coming directly off the microscope. They have the following structure:

* CYCLE_CYCLE#_RAWDATA_INCREMENT
    * Example: CYCLE_000001_RAWDATA_001000

The INCREMENT is increased by one per file internally in Prairie View during the recording.
This is done to ensure that each RAW file has a unique ID so new recordings can't overwrite old recordings that might be present on the file system.
It's extremely unlikely that an overwrite due to something like this would occur given how separate recordings are by design in bruker_control.py and especially Prairie View's output of files.

The max size for these files is 2.048GB.
For a particular imaging experiment at approximately 30 FPS for 25 minutes, you can expect about 35 of them.
The files are encoded with a 13-bit image depth at a resolution of 512x512. In total, with these parameters, approximately 2.8GB are generated per minute.
Note that transferring a typical full day of imaging (6-7 mice) takes approximately 5 hours to send over the network on the available 1GB line.

Raw .txt File
--------------
Prairie View tracks each raw data Cycle from an imaging experiment in a .txt file that's has its contents encoded in binary presumably.
You won't be able to open this file in a text editor and be able to read it yourself.
It's this file that the Image Ripper uses to know which Cycles to expect and then process into .OME.tiff files.

They have the following structure:

* CycleCYCLE#_Filelist
    * Example: Cycle00001_Filelist

Raw .xml File
-------------
Prairie View relies upon the use of XML v1.0, or Extensible Markup Language, for tracking many different properties about the microscope's state during recording.
The Raw .xml file keeps track of the frames that are gathered, the timestamp of each frame, and the name that each file will be called after the ripping process is complete.

Note that when using the stimulation features of Prairie View, errors can be encountered later as they implement XML v1.1. See below for notes about these errors.

These have the following structure:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw.env
    * Example: ``20211108_CSC20_plane1_-747.7_raw.env``

Converted .ome.tif Files
------------------------
Bruker's "ripper" performs conversions from their raw binary formats into OME Tiffs.
Unfortunately, it only outputs individual images and has no option to output multi-page tiffs at the moment.
The conversion of these many individual tiffs to HDF5 or Zarr can be handled either through MATLAB scripts or Python via `bruker_pipeline <https://github.com/Tyelab/bruker_pipeline>`_.

The first OME Tif has metadata about all the images collected as well, but as of right now the OME information is discarded.
A future development should be to save this metadata either in the H5 file that's created or, if Zarr is used, by writing to OME Zarr.

These tiffs are named like this:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw_TIF#.ome.tif
    * ``20211108_CSC20_plane1_-747.7_raw_000001.ome.tif``

.. _XML Errors:

XML 1.1 in Environment Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When using Prairie View's stimulation ability, Bruker's software inserts characters into the .env files that are not supported until XML v1.1.
When trying to parse the file, Python's built in XML Parser will throw an exception and fail because it is attempting to use v1.0 as defined in the .env file.
Use of the lxml library with the option recover=True will catch the exception and pass over the line that's throwing the error.
Code that illustrates this can be found `here <https://github.com/Tyelab/bruker_pipeline/blob/main/nwb_utils.py>`_ in the file nwb_utils.py in bruker_pipeline.

As of this writing, it is unknown what MATLAB's XML parser will do when it encounters this.

Bruker has been informed of this mismatch between characters that are inserted into the file and the version of XML that is used.
They have stated they are stuck with XML v1.0 in part because many software like MATLAB require v1.0 and also because Microsoft has failed to fix this problem for the past few decades.

Voltage Recording Files
=======================

The voltage recording generates files very similar to the imaging data stream.
This functionality is used to measure the timings of when ITIs are running, when solenoids open and close, when the mouse licks, and when optogenetic stimulations occur.

Raw Voltage Recording "Cycle" File
----------------------------------
Voltage recordings are associated with a "CYCLE" number just as imaging recordings are.
Unlike the imaging files however, where there are many RAWDATA files, there is typically only one raw file that takes the name generated by bruker_control.

It has the following structure:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw-INCREMENT-Cycle#_VoltageRecording_001
    * Example: ``20211108_CSC20_plane1_-747.7_raw-018_Cycle00001_VoltageRecording_001``

Raw Voltage Recording .XML File
-------------------------------
The Voltage Recording's .xml is written in XML v1.0 and primarily tracks the names of each channel recorded on the DAQ and the time that the recording was actually started.
This is used when aligning the timestamps of the imaging frames as well as the during the ripping process. 
Note that when using the stimulation features of Prairie View, errors can be encountered later as they implement XML v1.1. See :ref:`XML Errors` above.

These have the following structure:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw-INCREMENT-Cycle#_VoltageRecording_001.xml
    * Example: ``20211108_CSC20_plane1_-747.7_raw-018_Cycle00001_VoltageRecording_001.xml``

Raw Voltage Recording .txt File List
------------------------------------
Prairie View tracks Raw "Cycles" with a .txt file for the Voltage Recording the same way as imaging recordings.
It's this file that the Image Ripper uses to know which Cycles to expect and then process into a .csv file.

These have the following structure:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION_raw-INCREMENT-Cycle#_VoltageRecording_001_VRFilelist.txt
    * Example: ``20211108_CSC20_plane1_-747.7_raw-018_Cycle00001_VoltageRecording_001_VRFilelist.txt``

Facial Expression Videos
========================

The subject's face is recorded with the use of a Teledyne Genie Nano machine vision camera and encoded into a .mp4 file using the ffmpeg library and OpenH264 during the experiment.

These videos have the following structure:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION.mp4

These could be processed later into arrays of HOGs and HOG images through `this <https://github.com/Tyelab/MouseFacialExpressionAnalysis>`_ repository or on a Trial by Trial basis through
MATLAB code that's been written.

Configuration Files
===================
A .json encoded configuration file is generated at the time of the experiment that contains relevant metadata about the experiment being conducted:

* Trial structure rules
*  The trial structure itself
*  ITI durations
*  Tone durations
*  LED offset timings
*  A list of dropped frames if any packets were dropped during the experiment

This information can be used later for generating the behavior data sets after processing has been completed.

These files are named as follows:

* YYYYMMDD_SUBJECTID_PLANE#_PLANELOCATION.json
