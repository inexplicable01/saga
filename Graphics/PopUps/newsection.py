from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Graphics.QAbstract.ContainerListModel import ContainerListModel


import os
import sys
import requests
import json
from Config import BASE

# from PyQtTesting import BASE

import random
import string
from SagaApp.Section import Section
class newSectionDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle, advice):
        super().__init__()
        self.mainguihandle=mainguihandle
        uic.loadUi("Graphics/UI/newSection.ui", self)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            payload = {'newsectionname': self.newsectionedit.text(), 'newsectiondescription':self.sectiondescedit.text()}
            headers = {'Authorization': 'Bearer ' + sagaguimodel.authtoken}
            response = requests.post(BASE + 'SECTION/newsection', headers=headers, data=payload)
            #
        else:
            return None