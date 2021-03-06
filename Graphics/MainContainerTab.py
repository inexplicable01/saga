from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.Dialogs import alteredinputFileDialog
from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ErrorMessage, inputFileDialog, removeFileDialog, selectFileDialog, commitDialog,alteredinputFileDialog
from functools import partial
import requests
import os
import hashlib
from Config import BASE, typeInput,typeOutput,typeRequired, boxwidth, boxheight, colorscheme
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.WorldMap import WorldMap
from Graphics.GuiUtil import AddIndexToView
from Graphics.PopUps.AddInputPopUp import AddInputPopUp

class MainContainerTab():
    def __init__(self,mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        # self.resetbutton = mainguihandle.resetbutton
        # self.rebasebutton = mainguihandle.rebasebutton
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable
        self.refreshBttn = mainguihandle.refreshBttn
        self.refreshBttnUpstream = mainguihandle.refreshBttn_2
        self.downloadUpstreamBttn = mainguihandle.refreshBttn_3
        self.downloadUpstreamBttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        self.maincontainerview = mainguihandle.maincontainerview
        self.indexView1 = mainguihandle.indexView1
        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.inputFileButton_2 = mainguihandle.inputFileButton_2
        self.RequiredButton_2 = mainguihandle.RequiredButton_2
        self.outputFileButton_2 = mainguihandle.outputFileButton_2
        self.selectedfileheader = mainguihandle.selectedfileheader
        self.editFileButton_2 = mainguihandle.editFileButton_2
        self.removeFileButton_2 = mainguihandle.removeFileButton_2

        self.index=1

        self.mainguihandle =mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        self.maincontainerplot = None
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir=''
        # self.openContainerBttn.setText('Open Container')
        # self.openContainerBttn.clicked.connect(self.readcontainer)
        self.RequiredButton_2.clicked.connect(partial(self.AddToTempContainer, 'Required'))
        self.outputFileButton_2.clicked.connect(partial(self.AddToTempContainer, 'Output'))
        self.removeFileButton_2.clicked.connect(self.removeFileInfo)
        self.inputFileButton_2.clicked.connect(self.AddInputFile)
        self.refreshBttn.clicked.connect(self.checkdelta)
        self.refreshBttnUpstream.clicked.connect(self.checkUpstream)
        self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        # self.resetbutton.clicked.connect(self.resetrequest)
        # self.rebasebutton.clicked.connect(self.rebaserequest)
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        self.editFileButton_2.setEnabled(False)
        self.removeFileButton_2.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.alterRevertButton)
        self.alterfiletracks=[]
        self.curfileheader=None
        self.changes = {}

        AddIndexToView(self.indexView1)


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
            self.changes[count]['inputframe'].downloadInputFile(fileheader, self.mainContainer.workingFrame.localfilepath)
            fileEditPath = os.path.join(
                self.mainContainer.workingFrame.localfilepath + '/' + self.mainContainer.workingFrame.filestrack[fileheader].file_name)
            fileb = open(fileEditPath, 'rb')
            self.mainContainer.workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            self.mainContainer.workingFrame.filestrack[fileheader].connection.Rev = revArr[count]
            self.sceneObj[fileheader].setPen(QPen(Qt.black, 1))
            chgstr = chgstr + fileheader + '\t' + 'File Updated From Upstream' + '\n'
        self.frametextBrowser.setText(chgstr)
        self.downloadUpstreamBttn.setDisabled(True)

    def AddInputFile(self):
        addinputwindow = AddInputPopUp(mainguihandle=self.mainguihandle)
        upstreaminfo = addinputwindow.getInputs()
        if upstreaminfo:
            upstreamcontainer = upstreaminfo['UpstreamContainer']
            branch='Main'
            fullpath, filetrack = upstreamcontainer.workingFrame.downloadInputFile(upstreaminfo['fileheader'],self.workingdir)
            self.mainContainer.addInputFileObject(fileheader=upstreaminfo['fileheader'],
                                                  reffiletrack = filetrack,
                                                  fullpath=fullpath,
                                                  refContainerId=upstreamcontainer.containerId,
                                                  branch=branch,
                                                  rev='Rev' + str(upstreamcontainer.revnum))
            self.maincontainerplot.plot(self.changes)

    def checkUpstream(self):
        self.changes = self.compareToUpstream(self.mainguihandle.authtoken)
        if len(self.changes.keys())>0:
            # changesarr = [change['fileheader'] for change in self.changes]
            # for fileheader in self.mainContainer.FileHeaders.keys():
            #     if fileheader in changesarr:
            #         self.maincontainerplot.RectBox[fileheader].setBrush(QBrush(Qt.red))
            #     else:
            #         self.maincontainerplot.RectBox[fileheader].setBrush(QBrush(Qt.white))
            chgstr = ''
            for change in self.changes.keys():
                chgstr = chgstr + change['fileheader'] + '\t' + change['reason'] + '\n'
            self.frametextBrowser.setText(chgstr)
            self.downloadUpstreamBttn.setEnabled(True)
        else:
            print('No Upstream Updates')

    def compareToUpstream(self, authToken):
        workingFrame = self.mainContainer.workingFrame
        refframe = Frame(workingFrame.refframefn, None, workingFrame.localfilepath)
        changes = {}
        # changes = []
        # for fileheader in self.mainContainer.filestomonitor().keys():
        #     if workingFrame.filestrack[fileheader].connection is not None:
        #         if str(workingFrame.filestrack[fileheader].connection.connectionType) == 'ConnectionTypes.Input':
        #             if workingFrame.filestrack[fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
        #                 containerID = workingFrame.filestrack[fileheader].connection.refContainerId
        #                 if not os.path.exists(workingFrame.localfilepath + '/inputContainers/'):
        #                     os.mkdir(workingFrame.localfilepath + '/inputContainers/')
        #                 inputContainerPath = workingFrame.localfilepath + '/inputContainers/' + containerID
        #                 dlcontainyaml = Container.downloadContainerInfo(inputContainerPath, authToken, BASE,
        #                                                                 containerID)
        #                 print(dlcontainyaml)
        #                 dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
        #                 dlcontainer.downloadbranch('Main', BASE, authToken, inputContainerPath)
        #                 framePath = os.path.join(inputContainerPath + '/Main/' + 'Rev' + str(dlcontainer.revnum) + '.yaml')
        #                 inputFrame = Frame(framePath)
        #                 fileCheckPath = os.path.join(workingFrame.localfilepath + '/' + workingFrame.filestrack[fileheader].file_name)
        #                 fileb = open(fileCheckPath, 'rb')
        #                 workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
        #                 # calculate md5 of file, if md5 has changed, update md5
        #                 if workingFrame.filestrack[fileheader].md5 != inputFrame.filestrack[fileheader].md5:
        #                     changes.append({'fileheader': fileheader, 'reason': 'MD5 Updated Upstream', 'revision': inputFrame.filestrack[fileheader].connection.Rev, 'inputframe': inputFrame})
        return changes

    def checkdelta(self):
        allowCommit = False
        fixInput = False
        # allowCommit, changes, fixInput , self.alterfiletracks= self.mainContainer.checkFrame(self.mainContainer.workingFrame)
        self.changes, self.alterfiletracks = self.mainContainer.workingFrame.compareToRefFrame(self.mainContainer.filestomonitor())
        if len(self.changes) > 0:
            allowCommit = True

        self.commitBttn.setEnabled(allowCommit)
        self.commitmsgEdit.setDisabled(not allowCommit)
        # refresh plot
        self.maincontainerplot.plot(self.changes)

        # for fileheader in self.mainContainer.FileHeaders.keys():
        #     if fileheader in changes.keys():
        #         color = colorscheme[changes[fileheader]['reason']]
        #         self.maincontainerplot.RectBox[fileheader].setPen(QPen(color, 3))

        chgstr = ''
        for fileheader, change in self.changes.items():
            chgstr = chgstr + fileheader + '\t' + change['reason'] + '\n'
        self.frametextBrowser.setText(chgstr)

    def addressAlteredInput(self):
        for alterfiletrack in self.alterfiletracks:
            dialogWindow = alteredinputFileDialog(alterfiletrack)
            alterinputfileinfo = dialogWindow.getInputs()
            if alterinputfileinfo:
                self.mainContainer.workingFrame.dealwithalteredInput(alterinputfileinfo)
        self.readcontainer(os.path.join(self.mainContainer.workingFrame.localfilepath + '/containerstate.yaml'))
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
            self.mainguihandle.maptab.updateContainerMap()
            self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
            self.checkdelta()
            self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))


    def readcontainer(self,path):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.mainContainer = Container.LoadContainerFromYaml(path, revnum=None)
        [self.workingdir, file_name] = os.path.split(path)
        self.containerlabel.setText('Container Name : ' + self.mainContainer.containerName)

        self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
        self.commithisttable.setModel(HistoryListModel(self.mainContainer.commithistory()))
        self.commithisttable.setColumnWidth(0, self.commithisttable.width()*0.1)
        self.commithisttable.setColumnWidth(1, self.commithisttable.width() * 0.6)
        self.commithisttable.setColumnWidth(2, self.commithisttable.width() * 0.29)
        self.maincontainerplot=ContainerPlot(self, self.maincontainerview, container=self.mainContainer)
        self.maincontainerplot.plot(self.changes)
        # if self.menuContainer.isEnabled() and self.mainguihandle.authtoken:
        #     self.tabWidget.setEnabled(True)
        self.setTab(True)

    def coolerRectangleFeedback(self, type, view, fileheader , curContainer):
        self.curfileheader = fileheader
        self.curfiletype = type
        self.selectedfileheader.setText(fileheader)

        if fileheader in self.mainContainer.filestomonitor():
            self.removeFileButton_2.setEnabled(True)
        else:
            self.removeFileButton_2.setEnabled(False)
        print(type)
        print(fileheader)

    def AddToTempContainer(self, fileType: str):
        # self.inputFileButton_2.setEnabled(False)
        fileInfoDialog = selectFileDialog(fileType, self.mainContainer.containerworkingfolder, self.mainguihandle.worldlist)
        fileInfo = fileInfoDialog.getInputs()
        if fileInfo:
            self.mainContainer.addFileObject(fileInfo['fileheader'], fileInfo['ContainerFileInfo'], fileType)
            if fileType =='Required':
                self.mainContainer.workingFrame.addFileTotrack(fileInfo['FilePath'], fileInfo['fileheader'], fileType)
            if fileType=='Output':
                self.mainContainer.workingFrame.addOutputFileTotrack(fileInfo, fileType)
            self.maincontainerplot.plot(self.changes)

    def removeFileInfo(self):
        # remove fileheader from current main container
        wmap = WorldMap()
        candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(curcontainerid=self.mainContainer.containerId, fileheader=self.curfileheader,guiworkingdir=self.mainguihandle.guiworkingdir)
        fileDialog = removeFileDialog(self.curfileheader, candelete, candeletemesssage) # Dialog to confirm deleting container
        fileheader = fileDialog.removeFile()

        if fileheader:
            if self.curfileheader in self.mainContainer.workingFrame.filestrack.keys():
                del self.mainContainer.workingFrame.filestrack[self.curfileheader]
            if self.curfileheader in self.mainContainer.FileHeaders.keys():
                del self.mainContainer.FileHeaders[self.curfileheader]
            self.maincontainerplot.plot(self.changes)
            self.removeFileButton_2.setEnabled(False)

    def alterRevertButton(self,histtable):
        rownumber = histtable.row()
        index = histtable.model().index(rownumber, 0)
        self.reverttorev = histtable.model().data(index, 0)
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)