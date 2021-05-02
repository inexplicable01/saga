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
# from PyQtTesting import BASE

import random
import string

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def SignIn(MainGuiHandle):
    # print(BASE)
    inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
    inputs = inputwindow.getInputs()
    MainGuiHandle.getWorldContainers()
    # self.newContainerInputs = inputs
    # self.containerAddition(inputs[1])


def SignOut(MainGuiHandle):
    if os.path.exists("token.txt"):
        os.remove("token.txt")
    MainGuiHandle.checkUserStatus()
    print('sign out' + BASE)


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
    permissiongui = permissionsDialog(maincontainertab.mainContainer)
    inputs = permissiongui.getInputs()
    if inputs:
        maincontainertab.mainContainer.editusers(inputs['userlist'])
        # MainGuiHandle.tabWidget.setCurrentIndex(maincontainertab.index)



