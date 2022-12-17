from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.GuiUtil import setstyleoflabel

from Graphics.QAbstract.ContainerFileModel import ContainerFileModel, ContainerFileDelegate
from Graphics.QAbstract.historycelldelegate import HistoryCellDelegate

# from Graphics.Dialogs import alteredinputFileDialog
# from Graphics.ContainerPlot import ContainerPlot
from Graphics.Dialogs import ErrorMessage, removeFileDialog, commitDialog, alteredinputFileDialog\
    , downloadProgressBar, commitConflictCheck
from Graphics.PopUps.refreshContainerPopUp import refreshContainerPopUp

import os
from SagaGuiModel.GuiModelConstants import SERVERNEWREVISION, SERVERFILEADDED, SERVERFILEDELETED, NEWCONTAINERFN, TEMPCONTAINERFN, \
    LOCALCITEMNAMEADDED, TEMPFRAMEFN, colorscheme, roleOutput, roleInput, roleRequired, UPDATEDUPSTREAM
from Graphics.PopUps.AddFileToContainerPopUp import AddFileToContainerPopUp
from SagaCore.ContainerItem import ContainerItem
from SagaGuiModel import sagaguimodel
from datetime import datetime


class MainContainerTab():
    def __init__(self, mainguihandle):
        self.commitBttn = mainguihandle.commitBttn
        self.revertbttn = mainguihandle.revertbttn
        self.commitmsgEdit = mainguihandle.commitmsgEdit
        self.commithisttable = mainguihandle.commithisttable

        self.containersyncbttn = mainguihandle.containersyncbttn
        self.containersyncbttn.setDisabled(True)
        self.framelabel = mainguihandle.framelabel
        # self.maincontainerview = mainguihandle.maincontainerview

        self.menuContainer = mainguihandle.menuContainer
        self.frametextBrowser = mainguihandle.frametextBrowser
        self.containerlabel = mainguihandle.containerlabel
        self.addtocontainerbttn = mainguihandle.addtocontainerbttn
        self.containerstatuslabel = mainguihandle.containerstatuslabel
        self.commitmsglbl_2 = mainguihandle.commitmsglbl_2
        self.contstackedwidget = mainguihandle.contstackedwidget
        self.newcontaineredit = mainguihandle.newcontaineredit
        # self.selectedFileHeader = mainguihandle.selectedFileHeader
        self.removefilebttn = mainguihandle.removefilebttn

        self.containerfiletable = mainguihandle.containerfiletable
        self.containerfiletable.horizontalHeader().resizeSection(1, 200)
        self.containerfiletable.horizontalHeader().resizeSection(2, 200)
        # self.containerfiletable.header().resizeSection(2, 100)
        self.containerfiletable.horizontalHeader().setStretchLastSection(True)
        self.containerfiletable.clicked.connect(self.containerfileselected)

        self.newcontainerlbl = mainguihandle.newcontainerlbl
        self.commitmsgboxlbl = mainguihandle.commitmsgboxlbl
        self.containerdescriplbl = mainguihandle.containerdescriplbl
        self.container_subtab = mainguihandle.container_subtab
        self.getstatusbttn = mainguihandle.getstatusbttn

        self.container_subtab.setElideMode(Qt.ElideNone)


        # self.newcontaineredit = mainguihandle.newcontaineredit

        self.index = 1

        self.mainguihandle = mainguihandle

        self.GuiTab = mainguihandle.ContainerTab

        self.containerfiletable.setModel(sagaguimodel.containerfilemodel)
        self.containerfiletable.setItemDelegate(ContainerFileDelegate())
        self.commithisttable.setModel(sagaguimodel.histModel)
        self.commithisttable.setItemDelegate(HistoryCellDelegate())

        # self.maincontainerplot = ContainerPlot(self, self.maincontainerview, container=None)
        # self.openContainerBttn = mainguihandle.openContainerBttn
        self.commitBttn.setEnabled(False)
        # self.workingdir = ''
        self.removefilebttn.clicked.connect(self.removeFileInfo)
        self.addtocontainerbttn.clicked.connect(self.addToContainer)
        self.getstatusbttn.clicked.connect(self.checkdelta)
        # self.refreshBttn.clicked.connect(self.checkdelta)
        # self.downloadUpstreamBttn.clicked.connect(self.downloadUpstream)
        self.containersyncbttn.clicked.connect(self.containersync)
        self.allowcommit = False
        self.commitBttn.clicked.connect(self.commit)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)
        self.removefilebttn.setEnabled(False)
        # self.editFileButton_2.setEnabled(False)
        # self.removeFileButton_2.setEnabled(False)
        self.commitmsgEdit.setDisabled(True)
        # self.newcontaineredit.setDisabled(True)
        ###########History Info####
        self.commithisttable.clicked.connect(self.commithistselected)
        self.commithisttable.horizontalHeader().sectionClicked.connect(self.commithistheaderselected)
        self.alterfiletracks = []
        self.curcitem :ContainerItem= None
        self.changes = {}
        self.containerLoaded = False
        # self.newContainerStatus = False
        # self.containerstatuslabel = self.mainguihandle.containerStatusLabel
        self.refreshedrevision = 0
        self.refreshedcheck = False
        self.citemtorevertto=None
        self.commitmsgEdit.textChanged.connect(self.commitmsgeditchange)
        self.newcontaineredit.textChanged.connect(self.commitmsgeditchange)

        setstyleoflabel(colorscheme[roleInput], self.mainguihandle.inputlbl)
        setstyleoflabel(colorscheme[roleOutput], self.mainguihandle.outputlbl)
        setstyleoflabel(colorscheme[roleRequired], self.mainguihandle.requiredlbl)



    def containersync(self):
        # refreshrevnum = str(sagaguimodel.maincontainer.revnum) + '/' + str(sagaguimodel.newestrevnum)
        # need to update above line to add additional / when refreshing multiple container revisions

        conflictlistmodel2, noticelistmodel = sagaguimodel.getRefreshPopUpModels()
        conflictpopup = refreshContainerPopUp(conflictlistmodel2, noticelistmodel)
        combinedactionstate = conflictpopup.selectFiles()
        # oldframe = sagaguimodel.maincontainer.workingFrame.FrameName
        if combinedactionstate:
            alldownloaded, inputsupdate = sagaguimodel.dealWithUserSelection(combinedactionstate)
            if alldownloaded:
                sagaguimodel.downloadbranch()
            self.checkdelta()
            if alldownloaded:
                self.containerstatuslabel.setText(
                    'Container Refreshed!  This Container now is at a Rev ' + str(sagaguimodel.newestrevnum) + '+ state')
            if inputsupdate:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Commit will occur as Inputs are updated.')
                committed, newframerev, message = \
                    sagaguimodel.commitNewRevision('Committing new revision base on input synchonization')# Attention need to get information about which files where updated.

                if committed:
                    self.commitBttn.setDisabled(True)
                    self.mainguihandle.loadSection()  # Redownloads entire Section.   Is this right?
                    self.framelabel.setText(newframerev)
                    self.checkdelta()
                    self.commitmsgEdit.setText('')

        #         TO DO add to commit function check of conflicting files and spit out error message or have user choose which file to commit
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
        sagaguimodel.revertTo(self.reverttorev,self.citemtorevertto)
        self.commitmsgEdit.setText('Revert back to ' + self.reverttorev)
        self.checkdelta()

    def checkdelta(self):
        print('Checking' + datetime.now().isoformat())
        self.mainguihandle.maintabwidget.setCursor(QCursor(Qt.WaitCursor))
        # allowCommit, changes, fixInput , self.alterfiletracks= sagaguimodel.maincontainer.checkFrame(sagaguimodel.maincontainer.workingFrame)
        if sagaguimodel.maincontainer is None:
            return
        # print('before GetStatus' + datetime.now().isoformat())
        statustext, self.allowcommit, canrefresh,  changes = sagaguimodel.getStatus()
        # print('aft GetStatus' + datetime.now().isoformat())
        self.containerstatuslabel.setText(statustext)
        self.commitBttn.setEnabled(self.allowcommit)
        # if self.allowcommit:
        #     self.commitmsgeditchange()
        self.commitmsgEdit.setDisabled(not self.allowcommit)
        # self.newcontaineredit.setDisabled(not sagaguimodel.isNewContainer()) # if this is a new container, edit should be enabled.

        self.containersyncbttn.setEnabled(canrefresh)
        self.frametextBrowser.setText('')
        for fileheader, change in changes.items():
            if not change.worthNoting():
                continue
            self.frametextBrowser.append(change.writeHTMLStatus())
        # print('before filetableupdate GetStatus' + datetime.now().isoformat())
        self.containerfiletable.model().update()
        # width = self.containerfiletable.width()
        self.containerfiletable.setColumnWidth(0, 300)
        self.containerfiletable.setColumnWidth(1, 300)
        self.containerfiletable.setColumnWidth(3, 250)
        print('Check Done ' + datetime.now().isoformat())
        self.mainguihandle.maintabwidget.setCursor(QCursor(Qt.ArrowCursor))

    def commitmsgeditchange(self):
        canpresscommit = False
        # if sagaguimodel.isNewContainer():
        #     if len(self.commitmsgEdit.toPlainText()) >7 and len(self.newcontaineredit.text()) >7 :
        #         canpresscommit = True
        #     if len(self.commitmsgEdit.toPlainText()) <= 7:
        #         commitmsgboxtext = 'Commit Message : Needs to be longer than 7 characters'
        #     else:
        #         commitmsgboxtext = 'Commit Message'
        #     # if len(self.newcontaineredit.text()) <= 7:
        #     #     containerdescriptext = 'Container Description Message : Needs to be longer than 7 characters'
        #     # else:
        #     #     containerdescriptext = 'Container Description'
        #     # sagaguimodel.maincontainer.description = self.newcontaineredit.text()
        #     # self.newcontainerlbl.setText(containerdescriptext)
        # else:
        #     containerdescriptext = 'Container Description'
        if len(self.commitmsgEdit.toPlainText()) > 7:
            canpresscommit = True
            commitmsgboxtext = 'Commit Message :'
        else:
            canpresscommit = False
            commitmsgboxtext = 'Commit Message : Needs to be longer than 7 characters'
        if canpresscommit:
            self.commitBttn.setEnabled(self.allowcommit)
        self.commitmsgboxlbl.setText(commitmsgboxtext)

    def commit(self):
        error_dialog = QErrorMessage()
        self.checkdelta()
        if not self.allowcommit:
            print('not allowed to commit')
        if sagaguimodel.isNewContainer():
            ## opportunity to show way more information for Commit Dialog
            commitCheck = commitDialog(sagaguimodel.maincontainer.containerName, self.newcontaineredit.text(),
                                       self.commitmsgEdit.toPlainText())
            confirmcommit = commitCheck.commit()
            if confirmcommit:
                success = sagaguimodel.commitNewContainer(commitmessage = self.commitmsgEdit.toPlainText())
                if success:
                    containeryaml = os.path.join(sagaguimodel.maincontainer.containerworkingfolder, TEMPCONTAINERFN)
                    self.readcontainer(containeryaml)
                    self.mainguihandle.maintabwidget.setCurrentIndex(self.index)
                    self.mainguihandle.loadSection()
                    # self.mainguihandle.maptab.updateContainerMap()
                    self.newcontaineredit.setDisabled(True)
                else:
                    print('Commit failed, need to adjust the gui to show failure')
                self.commitmsgEdit.setText('')
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
            if commitreport['commitstatus']=='MISSINGITEMS':
                #         show popup with list of conflict files
                error_dialog.showMessage(commitreport['message'])
                error_dialog.exec_()
                return
            ###  Main Show
            committed, newframerev, message = \
                sagaguimodel.commitNewRevision(commitmessage = self.commitmsgEdit.toPlainText())
            ###  Main Show

            if committed:
                self.commitBttn.setDisabled(True)
                self.mainguihandle.loadSection() # Redownloads entire Section.   Is this right?
                self.framelabel.setText(newframerev)
                self.checkdelta()
                self.commitmsgEdit.setText('')
            else:
                error_dialog.showMessage(message)
                error_dialog.exec_()


    def reset(self):
        sagaguimodel.container_reset()
        self.containerlabel.setText('')
        self.frametextBrowser.setText('')
        # self.commithisttable.setModel(self.histModel)
        # self.maincontainerplot.reset()

    def readcontainer(self, containerpath):
        # path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        # print('start of readcontainer' + datetime.now().isoformat())
        print('Loading ' + containerpath)
        # sagaguimodel.container_reset()# In case there is no section switch
        cont = sagaguimodel.loadContainer(containerpath, ismaincontainer=True)
        print('end of loadcontainer' + datetime.now().isoformat())
        self.containerlabel.setText('Container Name : ' + cont.containerName)
        self.containerdescriplbl.setText(sagaguimodel.maincontainer.description)
        self.framelabel.setText(cont.workingFrame.FrameName)
        self.setTab(True)
        if sagaguimodel.isNewContainer():
            self.commitBttn.setText('Commit New Container')
            self.contstackedwidget.setCurrentIndex(1)## index 1 is new container description edit.
        else:
            self.commitBttn.setText('Commit')
            self.contstackedwidget.setCurrentIndex(0)## index 0 is container description
        ## Enable Permission button since Main Container
        self.mainguihandle.setPermissionsEnable()
        self.checkdelta()


    def addToContainer(self):
        addfilegui = AddFileToContainerPopUp(containerworkdir=sagaguimodel.maincontainer.containerworkingfolder,
                                             containerinfodict=sagaguimodel.containerinfodict,
                                             maincontainer=sagaguimodel.maincontainer
                                             )
        fileinfo = addfilegui.getInputs()
        if fileinfo:
            downloadfile = sagaguimodel.maincontainer.addFileObject(fileinfo=fileinfo)
            if downloadfile:
                sagaguimodel.downloadTrack(
                    track=downloadfile['filetrack'],
                    containerworkingfolder=sagaguimodel.maincontainer.containerworkingfolder)
            self.checkdelta()

    def removeFileInfo(self):
        # remove fileheader from current main container
        # wmap = WorldMap(sagaguimodel.appdata_saga)

        candelete, candeletemesssage = sagaguimodel.CheckContainerCanDeleteOutput(self.curcitem)
        fileDialog = removeFileDialog(self.curcitem, candelete,candeletemesssage)  # Dialog to confirm deleting container
        remove = fileDialog.removeFile()
        if remove:
            sagaguimodel.maincontainer.removeContainerItem(citemid=self.curcitem.containeritemid)
            self.checkdelta()
            self.removefilebttn.setEnabled(False)

    def containerfileselected(self, containerfileindex):
        r = containerfileindex.row()
        citemid = containerfileindex.model().containerfolderstatus[r].citemid
        if citemid in sagaguimodel.maincontainer.containeritems.keys():
            self.curcitem=sagaguimodel.maincontainer.containeritems[citemid]
            self.removefilebttn.setText('Remove : ' + str(self.curcitem.containeritemname))
            self.removefilebttn.setEnabled(True)
        else:
            self.curcitem='Selected File Not Part of your Project'
            self.removefilebttn.setText('Remove :')
            self.removefilebttn.setEnabled(False)


    def commithistselected(self, histableindex):
        self.reverttorev = histableindex.model().revheaders[histableindex.column()]
        self.citemtorevertto = histableindex.model().fileheaderlist[histableindex.row()]
        self.commitmsglbl_2.setText('Commit Message : '+histableindex.model().commitmsg[histableindex.column()])
        self.revertbttn.setText('Revert FileHeader ' + self.citemtorevertto + '  to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def commithistheaderselected(self, column):
        self.reverttorev = self.commithisttable.model().revheaders[column]
        self.citemtorevertto = None
        self.commitmsglbl_2.setText('Commit Message : '+self.commithisttable.model().commitmsg[column])
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def initiate(self, inputs):
        containerworkingfolder = inputs['dir']
        containername = inputs['containername']
        containerdesc = inputs['containerdesc']
        sagaguimodel.initiateNewContainer(containerworkingfolder, containername, containerdesc)
        self.containerlabel.setText(containername)
        self.contstackedwidget.setCurrentIndex(1)  ## index 1 is new container description edit.
        self.framelabel.setText('Revision 0 (New Container)')
        self.newcontaineredit.setEnabled(False)
        self.newcontaineredit.setText(containerdesc)
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
