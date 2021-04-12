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


def newSection(MainGuiHandle,newcontainertab):
    newsectiongui = newSectionDialog(MainGuiHandle,"In order to create a New Section, you must make a new profile.  For now, a profile can only belong in one Section", "newsection")
    inputs = newsectiongui.getInputs()
    if inputs:
        response = requests.post(BASE + 'auth/register',
                                 data=inputs)
        authtoken = response.json()
        print('usertoken[status] ' + authtoken['status'])
        with open('token.txt', 'w') as tokenfile:
            json.dump(authtoken, tokenfile)

        MainGuiHandle.checkUserStatus()

def enterSection(MainGuiHandle):
    newsectiongui = newSectionDialog(MainGuiHandle,"In order to enter an existing Section, you must make a new profile.  For now, a profile can only belong in one Section", "entersection")
    inputs = newsectiongui.getInputs()
    if inputs:
        response = requests.post(BASE + 'auth/register',
                                 data=inputs)
        authtoken = response.json()
        print('usertoken[status] ' + authtoken['status'])
        with open('token.txt', 'w') as tokenfile:
            json.dump(authtoken, tokenfile)

        MainGuiHandle.checkUserStatus()
        if authtoken['status']=='success':
            MainGuiHandle.maptab.updateContainerMap()

class newSectionDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, MainGuiHandle, advice, mode):
        super().__init__()
        uic.loadUi("Graphics/UI/newSection.ui", self)
        self.advicelabel.setText(advice)
        self.advicelabel.setWordWrap(True)
        self.dir=''

        self.checkedits={'last_name':self.lastnameedit,
        'first_name': self.firstnameedit,
        'password':self.passwordedit,
        'email':self.emailedit}

        if mode=='entersection':
            sectiondicts = Section.list()
            self.comboboxid = []
            for sectionid, sectiondict in sectiondicts.items():
                self.existingsectionbox.addItem(sectiondict['sectionname'] + " : " + sectiondict['description'])
                self.comboboxid.append(sectionid)
            self.sectiondescedit.setEnabled(False)
            self.newsectionedit.setEnabled(False)
            self.checkedits['sectionid'] = self.comboboxid
        elif  mode=='newsection':
            self.existingsectionbox.setEnabled(False)
            self.sectiondescedit.textChanged[str].connect(self.textChanged)
            self.newsectionedit.textChanged[str].connect(self.textChanged)
            self.checkedits['sectiondescription']=self.sectiondescedit
            self.checkedits['sectionname']=self.newsectionedit

        self.lastnameedit.textChanged[str].connect(self.textChanged)
        self.firstnameedit.textChanged[str].connect(self.textChanged)
        self.passwordedit.textChanged[str].connect(self.textChanged)
        self.emailedit.textChanged[str].connect(self.textChanged)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.warninglbl.setText('All enabled entries must be filled')
            # self.newsectionedit.setEnabled(False)
        # self.openDirButton.clicked.connect(self.openDirectory)
        # # self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        # self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        #
        # res = ''.join(random.choices(string.ascii_uppercase +
        #                              string.digits, k=7))
        # self.containernameEdit.setText(res)
        # # self.containerpathlbl.setText(os.path.join(self.dir, res))
        # self.containernameEdit.textChanged[str].connect(self.textChanged)

    # def openDirectory(self):
    #     dialog = QFileDialog()
    #     self.dir = os.path.normpath(dialog.getExistingDirectory(self, 'Select a dir to making your container'))
    #     if os.path.exists(self.dir):
    #         self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    #         self.containernameEdit.setEnabled(True)
    #         self.containerpathlbl.setText(os.path.join(self.dir,self.containernameEdit.text()))
    #
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