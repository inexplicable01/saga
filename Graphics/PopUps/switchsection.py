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


def enterSection(mainguihandle):
    # response = requests.get(BASE + 'user/getusersections', )
    headers = {'Authorization': 'Bearer ' + mainguihandle.authtoken}
    response = requests.get(BASE + 'USER/getusersections', headers=headers)

    resp = json.loads(response.content)
    sectioninfo = resp['sectioninfo']
    currentsection = resp['currentsection']

    switchsectiongui = switchSectionDialog(mainguihandle,sectioninfo,currentsection)
    needtoupdateworldmap = switchsectiongui.waitfordone()
    if needtoupdateworldmap:
        # print(inputs)
        mainguihandle.refresh()
        # mainguihandle.getWorldContainers()


class switchSectionDialog(QDialog):
    def __init__(self, MainGuiHandle,sectioninfo,currentsection):
        super().__init__()
        self.MainGuiHandle=MainGuiHandle
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

    # def done(self):

    def switchusersection(self):
        # print(self.comboboxid[self.existingsectionbox.currentIndex()])
        payload = {'newsectionid': self.comboboxid[self.existingsectionbox.currentIndex()]}
        headers = {'Authorization': 'Bearer ' + self.MainGuiHandle.authtoken}
        response = requests.post(BASE + 'USER/switchusersection', headers=headers, data=payload)
        resp = json.loads(response.content)
        report = resp['report']
        if report['status']=='User Current Section successfully changed':
            self.cursectionlbl.setText(resp['usersection'])
            self.newsection = resp['usersection']
        else:
            self.cursectionlbl.setText('Error Occured.  Your current section has not change')

    def waitfordone(self):
        if self.exec_() == QDialog.Accepted:
            if not self.oldsection==self.newsection:
                return True
            # formentry={}
            # for key, edit in self.checkedits.items():
            #     if key=='sectionid':
            #         formentry[key]=self.comboboxid[self.existingsectionbox.currentIndex()]
            #     else:
            #         formentry[key]=edit.text()
            return False
            #
        else:
            return False

