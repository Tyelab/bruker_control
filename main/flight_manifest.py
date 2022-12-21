# From Jonny Saunders, the legend
# See here: https://github.com/auto-pi-lot/autopilot/discussions/191

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtWidgets import QCheckBox, QPushButton, QLabel, QGroupBox, QWidget, QScrollArea, QMainWindow
from PySide2 import QtCore
from typing import List, Dict, Tuple, Optional
import sys
from pathlib import Path

SERVER_PATHS = {"specialk_cs": Path("V:"),
                "specialk_lh": Path("U:")}

class CheckList(QMainWindow):

    def __init__(self, project: str, title:str="bruker_control", **kwargs):
        super(CheckList, self).__init__(**kwargs)
        self.scroll = QScrollArea()
        self._flight_manifest = self.get_subjects(project)
        self._checkboxes = {} # type: Dict[str, QCheckBox]
        self.title = title
        self._selected_subjects = self.get_values()
        self.setWindowTitle(self.title)
        self.resize(300, 300)

        # Make "Take Off" Button for flight manifest
        take_off_button = QPushButton("Take Flight!")
        # Connect button to get_values method
        take_off_button.clicked.connect(self.get_values)

        # Use HBox layout
        self.layout = QtWidgets.QHBoxLayout()

        # Add checkboxes to layout
        self.scroll.setWidget(self._init_checkboxes())

        self.layout.addWidget(self.scroll)
        self.layout.addWidget(take_off_button)
        main_window = QWidget()
        main_window.setLayout(self.layout)
        self.setCentralWidget(main_window)

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
        check_group = QGroupBox("Subjects")
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