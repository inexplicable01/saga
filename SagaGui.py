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
from Graphics.PopUps.SagaFolderDialog import SagaFolderDialog

from SagaGuiModel import sagaguimodel

import os
import sys
import requests
import json
import logging
import traceback
import yaml
import warnings
from Config import BASE,mapdetailstxt, testerlogin, TEMPCONTAINERFN, sourcecodedirfromconfig
import sys
from datetime import datetime
from os.path import join
# with open('testing.txt', 'a+') as file:
#     file.write('\nmore12\n\n\n')
# # from NewContainerGraphics import newContainerGraphics
# # from hackpatch import downloadedFrames
# with open('testing.txt', 'a+') as file:
#     file.write('\nmore12\n\n\n')

if os.path.exists(sagaguimodel.tokenfile):
    os.remove(sagaguimodel.tokenfile)

logging.basicConfig(filename=os.path.join(sagaguimodel.desktopdir,'error.log'), filemode='a',
                    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
debugmode=False
debugsignin = False
if len(sys.argv)>1:
    if 'debug' ==sys.argv[1]:
        debugmode=True
        if len(sys.argv)>2:
            debugsignin = True

# print('something')


class UI(QMainWindow):
    def __init__(self):

        super(UI, self).__init__()
        # with open('C:/Users/waich/AppData/Roaming/SagaDesktop/testing.txt', 'a+') as file:
        #     file.write('\n1\n\n\n')
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","SagaGui.ui"), self)
        with open(os.path.join(sagaguimodel.desktopdir, 'testing.txt'), 'a+') as file:
            file.write('\n'+os.getcwd()+ '\n\n\n')
        # self.enterEvent=self.action_enterEvent
        if not os.name == 'nt':
            raise('saga designed only for windows right now')
        self.desktopdir = sagaguimodel.desktopdir
        sagaguimodel.mainguihandle = self
        with open(os.path.join(sagaguimodel.desktopdir, 'basicoutput.txt'),'w+') as file:
            file.write(sagaguimodel.sourcecodedir)
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
        # with open('C:/Users/waich/AppData/Roaming/SagaDesktop/testing.txt', 'a+') as file:
        #     file.write('\nhere we are \n\n\n')


        #
        # self.ContainerTab.installEventFilter(self)
        # self.containerfiletable.installEventFilter(self)
        self.versionLabel.setText(str(sagaguimodel.versionnumber))

        self.startingcheck = False

        setStyle(self, sagaguimodel.sourcecodedir)

        if debugsignin:
            signinstatus = sagaguimodel.sagaapicall.signInCall(testerlogin['email'],
                                                               testerlogin['password'],
                                                                  sagaguimodel.tokenfile)
            # self.mainguihandle.checkUserStatus()
            if signinstatus['status'] == 'success':
                self.adjustGuiByUserStatusChange()
                self.guireset()
                self.loadSection()
            containerexample = 'C:/Users/waich/LocalGitProjects/testcontainers_saga/FormationDesignGroup/ConflictsTester/'+TEMPCONTAINERFN
            self.maincontainertab.readcontainer(containerexample)
        self.show()

    # def eventFilter(self, source, event):
    #     if (event.type() in [QtCore.QEvent.FocusIn,QtCore.QEvent.MouseButtonPress]):
    #         #     and
    #         # source is self.ContainerTab):
    #         # print('eventFilter: focus in')
    #         # self.maincontainertab.checkdelta()
    #         # return true here to bypass default behaviour
    #     return super(UI, self).eventFilter(source, event)

    def SignIn(self):
        # print(BASE)
        inputwindow = SigninDialog(mainguihandle=self, sagaguimodel=sagaguimodel)
        inputs = inputwindow.getInputs()
        if inputs['signinsuccess']:
            self.adjustGuiByUserStatusChange()
            self.guireset()
            self.loadSection()
            # sagaguimodel.getWorldContainers()

    def SignOut(self):
        if os.path.exists(sagaguimodel.tokenfile):
            os.remove(sagaguimodel.tokenfile)
        sagaguimodel.signOut()
        self.adjustGuiByUserStatusChange()
        self.guireset()
        # self.loadSection()
        # print('sign out' + BASE)

    def SignUp(self):
        # print(BASE)
        newuserwindow = newUserDialog(mainguihandle=self)
        formentry = newuserwindow.getInputs()
        if formentry:
            signinsuccess = sagaguimodel.newUserSignUp(formentry)
            if signinsuccess:
                self.adjustGuiByUserStatusChange()
                self.guireset()
                self.loadSection()
            else:
                print('user sign in failed')

    def newContainer(self):
        newcontainergui = newContainerDialog("Select a local location for building your container")
        inputs = newcontainergui.getInputs()
        if inputs:
            self.maincontainertab.initiate(inputs)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)

    def find_Local_Container(self):
        # inputwindow = InputDialog(MainGuiHandle=MainGuiHandle)
        # (fname, fil) = QFileDialog.getOpenFileName(self, 'Open container file', '.',
        #                                            "Container (*containerstate.yaml)")
        # if fname:
        #     # print(fname)
        #     self.maincontainertab.readcontainer(fname)
        #     self.maintabwidget.setCurrentIndex(self.maincontainertab.index)
        #     self.maincontainertab.refreshedcheck = 0
        folderdialog = SagaFolderDialog(os.getcwd())
        containeryaml = folderdialog.getfilepath()
        if containeryaml:
            self.maincontainertab.readcontainer(containeryaml)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)


    def containerPermission(self):
        if sagaguimodel.maincontainer:
            permissiongui = permissionsDialog(sagaguimodel.maincontainer, self)
            permissiongui.exec_()
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
            with open(sagaguimodel.tokenfile, 'w') as tokenfile:
                json.dump(authtoken, tokenfile)
            self.guireset()
            self.loadSection()

    def enterSection(self):
        sectioninfo, currentsection = sagaguimodel.sagaapicall.getListofSectionsforUser()
        switchsectiongui = switchSectionDialog(self, sectioninfo, currentsection)
        needtoupdateworldmap = switchsectiongui.waitfordone()
        if needtoupdateworldmap:
            # self.adjustGuiByUserStatusChange()
            self.guireset()
            self.loadSection()

    def setPermissionsEnable(self):
        self.actionContainer_Permission.setEnabled(True)
        font = QFont('Times', 10)
        font.setStrikeOut(False)
        self.actionContainer_Permission.setFont(font)

    def guireset(self):
        self.maincontainertab.reset()
        self.maptab.reset()

    def loadSection(self):
        containerinfodict = sagaguimodel.getWorldContainers()
        print('start of map gen' + datetime.now().isoformat())
        self.maptab.generateContainerMap(containerinfodict)
        self.maptab.generateSagaTree(containerinfodict)
        # print('end of map gen' + datetime.now().isoformat())

    def adjustGuiByUserStatusChange(self):
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
                    sagaguimodel.getNewVersionInstaller(app)

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    logging.error("Error:", exc_info=(exc_type, exc_value, exc_tb))
    errorDialog.showMessage("ERROR MESSAGE:" + tb)
    # QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


if not debugmode:
    sys.excepthook = excepthook
app = QApplication([])
window = UI()
errorDialog = QtWidgets.QErrorMessage()

sys.exit(app.exec_())
