# Bruker 2-Photon NWB Utils
# Jeremy Delahanty August 2021
# Neurodata Without Borders at https://nwb.org/
# pyNWB at https://github.com/NeurodataWithoutBorders/pynwb
# pyNWB docs at https://pynwb.readthedocs.io/en/stable/

from datetime import datetime
from dateutil.tz import tzlocal
import uuid

from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.image import ImageSeries
from pynwb.ophys import TwoPhotonSeries, OpticalChannel

def gen_base_nwbfile(experimenter: str):
    """
    Build base NWB file with appropriate metadata.

    NWB Files require a set of metadata for the proper instantiation of NWB
    compliant datasets.  This generates a base NWB file and gathers the needed
    metadata for it so the data and configuration files can be appended to it
    immediately after the session is complete.

    Args:
        experimenter:
            Experimenter value from the metadata_args["experimenter"]

    Returns:
        nwbfile:
            NWB File with basic metadata for session
    """

    nwbfile = NWBFile(
        "Team Specialk Learned Helplessness 2P Session",
        str(uuid.uuid4()),
        datetime.now(tzlocal()),
        experimenter=experimenter,
        lab="Tye Lab",
        institution="The Salk Institute for Biological Studies",
        experiment_description="Test",
        session_id="Testing ID"
    )

    return nwbfile


def get_device_info(nwbfile: NWBFile):

    device = nwbfile.create_device(
        name="Bruker 2P Microscope",
        description="Tye Lab Bruker 2P Microscope",
        manufacturer="Bruker Microscopy"
    )

    optical_channel = OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda=500 # what is this on our scope?
    )

    imaging_plane = nwbfile.create_imaging_plane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30 #get from XML or Prairie View?
        description="mPFC or somewhere else...",
        device=device,
        excitation_lambda=600,
        indicator="GFP6 or something",
        location="mPFC",
        grid_spacing=[0.01, 0.01] # is this resolution of each pixel space?
        grid_spacing_unit="meters",
        origin_coords=[1., 2., 3.], # what are our origin coordinates? 000 right?
        origin_coords_unit="meters"
    )
