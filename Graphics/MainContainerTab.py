from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.Dialogs import alteredinputFileDialog
from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ganttChartFiles, ErrorMessage, removeFileDialog, commitDialog,alteredinputFileDialog
from functools import partial
from Graphics.PopUps.selectFileDialog import selectFileDialog

import requests
import os
import hashlib
from Config import BASE, typeInput,typeOutput,typeRequired, boxwidth, boxheight, colorscheme,TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.WorldMap import WorldMap
from Graphics.GuiUtil import AddIndexToView
from Graphics.PopUps.AddInputPopUp import AddInputPopUp
from os import listdir
import shutil
# import threading
# import time
import random
import string


class MainContainerTab():
    def __init__(self,mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        # self.resetbutton = mainguihandle.resetbutton
        # self.rebasebutton = mainguihandle.rebasebutton
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable
        self.refreshBttn = mainguihandle.checkChangesBttn
        self.refreshBttnUpstream = mainguihandle.checkUpstreamBttn
        self.downloadUpstreamBttn = mainguihandle.updateInputsBttn
        self.refreshContainerBttn = mainguihandle.refreshContainerBttn
        self.downloadUpstreamBttn.setDisabled(True)
        # self.refreshContainerBttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        self.maincontainerview = mainguihandle.maincontainerview
        self.indexView1 = mainguihandle.indexView1
        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.inputFileButton_2 = mainguihandle.inputFileButton_2
        self.RequiredButton_2 = mainguihandle.RequiredButton_2
        self.outputFileButton_2 = mainguihandle.outputFileButton_2
        self.commitmsgEdit_2=mainguihandle.commitmsgEdit_2
        self.selectedFileHeader = mainguihandle.selectedFileHeader
        # self.editFileButton_2 = mainguihandle.editFileButton_2
        self.removeFileButton_2 = mainguihandle.removeFileButton_2
        # self.testbttn= mainguihandle.testbttn
        # self.testremovebttn = mainguihandle.testremovebttn
        self.fileHistoryBttn = mainguihandle.fileHistoryBttn
        self.fileHistoryBttn.setDisabled(True)

        self.descriptionText = mainguihandle.commitmsgEdit_2

        self.index=1

        self.mainguihandle =mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        self.maincontainerplot = None
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir=''
        # self.openContainerBttn.setText('Open Container')
        # self.openContainerBttn.clicked.connect(self.readcontainer)
        # self.fileHistoryBttn.clicked.connect(self.fileGanttChart)
        self.RequiredButton_2.clicked.connect(partial(self.AddToTempContainer, 'Required'))
        self.outputFileButton_2.clicked.connect(partial(self.AddToTempContainer, 'Output'))
        self.removeFileButton_2.clicked.connect(self.removeFileInfo)
        self.inputFileButton_2.clicked.connect(self.AddInputFile)
        self.refreshBttn.clicked.connect(self.checkdelta)
        self.refreshBttnUpstream.clicked.connect(self.checkUpstream)
        self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        self.refreshContainerBttn.clicked.connect(self.refreshContainer)
        # self.testbttn.clicked.connect(self.numeroustest)
        # self.testremovebttn.clicked.connect(self.removenumeroustest)
        # self.resetbutton.clicked.connect(self.resetrequest)
        # self.rebasebutton.clicked.connect(self.rebaserequest)
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        # self.editFileButton_2.setEnabled(False)
        self.removeFileButton_2.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        self.descriptionText.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.alterRevertButton)
        self.alterfiletracks=[]
        self.curfileheader=None
        self.changes = {}
        self.containerLoaded = False
        self.newContainerStatus = False

        AddIndexToView(self.indexView1)
        # self.t = threading.Timer(1.0, self.checkingFileDelta)


    def refreshContainer(self):
    #     redownload ContainerMapWorkDir
        self.mainguihandle.getWorldContainers()
    #   Check to see if newer revision now exists
        revList = listdir(os.path.join(self.mainguihandle.guiworkingdir,
                                       'ContainerMapWorkDir',self.mainContainer.containerId,'Main'))
        if revList.count('temp_frame.yaml') > 0:
            revList.remove('temp_frame.yaml')
        for index, fileName in enumerate(revList):
            length = len(fileName)
            revList[index] = int(fileName[-(length-3):-5])
        # show Jimmy RegularExpression
        revNum = max(revList)
        if self.mainContainer.revnum < revNum:

        #     download container
        #           download updated containstate
        #           download updated frame yaml
        #           download updated files
        #     reload contain state into SAGA GUI
            openDirectoryDialog = QFileDialog().getExistingDirectory(self.mainguihandle,
                                                                     'Select Folder Space to Place ' + self.mainContainer.containerId
                                                                     + ' container folder.')
            if openDirectoryDialog:
                contdir = os.path.join(openDirectoryDialog, self.mainContainer.containerId)
                if not os.path.exists(contdir):
                    os.mkdir(contdir)
                else:
                    print('Container exists already...removing')
                    shutil.rmtree(contdir)
                dlcontainyaml = Container.downloadContainerInfo(openDirectoryDialog, self.mainguihandle.authtoken, BASE,
                                                                self.mainContainer.containerId)
                dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
                dlcontainer.downloadbranch('Main', BASE, self.mainguihandle.authtoken, contdir)
                dlcontainer.workingFrame.downloadfullframefiles()
                self.mainguihandle.maincontainertab.readcontainer(dlcontainyaml)
                self.mainguihandle.tabWidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
                # print(os.path.join(openDirectoryDialog, self.dlcontainer))
                if openDirectoryDialog:
                    print(os.path.split(openDirectoryDialog[0]))

        else:
            print('Container is the lastest revision')

    def fileGanttChart(self):
        self.ganttChart = ganttChartFiles()
        self.ganttChart.showChart()

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
        # fileheaderArr = [fileheader for fileheader,change in self.changes.items()]
        # revArr = [change['revision'] for fileheader,change in self.changes.items()]
        wf = self.mainContainer.workingFrame
        chgstr = ''
        for fileheader, change in self.changes.items():
            self.changes[fileheader]['inputframe'].downloadInputFile(fileheader, self.mainContainer.workingFrame.containerworkingfolder)
            fileEditPath = os.path.join(
                wf.containerworkingfolder,wf.filestrack[fileheader].ctnrootpath,wf.filestrack[fileheader].file_name)
            fileb = open(fileEditPath, 'rb')
            self.mainContainer.workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            # self.mainContainer.workingFrame.filestrack[fileheader].file_id = change['file_id']
            self.mainContainer.workingFrame.filestrack[fileheader].connection.Rev = change['revision']
            chgstr = chgstr + fileheader + '\t' + 'File Updated From Upstream' + '\n'
        wf.writeoutFrameYaml()
        self.changes = self.compareToUpstream(self.mainguihandle.authtoken)
        self.mainContainer.updatedInputs = True
        self.frametextBrowser.setText(chgstr)
        self.downloadUpstreamBttn.setDisabled(True)
        self.maincontainerplot.plot(self.changes)



    def checkUpstream(self):
        workingFrame = self.mainContainer.workingFrame
        self.changes = {}
        for fileheader in self.mainContainer.filestomonitor().keys():
            if workingFrame.filestrack[fileheader].connection is not None:
                if str(workingFrame.filestrack[fileheader].connection.connectionType) == 'ConnectionTypes.Input':
                    if workingFrame.filestrack[fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                        #Check to see if input file is internal to container, not referencing other containers
                        containerID = workingFrame.filestrack[fileheader].connection.refContainerId

                        # this is super slow and inefficient.
                        inputContainerPath = os.path.join(self.mainguihandle.guiworkingdir, 'ContainerMapWorkDir')
                        inputContainerPathID = os.path.join(self.mainguihandle.guiworkingdir, 'ContainerMapWorkDir', containerID)
                        dlcontainyaml = Container.downloadContainerInfo(inputContainerPath, self.mainguihandle.authtoken, BASE,
                                                                            containerID)
                        dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
                        dlcontainer.downloadbranch('Main', BASE, self.mainguihandle.authtoken, inputContainerPathID)
                        framePath = os.path.join(inputContainerPathID,'Main','Rev' + str(dlcontainer.revnum) + '.yaml')
                        inputFrame = Frame.loadRefFramefromYaml(framePath, dlcontainer.containerworkingfolder)
                        # ##Above Chuck of Code should be done in one line or two
                        # dlcontainer.workingFrame

                        ft = workingFrame.filestrack[fileheader]
                        fileCheckPath = os.path.join(workingFrame.containerworkingfolder,ft.ctnrootpath, ft.file_name)
                        fileb = open(fileCheckPath, 'rb')

                        # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                        # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.

                        workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()

                        if workingFrame.filestrack[fileheader].md5 != inputFrame.filestrack[fileheader].md5:
                            self.changes[fileheader] = {'reason': 'MD5 Updated Upstream',
                                                   'revision': inputFrame.FrameName,
                                                    'md5': inputFrame.filestrack[fileheader].md5,
                                                   'inputframe': inputFrame}

        # self.changes = self.compareToUpstream(self.mainguihandle.authtoken)
        if len(self.changes.keys())>0:
            chgstr = ''
            for fileheader, change in self.changes.items():
                chgstr = chgstr + fileheader + '\t' + change['reason'] + '\n'
            self.frametextBrowser.setText(chgstr)
            self.downloadUpstreamBttn.setEnabled(True)
            self.maincontainerplot.plot(self.changes)
        else:
            print('No Upstream Updates')


    def checkdelta(self):
        allowCommit = False
        fixInput = False
        # allowCommit, changes, fixInput , self.alterfiletracks= self.mainContainer.checkFrame(self.mainContainer.workingFrame)
        self.changes, self.alterfiletracks = self.mainContainer.workingFrame.compareToRefFrame(self.mainContainer.refframefullpath, self.mainContainer.filestomonitor())

        # workingFrame.SomeFrameMethod(data (no guihandles.))

        for fileheader, changedetails in self.changes.items():
            if fileheader in self.mainContainer.filestomonitor().keys():
                # only set allowCommit to true if the changes involve what is in the Container's need to monitor
                allowCommit = True
        refContainer = Container.LoadContainerFromYaml(self.mainContainer.yamlpath())

        identical, diff =Container.compare(refContainer,self.mainContainer)
        ## This primarily checks for differences (adding or removing ) filehandles.
        # There could be scenarios that filetracks are difffrerent but the filehandles did not change
        if not identical:
            allowCommit = True
        if self.mainContainer.yamlfn==NEWCONTAINERFN:
            allowCommit = True
            self.commitmsgEdit_2.setDisabled(False)

        self.commitBttn.setEnabled(allowCommit)
        self.commitmsgEdit.setDisabled(not allowCommit)
        # refresh plot
        self.maincontainerplot.plot(self.changes)

        chgstr = ''
        for fileheader, change in self.changes.items():
            chgstr = chgstr + fileheader + '\t' + change['reason'] + '\n'
        self.frametextBrowser.setText(chgstr)

    def addressAlteredInput(self):
        for alterfiletrack in self.alterfiletracks:
            dialogWindow = alteredinputFileDialog(alterfiletrack)
            alterinputfileinfo = dialogWindow.getInputs()
            if alterinputfileinfo:
                self.mainContainer.workingFrame.dealwithalteredInput(alterinputfileinfo, self.mainContainer.refframefullpath)
        self.readcontainer(os.path.join(self.mainContainer.containerworkingfolder ,TEMPCONTAINERFN))
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

        # self.addressAlteredInput()
        if self.newContainerStatus:
            if '' not in [self.descriptionText.toPlainText(),
                          self.commitmsgEdit.toPlainText()]:
                commitCheck = commitDialog(self.mainContainer.containerName, self.descriptionText.toPlainText(),
                                           self.commitmsgEdit.toPlainText())
                committed = commitCheck.commit()
                if committed:
                    containerName = self.mainContainer.containerName
                    commitmessage = self.commitmsgEdit.toPlainText()
                    success = self.mainContainer.CommitNewContainer(containerName, commitmessage,
                                                                    self.mainguihandle.authtoken, BASE)
                    if success:
                        self.newContainerStatus = False
                        containeryaml = os.path.join(self.mainContainer.containerworkingfolder, TEMPCONTAINERFN)
                        self.mainguihandle.maincontainertab.readcontainer(containeryaml)
                        self.mainguihandle.tabWidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
                        self.mainguihandle.refresh()
                        # self.mainguihandle.maptab.updateContainerMap()
                        self.descriptionText.setDisabled(True)
                    else:
                        print('Commit failed')
            else:
                self.errorMessage = ErrorMessage()
                self.errorMessage.showError()
        else:
            if self.mainguihandle.userdata['email'] not in self.mainContainer.allowedUser:
                error_dialog.showMessage('You do not have the privilege to commit to this container')
                error_dialog.exec_()
                return

            committed = self.mainContainer.commit(self.commitmsgEdit.toPlainText(), self.mainguihandle.authtoken, BASE)

        if committed:
            self.mainContainer.save()
            self.mainguihandle.refresh()
            self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
            self.checkdelta()
            self.histModel = HistoryListModel(self.mainContainer.commithistory())
            self.commithisttable.setModel(self.histModel)


    def readcontainer(self,path):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.mainContainerpath = path
        self.mainContainer = Container.LoadContainerFromYaml(path, revnum=None)
        # sel
        [self.workingdir, file_name] = os.path.split(path)
        self.containerlabel.setText('Container Name : ' + self.mainContainer.containerName)

        self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
        self.histModel = HistoryListModel(self.mainContainer.commithistory())
        self.commithisttable.setModel(self.histModel)
        self.commithisttable.setColumnWidth(0, self.commithisttable.width()*0.1)
        self.commithisttable.setColumnWidth(1, self.commithisttable.width() * 0.6)
        self.commithisttable.setColumnWidth(2, self.commithisttable.width() * 0.29)
        self.maincontainerplot=ContainerPlot(self, self.maincontainerview, container=self.mainContainer)
        self.maincontainerplot.plot(self.changes)
        ## Grab container history
        changesbyfile=self.mainContainer.commithistorybyfile()
        self.histModel.individualfilehistory(changesbyfile)

        # if self.menuContainer.isEnabled() and self.mainguihandle.authtoken:
        #     self.tabWidget.setEnabled(True)
        self.setTab(True)
        self.containerLoaded = True
        if self.mainContainer.yamlfn == NEWCONTAINERFN:
            self.commitBttn.setText('Commit New Container')
            self.newContainerStatus = True
        else:
            self.commitBttn.setText('Commit')
            self.newContainerStatus = False
        ## Enable Permission button since Main Container
        self.mainguihandle.setPermissionsEnable()

    def coolerRectangleFeedback(self, type, view, fileheader , curContainer):
        self.curfileheader = fileheader
        self.curfiletype = type
        self.selectedFileHeader.setText(fileheader)
        self.histModel.edithighlight(fileheader,type)
        # self.histModel.dataChanged()
        self.histModel.layoutChanged.emit()

        if fileheader in self.mainContainer.filestomonitor().keys():
            self.removeFileButton_2.setEnabled(True)
        else:
            self.removeFileButton_2.setEnabled(False)
        # print(type)
        # print(fileheader)
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

    def AddToTempContainer(self, fileType: str):
        # self.inputFileButton_2.setEnabled(False)
        fileInfoDialog = selectFileDialog(fileType, self.mainContainer.containerworkingfolder, self.mainguihandle.worldlist)
        fileInfo = fileInfoDialog.getInputs()
        if fileInfo:
            if fileType == 'Required' or fileType == 'Output':
                self.mainContainer.addFileObject(fileInfo['fileheader'], fileInfo['ContainerFileInfo'], fileInfo['FilePath'], fileType,fileInfo['ctnrootpathlist'])
            self.maincontainerplot.plot(self.changes)

    def removeFileInfo(self):
        # remove fileheader from current main container
        wmap = WorldMap()
        candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(curcontainerid=self.mainContainer.containerId, fileheader=self.curfileheader,guiworkingdir=self.mainguihandle.guiworkingdir, authtoken=self.mainguihandle.authtoken)
        fileDialog = removeFileDialog(self.curfileheader, candelete, candeletemesssage) # Dialog to confirm deleting container
        fileheader = fileDialog.removeFile()

        if fileheader:
            self.mainContainer.removeFileHeader(self.curfileheader)
            self.maincontainerplot.plot(self.changes)
            self.removeFileButton_2.setEnabled(False)

    def alterRevertButton(self,histtable):
        rownumber = histtable.row()
        index = histtable.model().index(rownumber, 0)
        self.reverttorev = histtable.model().data(index, 0)
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def initiate(self, inputs):
        os.mkdir(inputs['dir'])
        os.mkdir(os.path.join(inputs['dir'], 'Main'))

        self.mainContainer = Container.InitiateContainer(inputs['containername'], inputs['dir'])
        self.mainContainer.containerName = inputs['containername']
        self.mainContainer.containerworkingfolder = inputs['dir']
        self.mainContainer.save()
        self.containerlabel.setText(inputs['containername'])

        self.workingdir = inputs['dir']

        self.mainContainer.workingFrame = Frame.InitiateFrame(parentcontainerid=self.mainContainer.containerId,
                                                              parentcontainername=self.mainContainer.containerName,
                                                              localdir = inputs['dir'])
        self.mainContainer.workingFrame.parentcontainerid = inputs['containername']
        self.mainContainer.workingFrame.FrameName = 'Rev1'
        self.mainContainer.workingFrame.writeoutFrameYaml(os.path.join(inputs['dir'], 'Main', 'Rev1.yaml'))
        self.maincontainerplot = ContainerPlot(self, self.maincontainerview, self.mainContainer) #Edit to use refContainer
        # self.histModel.beginResetModel()
        # self.histModel.removeRows(0, self.histModel.rowCount(0))
        # self.histModel.endResetModel()
        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        self.framelabel.setText('Revision 0 (New Container)')
        self.newContainerStatus = True
        self.descriptionText.setEnabled(True)
        self.setTab(True)

    def numeroustest(self):
        maxinputadder=2
        counter = 0
        for ifile in range(0,20):
            fileheader = ''.join(random.choices(string.ascii_uppercase +
                                         string.digits, k=7))
            filepath = os.path.join(self.mainContainer.containerworkingfolder, 'Test' + fileheader + '.txt')
            with open(filepath, 'w') as newfile:
                newfile.write(''.join(random.choices(string.ascii_uppercase +string.digits, k=90)))
            fileType = random.choice([typeInput,typeRequired, typeOutput])
            # fileType=typeInput
            if fileType == typeInput and counter<maxinputadder:
                availablecontainers = os.listdir(os.path.join(self.mainguihandle.guiworkingdir, 'ContainerMapWorkDir'))
                print(availablecontainers)

                outputfile = []
                while len(outputfile)==0:
                    # print(random.choice(availablecontainers))
                    containerId = random.choice(availablecontainers)
                    refcontainerpath = os.path.join('ContainerMapWorkDir', containerId, 'containerstate.yaml')
                    refcontainer = Container.LoadContainerFromYaml(refcontainerpath)
                    for fileheader, containerdetails in refcontainer.FileHeaders.items():
                        if containerdetails['type']==typeOutput:
                            outputfile.append(fileheader)
                print(containerId)
                print(outputfile)
                upstreaminfo={'fileheader': random.choice(outputfile), 'type': fileType,
                              'UpstreamContainer': refcontainer}
                upstreamcontainer = upstreaminfo['UpstreamContainer']
                branch = 'Main'
                fullpath, filetrack = upstreamcontainer.workingFrame.downloadInputFile(upstreaminfo['fileheader'],
                                                                                       self.workingdir)
                self.mainContainer.addInputFileObject(fileheader=upstreaminfo['fileheader'],
                                                      reffiletrack=filetrack,
                                                      fullpath=fullpath,
                                                      refContainerId=upstreamcontainer.containerId,
                                                      branch=branch,
                                                      rev='Rev' + str(upstreamcontainer.revnum))
                counter +=1
            if fileType==typeRequired:
                containerFileInfo = {'Container': 'here', 'type': fileType}
                fileInfo = {'fileheader': fileheader, 'FilePath': filepath,
                            'Owner': 'owner', 'Description': 'descrip',
                            'ContainerFileInfo': containerFileInfo}
                self.mainContainer.addFileObject(fileheader, containerFileInfo, fileType)
                self.mainContainer.workingFrame.addFileTotrack(filepath, fileheader, fileType)
            if fileType==typeOutput:
                containerFileInfo = {'Container': [], 'type': fileType}
                fileInfo = {'fileheader': fileheader, 'FilePath': filepath,
                            'Owner': 'owner', 'Description': 'descrip',
                            'ContainerFileInfo': containerFileInfo}
                self.mainContainer.addFileObject(fileheader, containerFileInfo, fileType)
                self.mainContainer.workingFrame.addOutputFileTotrack(fileInfo, fileType)

        self.maincontainerplot.plot(self.changes)

    def removenumeroustest(self):
        for ifile in range(0, 5):
            remheader = random.choice(list(self.mainContainer.filestomonitor().keys()))
            wmap = WorldMap()
            candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(
                curcontainerid=self.mainContainer.containerId, fileheader=remheader,
                guiworkingdir=self.mainguihandle.guiworkingdir, authtoken=self.mainguihandle.authtoken)
            if candelete:
                if remheader in self.mainContainer.workingFrame.filestrack.keys():
                    del self.mainContainer.workingFrame.filestrack[remheader]
                if remheader in self.mainContainer.FileHeaders.keys():
                    del self.mainContainer.FileHeaders[remheader]
                print('delete File' + remheader)
            else:
                print('dont delete File' + remheader)
        self.maincontainerplot.plot({})
        # if fileheader:
        #     if self.curfileheader in self.mainContainer.workingFrame.filestrack.keys():
        #         del self.mainContainer.workingFrame.filestrack[self.curfileheader]
        #     if self.curfileheader in self.mainContainer.FileHeaders.keys():
        #         del self.mainContainer.FileHeaders[self.curfileheader]
        #     self.maincontainerplot.plot(self.changes)
        #     self.removeFileButton_2.setEnabled(False)



