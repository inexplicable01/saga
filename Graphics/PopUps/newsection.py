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


def newSection(mainguihandle):
    newsectiongui = newSectionDialog(mainguihandle,"In order to create a New Section, you must make a new profile.  For now, a profile can only belong in one Section")
    inputs = newsectiongui.getInputs()
    if inputs:
        response = requests.post(BASE + 'auth/register',
                                 data=inputs)
        authtoken = response.json()
        print('usertoken[status] ' + authtoken['status'])
        with open('token.txt', 'w') as tokenfile:
            json.dump(authtoken, tokenfile)

        mainguihandle.checkUserStatus()


class newSectionDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle, advice):
        super().__init__()
        self.mainguihandle=mainguihandle
        uic.loadUi("Graphics/UI/newSection.ui", self)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            payload = {'newsectionname': self.newsectionedit.text(), 'newsectiondescription':self.sectiondescedit.text()}
            headers = {'Authorization': 'Bearer ' + self.mainguihandle.authtoken}
            response = requests.post(BASE + 'SECTION/newsection', headers=headers, data=payload)
            #
        else:
            return None