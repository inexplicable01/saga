from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.HistoryListModel import HistoryListModel

from Graphics.TrayActions import SignIn, SignOut, newContainer, find_Local_Container

from Graphics.NewContainerTab import NewContainerTab
from Graphics.MainContainerTab import MainContainerTab
from Graphics.MapTab import MapTab
# from Graphics.Dialogs import errorPopUp
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Graphics.PopUps.newsection import newSection,enterSection

import os
import sys
import requests
import json
import logging
import traceback
import yaml

from functools import partial
from Config import BASE,mapdetailstxt
from SagaApp.WorldMap import WorldMap

# from NewContainerGraphics import newContainerGraphics
# from hackpatch import downloadedFrames

if os.path.exists("token.txt"):
    os.remove("token.txt")

logging.basicConfig(filename='error.log', filemode='a',
                    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

wmap = WorldMap()

class UI(QMainWindow):
    def __init__(self):
        # self.logf = open("C:\\Users\\waich\\LocalGitProjects\\saga\\error.txt", 'w+')
        super(UI, self).__init__()
        uic.loadUi("Graphics/UI/SagaGui.ui", self)
        # self.enterEvent=self.action_enterEvent

        self.guiworkingdir = os.getcwd()
        ## There are two main paths that the GUI needs to be concerns about
        #1. Where the current container of interests is.
        #2. Where is the GUI running from?  This contains settings about the GUI itself and some larger meta-data
        if not os.path.exists(os.path.join(self.guiworkingdir, 'SagaGuiData')):
            os.mkdir(os.path.join(self.guiworkingdir, 'SagaGuiData'))

        ## newcontainertab handles all the QT features on the new container tab, Initiates to false
        # self.newcontainertab = NewContainerTab(self)
        # self.newcontainertab.setTab(False)
        ## maincontainer tab is the active container the user is working on
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
        self.actionNew_Container.triggered.connect(partial(newContainer, self,self.maincontainertab))
        self.actionFind_Local_Container.triggered.connect(partial(find_Local_Container, self, self.maincontainertab))
        self.actionNew_Section.triggered.connect(partial(newSection, self))
        self.actionEnter_Section.triggered.connect(partial(enterSection, self))
        self.maincontainerview.installEventFilter(self)

        self.checkUserStatus()
        self.startingcheck = False

        # self.conect(self.testcreatemanyfiles)
        self.show()


    # def testcreatemanyfiles(self):
    #     Start by create a newuser and newSection
    #     createcontainers with required and output for the first one
    #     Create a hundred
    #     for 1 to 1000:
    #         createrandomfile
    #         add to current frame and container
    #         if input, then grab from randomcontainer:



    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.FocusIn and
            source is self.maincontainerview):
            print('eventFilter: focus in')
            self.maincontainertab.checkdelta()
            self.maincontainertab.checkUpstream()
            # return true here to bypass default behaviour
        return super(UI, self).eventFilter(source, event)

    def getWorldContainers(self):
        response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + self.authtoken['auth_token']})
        containerinfolist = json.loads(response.headers['containerinfolist'])
        if not os.path.exists(os.path.join(self.guiworkingdir,'ContainerMapWorkDir')):
            os.mkdir(os.path.join(self.guiworkingdir,'ContainerMapWorkDir'))
        for containerID in containerinfolist.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID}, headers={"Authorization": 'Bearer ' + self.authtoken['auth_token']})
            if not os.path.exists(os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID)):
                os.mkdir(os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID))
            open(os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name']), 'wb').write(response.content)
            cont = Container.LoadContainerFromYaml( os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name']))
            cont.downloadbranch('Main', BASE, self.authtoken,os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID))
        self.worldlist = containerinfolist.keys()
        if not os.path.exists(os.path.join(self.guiworkingdir, 'SagaGuiData', self.userdata['sectionid'])):
            os.mkdir(os.path.join(self.guiworkingdir, 'SagaGuiData',self.userdata['sectionid']))
            with open(os.path.join(self.guiworkingdir, 'SagaGuiData',self.userdata['sectionid'], mapdetailstxt),'w') as file:
                yaml.dump({'containerlocations':{}}, file)






    def getContainerInfo(self, listtable):
        response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + self.authtoken['auth_token']})
        containerinfolist = json.loads(response.headers['containerinfolist'])
        if not containerinfolist:
            containerinfolist= {'empty': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        listtable.setModel(ContainerListModel(containerinfolist))

    def action_enterEvent(self, event):
        if self.startingcheck:
            self.maincontainertab.checkdelta()

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                authtoken = json.load(json_file)
                response = requests.get(
                    BASE + '/auth/userdetails',
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


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    logging.error("Error:", exc_info=(exc_type, exc_value, exc_tb))
    errorDialog.showMessage("ERROR MESSAGE:" + tb)
    # QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


sys.excepthook = excepthook
app = QApplication([])
window = UI()
errorDialog = QtWidgets.QErrorMessage()

sys.exit(app.exec_())
