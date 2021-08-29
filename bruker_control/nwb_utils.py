# Bruker 2-Photon NWB Utils
# Jeremy Delahanty August 2021
# Neurodata Without Borders at https://nwb.org/
# pyNWB at https://github.com/NeurodataWithoutBorders/pynwb
# pyNWB docs at https://pynwb.readthedocs.io/en/stable/

from datetime import datetime
from dateutil.tz import tzlocal
from dateutil import parser as dt_parser
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET

from ruamel.yaml import YAML
from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.image import ImageSeries
from pynwb.ophys import TwoPhotonSeries, OpticalChannel

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
yaml_basepath = "X:/"

# Experimental configuration directories are in the Raw Data volume on the
# machine BRUKER which is mounted to E:. This is where configs will be written
env_basepath = "E:/teams/"


def build_nwb_file(experimenter: str, team: str, session_end_time: datetime,
                   imaging_plane: str, subject_id: str):

    bruker_metadata = get_bruker_metadata(team, imaging_plane)

    project_metadata = get_project_metadata(team, subject_id)

    nwbfile = gen_base_nwbfile(experimenter, team, bruker_metadata,
                               session_end_time, project_metadata)

    nwbfile = append_device_info(nwbfile, project_metadata, bruker_metadata,
                                 imaging_plane)

    print(nwbfile)
    # nwbfile = append_subject_info(nwbfile, mouse_metadata)


def get_bruker_metadata(team: str, imaging_plane: str) -> dict:

    # Build base path for microscopy session
    base_env_path = env_basepath + team + "/microscopy/"

    today = datetime.today()
    today = today.strftime("%Y%m%d")
    env_glob_pattern = f"{today}*{imaging_plane}*/*2p*.env"

    # Glob the current plane's path to find the environment file
    bruker_env_glob = [path for path in
                       Path(base_env_path).glob(env_glob_pattern)]

    # TODO: If there's multiple 2p environment files in one imaging plane's
    # set up there's something wrong. A warning at least or an exception should
    # be raised
    bruker_env_path = bruker_env_glob[0]

    metadata_root = ET.parse(bruker_env_path).getroot()

    bruker_metadata = get_pv_states(pv_state_idx_keys, pv_state_noidx_keys,
                                    metadata_root)

    return bruker_metadata


def get_project_metadata(team: str, subject_id: str):

    # Define YAML object parser with safe loading
    yaml = YAML(typ='safe')

    # Construct the base path for the project's YAML file
    base_yaml_path = yaml_basepath + team + "/2p_template_configs/"

    # Until teams and studies/projects are implemented across all directories,
    # this if/else will have to do
    if "LH" in subject_id:
        project_yaml_path = Path(base_yaml_path) / "nwb_lh_base.yml"
    else:
        project_yaml_path = base_yaml_path + "nwb_cs_base.yml"

    project_metadata = yaml.load(project_yaml_path)

    return project_metadata

def get_pv_states(pv_idx_keys: dict, pv_noidx_keys: list,
                  metadata_root: ET) -> dict:

    # Use dictionary comprehension for environment values in Root of .env to
    # start the bruker_metadata dictionary
    bruker_metadata = {key: value for key, value in metadata_root.items()}

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

def get_idx_states(pv_idx_keys, metadata_root):

    pv_idx_metadata = {}

    for key, idx in pv_idx_keys.items():
        xpath = f".//PVStateValue[@key='{key}']/IndexedValue[@index='{idx}']"
        element = metadata_root.find(xpath)
        pv_idx_metadata[key] = element.attrib["value"]

    return pv_idx_metadata


def get_noidx_states(pv_noidx_keys, metadata_root):

    pv_noidx_metadata = {}

    for key in pv_noidx_keys:
        xpath = f".//PVStateValue[@key='{key}']"
        element = metadata_root.find(xpath)
        pv_noidx_metadata[key] = element.attrib["value"]

    return pv_noidx_metadata


def gen_base_nwbfile(experimenter: str, team: str,
                     bruker_metadata: dict, session_end_time: datetime,
                     project_metadata: dict) -> NWBFile:
    """
    Build base NWB file with appropriate metadata.

    NWB Files require a set of metadata for the proper instantiation of NWB
    compliant datasets.  This generates a base NWB file and gathers the needed
    metadata for it so the data and configuration files can be appended to it
    immediately after the session is complete.

    Args:
        experimenter:
            Experimenter value from the metadata_args["experimenter"]
        project_metadata:
            Metadata for a given project's information for NWB standard
        bruker_metadata:
            Metadata for NWB parsed from Prairie View XML and env files.
        session_end_time:
            Time session ended the moment prairieview_utils.abort_recording()
            is completed.
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
        # session_end_time=session_end_time, no session_end_time required?
        experimenter=experimenter,
        lab=project_metadata["lab"],
        institution=project_metadata["institution"],
        experiment_description=project_metadata["experiment_description"],
        # TODO: Automatically generate the session ID names from subject's
        # directory. For LH, they should be: Baseline, Post LH, Post Ketamine
        session_id="Testing ID"
    )

    return nwbfile


def append_device_info(nwbfile: NWBFile, project_metadata: dict,
                       bruker_metadata: dict, imaging_plane) -> NWBFile:

    microscope = nwbfile.create_device(
        name=project_metadata["microscope_name"],
        description=project_metadata["microscope_description"],
        manufacturer=project_metadata["microscope_manufacturer"]
    )

    laser = nwbfile.create_device(
        name=project_metadata["laser_name"],
        description=project_metadata["laser_description"],
        manufacturer=project_metadata["microscope_manufacturer"]
    )

    optical_channel = OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda = float(bruker_metadata["laserWavelength"])
    )

    img_plane = nwbfile.create_imaging_plane(
        name="Imaging Plane at: " + imaging_plane,
        optical_channel=optical_channel,
        imaging_rate=float(bruker_metadata["framerate"]),
        description="Test",
        device=microscope,
        excitation_lambda=project_metadata["gcamp_excitation_lambda"],
        indicator=project_metadata["gcamp_indicator"],
        location=project_metadata["gcamp_location"],
        grid_spacing=[0.01, 0.01], # is this resolution of each pixel space?
        grid_spacing_unit="meters",
        origin_coords=[1., 2., 3.], # what are our origin coordinates? 000 right?
        origin_coords_unit="meters"
    )

    return nwbfile

def get_subject_info(nwbfile: NWBFile, mouse_metadata: dict) -> NWBFile:
    pass
