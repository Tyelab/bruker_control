# From Jonny Saunders, the legend
# See here: https://github.com/auto-pi-lot/autopilot/discussions/191

from PySide2 import QtWidgets
from PySide2.QtWidgets import QCheckBox, QPushButton, QLabel, QGroupBox, QWidget
from typing import List, Dict, Tuple, Optional
import sys
from pathlib import Path

SERVER_PATHS = {"specialk_cs": Path("V:"),
                "specialk_lh": Path("U:")}

class CheckList(QtWidgets.QWidget):

    def __init__(self, project: str, title:str="Subjects", **kwargs):
        super(CheckList, self).__init__(**kwargs)
        self._flight_manifest = self.get_subjects(project)
        self._checkboxes = {} # type: Dict[str, QCheckBox]
        self.title = title
        self._selected_subjects = self.get_values()

        self.layout = QtWidgets.QVBoxLayout()

        # Add checkboxes to layout
        self.layout.addWidget(self._init_checkboxes())
        # Add button to layout
        self.ok_button = QPushButton("OK")
        self.layout.addWidget(self.ok_button)

        # connect button to action triggered when clicked
        self.ok_button.clicked.connect(self.get_values)

        # set layout of main widget
        self.setLayout(self.layout)

    def value(self) -> Dict[str, bool]:
        return {
            sub: box.isChecked() for sub, box in self._checkboxes.items() 
        }

    @classmethod
    def get_subjects(cls, project) -> list:
        """
        Query server location for subjects.
        """

        print("Getting subjects for flight manifest...")

        subject_directory = SERVER_PATHS[project] / "subjects"

        flight_manifest = [subject.name for subject in subject_directory.glob("*")]

        return flight_manifest

    def _init_checkboxes(self) -> QGroupBox:
        # Button groupbox
        check_group = QGroupBox(self.title)
        # button layout
        check_layout = QtWidgets.QVBoxLayout()
        
        # make checkboxes
        for subject in self._flight_manifest:
            box = QCheckBox(subject)
            # add checkbox to layout so it's displayed
            check_layout.addWidget(box)
            # save reference to checkboxes to get value later
            self._checkboxes[subject] = box

        # set layout full of buttons for groupbox
        check_group.setLayout(check_layout)
        return check_group


    def get_values(self):
        # get subjects from value method
        selected_subjects = self.value()

        # grab only subjects that were selected
        selected_subjects = [subject for subject in selected_subjects if selected_subjects[subject]]
        
        self.close()

        return selected_subjects

        


def run(project):
    
    app = QtWidgets.QApplication(sys.argv)
    subjects = CheckList(project=project)
    subjects.show()
    app.exec_()
    passengers = subjects.get_values()
    return passengers