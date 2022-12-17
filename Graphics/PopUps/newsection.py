from PyQt5.QtWidgets import *
from PyQt5 import uic


import requests
import json

# from PyQtTesting import BASE
from os.path import join
from Config import sourcecodedirfromconfig

from SagaGuiModel import sagaguimodel
import random

import string
from SagaCore.Section import Section
class newSectionDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle):
        super().__init__()
        self.mainguihandle=mainguihandle
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "newSection.ui"), self)

    def newSection(self):
        if self.exec_() == QDialog.Accepted:
            success, newsection  = sagaguimodel.sagaapicall.newSectionCall(newsectionname=self.newsectionedit.text(), newsectiondesp=self.sectiondescedit.text())
            if success:
                self.mainguihandle.guireset()
                self.mainguihandle.loadSection()
        else:
            return None, None , False