from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.HistoryListModel import HistoryListModel

from Graphics.TrayActions import SignIn, SignOut,SignUp, newContainer, find_Local_Container , containerPermission

from Graphics.MainContainerTab import MainContainerTab
from Graphics.MapTab import MapTab
from Graphics.Dialogs import updateDialog
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Graphics.PopUps.newsection import newSection
from Graphics.PopUps.switchsection import enterSection
from SagaApp.SagaUtil import getContainerInfo



import os
import sys
import requests
import json
import logging
import traceback
import yaml
import warnings
from functools import partial
from Config import BASE,mapdetailstxt
from SagaApp.WorldMap import WorldMap
from subprocess import Popen
from SagaApp.SagaUtil import makefilehidden

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

        super(UI, self).__init__()
        uic.loadUi("Graphics/UI/SagaGui.ui", self)
        # self.enterEvent=self.action_enterEvent
        if not os.name == 'nt':
            raise('saga designed only for windows right now')
        self.guiworkingdir = os.getcwd()
        ## There are two main paths that the GUI needs to be concerns about
        #1. Where the current container of interests is.
        #2. Where is the GUI running from?  This contains settings about the GUI itself and some larger meta-data
        guidirs= [ 'SagaGuiData','ContainerMapWorkDir']
        for guidir in guidirs:
            guidatadir = os.path.join(self.guiworkingdir,guidir)
            if not os.path.exists(guidatadir):
                os.mkdir(guidatadir)
            makefilehidden(guidatadir)

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
        self.menuSection.setEnabled(False)


        ###########Tray Actions #############
        self.actionSign_In.triggered.connect(partial(SignIn, self))
        self.actionSign_Out.triggered.connect(partial(SignOut, self))
        self.actionSign_Up.triggered.connect(partial(SignUp, self))
        self.actionNew_Container.triggered.connect(partial(newContainer, self,self.maincontainertab))
        self.actionFind_Local_Container.triggered.connect(partial(find_Local_Container, self, self.maincontainertab))
        self.actionNew_Section.triggered.connect(partial(newSection, self))
        self.actionEnter_Section.triggered.connect(partial(enterSection, self))
        self.actionContainer_Permission.triggered.connect(partial(containerPermission, self, self.maincontainertab))
        # self.menuContainer.triggered.connect(self.testprint)
        # self.action1 = QAction('blahblah', self)
        # self.menuBar.addAction(self.action1)
        # self.action1.triggered.connect(self.testprint)

        self.maincontainerview.installEventFilter(self)
        self.versionNumber = 0.0
        self.versionLabel.setText(str(self.versionNumber))
        self.checkUserStatus()
        self.startingcheck = False

        # self.conect(self.testcreatemanyfiles)
        self.sourcefolderlbl.setText(self.guiworkingdir)
        self.show()

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.FocusIn and
            source is self.maincontainerview):
            print('eventFilter: focus in')
            self.maincontainertab.checkdelta()

            # return true here to bypass default behaviour
        return super(UI, self).eventFilter(source, event)

    def getWorldContainers(self):
        # response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfolist = getContainerInfo(self.authtoken)
        if 'EMPTY' in containerinfolist.keys():
            self.worldlist=None
            return containerinfolist

        for containerID in containerinfolist.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID}, headers={"Authorization": 'Bearer ' + self.authtoken})
            if not os.path.exists(os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID)):
                os.mkdir(os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID))
            if os.path.exists(os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name'])):
                open(os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name']), 'rb+').write(response.content)
            else:
                open(os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name']), 'wb').write(
                    response.content)
            cont = Container.LoadContainerFromYaml( os.path.join('ContainerMapWorkDir', containerID, response.headers['file_name']), fullload=False)
            cont.downloadbranch('Main', BASE, self.authtoken,os.path.join(self.guiworkingdir,'ContainerMapWorkDir',containerID))

        self.worldlist = containerinfolist.keys()

        if not os.path.exists(os.path.join(self.guiworkingdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(os.path.join(self.guiworkingdir, 'SagaGuiData',self.userdata['current_sectionid']))
            with open(os.path.join(self.guiworkingdir, 'SagaGuiData',self.userdata['current_sectionid'], mapdetailstxt),'w') as file:
                yaml.dump({'containerlocations':{}}, file)
        return containerinfolist
        # self.maptab.updateContainerMap()

    def refresh(self):
        self.checkUserStatus()
        containerinfolist = self.getWorldContainers()
        self.maptab.generateContainerMap(containerinfolist)

    def resetguionsectionswitch(self):
        self.maincontainertab.reset()
        self.maptab.reset()
        self.checkUserStatus()
        containerinfolist = self.getWorldContainers()

        self.maptab.generateContainerMap(containerinfolist)



    def action_enterEvent(self, event):
        if self.startingcheck:
            self.maincontainertab.checkdelta()

    def setPermissionsEnable(self):
        self.actionContainer_Permission.setEnabled(True)
        font = QFont('Times', 10)
        font.setStrikeOut(False)
        self.actionContainer_Permission.setFont(font)

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                token = json.load(json_file)
                response = requests.get(
                    BASE + '/auth/userdetails',
                    headers={"Authorization": 'Bearer ' + token['auth_token']}
                )
                usertoken = response.json()
                if usertoken['status'] == 'success':
                    self.userdata = usertoken['data']
                    self.userstatuslbl.setText('User ' + self.userdata['email'] + ' Signed in to Section ' + self.userdata['current_sectionname'])

                    self.authtoken = token['auth_token']
                    self.menuContainer.setEnabled(True)
                    self.menuSection.setEnabled(True)
                    self.tabWidget.setCurrentWidget(self.tabWidget.findChild(QWidget, "Map"))
                else:
                    self.authtoken = None
                    self.userstatuslbl.setText('Please sign in')
                    self.userdata = None
                    self.menuContainer.setEnabled(False)
                    self.menuSection.setEnabled(False)
                if self.menuContainer.isEnabled() and self.authtoken:
                    self.tabWidget.setEnabled(True)
                    serverVersion = self.userdata['version_num']
                    if self.versionNumber is not serverVersion:
                        updater = updateDialog()
                        if updater.update() == True:
                            response = requests.get(BASE + 'GENERAL/UpdatedInstallation', headers={"Authorization": 'Bearer ' + self.authtoken})
                            installPath = os.path.join(self.guiworkingdir, 'Saga.exe')
                            open(installPath, 'wb').write(response.content)
                            Popen(installPath, shell = True)
                            sys.exit(app.exec_())

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
