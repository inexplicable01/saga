from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

from os.path import join
from Config import sourcecodedirfromconfig
import sys
import requests
import json
from Config import BASE
from SagaGuiModel import sagaguimodel

class switchSectionDialog(QDialog):
    def __init__(self, mainguihandle,sectioninfo,currentsection):
        super().__init__()
        self.mainguihandle=mainguihandle

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "switchsection.ui"), self)
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
        switchtosectionid = self.comboboxid[self.existingsectionbox.currentIndex()]
        success, newsectionname = sagaguimodel.sectionSwitch(switchtosectionid)
        if success:
            self.cursectionlbl.setText(newsectionname)
            self.newsection = newsectionname
        else:
            self.cursectionlbl.setText('Error Occured.  Your current section has not change')


    def waitfordone(self):
        if self.exec_() == QDialog.Accepted:
            if not self.oldsection==self.newsection:
                return True
            return False
        else:
            return False

