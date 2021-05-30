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


class newUserDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle):
        super().__init__()
        uic.loadUi("Graphics/UI/newUser.ui", self)
        # self.advicelabel.setText(advice)
        # self.advicelabel.setWordWrap(True)
        self.dir=''

        self.checkedits={'last_name':self.lastnameedit,
        'first_name': self.firstnameedit,
        'password':self.passwordedit,
        'email':self.emailedit}

        # self.existingsectionbox.setEnabled(False)
        # self.sectiondescedit.textChanged[str].connect(self.textChanged)
        # self.newsectionedit.textChanged[str].connect(self.textChanged)
        # self.checkedits['sectiondescription']=self.sectiondescedit
        # self.checkedits['sectionname']=self.newsectionedit

        self.lastnameedit.textChanged[str].connect(self.textChanged)
        self.firstnameedit.textChanged[str].connect(self.textChanged)
        self.passwordedit.textChanged[str].connect(self.textChanged)
        self.emailedit.textChanged[str].connect(self.textChanged)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.warninglbl.setText('All enabled entries must be filled')

    def textChanged(self):
        formready = True
        for key,edit in self.checkedits.items():
            if key == 'sectionid':
                continue
            if len(edit.text())<1:
                formready=False
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(formready)
    #
    #
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            formentry={}
            for key, edit in self.checkedits.items():
                if key=='sectionid':
                    formentry[key]=self.comboboxid[self.existingsectionbox.currentIndex()]
                else:
                    formentry[key]=edit.text()
            return formentry
            #
        else:
            return None