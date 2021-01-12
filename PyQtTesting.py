from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.HistoryListModel import HistoryListModel

from Graphics.TrayActions import SignIn, SignOut, newContainer, find_Local_Container

from Graphics.NewContainerTab import NewContainerTab
from Graphics.MainContainerTab import MainContainerTab
from Graphics.MapTab import MapTab

from Frame.FrameStruct import Frame
from Frame.Container import Container

import os
import sys
import requests
import json

from functools import partial
from Config import BASE

# from NewContainerGraphics import newContainerGraphics
# from hackpatch import downloadedFrames

if os.path.exists("token.txt"):
    os.remove("token.txt")

class UI(QMainWindow):
    def __init__(self):
        # self.logf = open("C:\\Users\\waich\\LocalGitProjects\\saga\\error.txt", 'w+')
        super(UI, self).__init__()
        uic.loadUi("Graphics/SagaGui.ui", self)
        self.enterEvent=self.action_enterEvent

        self.newcontainertab = NewContainerTab(self)
        self.newcontainertab.setTab(False)
        self.maincontainertab = MainContainerTab(self)
        self.maincontainertab.setTab(False)
        self.maptab = MapTab(self)

        self.userdata = None
        self.authtoken = None
        self.tabWidget.setEnabled(False)
        self.menuContainer.setEnabled(False)

        ###########Tray Actions #############
        self.actionSign_In.triggered.connect(partial(SignIn, self))
        self.actionSign_Out.triggered.connect(partial(SignOut, self))
        self.actionNew_Container.triggered.connect(partial(newContainer, self,self.newcontainertab))
        self.actionFind_Local_Container.triggered.connect(partial(find_Local_Container, self, self.maincontainertab))

        self.checkUserStatus()
        self.startingcheck = False

        self.show()

    def getContainerInfo(self, listtable):
        response = requests.get(BASE + 'CONTAINERS/List')
        containerinfolist = json.loads(response.headers['containerinfolist'])
        listtable.setModel(ContainerListModel(containerinfolist))

    def action_enterEvent(self, event):
        if self.startingcheck:
            self.maincontainertab.checkdelta()

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                authtoken = json.load(json_file)
                response = requests.get(
                    BASE + '/auth/status',
                    headers={"Authorization": 'Bearer ' + authtoken['auth_token']}
                )
                usertoken = response.json()
                if usertoken['status'] == 'success':
                    self.userstatuslbl.setText('User ' + usertoken['data']['email'] + ' Signed in')
                    self.userdata = usertoken['data']
                    self.authtoken = authtoken

                    self.menuContainer.setEnabled(True)
                else:
                    self.authtoken = None
                    self.userstatuslbl.setText('Please sign in')
                    self.userdata = None

                    self.menuContainer.setEnabled(False)
                if self.menuContainer.isEnabled() and self.authtoken:
                    self.tabWidget.setEnabled(True)
        except Exception as e:
            print('No User Signed in yet')


app = QApplication([])
window = UI()
sys.exit(app.exec_())
