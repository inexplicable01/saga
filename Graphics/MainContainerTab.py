from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.Dialogs import alteredinputFileDialog
import requests
import os
from Config import BASE
from Config import typeInput,typeOutput,typeRequired, boxwidth, boxheight
from Frame.FrameStruct import Frame
from Frame.Container import Container

class MainContainerTab():
    def __init__(self,mainGuiHandle):
        self.commitBttn = mainGuiHandle.commitBttn
        self.resetbutton = mainGuiHandle.resetbutton
        self.rebasebutton = mainGuiHandle.rebasebutton
        self.revertbttn = mainGuiHandle.revertbttn
        self.commitmsgEdit = mainGuiHandle.commitmsgEdit
        self.commithisttable = mainGuiHandle.commithisttable
        self.refreshBttn = mainGuiHandle.refreshBttn
        self.framelabel = mainGuiHandle.framelabel
        self.frameView = mainGuiHandle.frameView
        self.menuContainer = mainGuiHandle.menuContainer
        self.frametextBrowser = mainGuiHandle.frametextBrowser
        self.index=1

        self.mainGuiHandle =mainGuiHandle

        self.GuiTab = mainGuiHandle.ContainerTab
        # self.openContainerBttn = mainGuiHandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir=''



        # self.openContainerBttn.setText('Open Container')
        # self.openContainerBttn.clicked.connect(self.readcontainer)
        self.refreshBttn.clicked.connect(self.checkdelta)
        self.resetbutton.clicked.connect(self.resetrequest)
        self.rebasebutton.clicked.connect(self.rebaserequest)
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.alterRevertButton)
        self.alterfiletracks=[]

    def resetrequest(self):
        response = requests.get(BASE + 'RESET')
        print(response.content)

    def rebaserequest(self):
        response = requests.post(BASE + 'RESET')
        print(response.content)

    def setTab(self, tabon):
        self.GuiTab.setEnabled(tabon)

    def revert(self):
        self.mainContainer.workingFrame.revertTo(self.reverttorev)
        self.commitmsgEdit.setText('Revert back to ' + self.reverttorev)
        self.commit()
        self.checkdelta()
        self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))

    def checkdelta(self):
        allowCommit = False
        fixInput = False
        # allowCommit, changes, fixInput , self.alterfiletracks= self.mainContainer.checkFrame(self.mainContainer.workingFrame)
        changes, self.alterfiletracks = self.mainContainer.workingFrame.compareToRefFrame()
        if len(changes) > 0:
            allowCommit = True

        self.commitBttn.setEnabled(allowCommit)
        self.commitmsgEdit.setDisabled(not allowCommit)

        changesarr=[change['fileheader'] for change in changes]
        for fileheader in self.mainContainer.FileHeaders.keys():
            if fileheader in changesarr:
                self.sceneObj[fileheader].setPen(QPen(Qt.red, 3))
            else:
                self.sceneObj[fileheader].setPen(QPen(Qt.black, 1))
        chgstr = ''
        for change in changes:
            chgstr = chgstr + change['fileheader'] + '\t' + change['reason'] + '\n'
        self.frametextBrowser.setText(chgstr)

    def addressAlteredInput(self):
        for alterfiletrack in self.alterfiletracks:
            dialogWindow = alteredinputFileDialog(alterfiletrack)
            alterinputfileinfo = dialogWindow.getInputs()
            if alterinputfileinfo:
                self.mainContainer.workingFrame.dealwithalteredInput(alterinputfileinfo)
        self.readcontainer()
        self.checkdelta()


    def commit(self):
        # print(self.commitmsgEdit.toPlainText() + str())
        error_dialog = QErrorMessage()
        # print()
        if len(self.commitmsgEdit.toPlainText()) <= 7:
            error_dialog.showMessage('You need to put in a commit message longer than 8 characters')
            error_dialog.exec_()
            return
            # return
        if self.userdata['email'] not in self.mainContainer.allowedUser:
            error_dialog.showMessage('You do not have the privilege to commit to this container')
            error_dialog.exec_()
            return

        self.addressAlteredInput()
        self.mainContainer.workingFrame, committed = self.mainContainer.commit(self.mainContainer.workingFrame,self.commitmsgEdit.toPlainText(), self.authtoken, BASE)

        if committed:
            self.curContainer.save()
            self.framelabel.setText(self.curContainer.workingFrame.FrameName)
            self.checkdelta()
            self.commithisttable.setModel(HistoryListModel(self.curContainer.commithistory()))


    def readcontainer(self,path):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.mainContainer = Container.LoadContainerFromYaml(path, revnum=None)
        [self.workingdir, file_name] = os.path.split(path)
        self.mainGuiHandle.startingcheck=True
        self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
        self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))
        self.commithisttable.setColumnWidth(0, self.commithisttable.width()*0.1)
        self.commithisttable.setColumnWidth(1, self.commithisttable.width() * 0.6)
        self.commithisttable.setColumnWidth(2, self.commithisttable.width() * 0.29)
        self.plotcontainer()
        # if self.menuContainer.isEnabled() and self.mainGuiHandle.authtoken:
        #     self.tabWidget.setEnabled(True)
        self.setTab(True)


    def plotcontainer(self):
        scene = QGraphicsScene()
        typeindex = {typeInput: 0, typeOutput: 2, typeRequired: 1}
        typecounter = {typeInput: 0, typeOutput: 0, typeRequired: 0}
        colorscheme = {typeInput: Qt.yellow, typeOutput: Qt.green, typeRequired: Qt.blue}

        for fileheader, fileinfo in self.mainContainer.FileHeaders.items():
            type = fileinfo['type']
            if type == 'references':
                continue
            self.sceneObj[fileheader] = scene.addRect(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type], \
                                                      boxwidth, boxheight, QPen(Qt.black), QBrush(colorscheme[type]))
            text = scene.addText(fileheader)
            text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type])
            if fileheader in self.mainContainer.workingFrame.filestrack.keys():
                text = scene.addText(self.mainContainer.workingFrame.filestrack[fileheader].file_name)
                text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type] + 20)
            else:
                text = scene.addText('Missing')
                text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type] + 20)
            typecounter[type] += 1
        self.frameView.setScene(scene)

    def alterRevertButton(self,histtable):
        rownumber = histtable.row()
        index = histtable.model().index(rownumber, 0)
        self.reverttorev = histtable.model().data(index, 0)
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)