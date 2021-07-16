from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
import sys
import requests
import json
from Config import BASE
from SagaGuiModel import sagaguimodel

class switchSectionDialog(QDialog):
    def __init__(self, mainguihandle,sectioninfo,currentsection):
        super().__init__()
        self.mainguihandle=mainguihandle
        uic.loadUi("Graphics/UI/switchsection.ui", self)
        print(sectioninfo)
        self.oldsection = currentsection
        self.newsection = currentsection
        self.cursectionlbl.setText(currentsection)
        self.comboboxid = []
        for sectionid, sectiondict in sectioninfo.items():
            self.existingsectionbox.addItem(sectiondict['sectionname'] + " : " + sectiondict['description'])
            self.comboboxid.append(sectionid)
        self.existingsectionbox.activated.connect(self.switchusersection)
        self.donebttn.clicked.connect(self.accept)

    def switchusersection(self):
        # print(self.comboboxid[self.existingsectionbox.currentIndex()])
        payload = {'newsectionid': self.comboboxid[self.existingsectionbox.currentIndex()]}
        headers = {'Authorization': 'Bearer ' + sagaguimodel.authtoken}
        response = requests.post(BASE + 'USER/switchusersection', headers=headers, data=payload)
        resp = json.loads(response.content)
        report = resp['report']
        if report['status']=='User Current Section successfully changed':
            self.cursectionlbl.setText(resp['usersection'])
            self.newsection = resp['usersection']
            self.mainguihandle.resetguionsectionswitch()
        else:
            self.cursectionlbl.setText('Error Occured.  Your current section has not change')


    def waitfordone(self):
        if self.exec_() == QDialog.Accepted:
            if not self.oldsection==self.newsection:
                return True
            return False
        else:
            return False

