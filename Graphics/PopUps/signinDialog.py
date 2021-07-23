from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
import sys
import requests
import json
from Config import BASE,testerlogin
from Graphics.PopUps.NewContainerDialog import newContainerDialog
# from PyQtTesting import BASE
from SagaGuiModel import sagaguimodel

import random
import string


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

class SigninDialog(QDialog):
    def __init__(self, mainguihandle, sagaguimodel,parent=None):
        super().__init__(parent)
        self.mainguihandle=mainguihandle
        self.sagaguimodel = sagaguimodel
        self.setWindowTitle('File Information')
        self.setMinimumSize(600,300)
        # self.username = QLineEdit(self)
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        self.passwordcheckbox = QCheckBox(self)
        self.passwordcheckbox.setText('Show Password')
        self.passwordcheckbox.stateChanged.connect(self.showpasswordstate)
        # self.username.setText(testerlogin['first_name'])
        self.email.setText(testerlogin['email'])
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setText(testerlogin['password'])
        self.signedin=False

        buttonBox = QDialogButtonBox(self)
        signinbttn = buttonBox.addButton('Sign In', QDialogButtonBox.ActionRole)
        # genbttn = buttonBox.addButton('Generate new User', QDialogButtonBox.ActionRole)
        # signupbttn = buttonBox.addButton('Sign Up', QDialogButtonBox.ActionRole)
        cancelbttn = buttonBox.addButton('Cancel', QDialogButtonBox.AcceptRole)

        # genbttn.clicked.connect(self.gen)
        cancelbttn.clicked.connect(self.close)
        # signupbttn.clicked.connect(self.signup)
        signinbttn.clicked.connect(self.signin)



        layout = QFormLayout(self)
        # layout.addRow("username", self.username)
        layout.addRow("Email", self.email)
        layout.addRow("Password", self.password)
        layout.addRow(self.passwordcheckbox)
        # layout.addRow("Owner", self.third)
        # layout.addRow("Description", self.fourth)
        layout.addWidget(buttonBox)

        # self.signupBttn.connect(self.signup)
        # self.signinBttn.connect(self.signin)
        # self.cancelBttn.connect(self.cancel)

    def showpasswordstate(self):
        if self.passwordcheckbox.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'signinsuccess':self.signedin}
        else:
            return {'signinsuccess': False}
    #
    # def gen(self):
    #     self.username.setText(random_char(7))
    #     self.email.setText(random_char(7)+"@gmail.com")
    #     self.password.setText(random_char(7))

    def signin(self):
        # print(self.email.text())
        signinstatus = sagaguimodel.sagaapicall.signInCall(self.email.text(), self.password.text(), sagaguimodel.tokenfile)

        # self.mainguihandle.checkUserStatus()
        if signinstatus['status']=='success':
            self.signedin = True
            self.accept()
        else:
            print('ATTENTION: View code to deal with sign in failure')