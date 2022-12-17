from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import requests
import json

# from PyQtTesting import BASE

import random
import string
from SagaGuiModel.GuiModelConstants import LOGININDEX,MAINAPPINDEX
from SagaGuiModel import sagaguimodel
from os.path import join
from Config import sourcecodedirfromconfig
import re
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class newUserDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    # super(CreateAccScreen, self).__init__()
    # uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "createacc.ui"), self)
    # self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
    # self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
    # self.signup.clicked.connect(self.signupfunction)
    def __init__(self, mainguihandle, sagaguimodel,widget):
        super().__init__()
        self.widget = widget
        self.mainguihandle = mainguihandle
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "createacc.ui"), self)
        # self.advicelabel.setText(advice)
        # self.advicelabel.setWordWrap(True)
        self.dir=''

        self.checkedits={'last_name':self.lastnamefield,
        'first_name': self.firstnamefield,
        'password':self.passwordfield,
        'email':self.emailfield}

        success, sectiondicts = sagaguimodel.getAvailableSections()
        self.comboboxid = []
        self.sectioncombobox.addItem('Please Select a Section to register to:')
        self.comboboxid.append('Invalid')
        # self.selectedsection = 'Invalid'
        i=0
        index = 0
        self.selectedsection = 'WorldMap'
        for sectionid, sectiondict in sectiondicts.items():
            self.sectioncombobox.addItem(sectiondict['sectionname'] + " : " + sectiondict['description'])
            self.comboboxid.append(sectionid)
            i+=1
            if sectiondict['sectionname']=='WorldMap':
                index =i
        self.sectioncombobox.setCurrentIndex(index)

        self.lastnamefield.textChanged[str].connect(self.entrychanged)
        self.firstnamefield.textChanged[str].connect(self.entrychanged)
        self.passwordfield.textChanged[str].connect(self.entrychanged)
        self.emailfield.textChanged[str].connect(self.entrychanged)
        self.confirmpasswordfield.textChanged[str].connect(self.entrychanged)

        self.sectioncombobox.activated.connect(self.selectionsection)

        self.signupbttn.setEnabled(False)
        self.signupbttn.clicked.connect(self.signup)

        self.warninglbl.setText('Please fill all entries.')
        self.loginlbl.mousePressEvent = self.goToLoginPage

    def goToLoginPage(self, event):
        self.widget.setCurrentIndex(LOGININDEX)

    def entrychanged(self):
        formready = True
        warninglbl = 'Please fill all entries.\n'
        for key,edit in self.checkedits.items():
            if self.selectedsection == 'Invalid':
                formready=False
                warninglbl = warninglbl + 'Please Select a section to register to\n'
                print(self.selectedsection)
            if len(edit.text())<1:
                formready=False
            if key=='email':
                if not (re.fullmatch(regex, edit.text())):
                    formready=False
                    warninglbl = warninglbl + 'Username must be valid email\n'

                # warninglbl = warninglbl + 'Please Fill ' + key + 'Entry'
                # print(edit.text())
        if not self.passwordfield.text() == self.confirmpasswordfield.text():
            formready = False
            warninglbl = warninglbl + 'Passwords don''t match.\n'
        if formready:
            warninglbl = 'Sign Up to Register. '

        self.signupbttn.setEnabled(formready)
        self.warninglbl.setText(warninglbl)

    def selectionsection(self):
        self.selectedsection = self.comboboxid[self.sectioncombobox.currentIndex()]
        self.entrychanged()
    #
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            formentry={}
            for key, edit in self.checkedits.items():
                formentry[key]=edit.text()
            formentry['sectionid'] = self.comboboxid[self.sectioncombobox.currentIndex()]
            return self.emailfield.text(), self.passwordfield.text(), self.firstnamefield.text(),\
                   self.lastnamefield.text(),self.comboboxid[self.sectioncombobox.currentIndex()]
        else:
            return None, None, None, None, None

    def signup(self):
        success, respdict = sagaguimodel.newUserSignUp(self.emailfield.text(), self.passwordfield.text(),
                                                   self.firstnamefield.text(), self.lastnamefield.text(),
                                                   self.comboboxid[self.sectioncombobox.currentIndex()])
        if success:
            self.mainguihandle.adjustGuiByUserStatusChange()
            self.mainguihandle.guireset()
            self.mainguihandle.loadSection()
            self.widget.setCurrentIndex(MAINAPPINDEX)
        else:
            if respdict['failmessage']== 'User already exists. Please Log in.':
                self.warninglbl.setText(respdict['failmessage'])
            else:
                self.warninglbl.setText('Server return error. Sign up failed.' + respdict['message'])

# class CreateAccScreen(QDialog):
#     def __init__(self):
#
#
#     def signupfunction(self):
#         user = self.emailfield.text()
#         password = self.passwordfield.text()
#         confirmpassword = self.confirmpasswordfield.text()
#
#         if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
#             self.error.setText("Please fill in all inputs.")
#
#         elif password!=confirmpassword:
#             self.error.setText("Passwords do not match.")
#         else:
#             self.error.setText("Passwords do not match.")