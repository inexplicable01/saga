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

import random
import string


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

class InputDialog(QDialog):
    def __init__(self, MainGuiHandle, parent=None):
        super().__init__(parent)
        self.MainGuiHandle=MainGuiHandle
        self.setWindowTitle('File Information')
        self.setMinimumSize(600,300)
        # self.username = QLineEdit(self)
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        # self.username.setText(testerlogin['first_name'])
        self.email.setText(testerlogin['email'])
        self.password.setText(testerlogin['password'])


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
        # layout.addRow("Owner", self.third)
        # layout.addRow("Description", self.fourth)
        layout.addWidget(buttonBox)

        # self.signupBttn.connect(self.signup)
        # self.signinBttn.connect(self.signin)
        # self.cancelBttn.connect(self.cancel)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return (self.first.text(), self.second.text(), self.third.text(), self.fourth.text())

    def gen(self):
        self.username.setText(random_char(7))
        self.email.setText(random_char(7)+"@gmail.com")
        self.password.setText(random_char(7))

    def signin(self):
        print(self.email.text())
        response = requests.post(BASE + 'auth/login',
            json={"email":self.email.text(),
            "password":self.password.text()},
        )
        authtoken = response.json()
        print('usertoken[status] ' + authtoken['status'] )
        with open('token.txt', 'w') as tokenfile:
            json.dump(authtoken, tokenfile)
        # else:

        self.MainGuiHandle.checkUserStatus()
        if authtoken['status']=='success':
            self.MainGuiHandle.maptab.updateContainerMap()
        self.close()


    def signup(self):
        response = requests.post(BASE + 'auth/register',
                                 json={"email": self.email.text(),
                                       "password": self.password.text()},
                                 )
        authtoken = response.json()
        print('usertoken[status] ' + authtoken['status'])
        with open('token.txt', 'w') as tokenfile:
            json.dump(authtoken, tokenfile)
        # else:

        self.MainGuiHandle.checkUserStatus()
        self.close()