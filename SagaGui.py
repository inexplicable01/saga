# Needles Broken. Feelings Awoken.
# Should we just let it all fade?
# Is it just time?

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# from Graphics.QAbstract.ContainerListModel import ContainerListModel
# from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.MainContainerTab import MainContainerTab
from Graphics.MapTab import MapTab
from Graphics.Dialogs import updateDialog
from Graphics.PopUps.newsection import newSectionDialog
from Graphics.PopUps.NewContainerDialog import newContainerDialog
from Graphics.PopUps.signinDialog import  LoginScreen
from Graphics.PopUps.permissionsDialog import permissionsDialog
from Graphics.PopUps.newuser import newUserDialog
from Graphics.PopUps.switchsection import switchSectionDialog
from Graphics.PopUps.sectionSynchDialog import sectionSynchDialog
from Graphics.PopUps.AddChildContainerDialog import AddChildContainerDialog
from Graphics.GuiUtil import setStyle, makeganttchartlegend
from Graphics.PopUps.SagaFolderDialog import SagaFolderDialog
from Graphics.PopUps.inviteUserToSection import inviteUserToSectionDialog

from SagaGuiModel import sagaguimodel

import os
import sys
import requests
import json
import logging
import traceback
import yaml
import warnings
from SagaGuiModel.DevConstants import  testerlogin
from SagaGuiModel.GuiModelConstants import *
from Config import sourcecodedirfromconfig, chosenlogin
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

logging.basicConfig(filename=os.path.join(sagaguimodel.appdata_saga,'error.log'), filemode='a',
                    format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
debugmode=False
debugsignin = False
if len(sys.argv)>1:
    if 'debug' ==sys.argv[1]:
        debugmode=True
        if len(sys.argv)>2:
            debugsignin = True

class SagaUI(QMainWindow):
    def __init__(self):
        super(SagaUI, self).__init__()
        # with open('C:/Users/waich/AppData/Roaming/SagaDesktop/testing.txt', 'a+') as file:
        #     file.write('\n1\n\n\n')
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","SagaGui.ui"), self)
        with open(os.path.join(sagaguimodel.appdata_saga, 'testing.txt'), 'a+') as file:
            file.write('\n'+os.getcwd()+ '\n\n\n')
        # self.enterEvent=self.action_enterEvent
        if not os.name == 'nt':
            raise('saga designed only for windows right now')
        self.appdata_saga = sagaguimodel.appdata_saga
        sagaguimodel.mainguihandle = self
        self.errormessageboxhandle = QMessageBox()

        sagaguimodel.sagaapicall.mainguihandle = self
        sagaguimodel.assignErrorMessageBoxHandle(self.errormessageboxhandle)

        with open(os.path.join(sagaguimodel.appdata_saga, 'basicoutput.txt'),'w+') as file:
            file.write(sagaguimodel.sourcecodedir)
        sagaguimodel.debugmode = debugmode
        ## There are two main paths that the GUI needs to be concerns about
        #1. Where the current container of interests is.
        #2. Where is the GUI running from?  This contains settings about the GUI itself and some larger meta-data


        ## newcontainertab handles all the QT features on the new container tab, Initiates to false
        # self.newcontainertab = NewContainerTab(self)
        # self.newcontainertab.setTab(False)
        ## maincontainer tab is the active container the user is working on
        # self.setStyleSheet("QLineEdit { background-color: white }")
        self.maincontainertab = MainContainerTab(self)
        self.maincontainertab.setTab(False)
        self.maptab = MapTab(self)

        self.maintabwidget.setEnabled(False)
        self.menuContainer.setEnabled(False)
        self.menuSection.setEnabled(False)

        ###########Tray Actions #############
        # self.actionSign_In.triggered.connect(self.SignIn)
        self.actionSign_Out.triggered.connect(self.SignOut)
        # self.actionSign_Up.triggered.connect(self.SignUp)
        self.actionNew_Container.triggered.connect(self.newContainer)
        self.actionFind_Local_Container.triggered.connect(self.find_Local_Container)
        self.actionCreate_Child_Container.triggered.connect(self.createChildContainer)
        self.actionNew_Section.triggered.connect(self.newSection)
        # self.actionwhat_sogi.triggered.connect(self.print)
        self.actionEnter_Section.triggered.connect(self.enterSection)
        # self.actionContainer_Permission.triggered.connect(self.containerPermission)
        self.actionContainer_Permission.triggered.connect(self.containerPermission)
        self.actionSection_Sync_Status.triggered.connect(self.sectionsynchronizationwindow)
        self.actionInvite_Users_to_Section.triggered.connect(self.inviteUsertoSection)
        # l1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setCursor(QCursor(Qt.ArrowCursor))
        # with open('C:/Users/waich/AppData/Roaming/SagaDesktop/testing.txt', 'a+') as file:
        #     file.write('\nhere we are \n\n\n')
        # self.ContainerTab.installEventFilter(self)
        # self.containerfiletable.installEventFilter(self)
        self.versionLabel.setText(str(sagaguimodel.versionnumber))
        self.titlefct = None
        self.startingcheck = False

        setStyle(self, sagaguimodel.sourcecodedir)

        # if debugsignin:
        #     status , usertokeninfo = sagaguimodel.signIn(testerlogin['email'], testerlogin['password'], saveprofile=True)
        #     # self.mainguihandle.checkUserStatus()
        #     if status:
        #         self.adjustGuiByUserStatusChange()
        #         self.guireset()
        #         self.loadSection()
        #         containerexample = 'C:/Users/waich/LocalGitProjects/testcontainers_saga/Structures/'+CONTAINERFN
        #         self.maincontainertab.readcontainer(containerexample)
        self.show()
        makeganttchartlegend(self.ganttlegendview)
        # self.setWindowTitle('SagaGui')

    # def eventFilter(self, source, event):
    #     if (event.type() in [QtCore.QEvent.FocusIn,QtCore.QEvent.MouseButtonPress]):
    #         #     and
    #         # source is self.ContainerTab):
    #         # print('eventFilter: focus in')
    #         # self.maincontainertab.checkdelta()
    #         # return true here to bypass default behaviour
    #     return super(UI, self).eventFilter(source, event)

    # def SignIn(self):
    #     # print(BASE)
    #     inputwindow = SigninDialog(mainguihandle=self, sagaguimodel=sagaguimodel)
    #     inputs = inputwindow.getInputs()
    #     if inputs['signinsuccess']:
    #         self.adjustGuiByUserStatusChange()
    #         self.guireset()
    #         self.loadSection()
    #         # sagaguimodel.getWorldContainers()

    def setTitleEditorFunction(self,setTitleEditorFunction):
        self.titlefct = setTitleEditorFunction

    def SignOut(self):
        if os.path.exists(sagaguimodel.tokenfile):
            os.remove(sagaguimodel.tokenfile)
        sagaguimodel.signOut()
        self.adjustGuiByUserStatusChange()
        self.guireset()
        widget.setCurrentIndex(0)


        # self.loadSection()
        # print('sign out' + BASE)

    # def SignUp(self):
    #     # print(BASE)
    #     newuserwindow = newUserDialog(mainguihandle=self)
    #     # self.emaileditself.text(), self.passwordedit, self.firstnameedit.text(), \
    #     # self.lastnameedit.text(), self.comboboxid[self.sectioncombobox.currentIndex()]
    #     email, password, firstname, lastname, sectionid = newuserwindow.getInputs()
    #     if email:
    #         signinsuccess = sagaguimodel.newUserSignUp(email, password, firstname, lastname, sectionid )
    #         if signinsuccess:
    #             self.adjustGuiByUserStatusChange()
    #             self.guireset()
    #             self.loadSection()
    #         else:
    #             print('user sign in failed')

    def newContainer(self):
        newcontainergui = newContainerDialog("Select a local location for building your container")
        inputs = newcontainergui.getInputs()
        if inputs:
            self.maincontainertab.initiate(inputs)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)

    def createChildContainer(self):
        childcontainergui = AddChildContainerDialog(os.getcwd())
        childcontainerdict = childcontainergui.getInputs()
        if childcontainerdict:
            sagaguimodel.addChildContainer(childcontainerdict)

    def find_Local_Container(self):
        folderdialog = SagaFolderDialog(os.getcwd())
        containeryaml = folderdialog.getfilepath()
        if containeryaml:
            self.maincontainertab.readcontainer(containeryaml)
            self.maintabwidget.setCurrentIndex(self.maincontainertab.index)


    def containerPermission(self):
        if sagaguimodel.maincontainer:
            permissionsDialog(self)
        # self.gantttable.setModel(GanttListModel([], sagaguimodel.appdata_saga))

    def newSection(self):
        newsectiongui = newSectionDialog(self)
        newsectiongui.newSection()

    def enterSection(self):
        success,sectioninfo, currentsection = sagaguimodel.sagaapicall.getListofSectionsforUser()
        switchsectiongui = switchSectionDialog(self, sectioninfo, currentsection)
        needtoupdateworldmap = switchsectiongui.waitfordone()
        if needtoupdateworldmap:
            self.guireset()
            self.loadSection()

    def inviteUsertoSection(self):
        emailsToInviteToSection = inviteUserToSectionDialog(self)
        # emailsToInvite = emailsToInviteToSection.getInputs()
        # if emailsToInvite:
        #     sagaguimodel.addEmailsToSection(emailsToInvite)

    def sectionsynchronizationwindow(self):
        if sagaguimodel.usersess is not None:
            if sagaguimodel.usersess.current_sectionid:
                sectionSynchDialog(self)

    def setPermissionsEnable(self):
        self.actionContainer_Permission.setEnabled(True)
        font = QFont('Times', 10)
        font.setStrikeOut(False)
        self.actionContainer_Permission.setFont(font)

    def guireset(self):
        self.maincontainertab.reset()
        self.maptab.reset()

    def loadSection(self):
        containerinfodict , current_sectionname = sagaguimodel.getWorldContainers()
        print('start of map gen' + datetime.now().isoformat())
        self.maptab.generateContainerMap(containerinfodict)
        self.maptab.generateSagaTree(containerinfodict)
        self.titlefct('Saga Gui,  Current Section : ' + current_sectionname)
        # print('end of map gen' + datetime.now().isoformat())

    def adjustGuiByUserStatusChange(self):
        success,usersess = sagaguimodel.checkUserStatus()
        if usersess:
            userstatusstatement= 'User ' + usersess.email + ' Signed in to Section ' + usersess.current_sectionname
        else:
            userstatusstatement=''
        self.userstatuslbl.setText(userstatusstatement)
        self.menuContainer.setEnabled(success)
        self.menuSection.setEnabled(success)
        self.maintabwidget.setEnabled(success)
        self.actionNew_Section.setEnabled(success)
        if success:
            self.maintabwidget.setCurrentWidget(self.maintabwidget.findChild(QWidget, "Map"))
            serverVersion = sagaguimodel.usersess.version_num
            if sagaguimodel.versionnumber != serverVersion:
                updater = updateDialog()
                if updater.update() == True:
                    sagaguimodel.getNewVersionInstaller(app)

    def errout(self,errmsg):
        self.errormessageboxhandle.setText(errmsg)
        self.errormessageboxhandle.exec_()
        # QtWidgets.QApplication.quit()

    def setPageIndexes(self,SIGNINPAGEINDEX, CREATEACCINDEX, LOGININDEX,MAINAPPINDEX):
        self.index = SIGNINPAGEINDEX


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    logging.error("Error:", exc_info=(exc_type, exc_value, exc_tb))
    errorDialog.showMessage("ERROR MESSAGE:" + tb)
    # QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "welcomescreen.ui"), self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        widget.setCurrentIndex(LOGININDEX)

    def gotocreate(self):
        widget.setCurrentIndex(CREATEACCINDEX)


class FillProfileScreen(QDialog):
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","fillprofile.ui"),self)
        self.image.setPixmap(QPixmap('placeholder.png'))

if not debugmode:
    sys.excepthook = excepthook

# SIGNINPAGEINDEX = 0
# CREATEACCINDEX = 1
# LOGININDEX = 2
# MAINAPPINDEX = 3

app = QApplication([])
# window = UI()
mainguihandle = SagaUI()
errorDialog = QtWidgets.QErrorMessage()
widget = QtWidgets.QStackedWidget()

def widgetwindoweditor(windowtitle):
    widget.setWindowTitle(windowtitle)
mainguihandle.setTitleEditorFunction(widgetwindoweditor)
widget.insertWidget(SIGNINPAGEINDEX,WelcomeScreen())
widget.insertWidget(CREATEACCINDEX,newUserDialog(mainguihandle, sagaguimodel,widget))
widget.insertWidget(LOGININDEX,LoginScreen(mainguihandle, sagaguimodel,widget))
widget.insertWidget(MAINAPPINDEX,mainguihandle)


mainguihandle.setPageIndexes(SIGNINPAGEINDEX=SIGNINPAGEINDEX, CREATEACCINDEX=CREATEACCINDEX,LOGININDEX=LOGININDEX,
                             MAINAPPINDEX=MAINAPPINDEX)


# widget.setFixedHeight(900)
# widget.setFixedWidth(1200)
widget.setWindowTitle('Saga Gui')
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
