from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import random
import string
import os
from SagaCore.Container import Container
from Graphics.QAbstract.UserListModel import UserListModel,SectionUserListModel
import json
import re
import requests
# Make a regular expression
# for validating an Email
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
from SagaGuiModel import sagaguimodel

from os.path import join
from Config import sourcecodedirfromconfig


def check(email):
    # pass the regular expression
    # and the string in search() method
    if (re.search(regex, email)):
        print("Valid Email")

    else:
        print("Invalid Email")

class permissionsDialog(QDialog):
    def __init__(self, mainguihandle):
        super().__init__()
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "permissionsDialog.ui"), self)
        self.mainguihandle= mainguihandle
        self.maincontainer = sagaguimodel.maincontainer

        allowedUser, sectionUser = sagaguimodel.getContainerPermissions()
        # permissionsresponse = json.loads(response.content)
        self.allowedToAdd = False
        # if sagaguimodel.usersess.email in permissionsresponse['allowedUser']:
        if sagaguimodel.usersess.email in allowedUser:
            self.allowedToAdd = True

        self.usermodel = UserListModel(self.maincontainer.allowedUser)
        self.alloweduserview.setModel(self.usermodel)

        self.sectionUser = SectionUserListModel(sectionUser)
        self.regsectionuserview.setModel(self.sectionUser)
        self.regsectionuserview.clicked.connect(self.setemailedit)

        # self.emailedit.setEnabled(self.allowedToAdd)

        self.adduserbttn.clicked.connect(self.adduser)
        self.adduserbttn.setEnabled(False)
        # self.emailedit.textChanged[str].connect(self.textChanged)
        # self.adduserbttn.clicked.connect()
        self.exitbttn.clicked.connect(self.accept)
        self.selecteduseremail=None
        self.exec_()

    def adduser(self):
        success, servermessage, allowedUsers  = sagaguimodel.addUserToContainer(self.selecteduseremail)
        # print(permissionsresponse['ServerMessage'])
        if success:
            # self.emailedit.setText('')
            self.usermodel.listusers(allowedUsers)
            self.usermodel.layoutChanged.emit()
            self.errorlbl.setText('')
        else:
            # print(servermessage)
            self.errorlbl.setText(servermessage)

    def textChanged(self, email):
        # print(ttext)
        if re.search(regex, email):
            self.adduserbttn.setEnabled(True)
        else:
            self.adduserbttn.setEnabled(False)

    def setemailedit(self, selectedIndex):
        # rownumber = emailList.row()
        self.adduserbttn.setEnabled(True)
        self.selecteduseremail=self.sectionUser.getemail(selectedIndex)
        # self.emailedit.setText(email)

        # containerId = containerList.model().data(index, 0)
        # refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , CONTAINERFN)
        # if os.path.exists(refcontainerpath):
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # else:
        #     refpath = os.path.join(sagaguimodel.appdata_saga,'ContainerMapWorkDir')
        #     Container.sagaguimodel.downloadContainerState(refpath,sagaguimodel.authtoken, BASE, containerId)
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # # self.tester.setText(self.selectedContainer.containerName)
        # self.refContainerPlot.changeContainer(self.selectedContainer)
        # self.refContainerPlot.plot({})

    # def getInputs(self):
    #     if self.exec_() == QDialog.Accepted:
    #         return {'userlist':self.usermodel.userlist()}
    #         # print()
    #     else:
    #         return None

