from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.QAbstract.ConflictListModel import ConflictListModel
from Graphics.QAbstract.historycelldelegate import HistoryCellDelegate
from Graphics.Dialogs import alteredinputFileDialog
from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ErrorMessage, removeFileDialog, commitDialog,alteredinputFileDialog, refreshContainerPopUp, downloadProgressBar,commitConflictCheck
from functools import partial
from Graphics.PopUps.selectFileDialog import selectFileDialog

import requests
import os
import hashlib
from Config import BASE,NEWREVISION,FILEADDED,FILEDELETED,NEWCONTAINERFN, TEMPCONTAINERFN,NEWFILEADDED,TEMPFRAMEFN
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.WorldMap import WorldMap
from Graphics.GuiUtil import AddIndexToView
from Graphics.PopUps.AddFileToContainerPopUp import AddFileToContainerPopUp
from os import listdir
from os.path import isfile, join
import json
from SagaGuiModel import sagaguimodel

class MainContainerTab():
    def __init__(self,mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        # self.resetbutton = mainguihandle.resetbutton
        # self.rebasebutton = mainguihandle.rebasebutton
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable
        # self.refreshBttn = mainguihandle.checkChangesBttn
        # self.downloadUpstreamBttn = mainguihandle.updateInputsBttn
        self.refreshContainerBttn = mainguihandle.refreshContainerBttn
        # self.downloadUpstreamBttn.setDisabled(True)
        self.refreshContainerBttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        self.maincontainerview = mainguihandle.maincontainerview
        self.indexView1 = mainguihandle.indexView1
        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.addtocontainerbttn = mainguihandle.addtocontainerbttn
        # self.RequiredButton_2 = mainguihandle.RequiredButton_2
        # self.outputFileButton_2 = mainguihandle.outputFileButton_2
        self.commitmsgEdit_2=mainguihandle.commitmsgEdit_2
        self.selectedFileHeader = mainguihandle.selectedFileHeader
        # self.editFileButton_2 = mainguihandle.editFileButton_2
        # self.removeFileButton_2 = mainguihandle.removeFileButton_2
        # self.testbttn= mainguihandle.testbttn
        self.removefilebttn = mainguihandle.removefilebttn
        # self.fileHistoryBttn = mainguihandle.fileHistoryBttn
        # self.fileHistoryBttn.setDisabled(True)

        self.descriptionText = mainguihandle.commitmsgEdit_2

        self.index=1

        self.mainguihandle =mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        self.maincontainerplot = ContainerPlot(self, self.maincontainerview, container=None)
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir=''
        self.removefilebttn.clicked.connect(self.removeFileInfo)
        self.addtocontainerbttn.clicked.connect(self.addToContainer)
        # self.refreshBttn.clicked.connect(self.checkdelta)
        # self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        self.refreshContainerBttn.clicked.connect(self.updateToLatestRevision)
        # self.testbttn.clicked.connect(self.numeroustest)
        # self.testremovebttn.clicked.connect(self.removenumeroustest)
        # self.resetbutton.clicked.connect(self.resetrequest)
        # self.rebasebutton.clicked.connect(self.rebaserequest)
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        # self.editFileButton_2.setEnabled(False)
        # self.removeFileButton_2.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        self.descriptionText.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.alterRevertButton)
        self.alterfiletracks=[]
        self.curfileheader=None
        self.changes = {}
        self.containerLoaded = False
        self.newContainerStatus = False
        # self.containerstatuslabel = self.mainguihandle.containerStatusLabel
        self.refreshedrevision = 0
        self.refreshedcheck = False
        AddIndexToView(self.indexView1)
        # self.t = threading.Timer(1.0, self.checkingFileDelta)


    def checkLatestRevision(self):
        payload = {'containerID': self.mainContainer.containerId}

        headers = {
            'Authorization': 'Bearer ' + sagaguimodel.authtoken
        }

        response = requests.get(BASE + 'CONTAINERS/newestrevnum', headers=headers, data=payload)
        resp = json.loads(response.content)
        self.newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        self.newestrevnum = resp['newestrevnum']
        self.newestFiles = {}
        if self.mainContainer.revnum < self.newestrevnum:
            self.refreshContainerBttn.setEnabled(True)
            if self.refreshedcheck:
                self.containerstatuslabel.setText(
                    'Newer Revision Exists!' + ' Current Rev: ' + self.refreshrevnum
                    + ', Latest Rev: ' + str(self.newestrevnum))
            else:
                self.containerstatuslabel.setText('Newer Revision Exists!' + ' Current Rev: ' + str(self.mainContainer.revnum)
                                                  + ', Latest Rev: ' + str(self.newestrevnum))
            #if the newest rev num is different from local rev num:
            #loop through filesttrack of both newest frame, check if file exists in current frame and compare MD5s,
            # if exists, add update message to changes, if notadd new file message
            for fileheader in self.newestframe.filestrack.keys():
                if fileheader in self.mainContainer.workingFrame.filestrack.keys():
                    if self.newestframe.filestrack[fileheader].md5 != self.mainContainer.workingFrame.filestrack[fileheader].md5:
                        if fileheader in self.changes.keys():
                            self.changes[fileheader]['reason'].append(NEWREVISION)
                        else:
                            self.changes[fileheader] = {'reason': [NEWREVISION]}
                        #if 'File updated....' is within changes reason dictionary, display delta in GUI
                else:
                    self.changes[fileheader] = {'reason': FILEADDED}

            # Loop through working frame to check if any files have been deleted in new revision
            for fileheader in self.mainContainer.workingFrame.filestrack.keys():
                if fileheader not in self.newestframe.filestrack.keys():
                    if fileheader in self.changes.keys():
                        self.changes[fileheader]['reason'].append(FILEDELETED)
                    else:
                        self.changes[fileheader] = {'reason': [FILEDELETED]}

    def updateToLatestRevision(self):
        self.refreshedcheck = True
        self.refreshContainerBttn.setDisabled(True)
        self.refreshrevnum = str(self.mainContainer.revnum) + '/' + str(self.newestrevnum)
        self.containerstatuslabel.setText('Container Refreshed' + ' Current Rev: ' + self.refreshrevnum + ', Latest Rev: ' + str(self.newestrevnum))
        self.conflictlistmodel = ConflictListModel(self.changes, self.newestframe)
        conflictpopup = refreshContainerPopUp(self.changes, self.conflictlistmodel)
        filestodownload = conflictpopup.selectFiles()
        for fileheader in filestodownload.keys():
            if filestodownload[fileheader] != 'Do not download':
                wf = self.mainContainer.workingFrame
                payload = {'md5': self.newestframe.filestrack[fileheader].md5,
                           'file_name': self.newestframe.filestrack[fileheader].file_name}
                headers = {}
                response = requests.get(BASE + 'FILES', headers=headers, data=payload)
                self.progress = downloadProgressBar(response.headers['file_name'])
                dataDownloaded = 0
                self.progress.updateProgress(dataDownloaded)
                if filestodownload[fileheader] == 'Overwrite':
                    fileEditPath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        wf.filestrack[fileheader].file_name)
                    with open(fileEditPath, 'wb') as f:
                        for data in response.iter_content(1024):
                            dataDownloaded += len(data)
                            f.write(data)
                            percentDone = 100 * dataDownloaded / len(response.content)
                            self.progress.updateProgress(percentDone)
                            QGuiApplication.processEvents()
                    self.mainContainer.workingFrame.filestrack[fileheader].md5 = self.newestframe.filestrack[fileheader].md5
                    self.mainContainer.workingFrame.filestrack[fileheader].lastEdited = os.path.getmtime(fileEditPath)

                elif filestodownload[fileheader] == 'Download Copy':
                    filePath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        wf.filestrack[fileheader].file_name)
                    filecopy_name = os.path.splitext(filePath)[0] + '_' + self.newestframe.FrameName + 'Copy' + \
                                    os.path.splitext(filePath)[1]
                    fileEditPath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        filecopy_name)
                    with open(fileEditPath, 'wb') as f:
                        for data in response.iter_content(1024):
                            dataDownloaded += len(data)
                            f.write(data)
                            percentDone = 100 * dataDownloaded / len(response.content)
                            self.progress.updateProgress(percentDone)
                            QGuiApplication.processEvents()
                    print('No changes to Frame')

                elif filestodownload[fileheader] == 'Download':
                    filePath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        self.newestframe.filestrackk[fileheader].file_name)
                    with open(filePath, 'wb') as f:
                        for data in response.iter_content(1024):
                            dataDownloaded += len(data)
                            f.write(data)
                            percentDone = 100 * dataDownloaded / len(response.content)
                            self.progress.updateProgress(percentDone)
                            QGuiApplication.processEvents()
                    containerfileinfo = {'Container': 'here', 'type': self.newestframe.filestrack[fileheader].style}
                    self.mainContainer.addFileObject(fileheader, containerfileinfo, filePath, self.newestframe.filestrack[fileheader].style, '')

                elif filestodownload[fileheader] == 'Delete':
                    filePath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        wf.filestrack[fileheader].file_name)
                    if os.path.exists(filePath):
                        os.remove(filePath)
                        self.mainContainer.removeFileHeader(fileheader)
                    else:
                        print("The file does not exist")
        # TO DO add to commit function check of conflicting files and spit out error message or have user choose which file to commit

        # pass along list of files different to pop up screen


        # populate new pop up screen with list of files different and option for user to overwrite or download a copy
        # return user selections
        # download files from newest frame
        # loop through changed files to overwrite or write a new copy
        # add functionality to commit to prevent commit if conflict exists
        #
        #     download container
        #           download updated containstate
        #           download updated frame yaml
        #           download updated files
        #     reload contain state into SAGA GUI


    # def fileGanttChart(self):
    #     self.ganttChart = ganttChartFiles()
    #     self.ganttChart.showChart()

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
        self.mainContainer.updatedInputs = True
        self.frametextBrowser.setText(chgstr)
        self.downloadUpstreamBttn.setDisabled(True)
        self.maincontainerplot.plot(self.changes)


    def checkUpstream(self):
        workingFrame = self.mainContainer.workingFrame
        refFrame = Frame.loadRefFramefromYaml(self.mainContainer.refframefullpath,self.mainContainer.workingFrame.containerworkingfolder)
        for fileheader in self.mainContainer.filestomonitor().keys():
            if workingFrame.filestrack[fileheader].connection is not None:
                if str(workingFrame.filestrack[fileheader].connection.connectionType) == 'ConnectionTypes.Input':
                    if workingFrame.filestrack[fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                        #Check to see if input file is internal to container, not referencing other containers
                        containerID = workingFrame.filestrack[fileheader].connection.refContainerId

                        # this is super slow and inefficient.
                        inputContainerPath = os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir')
                        inputContainerPathID = os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerID)
                        dlcontainyaml = Container.downloadContainerInfo(inputContainerPath, sagaguimodel.authtoken, BASE,
                                                                            containerID)
                        dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
                        dlcontainer.downloadbranch('Main', BASE, sagaguimodel.authtoken, inputContainerPathID)
                        framePath = os.path.join(inputContainerPathID,'Main','Rev' + str(dlcontainer.revnum) + '.yaml')
                        inputFrame = Frame.loadRefFramefromYaml(framePath, dlcontainer.containerworkingfolder)
                        # ##Above Chuck of Code should be done in one line or two
                        # dlcontainer.workingFrame

                        ft = workingFrame.filestrack[fileheader]
                        fileCheckPath = os.path.join(workingFrame.containerworkingfolder,ft.ctnrootpath, ft.file_name)
                        fileb = open(fileCheckPath, 'rb')

                        # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                        # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.

                        # workingFrame.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()

                        if refFrame.filestrack[fileheader].md5 != inputFrame.filestrack[fileheader].md5:
                            if fileheader in self.changes.keys():
                                self.changes[fileheader]['reason'].append('MD5 Updated Upstream')
                            else:
                                self.changes[fileheader] = {'reason': ['MD5 Updated Upstream'],
                                                   'revision': inputFrame.FrameName,
                                                    'md5': inputFrame.filestrack[fileheader].md5,
                                                   'inputframe': inputFrame}

        # if len(self.changes.keys())>0:
        #     # self.downloadUpstreamBttn.setEnabled(True)
        # else:
        #     print('No Upstream Updates')


    def checkdelta(self):
        allowCommit = False
        fixInput = False
        self.changes = {}
        # allowCommit, changes, fixInput , self.alterfiletracks= self.mainContainer.checkFrame(self.mainContainer.workingFrame)
        self.changes, self.alterfiletracks = self.mainContainer.workingFrame.compareToRefFrame(self.mainContainer.refframefullpath, self.mainContainer.filestomonitor(), self.changes)
        self.checkUpstream()
        self.checkLatestRevision()
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
            chgstr = chgstr + fileheader + '\t' + ', '.join(change['reason']) + '\n'
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
                                                                    sagaguimodel.authtoken, BASE)
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
            # Check if there are any conflicting files from refresh action with 'RevXCopy' in file name
            if self.refreshedcheck is True:
                filepath = self.mainContainer.workingFrame.containerworkingfolder
                files =  [f for f in listdir(filepath) if isfile(join(filepath, f))]
                searchstring = 'Rev' + str(self.newestrevnum) + 'Copy'
                conflictfiles = [f for f in files if searchstring in f]
                if len(conflictfiles) > 0:
            #         show popup with list of conflict files
                    commitconflictpopup = commitConflictCheck(conflictfiles)
                    commitconflictpopup.showconflicts()
                    return
            committed = self.mainContainer.commit(self.commitmsgEdit.toPlainText(), sagaguimodel.authtoken, BASE)

        if committed:
            self.mainContainer.save()
            self.mainguihandle.refresh()
            self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
            self.checkdelta()
            self.histModel = HistoryListModel(self.mainContainer.commithistory())
            self.commithisttable.setModel(self.histModel)

    def reset(self):
        self.mainContainer=None
        self.containerlabel.setText('')
        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        self.maincontainerplot.reset()

    def readcontainer(self,path):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        loadingcontainer = Container.LoadContainerFromYaml(path, revnum=None)
        # section check

        payload = {'containerid': loadingcontainer.containerId}
        headers = {'Authorization': 'Bearer ' + sagaguimodel.authtoken}
        permissionsresponse = requests.get(BASE + 'USER/checkcontainerpermissions', headers=headers, data=payload)
        print(permissionsresponse.headers['message'])
        permissionsresponsecontent = json.loads(permissionsresponse.content)
        if permissionsresponsecontent['goswitch']:
            ### To Jimmy ####  Below code is copy and based from the Graphics/Popups/switchsection.py
            ### This is another example of where seperating view and model can clean up code.
            # switchsection.py SHOULD be a view, the view should be be calling a
            # method called switchusersection that resides in a model
            # All the py in pop up guis are technically views and there should be another place for model.
            ## I'm not sure what the Model organization should actually look like yet.  It might reside in SagaApp folder
            payload = {'newsectionid': permissionsresponsecontent['sectionid']}
            headers = {'Authorization': 'Bearer ' + sagaguimodel.authtoken}
            switchresponse = requests.post(BASE + 'USER/switchusersection', headers=headers, data=payload)
            resp = json.loads(switchresponse.content)
            report = resp['report']
            msg = QMessageBox()
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText(report['status'])
            if report['status'] == 'User Current Section successfully changed':
                msg.setIcon(QMessageBox.Information)
                self.mainguihandle.resetguionsectionswitch()
            else:
                msg.setIcon(QMessageBox.Critical)
                ## if we arrived here, then that means either
            msg.exec_()
        else: ##if not goswitch then either user is in currentsection, (which is great) or containerid exists nowhere on the server
            if permissionsresponsecontent['sectionid']:
               print('Loading ' + loadingcontainer.containerName)
            else:
                msg = QMessageBox()
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setText(permissionsresponse.headers['message'])
                msg.exec_()
                return
        self.mainContainer = loadingcontainer
        [self.workingdir, file_name] = os.path.split(path)  ## working dir should be app level
        self.containerlabel.setText('Container Name : ' + self.mainContainer.containerName)

        self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
        self.histModel = HistoryListModel(self.mainContainer.commithistory())
        historydelegate = HistoryCellDelegate()
        self.commithisttable.setModel(self.histModel)
        self.commithisttable.setItemDelegate(historydelegate)
        self.maincontainerplot.setContainer(curContainer = self.mainContainer)
        self.maincontainerplot.plot(self.changes)
        ## Grab container history
        changesbyfile=self.mainContainer.commithistorybyfile()
        self.histModel.individualfilehistory(changesbyfile)

        # if self.menuContainer.isEnabled() and sagaguimodel.authtoken:
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

    def FileViewItemRectFeedback(self, type, view, fileheader , curContainer):
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


    def addToContainer(self):
        addfilegui = AddFileToContainerPopUp(mainguihandle=self.mainguihandle,
                                            containerworkdir=self.mainContainer.containerworkingfolder,
                                        maincontainer = self.mainContainer)
        fileInfo = addfilegui.getInputs()
        if fileInfo:
            self.mainContainer.addFileObject(fileInfo=fileInfo)
            self.maincontainerplot.plot(self.changes)

    def removeFileInfo(self):
        # remove fileheader from current main container
        wmap = WorldMap(sagaguimodel.desktopdir)
        candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(curcontainerid=self.mainContainer.containerId, fileheader=self.curfileheader,desktopdir=sagaguimodel.desktopdir, authtoken=sagaguimodel.authtoken)
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

        self.mainContainer = Container.InitiateContainer( inputs['dir'],inputs['containername'])
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

        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        self.framelabel.setText('Revision 0 (New Container)')
        self.newContainerStatus = True
        self.descriptionText.setEnabled(True)
        self.setTab(True)

