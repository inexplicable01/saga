from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import requests
import json
from Config import BASE

# from PyQtTesting import BASE

import random
import string
from SagaApp.Section import Section
from SagaGuiModel import sagaguimodel
from os.path import join
from Config import sourcecodedirfromconfig

class newUserDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "newUser.ui"), self)
        # self.advicelabel.setText(advice)
        # self.advicelabel.setWordWrap(True)
        self.dir=''

        self.checkedits={'last_name':self.lastnameedit,
        'first_name': self.firstnameedit,
        'password':self.passwordedit,
        'email':self.emailedit}

        sectiondict = sagaguimodel.getAvailableSections()
        self.comboboxid = []
        self.sectioncombobox.addItem('Please Select a Section to register to:')
        self.comboboxid.append('Invalid')
        self.selectedsection = 'Invalid'
        for sectionid, sectiondict in sectiondict.items():
            self.sectioncombobox.addItem(sectiondict['sectionname'] + " : " + sectiondict['description'])
            self.comboboxid.append(sectionid)

        # self.sectioncombobox.setEnabled(False)
        # self.sectiondescedit.entrychanged[str].connect(self.entrychanged)
        # self.newsectionedit.entrychanged[str].connect(self.entrychanged)
        # self.checkedits['sectiondescription']=self.sectiondescedit
        # self.checkedits['sectionname']=self.newsectionedit

        self.lastnameedit.textChanged[str].connect(self.entrychanged)
        self.firstnameedit.textChanged[str].connect(self.entrychanged)
        self.passwordedit.textChanged[str].connect(self.entrychanged)
        self.emailedit.textChanged[str].connect(self.entrychanged)

        self.sectioncombobox.activated.connect(self.selectionsection)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.warninglbl.setText('All enabled entries must be filled')

    def entrychanged(self):
        formready = True
        for key,edit in self.checkedits.items():
            if self.selectedsection == 'Invalid':
                formready=False
                wrningtext='Please Select a section to register to'
                print(self.selectedsection)
            if len(edit.text())<1:
                formready=False
                print(edit.text())
        if formready:
            self.warninglbl.setText('Hit Okay to Register')
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(formready)

    def selectionsection(self):
        self.selectedsection = self.comboboxid[self.sectioncombobox.currentIndex()]
        self.entrychanged()
    #
    #
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            formentry={}
            for key, edit in self.checkedits.items():
                formentry[key]=edit.text()
            formentry['sectionid'] = self.comboboxid[self.sectioncombobox.currentIndex()]
            return formentry
            #
        else:
            return None