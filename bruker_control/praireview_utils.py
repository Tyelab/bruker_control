# Bruker 2-Photon Prairie View Utils
# Jeremy Delahanty May 2021
# Written with assistance from Michael Fox, Sr Software Engineer Bruker

###############################################################################
# Import Packages
###############################################################################
###############################################################################
# Import Packages
###############################################################################

# Import Prairie View Application
# NOTE Prairie View Interface Installation:  Do NOT use pip install, use conda.
# conda install pywin32
import win32com.client

# Import pathlib for file manipulation and directory creation
from pathlib import Path

# Save the Praire View application as pl
pl = win32com.client.Dispatch("PrairieLink.Application")

# Get current working directory for above paths to work
current_dir = Path.cwd()

###############################################################################
# Functions
###############################################################################

# -----------------------------------------------------------------------------
# PrairieLink Connect Function
# -----------------------------------------------------------------------------


def prairie_connect():
    print("Connecting to Prairie View")
    pl.Connect()
    print("Connected to Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Disconnect Function
# -----------------------------------------------------------------------------


def prairie_disconnect():
    print("Disconnecting from Prairie View")
    pl.disconnect()
    print("Disonnected from Prairie View")


# -----------------------------------------------------------------------------
# PrairieLink Abort Function
# -----------------------------------------------------------------------------


def prairie_abort():
    print("Aborting Recording...")
    prairie_connect()
    pl.SendScriptCommands("-Abort")
    prairie_disconnect()


# -----------------------------------------------------------------------------
# PrairieLink Set Directory Function
# -----------------------------------------------------------------------------


def prairie_dir_and_filename(project_name, config_filename):
    print("Setting Directory")
    microscopy_basepath = "E:/studies/" + project_name + "/microscopy/"
    microscopy_filename = config_filename
    microscopy_fullpath = microscopy_basepath + microscopy_filename

    prairie_connect()
    pl.SendScriptCommands("-SetSavePath" "{%s}" (microscopy_fullpath))
    print("Set 2P Image Path: " + microscopy_fullpath)

    pl.SendScriptCommands("-SetFileName" "type (Tseries)" "{%s}" (microscopy_filename))
    prairie_disconnect()
