# Needles Broken. Feelings Awoken.
# Should we just let it all fade?
# Is it just time?

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.MainContainerTab import MainContainerTab
from Graphics.MapTab import MapTab
from Graphics.Dialogs import updateDialog
from Graphics.PopUps.newsection import newSectionDialog
from Graphics.PopUps.NewContainerDialog import newContainerDialog
from Graphics.PopUps.signinDialog import SigninDialog
from Graphics.PopUps.permissionsDialog import permissionsDialog
from Graphics.PopUps.newuser import newUserDialog
from Graphics.PopUps.switchsection import switchSectionDialog
from Graphics.GuiUtil import setStyle


from SagaGuiModel import sagaguimodel

import os
import sys
import requests
import json
import logging
import traceback
import yaml
import warnings
from functools import partial
from Config import BASE,mapdetailstxt, testerlogin, TEMPCONTAINERFN
from subprocess import Popen

import sys



# from NewContainerGraphics import newContainerGraphics
# from hackpatch import downloadedFrames

if os.path.exists("token.txt"):
    os.remove("token.txt")

logging.basicConfig(filename='error.log', filemode='a',
                    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
debugmode=False
if len(sys.argv)>1:
    if 'debug' ==sys.argv[1]:
        debugmode=True
# print('something')


class UI(QMainWindow):
    def __init__(self):

        super(UI, self).__init__()
        uic.loadUi("Graphics/UI/SagaGui.ui", self)
        # self.enterEvent=self.action_enterEvent
        if not os.name == 'nt':
            raise('saga designed only for windows right now')
        self.desktopdir = sagaguimodel.desktopdir
        ## There are two main paths that the GUI needs to be concerns about
        #1. Where the current container of interests is.
        #2. Where is the GUI running from?  This contains settings about the GUI itself and some larger meta-data

        ## newcontainertab handles all the QT features on the new container tab, Initiates to false
        # self.newcontainertab = NewContainerTab(self)
        # self.newcontainertab.setTab(False)
        ## maincontainer tab is the active container the user is working on
        self.setStyleSheet("QLineEdit { background-color: white }")
        self.maincontainertab = MainContainerTab(self)
        self.maincontainertab.setTab(False)
        self.maptab = MapTab(self)

        # self.userdata = None
        # self.authtoken = None
        self.maintabwidget.setEnabled(False)
        self.menuContainer.setEnabled(False)
        self.menuSection.setEnabled(False)


        ###########Tray Actions #############
        self.actionSign_In.triggered.connect(self.SignIn)
        self.actionSign_Out.triggered.connect(self.SignOut)
        self.actionSign_Up.triggered.connect(self.SignUp)
        self.actionNew_Container.triggered.connect(self.newContainer)
        self.actionFind_Local_Container.triggered.connect(self.find_Local_Container)
        self.actionNew_Section.triggered.connect(self.newSection)
        self.actionEnter_Section.triggered.connect(self.enterSection)
        self.actionContainer_Permission.triggered.connect(self.containerPermission)
        # l1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setCursor(QCursor(Qt.ArrowCursor))

        self.ContainerTab.installEventFilter(self)
        self.containerfiletable.installEventFilter(self)
        self.versionLabel.setText(str(sagaguimodel.versionnumber))

        self.startingcheck = False

        setStyle(self, sagaguimodel.sourcecodedir)

        if debugmode:
            signinstatus = sagaguimodel.sagaapicall.signInCall(testerlogin['email'],
                                                               testerlogin['password'],
                                                               sagaguimodel.tokenfile)
            # self.mainguihandle.checkUserStatus()
            if signinstatus['status'] == 'success':
                self.refresh()
            containerexample = 'C:/Users/waich/LocalGitProjects/testcontainers_saga/Structures/'+TEMPCONTAINERFN
            self.maincontainertab.readcontainer(containerexample)
        self.show()

    def eventFilter(self, source, event):
        if (event.type() in [QtCore.QEvent.FocusIn,QtCore.QEvent.MouseButtonPress]):
            #     and
            # source is self.ContainerTab):
            # print('eventFilter: focus in')
            self.maincontainertab.checkdelta()
            # return true here to bypass default behaviour
        return super(UI, self).eventFilter(source, event)

    def SignIn(self):
        # print(BASE)
        inputwindow = SigninDialog(mainguihandle=self, sagaguimodel=sagaguimodel)
        inputs = inputwindow.getInputs()
        if inputs['signinsuccess']:
            self.refresh()
            # sagaguimodel.getWorldContainers()

    def SignOut(self):
        if os.path.exists("token.txt"):
            os.remove("token.txt")
        self.adjustGuiPerUserStatus()
        # print('sign out' + BASE)

    def SignUp(self):
        # print(BASE)
        newuserwindow = newUserDialog(mainguihandle=self)
        inputs = newuserwindow.getInputs()
        if inputs:
            response = requests.post(BASE + 'auth/register',
                                     data=inputs)
            authtoken = response.json()
            if 'status' in authtoken.keys() and authtoken['status'] == 'success':
                with open('token.txt', 'w') as tokenfile:
                    json.dump(authtoken, tokenfile)
                self.adjustGuiPerUserStatus()
                # sagaguimodel.getWorldContainers()
            else:
                print('usertoken[status] ' + authtoken['status'])

    def newContainer(self):
        newcontainergui = newContainerDialog("Select a local location for building your container")
        inputs = newcontainergui.getInputs()
        if inputs:
            self.maincontainertab.initiate(inputs)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)

    def find_Local_Container(self):
        # inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
        (fname, fil) = QFileDialog.getOpenFileName(self, 'Open container file', '.',
                                                   "Container (*containerstate.yaml)")
        if fname:
            # print(fname)
            self.maincontainertab.readcontainer(fname)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)
            self.maincontainertab.refreshedcheck = 0

    def containerPermission(self):
        if self.maincontainertab.mainContainer:
            permissiongui = permissionsDialog(self.maincontainertab.mainContainer, self)
            permissiongui.exec_()

    def refresh(self):
        self.adjustGuiPerUserStatus()
        containerinfodict = sagaguimodel.getWorldContainers()
        self.maptab.generateContainerMap(containerinfodict)
        self.maptab.generateSagaTree(containerinfodict)


    def resetguionsectionswitch(self):
        self.maincontainertab.reset()
        self.maptab.reset()
        self.adjustGuiPerUserStatus()

        ##Regenerate Container Ids of new section that got switched to.
        containerinfodict = sagaguimodel.getWorldContainers()
        self.maptab.generateContainerMap(containerinfodict)
        self.maptab.generateSagaTree(containerinfodict)
        # self.gantttable.setModel(GanttListModel([], sagaguimodel.desktopdir))

    def newSection(self):
        newsectiongui = newSectionDialog(self,
                                         "In order to create a New Section, you must make a new profile.  For now, a profile can only belong in one Section")
        inputs = newsectiongui.getInputs()

        if inputs:
            response = requests.post(BASE + 'auth/register',
                                     data=inputs)
            authtoken = response.json()
            print('usertoken[status] ' + authtoken['status'])
            with open('token.txt', 'w') as tokenfile:
                json.dump(authtoken, tokenfile)

            self.adjustGuiPerUserStatus()

    def enterSection(self):
        # response = requests.get(BASE + 'user/getusersections', )
        headers = {'Authorization': 'Bearer ' + sagaguimodel.authtoken}
        response = requests.get(BASE + 'USER/getusersections', headers=headers)

        resp = json.loads(response.content)
        sectioninfo = resp['sectioninfo']
        currentsection = resp['currentsection']

        switchsectiongui = switchSectionDialog(self, sectioninfo, currentsection)
        needtoupdateworldmap = switchsectiongui.waitfordone()
        # if needtoupdateworldmap:
        #     # print(inputs)
        #     self.refresh()

    def setPermissionsEnable(self):
        self.actionContainer_Permission.setEnabled(True)
        font = QFont('Times', 10)
        font.setStrikeOut(False)
        self.actionContainer_Permission.setFont(font)

    def adjustGuiPerUserStatus(self):
        status = sagaguimodel.checkUserStatus()
        self.userstatuslbl.setText(status['userstatusstatement'])
        self.menuContainer.setEnabled(status['signinsuccess'])
        self.menuSection.setEnabled(status['signinsuccess'])
        self.maintabwidget.setEnabled(status['signinsuccess'])
        if status['signinsuccess']:
            self.maintabwidget.setCurrentWidget(self.maintabwidget.findChild(QWidget, "Map"))
        if status['signinsuccess']:
            serverVersion = sagaguimodel.userdata['version_num']
            if sagaguimodel.versionnumber != serverVersion:
                updater = updateDialog()
                if updater.update() == True:
                    response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
                                            headers={"Authorization": 'Bearer ' + self.authtoken})
                    installPath = os.path.join(sagaguimodel.desktopdir, 'Saga.exe')
                    open(installPath, 'wb').write(response.content)
                    Popen(installPath, shell=True)
                    sys.exit(app.exec_())




def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    logging.error("Error:", exc_info=(exc_type, exc_value, exc_tb))
    errorDialog.showMessage("ERROR MESSAGE:" + tb)
    # QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


# sys.excepthook = excepthook
app = QApplication([])
window = UI()
errorDialog = QtWidgets.QErrorMessage()

sys.exit(app.exec_())
