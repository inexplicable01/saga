from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.Dialogs import alteredinputFileDialog
import requests
import os
import hashlib
from Config import BASE
from Config import typeInput,typeOutput,typeRequired, boxwidth, boxheight
from Frame.FrameStruct import Frame
from Frame.Container import Container

class MainContainerTab():
    def __init__(self,mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        self.resetbutton = mainguihandle.resetbutton
        self.rebasebutton = mainguihandle.rebasebutton
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable
        self.refreshBttn = mainguihandle.refreshBttn
        self.refreshBttnUpstream = mainguihandle.refreshBttn_2
        self.downloadUpstreamBttn = mainguihandle.refreshBttn_3
        self.downloadUpstreamBttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        self.frameView = mainguihandle.frameView
        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.index=1

        self.mainguihandle =mainguihandle

        self.GuiTab = mainguihandle.ContainerTab
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir=''
        # self.openContainerBttn.setText('Open Container')
        # self.openContainerBttn.clicked.connect(self.readcontainer)
        self.refreshBttn.clicked.connect(self.checkdelta)
        self.refreshBttnUpstream.clicked.connect(self.checkUpstream)
        self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
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
        # self.commit()
        self.checkdelta()
        # self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))

    def downloadUpstream(self):
        fileheaderArr = [change['fileheader'] for change in self.changes]
        revArr = [change['revision'] for change in self.changes]
        chgstr = ''
        for count, fileheader in enumerate(fileheaderArr):
            self.mainContainer.workingFrame.downloadInputFile(fileheader, self.mainContainer.workingFrame.localfilepath)
            fileEditPath = os.path.join(
                self.mainContainer.workingFrame.localfilepath + '/' + self.mainContainer.workingFrame.filestrack[fileheader].file_name)
            fileb = open(fileEditPath, 'rb')
            self.mainContainer.workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            self.mainContainer.workingFrame.filestrack[fileheader].connection.Rev = revArr[count]
            self.sceneObj[fileheader].setPen(QPen(Qt.black, 1))
            chgstr = chgstr + fileheader + '\t' + 'File Updated From Upstream' + '\n'
        self.frametextBrowser.setText(chgstr)
        self.downloadUpstreamBttn.setDisabled(True)


    def checkUpstream(self):
        self.changes = self.compareToUpstream(self.mainguihandle.authtoken)
        if self.changes:
            changesarr = [change['fileheader'] for change in self.changes]
            for fileheader in self.mainContainer.FileHeaders.keys():
                if fileheader in changesarr:
                    self.sceneObj[fileheader].setPen(QPen(Qt.red, 3))
                else:
                    self.sceneObj[fileheader].setPen(QPen(Qt.black, 1))
            chgstr = ''
            for change in self.changes:
                chgstr = chgstr + change['fileheader'] + '\t' + change['reason'] + '\n'
            self.frametextBrowser.setText(chgstr)
            self.downloadUpstreamBttn.setEnabled(True)
        else:
            print('No Upstream Updates')

    def compareToUpstream(self, authToken):
        workingFrame = self.mainContainer.workingFrame
        refframe = Frame(workingFrame.refframefn, workingFrame.filestomonitor, workingFrame.localfilepath)
        changes = []
        for fileheader in workingFrame.filestomonitor.keys():
            if workingFrame.filestrack[fileheader].connection is not None:
                if str(workingFrame.filestrack[fileheader].connection.connectionType) == 'ConnectionTypes.Input':
                    if workingFrame.filestrack[fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                        containerID = workingFrame.filestrack[fileheader].connection.refContainerId
                        if not os.path.exists(workingFrame.localfilepath + '/inputContainers/'):
                            os.mkdir(workingFrame.localfilepath + '/inputContainers/')
                        inputContainerPath = workingFrame.localfilepath + '/inputContainers/' + containerID
                        dlcontainyaml = Container.downloadContainerInfo(inputContainerPath, authToken, BASE,
                                                                        containerID)
                        print(dlcontainyaml)
                        dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
                        dlcontainer.downloadbranch('Main', BASE, authToken, inputContainerPath)
                        framePath = os.path.join(inputContainerPath + '/Main/' + 'Rev' + str(dlcontainer.revnum) + '.yaml')
                        inputFrame = Frame(framePath)
                        fileCheckPath = os.path.join(workingFrame.localfilepath + '/' + workingFrame.filestrack[fileheader].file_name)
                        fileb = open(fileCheckPath, 'rb')
                        workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
                        # calculate md5 of file, if md5 has changed, update md5
                        if workingFrame.filestrack[fileheader].md5 != inputFrame.filestrack[fileheader].md5:
                            changes.append({'fileheader': fileheader, 'reason': 'MD5 Updated Upstream', 'revision': inputFrame.filestrack[fileheader].connection.Rev})
        return changes

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
        if self.mainguihandle.userdata['email'] not in self.mainContainer.allowedUser:
            error_dialog.showMessage('You do not have the privilege to commit to this container')
            error_dialog.exec_()
            return

        # self.addressAlteredInput()
        self.mainContainer.workingFrame, committed = self.mainContainer.commit(self.commitmsgEdit.toPlainText(), self.mainguihandle.authtoken, BASE)

        if committed:
            self.mainContainer.save()
            self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
            self.checkdelta()
            self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))


    def readcontainer(self,path):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.mainContainer = Container.LoadContainerFromYaml(path, revnum=None)
        [self.workingdir, file_name] = os.path.split(path)
        self.containerlabel.setText('Container Name : ' + self.mainContainer.containerName)
        self.mainguihandle.startingcheck=True
        self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
        self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))
        self.commithisttable.setColumnWidth(0, self.commithisttable.width()*0.1)
        self.commithisttable.setColumnWidth(1, self.commithisttable.width() * 0.6)
        self.commithisttable.setColumnWidth(2, self.commithisttable.width() * 0.29)
        self.plotcontainer()
        # if self.menuContainer.isEnabled() and self.mainguihandle.authtoken:
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