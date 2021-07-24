from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.GuiUtil import setstyleoflabel
from Graphics.QAbstract.HistoryListModel import HistoryListModel

from Graphics.QAbstract.ContainerFileModel import ContainerFileModel, ContainerFileDelegate
from Graphics.QAbstract.historycelldelegate import HistoryCellDelegate

# from Graphics.Dialogs import alteredinputFileDialog
# from Graphics.ContainerPlot import ContainerPlot


from Graphics.Dialogs import alteredinputFileDialog
from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ErrorMessage, removeFileDialog, commitDialog, alteredinputFileDialog, \
    refreshContainerPopUp, downloadProgressBar, commitConflictCheck

from functools import partial
from Graphics.PopUps.selectFileDialog import selectFileDialog

import requests
import os
from Config import BASE, SERVERNEWREVISION, SERVERFILEADDED, SERVERFILEDELETED, NEWCONTAINERFN, TEMPCONTAINERFN, \
    LOCALFILEHEADERADDED, TEMPFRAMEFN, colorscheme, typeOutput, typeInput, typeRequired, UPDATEDUPSTREAM
from SagaApp.WorldMap import WorldMap
from Graphics.GuiUtil import AddIndexToView
from Graphics.PopUps.AddFileToContainerPopUp import AddFileToContainerPopUp
from SagaGuiModel import sagaguimodel
from datetime import datetime


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
        self.commitmsgboxlbl = mainguihandle.commitmsgboxlbl
        self.containerdescriplbl = mainguihandle.containerdescriplbl
        self.container_subtab = mainguihandle.container_subtab

        self.container_subtab.setElideMode(Qt.ElideNone)


        self.newcontaineredit = mainguihandle.newcontaineredit

        self.index = 1

        self.mainguihandle = mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        # self.maincontainerplot = ContainerPlot(self, self.maincontainerview, container=None)
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        # self.workingdir = ''
        self.removefilebttn.clicked.connect(self.removeFileInfo)
        self.addtocontainerbttn.clicked.connect(self.addToContainer)
        # self.refreshBttn.clicked.connect(self.checkdelta)
        # self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        self.refreshcontainerbttn.clicked.connect(self.updateToLatestRevision)

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
        self.commitmsgEdit.textChanged.connect(self.commitmsgeditchange)

        setstyleoflabel(colorscheme[typeInput], self.mainguihandle.inputlbl)
        setstyleoflabel(colorscheme[typeOutput], self.mainguihandle.outputlbl)
        setstyleoflabel(colorscheme[typeRequired], self.mainguihandle.requiredlbl)


    def updateToLatestRevision(self):
        refreshrevnum = str(sagaguimodel.maincontainer.revnum) + '/' + str(sagaguimodel.newestrevnum)
        # need to update above line to add additional / when refreshing multiple container revisions

        conflictlistmodel, addedlistmodel, deletedlistmodel, upstreamlistmodel, changes = sagaguimodel.getRefreshPopUpModels()
        conflictpopup = refreshContainerPopUp(changes, conflictlistmodel, addedlistmodel,
                                              deletedlistmodel,  upstreamlistmodel)
        filelist = conflictpopup.selectFiles()
        sagaguimodel.dealWithUserSelection(filelist)

        if sagaguimodel.sagasync.iscontainerinsync():
            sagaguimodel.downloadbranch()
            self.containerstatuslabel.setText(
                'Container Refreshed!  This Container now is at a Rev ' + refreshrevnum + '+ state')
        sagaguimodel.getStatus()
        self.containerfiletable.model().update()
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
        sagaguimodel.revertTo(self.reverttorev,self.fileheadertorevertto)
        self.commitmsgEdit.setText('Revert back to ' + self.reverttorev)
        self.checkdelta()

    def checkdelta(self):
        print('Checking' + datetime.now().isoformat())
        # allowCommit, changes, fixInput , self.alterfiletracks= sagaguimodel.maincontainer.checkFrame(sagaguimodel.maincontainer.workingFrame)
        if sagaguimodel.maincontainer is None:
            return

        statustext, allowcommit, needtorefresh,  changes = sagaguimodel.getStatus()
        self.containerstatuslabel.setText(statustext)
        self.commitBttn.setEnabled(allowcommit)
        self.commitmsgEdit.setDisabled(not allowcommit)
        self.newcontaineredit.setDisabled(not sagaguimodel.isNewContainer()) # if this is a new container, edit should be enabled.
        self.containerfiletable.model().update()
        self.refreshcontainerbttn.setEnabled(needtorefresh)
        self.frametextBrowser.setText('')
        for fileheader, change in changes.items():
            # chgstr = chgstr + fileheader + '\t' + ', '.join(change['reason']) + '\n'
            text = '<b>'+fileheader + '</b>   :  '
            for reason in change['reason']:
                hexcolor = QColor(colorscheme[reason]).name()
                text = text + '<span style = "color:' + hexcolor + '"> '+reason+'</span>, '
            self.frametextBrowser.append(text)
        print('Check Done ' + datetime.now().isoformat())

    def commitmsgeditchange(self):
        if len(self.commitmsgEdit.toPlainText()) <= 7:
            self.commitBttn.setEnabled(False)
            self.commitmsgboxlbl.setText('Commit Message : Needs to be longer than 7 characters')
        else:
            if sagaguimodel.isNewContainer():
                if len(self.newcontaineredit.toPlainText()) <= 7:
                    self.commitBttn.setEnabled(False)
                    self.containerdescriplbl.setText('New Container Descrption Needs to be longer than  7 characters')
                else:
                    self.commitBttn.setEnabled(True)
                    self.commitmsgboxlbl.setText('Commit Message :')
            else:
                self.commitBttn.setEnabled(True)
                self.commitmsgboxlbl.setText('Commit Message :')


    def commit(self):
        error_dialog = QErrorMessage()

        if sagaguimodel.isNewContainer():
            ## opportunity to show way more information for Commit Dialog
            commitCheck = commitDialog(sagaguimodel.maincontainer.containerName, self.newcontaineredit.toPlainText(),
                                       self.commitmsgEdit.toPlainText())
            confirmcommit = commitCheck.commit()
            if confirmcommit:
                success = sagaguimodel.commitNewContainer(commitmessage = self.commitmsgEdit.toPlainText())
                if success:
                    # self.newContainerStatus = False
                    containeryaml = os.path.join(sagaguimodel.maincontainer.containerworkingfolder, TEMPCONTAINERFN)
                    self.mainguihandle.maincontainertab.readcontainer(containeryaml)
                    self.mainguihandle.tabWidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
                    self.mainguihandle.refresh()
                    # self.mainguihandle.maptab.updateContainerMap()
                    self.newcontaineredit.setDisabled(True)
                else:
                    print('Commit failed, need to adjust the gui to show failure')

        else:
            commitreport = sagaguimodel.checkAllowedtoCommit()
            if commitreport['commitstatus']=='UserDenied':
                error_dialog.showMessage(commitreport['message'])
                error_dialog.exec_()
                return
            # if sagaguimodel.maincontainer.workingFrame.refreshedcheck is True:  ## this check should always happen.
            if commitreport['commitstatus']=='ConflictedFiles':
                #         show popup with list of conflict files
                commitconflictpopup = commitConflictCheck(commitreport['conflictfiles'])
                commitconflictpopup.showconflicts()
                return
            ###  Main Show
            committed, newframerev, message = \
                sagaguimodel.commitNewRevision(commitmessage = self.commitmsgEdit.toPlainText())
            ###  Main Show

            if committed:
                self.commitBttn.setDisabled(True)
                self.mainguihandle.refresh()
                self.framelabel.setText(newframerev)
                self.checkdelta()
                self.commitmsgEdit.setText('')
            else:
                error_dialog.showMessage(message)
                error_dialog.exec_()


    def reset(self):
        sagaguimodel.maincontainer = None
        self.containerlabel.setText('')
        self.histModel = HistoryListModel({})
        self.commithisttable.setModel(self.histModel)
        # self.maincontainerplot.reset()

    def readcontainer(self, containerpath):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'

        goswitch, newsectionid , shouldmodelswitchmessage= sagaguimodel.shouldModelSwitch(containerpath)
        msg = QMessageBox()
        msg.setStandardButtons(QMessageBox.Ok)
        if newsectionid is None:
            print('shouldModelSwitch call produced some sort of error')
            msg.setText(shouldmodelswitchmessage)
            msg.exec_()

        if goswitch:
            switchstatus = sagaguimodel.sectionSwitch(newsectionid)
            msg.setText(switchstatus)
            if switchstatus== 'User Current Section successfully changed':
                msg.setIcon(QMessageBox.Information)
                self.mainguihandle.resetguionsectionswitch()
            else:
                msg.setIcon(QMessageBox.Critical)
                ## if we arrived here, then that means either
            msg.exec_()

        print('Loading ' + containerpath)
        cont, histModel, containerfilemodel = sagaguimodel.loadContainer(containerpath)

        # [self.workingdir, file_name] = os.path.split(containerpath)  ## working dir should be app level
        self.containerlabel.setText('Container Name : ' + cont.containerName)
        self.framelabel.setText(cont.workingFrame.FrameName)

        self.commithisttable.setModel(histModel)
        self.commithisttable.setItemDelegate(HistoryCellDelegate())
        # self.maincontainerplot.setContainer(curContainer = sagaguimodel.maincontainer)
        # self.maincontainerplot.plot(sagaguimodel.changes)

        self.containerfiletable.setModel(containerfilemodel)
        self.containerfiletable.setItemDelegate(ContainerFileDelegate())
        sagaguimodel.getStatus()
        self.containerfiletable.model().update()


        self.setTab(True)
        self.containerLoaded = True
        if sagaguimodel.isNewContainer():
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

        if fileheader in sagaguimodel.maincontainer.filestomonitor().keys():
            self.removeFileButton_2.setEnabled(True)
        else:
            self.removeFileButton_2.setEnabled(False)

    def addToContainer(self):
        addfilegui = AddFileToContainerPopUp(containerworkdir=sagaguimodel.maincontainer.containerworkingfolder,
                                             containerinfodict = sagaguimodel.sagaapicall.getContainerInfoDict(),
                                             maincontainer=sagaguimodel.maincontainer
                                             )
        fileinfo = addfilegui.getInputs()
        if fileinfo:
            sagaguimodel.maincontainer.addFileObject(fileinfo=fileinfo)
            sagaguimodel.getStatus()
            self.containerfiletable.model().update()


    def removeFileInfo(self):
        # remove fileheader from current main container
        wmap = WorldMap(sagaguimodel.desktopdir)
        candelete, candeletemesssage = wmap.CheckContainerCanDeleteOutput(curcontainerid=sagaguimodel.maincontainer.containerId,
                                                                          fileheader=self.curfileheader,
                                                                          desktopdir=sagaguimodel.desktopdir,
                                                                          authtoken=sagaguimodel.authtoken)
        fileDialog = removeFileDialog(self.curfileheader, candelete,
                                      candeletemesssage)  # Dialog to confirm deleting container
        remove = fileDialog.removeFile()

        if remove:
            sagaguimodel.maincontainer.removeFileHeader(self.curfileheader)
            sagaguimodel.getStatus()
            self.containerfiletable.model().update()
            self.removefilebttn.setEnabled(False)

    def containerfileselected(self, containerfileindex):
        r = containerfileindex.row()
        fileheader = containerfileindex.model().containerfiles[r]['fileheader']
        if fileheader in sagaguimodel.maincontainer.FileHeaders.keys():
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
        containerworkingfolder = inputs['dir']
        containername = inputs['containername']
        containerfilemodel = sagaguimodel.initiateNewContainer(containerworkingfolder, containername)
        self.containerlabel.setText(containername)
        self.containerfiletable.setModel(containerfilemodel)
        self.commithisttable.setModel(self.histModel)
        self.framelabel.setText('Revision 0 (New Container)')
        self.newcontaineredit.setEnabled(True)
        self.setTab(True)
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
