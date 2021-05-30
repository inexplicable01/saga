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
from Graphics.PopUps.InputDialog import InputDialog
from Graphics.PopUps.permissionsDialog import permissionsDialog
from Graphics.PopUps.newuser import newUserDialog
# from PyQtTesting import BASE

import random
import string

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def SignIn(mainguihandle):
    # print(BASE)
    inputwindow = InputDialog(mainguihandle=mainguihandle)
    inputs = inputwindow.getInputs()
    if inputs:
        mainguihandle.getWorldContainers()
    # self.newContainerInputs = inputs
    # self.containerAddition(inputs[1])

def SignOut(MainGuiHandle):
    if os.path.exists("token.txt"):
        os.remove("token.txt")
    MainGuiHandle.checkUserStatus()
    print('sign out' + BASE)

class InputDialog(QDialog):
    def __init__(self, MainGuiHandle, parent=None):
        super().__init__(parent)
        self.MainGuiHandle=MainGuiHandle
        self.setWindowTitle('File Information')
        self.setMinimumSize(600,300)
        # self.username = QLineEdit(self)
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        # self.username.setText('UserC')
        self.email.setText('jimmyleong113@gmail.com')
        self.password.setText('passwordJ')

        buttonBox = QDialogButtonBox(self)
        cancelbttn = buttonBox.addButton('Cancel', QDialogButtonBox.AcceptRole)
        signinbttn = buttonBox.addButton('Sign In', QDialogButtonBox.ActionRole)
        # genbttn = buttonBox.addButton('Generate new User', QDialogButtonBox.ActionRole)
        # signupbttn = buttonBox.addButton('Sign Up', QDialogButtonBox.ActionRole)


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

def SignUp(mainguihandle):
    # print(BASE)
    newuserwindow = newUserDialog(mainguihandle=mainguihandle)
    inputs = newuserwindow.getInputs()

    # newsectiongui = newUserDialog(mainguihandle,"In order to create a New Section, you must make a new profile.  For now, a profile can only belong in one Section")
    # inputs = newsectiongui.getInputs()
    if inputs:
        response = requests.post(BASE + 'auth/register',
                                 data=inputs)
        authtoken = response.json()
        if 'status' in authtoken.keys() and authtoken['status']=='success':
            with open('token.txt', 'w') as tokenfile:
                json.dump(authtoken, tokenfile)
            mainguihandle.checkUserStatus()
            mainguihandle.getWorldContainers()
        else:
            print('usertoken[status] ' + authtoken['status'])



def newContainer(MainGuiHandle,maincontainertab):
    newcontainergui = newContainerDialog("Select a local location for building your container")
    inputs = newcontainergui.getInputs()
    if inputs:
        maincontainertab.initiate(inputs)
        MainGuiHandle.tabWidget.setCurrentIndex(maincontainertab.index)

    # dialog = QFileDialog()
    # foo_dir = dialog.getExistingDirectory(MainGuiHandle, 'Select an awesome directory')
    # print(foo_dir)

def find_Local_Container(MainGuiHandle,maincontainertab):
    # inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
    (fname,fil) = QFileDialog.getOpenFileName(MainGuiHandle, 'Open container file','.', "Container (*containerstate.yaml)")
    if fname:
        # print(fname)
        maincontainertab.readcontainer(fname)
        MainGuiHandle.tabWidget.setCurrentIndex(maincontainertab.index)

def containerPermission(mainguihandle, maincontainertab):
    permissiongui = permissionsDialog(maincontainertab.mainContainer, mainguihandle)
    permissiongui.exec_()
    # if inputs:
    #     maincontainertab.mainContainer.editusers(inputs['userlist'])
        # MainGuiHandle.tabWidget.setCurrentIndex(maincontainertab.index)



