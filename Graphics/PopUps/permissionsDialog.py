from PyQt5.QtWidgets import *
from PyQt5 import uic
import random
import string
import os
from SagaApp.Container import Container
from Graphics.QAbstract.UserListModel import UserListModel

import re

# Make a regular expression
# for validating an Email
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


# Define a function for
# for validating an Email


def check(email):
    # pass the regular expression
    # and the string in search() method
    if (re.search(regex, email)):
        print("Valid Email")

    else:
        print("Invalid Email")

class permissionsDialog(QDialog):
    def __init__(self, mainContainer:Container):
        super().__init__()
        uic.loadUi("Graphics/UI/permissionsDialog.ui", self)

        self.usermodel = UserListModel(mainContainer.allowedUser)
        self.alloweduserview.setModel(self.usermodel)

        self.adduserbttn.clicked.connect(self.adduser)
        self.adduserbttn.setEnabled(False)
        self.emailedit.textChanged[str].connect(self.textChanged)

    def adduser(self):
        self.usermodel.adduser(self.emailedit.text())
        self.usermodel.layoutChanged.emit()

    def textChanged(self, email):
        # print(ttext)
        if re.search(regex, email):
            self.adduserbttn.setEnabled(True)
        else:
            self.adduserbttn.setEnabled(False)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'userlist':self.usermodel.userlist()}
            # print()
        else:
            return None

