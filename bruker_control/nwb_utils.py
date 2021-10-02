# Bruker 2-Photon NWB Utils
# Jeremy Delahanty August 2021
# Neurodata Without Borders at https://nwb.org/
# pyNWB at https://github.com/NeurodataWithoutBorders/pynwb
# pyNWB docs at https://pynwb.readthedocs.io/en/stable/
# Assistance from Chris Roat, Stanford University Deisseroth Lab August 2021
# https://github.com/chrisroat
# https://github.com/deisseroth-lab/two-photon/blob/main/two_photon/metadata.py
# Assistance from Ryan Ly, Lawrence Berkeley National Lab August 2021
# https://github.com/rly

# Import datetime for file grepping and date manipulation
from datetime import datetime
# Import dateutil.tz for timezone functions
from dateutil.tz import tzlocal
# Import datetime parser for getting Bruker's timestamps into correct format
from dateutil import parser as dt_parser
# Import uuid module for generating unique IDs for given recording
import uuid
# Import pathlib for path manipulation and creation
from pathlib import Path
# Import xml.etree for parsing data from Bruker .env files
import xml.etree.ElementTree as ET
# Import YAML for gathering metadata about project
from ruamel.yaml import YAML
# Import Tuple typing for typehints in documentation
from typing import Tuple

# Import necessary pyNWB modules for writing out base NWB file to disk
from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.file import Subject
from pynwb.image import ImageSeries
from pynwb.ophys import OpticalChannel

# NWB Metadata Requirements: Prairie View Keys
# Environment keys at Root node of .env file
pv_env_keys = ["version", "date"]
# State keys at PVStateValue nodes of .env file
pv_state_noidx_keys = ["framerate", "activeMode"]
# State keys at PVStateValue nodes of .env file also containing indexed values
pv_state_idx_keys = {"laserWavelength": 0, "laserPower": 0, "pmtGain": 0}

# Project template configuration directories are within project directories.
# The snlkt server housing these directories is mounted to the X: volume on the
# machine BRUKER.
server_basepath = "X:/"

# Bruker environment files are written to folders within the selected teams'
# directories in the Raw Data volume E: on the machine BRUKER. This is where
# Bruker .env files are written.
env_basepath = "E:/teams/"


def build_nwb_file(experimenter: str, team: str, subject_id: str,
                   imaging_plane: str, subject_metadata: dict,
                   project_metadata: dict, surgery_metadata: dict):
    """
    Builds base NWB file with relevant metadata for session.

    Generates an NWB file and writes it to the project's directory according
    to animal's place along the study (ie baseline).  Unites different
    functions together when buliding the NWB file.

    Args:
        experimenter:
            Experimenter value from the metadata_args["experimenter"]
        team:
            Team value from metadata_args["team"]
        subject_id:
            Subject ID from metadata_args["subject"]
        imaging_plane:
            Plane 2P images were acquired at, the Z-axis value
        surgery_metadata:
            Surgical information about the subject being imaged including the
            types of indicators used and positions of those injections/implants.
    """

    # Get the formatted session_id and newly created session path
    session_id, session_fullpath = gen_session_id(team, subject_id)

    # Parse Bruker's metadata for NWB file
    bruker_metadata = get_bruker_metadata(team, imaging_plane)

    # Build the base NWB file
    nwbfile = gen_base_nwbfile(experimenter, session_id, bruker_metadata,
                               project_metadata)

    # Add imaging information to the NWB file
    nwbfile = append_imaging_info(nwbfile,
        project_metadata,
        bruker_metadata,
        imaging_plane,
        surgery_metadata
        )

    nwbfile = append_subject_info(nwbfile, subject_metadata)

    # TODO: Implement append_behavior_info
    # nwbfile = append_behavior_info(nwbfile)

    print(nwbfile)

    # Write the NWB files to disk
    write_nwb_file(nwbfile, session_fullpath, subject_id, session_id)


def write_nwb_file(nwbfile: NWBFile, session_fullpath: Path, subject_id: str,
                   session_id: str):
    """
    Writes base NWB file to disk

    Receives base NWB file and writes file to disk according to subject's place
    in the study.

    Args:
        nwbfile:
            Base NWB file generated during build_nwb_file()
        session_fullpath:
            Full path to the appropriate session that was just completed for
            the subject
        subject_id:
            Subject ID from metadata_args["subject"]
        session_id:
            Formatted session ID describing the session's place in the broader
            context of the study.
    """

    # Get today's date for file formatting and convert to formatted string
    today = datetime.today()
    today = today.strftime("%Y%m%d")

    # Create filename for the NWB file
    nwb_filename = "_".join([today, subject_id, session_id, "2P"])

    # Append the NWB filename just created to the session path
    nwb_path = session_fullpath / (nwb_filename + ".nwb")

    # Create NWBHDF5IO object and give it the nwb_path, write the file to disk,
    # and close the IO writer.
    io = NWBHDF5IO(nwb_path, mode="w")
    io.write(nwbfile)
    io.close()


def get_bruker_metadata(team: str, imaging_plane: str) -> dict:
    """
    Parses Prairie View .env file for NWB metadata.

    Grabs newly created .env file from Prairie View session and formats
    the information into NWB metadata.

    Args:
        team:
            Team value from metadata_args["team"]
        imaging_plane:
            Plane 2P images were acquired at, the Z-axis value

    Returns:
        bruker_metadata
    """

    # Build base path for microscopy session
    base_env_path = env_basepath + team + "/microscopy/"

    # Get today's date for file formatting and convert to formatted string
    today = datetime.today()
    today = today.strftime("%Y%m%d")

    # Build .env file glob pattern
    env_glob_pattern = f"{today}*{imaging_plane}*/*raw*.env"

    # Glob the current plane's path to find the environment file and put
    # results into a list
    bruker_env_glob = [path for path in
                       Path(base_env_path).glob(env_glob_pattern)]

    # TODO: If there's multiple 2p environment files in one imaging plane's
    # set up there's something wrong. A warning at least or an exception should
    # be raised
    # There will only be one .env file for the globbed files, so grab it's path
    bruker_env_path = bruker_env_glob[0]

    # Parse the Bruker metadata .env, which is formatted as XML, and get the
    # "root" of the XML tree
    metadata_root = ET.parse(bruker_env_path).getroot()

    # Get Prairie View states out of the XML with get_pv_states
    bruker_metadata = get_pv_states(pv_state_idx_keys, pv_state_noidx_keys,
                                    metadata_root)

    return bruker_metadata


def get_pv_states(pv_idx_keys: dict, pv_noidx_keys: list,
                  metadata_root: ET) -> dict:
    """
    Parse Bruker .env file for NWB standard metadata.

    Gets values from Bruker .env file based on selected keys relevant for NWB
    standard.  Parses file for both indexed and non-indexed values.

    Args:
        pv_idx_keys:
            Indexed keys in the .env file
        pv_noidx_keys:
            Keys that are directly accessible in PVStateValues
        metadata_root:
            Parsed XML root from .env tree

    Returns:
        bruker_metadata
    """

    # Use dictionary comprehension for environment values in Root of .env to
    # start the bruker_metadata dictionary
    bruker_metadata = {key: value for key, value in metadata_root.items()}

    # Get start time from .env file and convert to datetime object.  Then add
    # the local timezone information for NWB standard.
    bruker_metadata["date"] = dt_parser.parse(bruker_metadata["date"])
    bruker_metadata["date"] = bruker_metadata["date"].replace(tzinfo=tzlocal())

    # Get metadata that requires indexed values
    pv_idx_metadata = get_idx_states(pv_idx_keys, metadata_root)

    # Append the indexed metadata to bruker_metadata
    for key, value in pv_idx_metadata.items():
        bruker_metadata[key] = value

    # Get metadata that does NOT require indexed values
    pv_noidx_metadata = get_noidx_states(pv_noidx_keys, metadata_root)

    # Append non-indexed metadata to bruker_metadata
    for key, value in pv_noidx_metadata.items():
        bruker_metadata[key] = value

    return bruker_metadata


def get_idx_states(pv_idx_keys: dict, metadata_root: ET) -> dict:
    """
    Gets indexed values from Prairie View .env file.

    Args:
        pv_idx_keys:
            Indexed keys in the .env file
        metadata_root:
            Parsed XML root from .env tree

    Returns:
        pv_idx_metadata
    """

    # Build empty metadata dictionary to append metadata to
    pv_idx_metadata = {}

    # For each key and index requested in the pv_idx_keys, build an xpath for
    # the values and search the metadata root for it.  Finally, append those
    # values to the dictionary.
    for key, idx in pv_idx_keys.items():
        xpath = f".//PVStateValue[@key='{key}']/IndexedValue[@index='{idx}']"
        element = metadata_root.find(xpath)
        pv_idx_metadata[key] = element.attrib["value"]

    return pv_idx_metadata


def get_noidx_states(pv_noidx_keys, metadata_root) -> dict:
    """
    Gets non-indexed values from Prairie View .env file.

    Args:
        pv_noidx_keys:
            Keys that are directly accessible in PVStateValues
        metadata_root:
            Parsed XML root from .env tree

    Returns:
        pv_noidx_metadata
    """

    # Build empty metadata dictionary to append metadata to
    pv_noidx_metadata = {}

    # For the keys in pv_noidx_keys, build an xpath for each one and search the
    # metadata root for it.  Finally, append those values to the dictionary.
    for key in pv_noidx_keys:
        xpath = f".//PVStateValue[@key='{key}']"
        element = metadata_root.find(xpath)
        pv_noidx_metadata[key] = element.attrib["value"]

    return pv_noidx_metadata


def gen_base_nwbfile(experimenter: str, session_id: str,
                     bruker_metadata: dict, project_metadata: dict) -> NWBFile:

    """
    Build base NWB file with appropriate metadata.

    NWB Files require a set of metadata for the proper instantiation of NWB
    compliant datasets.  This generates a base NWB file and gathers the needed
    metadata for it so the data and configuration files can be appended to it
    immediately after the session is complete.

    Args:
        experimenter:
            Experimenter value from the metadata_args["experimenter"]
        team:
            Team value from metadata_args["team"]
        subject_id:
            Subject ID from metadata_args["subject"]
        session_id:
            Appropriately set value for session_id NWB parameter.
        bruker_metadata:
            Metadata for NWB parsed from Prairie View XML and env files.
        project_metadata:
            Metadata obtained from team project's YAML file.

    Returns:
        nwbfile:
            NWB File with basic metadata for session
    """

    nwbfile = NWBFile(
        session_description=project_metadata["session_description"] ,
        identifier=str(uuid.uuid4()),
        session_start_time=bruker_metadata["date"],
        experimenter=experimenter,
        lab=project_metadata["lab"],
        institution=project_metadata["institution"],
        experiment_description=project_metadata["experiment_description"],
        session_id=session_id
    )

    return nwbfile


def append_imaging_info(nwbfile: NWBFile, project_metadata: dict,
                        bruker_metadata: dict, imaging_plane,
                        surgery_metadata: dict) -> NWBFile:
    """
    Appends relevant 2P imaging metadata to a base NWB file.

    Creates NWB devices for laser and microscope, optical channel for imaged
    and populates them with appropriate metadata.

    Args:
        nwbfile:
            NWB File with basic metadata for session
        project_metadata:
            Metadata for given project from project's yml file
        bruker_metadata:
            Metadata for microscopy session from Prairie View .env file
        imaging_plane:
            Plane 2P images were acquired at, the Z-axis value
        surgery_metadata:
            Surgical information about the subject being imaged including the
            types of indicators used and positions of those injections/implants.

    Returns:
        NWBFile
            NWB File with base imaging information appended.
    """

    # Build microscope object
    microscope = nwbfile.create_device(
        name=project_metadata["microscope_name"],
        description=project_metadata["microscope_description"],
        manufacturer=project_metadata["microscope_manufacturer"]
    )

    # Build laser object
    laser = nwbfile.create_device(
        name=project_metadata["laser_name"],
        description=project_metadata["laser_description"],
        manufacturer=project_metadata["microscope_manufacturer"]
    )

    # Build camera device object
    camera = nwbfile.create_device(
        name=project_metadata["camera_name"],
        description=project_metadata["camera_description"],
        manufacturer=project_metadata["camera_manufacturer"]
    )

    # TODO: Build arduino device object

    # Build optical channel object; References the gcamp indicator used in
    # the experiment similar to an RGB channel in an image.
    optical_channel = OpticalChannel(
        name=surgery_metadata["brain_injections"]["gcamp"]["fluorophore"],
        description=surgery_metadata["brain_injections"]["gcamp"]["description"],
        emission_lambda = surgery_metadata["brain_injections"]["gcamp"]["fluorophore_emission_lambda"]
    )

    # Build imaging plane
    img_plane = nwbfile.create_imaging_plane(
        name=nwbfile.session_id + ": " + imaging_plane,
        optical_channel=optical_channel,
        imaging_rate=float(bruker_metadata["framerate"]),
        description="2P Discrimination Task Imaging at " + imaging_plane,
        device=microscope,
        excitation_lambda=float(bruker_metadata["laserWavelength"]),
        indicator=surgery_metadata["brain_injections"]["gcamp"]["fluorophore"],
        location=surgery_metadata["brain_injections"]["gcamp"]["target"],
        grid_spacing=[0.01, 0.01], # is this resolution of each pixel space? <- yes!
        grid_spacing_unit="meters",
        origin_coords=[
            surgery_metadata["brain_injections"]["gcamp"]["ap"],
            surgery_metadata["brain_injections"]["gcamp"]["ml"],
            surgery_metadata["brain_injections"]["gcamp"]["ml"]
        ],
        origin_coords_unit="meters"
    )

    return nwbfile


def gen_session_id(team: str, subject_id: str) -> Tuple[str, Path]:
    """
    Generates session ID for NWB files.

    NWB IDs for recordings contain information describing basic information
    about the recording (ie baseline, pre-treatment, post-treatment).  This
    function creates the ID for the mouse and builds new directories to write
    NWB files to.

    Args:
        team:
            Team value from metadata_args["team"]
        subject_id:
            Subject ID from metadata_args["subject"]

    Returns:
        session_id
        session_fullpath

    """

    # Create list of elements that compose the session path
    session_elements = [server_basepath, team, "learned_helplessness",
                        subject_id, "2p"]

    # Build the session's name for converting into a path object
    session_basename = "/".join(session_elements)

    # Convert basename into a path object with pathlib.Path
    session_basepath = Path(session_basename)

    # Gather list of sessions completed for animal by globbing directory
    sessions = [session.name for session in session_basepath.glob("*")]

    # Use determine_session() for finding which session was just completed as
    # well as the full path for the writing the NWB file to server
    session, session_fullpath = determine_session(sessions, session_basepath)

    # Convert the session ID to all uppercase for consistent string formatting
    session_id = session.upper()

    return session_id, session_fullpath


# TODO: Expand this to include CMS mice; long term, this needs to be
# far more generalized, probably a part of the project configuration file
# and the directories to look for/build should be constructed as classes that
# this function operates upon. Will be part of the refactor of configs into
# class objects
def determine_session(sessions: list, session_basepath: Path) -> Tuple[str,
                                                                       Path]:
    """
    Determines which imaging session the recording belongs to.

    Takes in list of session paths, determines the length of that list, and
    builds a new directory for storing the NWB file to be written in the next
    steps.  In doing so, it also assigns a session ID to the file. Each project
    has a known schedule of imaging for their experiments so the appropriate
    names can be inferred by looking at how many sessions have been completed
    in a given subject's 2p folder.

    Args:
        sessions:
            List of globbed Path objects for subjects 2P recordings
        session_basepath:
            Base directory for location of subject's 2P recording

    Returns:
        session
        session_fullpath
    """

    # If the length of sessions list is 0, that means this is the first session
    # for the subject.  Therefore, this is the baseline session.
    if len(sessions) == 0:

        # Append the appropriate session label to the path and build the
        # directory.
        session_fullpath = session_basepath / "baseline"
        session_fullpath.mkdir(parents=True)
        session = "baseline"

    # If the length of sessions list is 1, that means this is the second
    # session for the subject.  Therefore, this is the post learned
    # helplessness session.
    elif len(sessions) == 1:

        # Append the appropriate session label to the path and build the
        # directory.
        session_fullpath = session_basepath / "post_lh"
        session_fullpath.mkdir(parents=True)
        session = "post_lh"

    # If the length of sessions list is 2, that means this is the third
    # session for the subject.  Therefore, this is the post ketamine
    # administration session.
    elif len(sessions) == 2:

        # Append the appropriate session label to the path and build the
        # directory.
        session_fullpath = session_basepath / "post_ketamine"
        session_fullpath.mkdir(parents=True)
        session = "post_ketamine"

    return session, session_fullpath


def append_subject_info(nwbfile: NWBFile, subject_metadata: dict) -> NWBFile:
    """
    Adds subject metadata to the base NWB file.

    Takes subject metadata and builds NWB.Subject class.  Also gathers
    appropriate weight for the animal on the day of the recording through the
    subject metadata dictionary.

    Args:
        nwbfile:
            NWB File with basic metadata for session
        subject_metadata:
            Metadata for given subject from subject's yml file

    Returns:
        NWB file with subject information added
    """

    today = datetime.today()
    today = today.strftime("%Y%m%d")

    date_of_birth = dt_parser.parse(subject_metadata["dob"])
    date_of_birth = date_of_birth.replace(tzinfo=tzlocal())

    nwbfile.subject = Subject(
        subject_id=subject_metadata["subject_id"],
        date_of_birth= date_of_birth,
        description=subject_metadata["description"],
        genotype=subject_metadata["genotype"],
        sex=subject_metadata["sex"],
        species=subject_metadata["species"],
        strain=subject_metadata["strain"],
        weight=subject_metadata["weights"][today]
    )

    return nwbfile
