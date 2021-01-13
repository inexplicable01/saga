from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# from flask_user import login_required, UserManager, UserMixin
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.ContainerMap import ContainerMap
from Graphics.DetailedMap import DetailedMap
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrack
from Frame.commit import commit
import os
import sys
import requests
import json
from Config import BASE

# from PyQtTesting import BASE

import random
import string
def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

def SignIn(MainGuiHandle):
    # print(BASE)
    inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
    inputs = inputwindow.getInputs()
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
        self.username = QLineEdit(self)
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        self.username.setText('UserC')
        self.email.setText('usercemail@gmail.com')
        self.password.setText('passwordC')

        # self.third = QLineEdit(self)
        # self.fourth = QLineEdit(self)
        # self.signinBttn = QPushButton('Sign In',self)
        # self.signupBttn = QPushButton('Sign Up', self)
        # self.cancelBttn = QPushButton('Cancel',self)
        # self.cancelBttn.setText()
        buttonBox = QDialogButtonBox(self)
        signinbttn = buttonBox.addButton('Sign In', QDialogButtonBox.ActionRole)
        genbttn = buttonBox.addButton('Generate new User', QDialogButtonBox.ActionRole)
        signupbttn = buttonBox.addButton('Sign Up', QDialogButtonBox.ActionRole)
        cancelbttn = buttonBox.addButton('Cancel', QDialogButtonBox.AcceptRole)

        genbttn.clicked.connect(self.gen)
        cancelbttn.clicked.connect(self.cancel)
        signupbttn.clicked.connect(self.signup)
        signinbttn.clicked.connect(self.signin)



        layout = QFormLayout(self)
        layout.addRow("username", self.username)
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

    def cancel(self):
        self.close()

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

def newContainer(MainGuiHandle,newcontainertab):
    # print('aldskjf')
    newcontainergui = newContainerDialog("Select a local location for building your container")
    inputs = newcontainergui.getInputs()
    newcontainertab.initiate(inputs)
    MainGuiHandle.tabWidget.setCurrentIndex(newcontainertab.index)
    # dialog = QFileDialog()
    # foo_dir = dialog.getExistingDirectory(MainGuiHandle, 'Select an awesome directory')
    # print(foo_dir)

def find_Local_Container(MainGuiHandle,maincontainertab):
    # inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
    (fname,fil) = QFileDialog.getOpenFileName(MainGuiHandle, 'Open container file','.', "Container (containerstate.yaml)")
    if fname:
        # print(fname)
        maincontainertab.readcontainer(fname)
        MainGuiHandle.tabWidget.setCurrentIndex(maincontainertab.index)

class newContainerDialog(QDialog):
    def __init__(self, path):
        super().__init__()
        uic.loadUi("Graphics/newContainer.ui", self)
        self.containerpathlbl.setText(path)
        self.dir=''
        self.openDirButton.clicked.connect(self.openDirectory)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.containernameEdit.textChanged[str].connect(self.textChanged)

    def openDirectory(self):
        dialog = QFileDialog()
        self.dir = dialog.getExistingDirectory(self, 'Select a dir to making your container')
        self.containernameEdit.setEnabled(True)
        self.containerpathlbl.setText(self.dir)

    def textChanged(self,containername):
        # print(ttext)
        if len(containername)>4:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.containerpathlbl.setText(os.path.join(self.dir,containername))
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.containerpathlbl.setText(self.dir)
            self.advicelabel.setText('Container Name needs to be at least 4 charaters long')


    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'dir':self.containerpathlbl.text(), 'containername':self.containernameEdit.text()}
            # print()
        else:
            return None

