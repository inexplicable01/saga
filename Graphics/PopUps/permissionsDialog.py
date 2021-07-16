from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import random
import string
import os
from SagaApp.Container import Container
from Graphics.QAbstract.UserListModel import UserListModel,SectionUserListModel
import json
import re
import requests
# Make a regular expression
# for validating an Email
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

from Config import BASE
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
    def __init__(self, mainContainer:Container, mainguihandle):
        super().__init__()
        uic.loadUi("Graphics/UI/permissionsDialog.ui", self)
        self.mainguihandle= mainguihandle
        self.mainContainer = mainContainer
        response = requests.get(BASE + 'PERMISSIONS/getByContainer',
                                 json={"email": self.mainguihandle.userdata['email'] ,
                                        "sectionid":self.mainguihandle.userdata['current_sectionid'],
                                       "containerId": self.mainContainer.containerId}
                                 )

        permissionsresponse = json.loads(response.content)
        self.allowedToAdd = False
        if mainguihandle.userdata['email'] in permissionsresponse['allowedUser']:
            self.allowedToAdd = True

        self.usermodel = UserListModel(mainContainer.allowedUser)
        self.alloweduserview.setModel(self.usermodel)

        self.sectionUser = SectionUserListModel(permissionsresponse['sectionUser'])
        self.regsectionuserview.setModel(self.sectionUser)
        self.regsectionuserview.clicked.connect(self.setemailedit)

        self.emailedit.setEnabled(self.allowedToAdd)

        self.adduserbttn.clicked.connect(self.adduser)
        self.adduserbttn.setEnabled(False)
        self.emailedit.textChanged[str].connect(self.textChanged)
        # self.adduserbttn.clicked.connect()
        self.exitbttn.clicked.connect(self.reject)

    def adduser(self):
        response = requests.post(BASE + 'PERMISSIONS/AddUserToContainer',
                                 headers={"Authorization": 'Bearer ' + sagaguimodel.authtoken},
                                 json={"email": self.mainguihandle.userdata['email'],
                                       "new_email":self.emailedit.text(),
                                        "sectionid":self.mainguihandle.userdata['current_sectionid'],
                                       "containerId": self.mainContainer.containerId,
                                       }
                                 )
        permissionsresponse = json.loads(response.content)
        print(permissionsresponse['ServerMessage'])
        if permissionsresponse['result']:
            self.mainContainer.setAllowedUser(permissionsresponse['allowedUser'])
            self.emailedit.setText('')
            self.usermodel.listusers(self.mainContainer.allowedUser)
            self.usermodel.layoutChanged.emit()
        else:
            self.errorlbl.setText(permissionsresponse['ServerMessage'])

    def textChanged(self, email):
        # print(ttext)
        if re.search(regex, email):
            self.adduserbttn.setEnabled(True)
        else:
            self.adduserbttn.setEnabled(False)

    def setemailedit(self, selectedIndex):
        # rownumber = emailList.row()
        email = self.sectionUser.getemail(selectedIndex)
        self.emailedit.setText(email)

        # containerId = containerList.model().data(index, 0)
        # refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , CONTAINERFN)
        # if os.path.exists(refcontainerpath):
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # else:
        #     refpath = os.path.join(sagaguimodel.desktopdir,'ContainerMapWorkDir')
        #     Container.downloadContainerInfo(refpath,sagaguimodel.authtoken, BASE, containerId)
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

