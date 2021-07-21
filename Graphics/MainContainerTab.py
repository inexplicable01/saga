from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.HistoryListModel import HistoryListModel

from Graphics.QAbstract.ContainerFileModel import ContainerFileModel, ContainerFileDelegate
from Graphics.QAbstract.historycelldelegate import HistoryCellDelegate

# from Graphics.Dialogs import alteredinputFileDialog
# from Graphics.ContainerPlot import ContainerPlot

from Graphics.QAbstract.ConflictListModel import ConflictListModel, AddedListModel, DeletedListModel, UpstreamListModel
from Graphics.Dialogs import alteredinputFileDialog
from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ErrorMessage, removeFileDialog, commitDialog, alteredinputFileDialog, \
    refreshContainerPopUp, downloadProgressBar, commitConflictCheck

from functools import partial
from Graphics.PopUps.selectFileDialog import selectFileDialog

import requests
import os
import hashlib
from Config import BASE, NEWREVISION, FILEADDED, FILEDELETED, NEWCONTAINERFN, TEMPCONTAINERFN, \
    NEWFILEADDED, TEMPFRAMEFN, colorscheme, typeOutput, typeInput, typeRequired, UPDATEDUPSTREAM
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
    def __init__(self, mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        # self.resetbutton = mainguihandle.resetbutton
        # self.rebasebutton = mainguihandle.rebasebutton
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable
        # self.refreshBttn = mainguihandle.checkChangesBttn
        # self.downloadUpstreamBttn = mainguihandle.updateInputsBttn
        self.refreshcontainerbttn = mainguihandle.refreshcontainerbttn
        # self.downloadUpstreamBttn.setDisabled(True)
        self.refreshcontainerbttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        self.maincontainerview = mainguihandle.maincontainerview
        # self.indexView1 = mainguihandle.indexView1
        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.addtocontainerbttn = mainguihandle.addtocontainerbttn
        self.containerstatuslabel = mainguihandle.containerstatuslabel
        self.commitmsglbl_2 = mainguihandle.commitmsglbl_2
        # self.outputFileButton_2 = mainguihandle.outputFileButton_2
        self.newcontaineredit = mainguihandle.newcontaineredit
        self.selectedFileHeader = mainguihandle.selectedFileHeader
        # self.editFileButton_2 = mainguihandle.editFileButton_2
        # self.removeFileButton_2 = mainguihandle.removeFileButton_2
        # self.testbttn= mainguihandle.testbttn
        self.removefilebttn = mainguihandle.removefilebttn
        # self.fileHistoryBttn = mainguihandle.fileHistoryBttn
        # self.fileHistoryBttn.setDisabled(True)
        self.containerfiletable = mainguihandle.containerfiletable
        self.containerfiletable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.containerfiletable.clicked.connect(self.containerfileselected)


        self.newcontaineredit = mainguihandle.newcontaineredit

        self.index = 1

        self.mainguihandle = mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        # self.maincontainerplot = ContainerPlot(self, self.maincontainerview, container=None)
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        self.workingdir = ''
        self.removefilebttn.clicked.connect(self.removeFileInfo)
        self.addtocontainerbttn.clicked.connect(self.addToContainer)
        # self.refreshBttn.clicked.connect(self.checkdelta)
        # self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        self.refreshcontainerbttn.clicked.connect(self.updateToLatestRevision)
        # self.testbttn.clicked.connect(self.numeroustest)
        # self.testremovebttn.clicked.connect(self.removenumeroustest)
        # self.resetbutton.clicked.connect(self.resetrequest)
        # self.rebasebutton.clicked.connect(self.rebaserequest)
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        self.removefilebttn.setEnabled(False)
        # self.editFileButton_2.setEnabled(False)
        # self.removeFileButton_2.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        self.newcontaineredit.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.commithistselected)
        self.commithisttable.horizontalHeader().sectionClicked.connect(self.commithistheaderselected)
        self.alterfiletracks = []
        self.curfileheader = None
        self.changes = {}
        self.containerLoaded = False
        # self.newContainerStatus = False
        # self.containerstatuslabel = self.mainguihandle.containerStatusLabel
        self.refreshedrevision = 0
        self.refreshedcheck = False
        self.fileheadertorevertto=None

        # AddIndexToView(self.indexView1)
        # color=

        def setstyleoflabel(color, label):
            alpha = 140
            values = "{r}, {g}, {b}, {a}".format(r=color.red(),
                                                 g=color.green(),
                                                 b=color.blue(),
                                                 a=alpha
                                                 )
            label.setStyleSheet("QLabel { background-color: rgba(" + values + "); }")

        setstyleoflabel(colorscheme[typeInput], self.mainguihandle.inputlbl)
        setstyleoflabel(colorscheme[typeOutput], self.mainguihandle.outputlbl)
        setstyleoflabel(colorscheme[typeRequired], self.mainguihandle.requiredlbl)
        # self.mainguihandle.outputlbl.setStyleSheet("QLabel { background-color : red; color : black; }")
        # self.mainguihandle.requiredlbl.setStyleSheet("QLabel { background-color : red; color : black; }")
        # self.t = threading.Timer(1.0, self.checkingFileDelta)

    # def downloadUpstream(self):
    #     wf = self.mainContainer.workingFrame
    #     chgstr = ''
    #     for fileheader, change in sagaguimodel.changes.items():
    #         if UPDATEDUPSTREAM in change['reason']:
    #
    #             chgstr = chgstr + fileheader + '\t' + 'File Updated From Upstream' + '\n'
    #     wf.writeoutFrameYaml()  ## should we force a commit?
    #     self.mainContainer.updatedInputs = True
    #     self.frametextBrowser.setText(chgstr)



    def updateToLatestRevision(self):
        self.mainContainer.workingFrame.refreshrevnum = str(self.mainContainer.revnum) + '/' + str(sagaguimodel.newestrevnum)
        # need to update above line to add additional / when refreshing multiple container revisions

        self.conflictlistmodel = ConflictListModel(sagaguimodel.changes, sagaguimodel.newestframe)
        self.addedlistmodel = AddedListModel(sagaguimodel.changes, sagaguimodel.newestframe)
        self.deletedlistmodel = DeletedListModel(sagaguimodel.changes, sagaguimodel.newestframe, self.mainContainer.workingFrame)
        self.upstreamlistmodel = UpstreamListModel(sagaguimodel.changes)
        conflictpopup = refreshContainerPopUp(sagaguimodel.changes, self.conflictlistmodel, self.addedlistmodel,
                                              self.deletedlistmodel,  self.upstreamlistmodel)
        filelist = conflictpopup.selectFiles()
        wf = self.mainContainer.workingFrame
        if filelist:
            self.mainContainer.workingFrame.refreshedcheck = True
            for fileheader in filelist.keys():

                if filelist[fileheader] == 'Overwrite':
                    fn = sagaguimodel.downloadFile(sagaguimodel.newestframe.filestrack[fileheader],
                                                   wf.containerworkingfolder)
                    self.mainContainer.workingFrame.filestrack[fileheader].md5 = \
                        sagaguimodel.newestframe.filestrack[fileheader].md5
                    self.mainContainer.workingFrame.filestrack[fileheader].lastEdited = os.path.getmtime(fn)

                elif filelist[fileheader] == 'Download Copy':
                    filename, ext = os.path.splitext(wf.filestrack[fileheader].file_name)
                    filecopy_name = filename + '_' + sagaguimodel.newestframe.FrameName + 'Copy' + \
                                    ext
                    fn = sagaguimodel.downloadFile(sagaguimodel.newestframe.filestrack[fileheader],
                                                   wf.containerworkingfolder, filecopy_name)
                    print('No changes to Frame')
                elif filelist[fileheader] == 'Download':
                    fn = sagaguimodel.downloadFile(sagaguimodel.newestframe.filestrack[fileheader],
                                                   wf.containerworkingfolder)
                    ft = sagaguimodel.newestframe.filestrack[fileheader]
                    # filefullpath = os.path.join(
                    #     self.mainContainer.containerworkingfolder, sagaguimodel.newestframe.filestrack[fileheader].ctnrootpath,
                    #     sagaguimodel.newestframe.filestrack[fileheader].file_name)
                    if ft.connection.connectionType.name in [typeRequired, typeOutput] :
                        self.mainContainer.workingFrame.filestrack[fileheader] = \
                            sagaguimodel.newestframe.filestrack[fileheader]
                    else:
                        raise ('Under Construction')
                    # self.mainContainer.addFileObject(fileinfo=newfileobj)
                elif filelist[fileheader] == 'Delete':
                    filePath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        wf.filestrack[fileheader].file_name)
                    if os.path.exists(filePath):
                        os.remove(filePath)
                        self.mainContainer.removeFileHeader(fileheader)
                    else:
                        print("The file does not exist")
                elif filelist[fileheader] == 'ReplaceInput':
                    upstreamframe = sagaguimodel.changes[fileheader]['inputframe']
                    fileEditPath = sagaguimodel.downloadFile(upstreamframe.filestrack[fileheader],
                                                             wf.containerworkingfolder)
                    fileb = open(fileEditPath, 'rb')
                    upstreammd5 = hashlib.md5(fileb.read()).hexdigest()  ## md5 shouldn't need to be reread
                    if upstreammd5 != upstreamframe.filestrack[fileheader].md5:
                        raise (
                            'Saga Error: upstream md5 and downloaded md5 file does not match')  # sanity check for now
                    wf.filestrack[fileheader].md5 = upstreammd5  ### IS this really necessary?
                    wf.filestrack[fileheader].connection.Rev = sagaguimodel.changes[fileheader]['revision']

            wf.writeoutFrameYaml()
            self.containerstatuslabel.setText(
                'Container Refreshed' + ' Current Rev: ' + self.mainContainer.workingFrame.refreshrevnum + ', Latest Rev: ' + str(
                    sagaguimodel.newestrevnum))
            sagaguimodel.downloadbranch(self.mainContainer.containerworkingfolder, self.mainContainer)
        sagaguimodel.getStatus(self.mainContainer)
        self.containerfiletable.model().update()
        self.containerfiletable.model().updateFromChanges(sagaguimodel.changes)
        #         TO DO add to commit function check of conflicting files and spit out error message or have user choose which file to commit
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

    def setTab(self, tabon):
        self.GuiTab.setEnabled(tabon)

    def revert(self):
        # self.mainContainer.workingFrame.revertTo()
        sagaguimodel.revertTo(self.reverttorev,self.fileheadertorevertto , self.mainContainer.containerworkingfolder)
        self.commitmsgEdit.setText('Revert back to ' + self.reverttorev)
        self.checkdelta()

    def checkdelta(self):
        # allowCommit, changes, fixInput , self.alterfiletracks= self.mainContainer.checkFrame(self.mainContainer.workingFrame)
        statustext,isnewcontainer, allowcommit, needtorefresh, chgstr, changes = sagaguimodel.getStatus(self.mainContainer)
        self.containerstatuslabel.setText(statustext)
        self.commitBttn.setEnabled(allowcommit)
        self.commitmsgEdit.setDisabled(not allowcommit)
        self.newcontaineredit.setDisabled(not isnewcontainer) # if this is a new container, edit should be enabled.
        self.containerfiletable.model().update()
        self.containerfiletable.model().updateFromChanges(sagaguimodel.changes)
        self.refreshcontainerbttn.setEnabled(needtorefresh)
        self.frametextBrowser.setText('')
        for fileheader, change in changes.items():
            chgstr = chgstr + fileheader + '\t' + ', '.join(change['reason']) + '\n'
            text = '<b>'+fileheader + '</b>   :  '
            for reason in change['reason']:
                hexcolor = QColor(colorscheme[reason]).name()
                text = text + '<span style = "color:' + hexcolor + '"> '+reason+'</span>, '
            self.frametextBrowser.append(text)
            # self.frametextBrowser.append( 'Blah blah <b>Bold  </b>')
 # self.frametextBrowser.append(fileheader + '\t' + ', '.join(change['reason']) + '\n')
        # self.frametextBrowser.setText(chgstr)

    def commit(self):
        error_dialog = QErrorMessage()
        if len(self.commitmsgEdit.toPlainText()) <= 7:
            error_dialog.showMessage('You need to put in a commit message longer than 8 characters')
            error_dialog.exec_()
            return
            # return

        # self.addressAlteredInput()
        if sagaguimodel.isNewContainer(self.mainContainer):
            if '' not in [self.newcontaineredit.toPlainText(),
                          self.commitmsgEdit.toPlainText()]:
                commitCheck = commitDialog(self.mainContainer.containerName, self.newcontaineredit.toPlainText(),
                                           self.commitmsgEdit.toPlainText())
                confirmcommit = commitCheck.commit()
                if confirmcommit:
                    containerName = self.mainContainer.containerName
                    commitmessage = self.commitmsgEdit.toPlainText()
                    success = self.mainContainer.CommitNewContainer(containerName, commitmessage,
                                                                    sagaguimodel.authtoken, BASE)
                    if success:
                        # self.newContainerStatus = False
                        containeryaml = os.path.join(self.mainContainer.containerworkingfolder, TEMPCONTAINERFN)
                        self.mainguihandle.maincontainertab.readcontainer(containeryaml)
                        self.mainguihandle.tabWidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
                        self.mainguihandle.refresh()
                        # self.mainguihandle.maptab.updateContainerMap()
                        self.newcontaineredit.setDisabled(True)
                    else:
                        print('Commit failed, need to adjust the gui to show failure')
            else:
                self.errorMessage = ErrorMessage()
                self.errorMessage.showError()
        else:
            if sagaguimodel.userdata['email'] not in self.mainContainer.allowedUser:
                error_dialog.showMessage('You do not have the privilege to commit to this container')
                error_dialog.exec_()
                return
            # Check if there are any conflicting files from refresh action with 'RevXCopy' in file name
            # if self.mainContainer.workingFrame.refreshedcheck is True:  ## this check should always happen.
            filepath = self.mainContainer.workingFrame.containerworkingfolder
            files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
            searchstring = 'Rev' + str(sagaguimodel.newestrevnum) + 'Copy'
            conflictfiles = [f for f in files if searchstring in f]
            if len(conflictfiles) > 0:
                #         show popup with list of conflict files
                commitconflictpopup = commitConflictCheck(conflictfiles)
                commitconflictpopup.showconflicts()
                return
            committed = self.mainContainer.commit(self.commitmsgEdit.toPlainText(), sagaguimodel.authtoken, BASE)

        if committed:
            self.commitBttn.setDisabled(True)
            self.mainContainer.save()
            self.mainguihandle.refresh()
            self.framelabel.setText(self.mainContainer.workingFrame.FrameName)
            self.checkdelta()
            self.histModel = HistoryListModel(self.mainContainer.commithistory())
            self.commithisttable.setModel(self.histModel)

    def reset(self):
        self.mainContainer = None
        self.containerlabel.setText('')
        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        # self.maincontainerplot.reset()

    def readcontainer(self, path):
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
        else:  ##if not goswitch then either user is in currentsection, (which is great) or containerid exists nowhere on the server
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
        # self.maincontainerplot.setContainer(curContainer = self.mainContainer)
        # self.maincontainerplot.plot(sagaguimodel.changes)

        self.containerfiletable.setModel(ContainerFileModel(self.mainContainer))
        self.containerfiletable.setItemDelegate(ContainerFileDelegate())
        sagaguimodel.getStatus(self.mainContainer)
        self.containerfiletable.model().update()
        self.containerfiletable.model().updateFromChanges(sagaguimodel.changes)

        ## Grab container history
        changesbyfile = self.mainContainer.commithistorybyfile()
        self.histModel.individualfilehistory(changesbyfile)

        # if self.menuContainer.isEnabled() and sagaguimodel.authtoken:
        #     self.tabWidget.setEnabled(True)
        self.setTab(True)
        self.containerLoaded = True
        if self.mainContainer.yamlfn == NEWCONTAINERFN:
            self.commitBttn.setText('Commit New Container')
        else:
            self.commitBttn.setText('Commit')
        ## Enable Permission button since Main Container
        self.mainguihandle.setPermissionsEnable()
        self.checkdelta()

    def FileViewItemRectFeedback(self, type, view, fileheader, curContainer):
        self.curfileheader = fileheader
        self.curfiletype = type
        self.selectedFileHeader.setText(fileheader)
        self.histModel.edithighlight(fileheader, type)
        # self.histModel.dataChanged()
        self.histModel.layoutChanged.emit()

        if fileheader in self.mainContainer.filestomonitor().keys():
            self.removeFileButton_2.setEnabled(True)
        else:
            self.removeFileButton_2.setEnabled(False)

    def addToContainer(self):
        addfilegui = AddFileToContainerPopUp(mainguihandle=self.mainguihandle,
                                             containerworkdir=self.mainContainer.containerworkingfolder,
                                             maincontainer=self.mainContainer)
        fileinfo = addfilegui.getInputs()
        if fileinfo:
            self.mainContainer.addFileObject(fileinfo=fileinfo)
            sagaguimodel.getStatus(self.mainContainer)
            self.containerfiletable.model().update()
            self.containerfiletable.model().updateFromChanges(sagaguimodel.changes)


    def removeFileInfo(self):
        # remove fileheader from current main container
        wmap = WorldMap(sagaguimodel.desktopdir)
        candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(curcontainerid=self.mainContainer.containerId,
                                                                          fileheader=self.curfileheader,
                                                                          desktopdir=sagaguimodel.desktopdir,
                                                                          authtoken=sagaguimodel.authtoken)
        fileDialog = removeFileDialog(self.curfileheader, candelete,
                                      candeletemesssage)  # Dialog to confirm deleting container
        remove = fileDialog.removeFile()

        if remove:
            self.mainContainer.removeFileHeader(self.curfileheader)
            sagaguimodel.getStatus(self.mainContainer)
            self.containerfiletable.model().update()
            self.containerfiletable.model().updateFromChanges(sagaguimodel.changes)

            self.removefilebttn.setEnabled(False)

    def containerfileselected(self, containerfileindex):
        r = containerfileindex.row()
        fileheader = containerfileindex.model().containerfiles[r]['fileheader']
        if fileheader in self.mainContainer.FileHeaders.keys():
            self.curfileheader=fileheader
            self.removefilebttn.setText('Remove : ' + self.curfileheader)
            self.removefilebttn.setEnabled(True)
        else:
            self.curfileheader='Selected File Not Part of your Project'
            self.removefilebttn.setText('Remove :')
            self.removefilebttn.setEnabled(False)


    def commithistselected(self, histableindex):
        self.reverttorev = histableindex.model().revheaders[histableindex.column()]
        self.fileheadertorevertto = histableindex.model().fileheaderlist[histableindex.row()]
        self.commitmsglbl_2.setText('Commit Message : '+histableindex.model().commitmsg[histableindex.column()])
        self.revertbttn.setText('Revert FileHeader ' + self.fileheadertorevertto + '  to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def commithistheaderselected(self, column):
        self.reverttorev = self.commithisttable.model().revheaders[column]
        self.fileheadertorevertto = None
        self.commitmsglbl_2.setText('Commit Message : '+self.commithisttable.model().commitmsg[column])
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def initiate(self, inputs):
        os.mkdir(inputs['dir'])
        os.mkdir(os.path.join(inputs['dir'], 'Main'))

        self.mainContainer = Container.InitiateContainer(inputs['dir'], inputs['containername'])
        self.mainContainer.containerName = inputs['containername']
        self.mainContainer.containerworkingfolder = inputs['dir']
        self.mainContainer.save()
        self.containerlabel.setText(inputs['containername'])

        self.workingdir = inputs['dir']

        self.mainContainer.workingFrame = Frame.InitiateFrame(parentcontainerid=self.mainContainer.containerId,
                                                              parentcontainername=self.mainContainer.containerName,
                                                              localdir=inputs['dir'])
        self.mainContainer.workingFrame.parentcontainerid = inputs['containername']
        self.mainContainer.workingFrame.FrameName = 'Rev1'
        self.mainContainer.workingFrame.writeoutFrameYaml(os.path.join(inputs['dir'], 'Main', 'Rev1.yaml'))
        # self.maincontainerplot = ContainerPlot(self, self.maincontainerview, self.mainContainer) #Edit to use refContainer
        self.containerfiletable.setModel(ContainerFileModel(self.mainContainer))
        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        self.framelabel.setText('Revision 0 (New Container)')
        # self.newContainerStatus = True
        self.newcontaineredit.setEnabled(True)
        self.setTab(True)

