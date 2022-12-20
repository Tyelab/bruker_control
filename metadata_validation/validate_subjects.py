# Import config_utils from main
from ruamel.yaml import YAML
from pathlib import Path
import argparse

# Define Server Paths for projects using scope
SERVER_PATHS = {"specialk_cs": Path("V:"),
                "specialk_lh": Path("U:")}

# Define argument parser
parser = argparse.ArgumentParser(
    description="Validate Bruker Subject Metadata",
    epilog="Good luck on your work!",
    prog="Bruker Metadata Validation"
    )

# Add project flag
parser.add_argument("-p",
                    "--project",
                    type=str,
                    action="store",
                    dest="project",
                    help="Project Name (required)",
                    required=True
                    )

# Parse arguments
project = parser.parse_args().project

# Define subject metadata directory
directory = SERVER_PATHS[project] / "subjects"

# Define list of subject metadata files
subjects = directory.glob("*/*.yml")

# Define YAML parser
yaml = YAML(typ='safe')

# Iterate through subject metadata files
for subject in subjects:

    # Skip weight files as they're not used in the system currently
    if "weights" in subject.name:
        pass
    else:
        # Try to load subject metadata file
        try:
            # If it loads successfully, no action is needed
            subject_metadata = yaml.load(subject)
        
        # If it fails, print the subject name for the user
        except:
            print("ERROR", subject.name)

