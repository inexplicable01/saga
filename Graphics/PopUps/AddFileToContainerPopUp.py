from PyQt5.QtWidgets import *
from PyQt5 import uic
from SagaCore.Container import Container
from Graphics.PYQTView.ContainerIconList import ContainerPlot
from SagaGuiModel.GuiModelConstants import roleInput,roleRequired,roleOutput
from SagaCore.ContainerItem import ContainerItemType
from SagaCore.SagaUtil import getFolderAftofContainerWkrFldr
import os
from os.path import normpath
from shutil import copyfile
from os.path import join
from Config import sourcecodedirfromconfig
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from SagaGuiModel import sagaguimodel
import uuid

class AddFileToContainerPopUp(QDialog):
    def __init__(self, containerworkdir,containerinfodict,maincontainer:Container,filerole=roleRequired, filetype = ContainerItemType.Singlefile.name):
        super().__init__()
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "AddFileToContainer.ui"), self)
        # self.containerpathlbl.setText(path)
        containerinfodict = sagaguimodel.containerinfodict
        if maincontainer.containerId in containerinfodict: del containerinfodict[maincontainer.containerId]### self container should not show up in input.
        self.fileroleradiogroup = QButtonGroup(self)
        # self.fileroleradiogroup.addButton(self.inputradiobttn)
        # self.inputradiobttn.setText(roleInput)
        #
        self.maincontainer=maincontainer
        self.fileroleradiogroup.addButton(self.workingradiobttn)
        self.fileroleradiogroup.addButton(self.outputradiobttn)
        self.fileroleradiogroup.buttonToggled.connect(self.rolechanged)
        self.workingradiobttn.setChecked(True)

        self.filetyperadiogroup = QButtonGroup(self)
        self.filetyperadiogroup.addButton(self.singlefileradiobttn)
        self.filetyperadiogroup.addButton(self.folderradiobttn)
        self.filetyperadiogroup.buttonToggled.connect(self.typechanged)
        self.filePathEdit.setEnabled(True)
        self.openFileButton.setEnabled(True)
        self.folderPathEdit.setEnabled(False)
        self.openDirButton.setEnabled(False)
        self.singlefileradiobttn.setChecked(True)


        self.containerlisttable.setModel(ContainerListModel(containerinfodict))
        self.containerlisttable.clicked.connect(self.showContainerFromList)
        # self.containerlisttable.header().setSectionResizeMode(QHeaderView.Stretch)

        self.refContainerPlot = ContainerPlot(self, self.refContainerView)
        self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox1.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox1.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        # self.tabWidget.currentChanged.connect(self.ontabchanged)

        self.filetype = filetype
        self.filerole = filerole
        self.ctnrootpathlist = []
        self.openFileButton.clicked.connect(self.getfile)
        self.openDirButton.clicked.connect(self.selectDirectory)
        self.containerworkdir=containerworkdir

        self.tabWidget.currentChanged.connect(self.ontabchanged)

        self.containerlisttable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.citemname = None
        self.inputcitemname = None
        self.inputfiletype = None
        self.localfiletype = ContainerItemType.Singlefile.name
        self.curContainer = None
        self.descriptionEdit.setText('Description for how this file behaves for the larger project')
        self.filePathEdit.textChanged[str].connect(self.textChanged)
        self.folderPathEdit.textChanged[str].connect(self.textChanged)
        self.descriptionEdit.textChanged[str].connect(self.textChanged)
        self.citemnameEdit.textChanged[str].connect(self.textChanged)
        self.fields = [self.descriptionEdit, self.filePathEdit, self.folderPathEdit, self.citemnameEdit]
        textfilled = {'filepath':0,'description':0,'citemname':0, 'folderpath':0}
        self.allfieldsentered = False
        self.okpermissions()

        self.citemnameEdit.setEnabled(False)

    def textChanged(self, strentry):
        if self.filerole in [roleRequired, roleOutput]:
            self.allfieldsentered = True
            if self.localfiletype==ContainerItemType.Singlefile.name:
                self.checkedits = {'description': self.descriptionEdit,
                                   'filepath': self.filePathEdit,
                                   'citemname': self.citemnameEdit}
            else:
                self.checkedits = {'description': self.descriptionEdit,
                                   'folderpath': self.folderPathEdit,
                                   'citemname': self.citemnameEdit}
            for key, edit in self.checkedits.items():
                if len(edit.text()) < 7:
                    self.allfieldsentered = False
                # warninglbl = warninglbl + 'Please Fill ' + key + 'Entry'
                # print(edit.text())
        self.okpermissions()

    def ontabchanged(self, tabindex):
        if tabindex==0:
            self.filerole = roleInput
        else:
            if self.fileroleradiogroup.checkedButton():
                if self.fileroleradiogroup.checkedButton().text() in [roleRequired,roleOutput]:
                    self.filerole = self.fileroleradiogroup.checkedButton().text()
                else:
                    self.filerole = None
            else:
                self.filerole = None

    def rolechanged(self, clickedbutton):
        # print(button.text())
        if 'Output' in clickedbutton.text():
            self.filerole= roleOutput
        elif 'Working' in clickedbutton.text():
            self.filerole=roleRequired
        self.okpermissions()

    def typechanged(self, clickedbutton):
        # print(button.text())
        if 'Add File' in clickedbutton.text():
            self.filePathEdit.setEnabled(True)
            self.openFileButton.setEnabled(True)
            self.folderPathEdit.setEnabled(False)
            self.openDirButton.setEnabled(False)
            self.localfiletype= ContainerItemType.Singlefile.name
        elif 'Add Folder' in clickedbutton.text():
            self.filePathEdit.setEnabled(False)
            self.openFileButton.setEnabled(False)
            self.folderPathEdit.setEnabled(True)
            self.openDirButton.setEnabled(True)
            self.localfiletype= ContainerItemType.Folder.name
        self.okpermissions()

    def okpermissions(self):
        if self.tabWidget.currentIndex()==0:
            ##If on the Input Tab
            if self.curContainer and self.inputcitemid:
                ## Input to be added, a container needs to be selected and a inputcitemid needs to be identified.
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        elif self.tabWidget.currentIndex()==1:
            # self.tabWidget.setCurrentIndex(1)
            if (os.path.exists(self.filePathEdit.text()) or os.path.exists(self.folderPathEdit.text())) and len(self.citemnameEdit.text())>7 and self.allfieldsentered:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)

    def FileViewItemRectFeedback(self, filerole, view, citemname,citem, curContainer:Container, filetype):

        if filerole==roleOutput:
            self.inputcitemid = citemname
            self.inputcitem = citem
            self.curContainer = curContainer
            self.inputfiletype = filetype
            self.fileheaderlbl.setText("ItemName: " + citemname)
            self.fromcontainerlbl.setText("From Container: " + curContainer.containerName)
            self.revlbl.setText("Rev: " + curContainer.refframe.FrameName)
            self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.inputcitemid = None
            self.inputcitem = None
            self.curContainer = None
            self.inputfiletype =None
            self.fileheaderlbl.setText("ItemName: (Need to select Output)")
            self.fromcontainerlbl.setText("From Container: ")
            self.revlbl.setText("Rev: ")
            self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)

    def showContainerFromList(self, containerListindex):
        rownumber = containerListindex.row()
        index = containerListindex.model().index(rownumber, 0)
        # containerId = containerListindex.model().data(index, 0)
        containerName = containerListindex.model().data(index, 0)
        containerId=containerListindex.model().containernametoid[containerName]

        # refcontainerpath = os.path.join(sagaguimodel.appdata_saga, 'ContainerMapWorkDir', containerId , CONTAINERFN)
        # if os.path.exists(refcontainerpath):
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # else:
        #
        #     containerworkingfolder, self.selectedContainer=sagaguimodel.downloadContainer(containerworkingfolder, containerId)
        self.selectedContainer = sagaguimodel.provideContainer(containerId)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.setContainer(self.selectedContainer)
        self.refContainerPlot.plot({})

    def selectDirectory(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder', self.containerworkdir)
        foldertoadd= getFolderAftofContainerWkrFldr(folderpath, self.containerworkdir)
        # print(foldertoadd)
        self.folderPathEdit.setText(join(self.containerworkdir, foldertoadd))
        path, citemname = os.path.split(foldertoadd)
        if not self.maincontainer.canAddName(citemname):
            citemname = citemname + '_2'
        self.citemnameEdit.setText(citemname)
        self.folderpath = foldertoadd
        self.okpermissions()

    def getfile(self):
        openDirectoryDialog = QFileDialog.getOpenFileName(self, "Get Dir Path", self.containerworkdir)
        if openDirectoryDialog:
            [path, filename_est] = os.path.split(openDirectoryDialog[0])
            if normpath(self.containerworkdir)==normpath(path):#root folder
                self.filePathEdit.setText(join(self.containerworkdir, filename_est))
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
                self.localfilename = filename_est
                [filename, est] = os.path.splitext(filename_est)
                if not self.maincontainer.canAddName(filename):
                    filename = filename + '_2'
                self.citemnameEdit.setText(filename)
            elif normpath(self.containerworkdir) in normpath(path):# Subfolder
                print('sub Folder')
                self.filePathEdit.setText(join(normpath(path), filename_est))
                remainingpath = normpath(path).split(normpath(self.containerworkdir))[1]
                # l = []
                self.localfilename = join(remainingpath, filename_est)
                for folder in remainingpath.split(os.path.sep):
                    if len(folder)>0 and not folder=='.' and not folder=='..':
                        self.ctnrootpathlist.append(folder)
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)

                [filename, est] = os.path.splitext(filename_est)
                if not self.maincontainer.canAddName(filename):
                    filename = filename + '_2'
                self.citemnameEdit.setText(filename)
            else:
                choice = QMessageBox.question(self, 'File not in Container',
                                                    "Copy file into Container folder?",
                                                    QMessageBox.Ok | QMessageBox.No)
                if choice==QMessageBox.Ok:
                    newfilepath = join(self.containerworkdir,filename_est)
                    copyfile(join(path,filename_est), newfilepath)
                    lastedited = os.path.getmtime(join(path,filename_est))
                    os.utime(newfilepath, (lastedited, lastedited))
                    self.filePathEdit.setText(join(self.containerworkdir,filename_est))
                    self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)

                # self.ctnrootpath = '.'
        self.okpermissions()

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.filerole in [roleRequired,roleOutput]:
                citemid = None
                citemname = self.citemnameEdit.text().replace(" ", "")
                relevCont = None
                filetype = self.localfiletype
                if filetype==ContainerItemType.Singlefile.name:
                    ItemPath = self.localfilename
                elif filetype==ContainerItemType.Folder.name:
                    ItemPath = self.folderpath
                if self.filerole==roleRequired:
                    refcontainerid = 'here'
                else:
                    refcontainerid = []
                description =self.descriptionEdit.text()
            elif self.filerole == roleInput:
                citemid= self.inputcitemid
                citemname = self.inputcitem.containeritemname
                refcontainerid=self.curContainer.containerId
                relevCont = self.curContainer
                filetype = self.inputfiletype
                ItemPath=None
                description = self.descriptionEdit.text()
            return {'citemid': citemid,
                    'citemname': citemname,
                    'filerole': self.filerole,
                    'refcontainerid':refcontainerid,
                    # 'containerfileinfo': {'Container': refcontainerid, 'type':self.filerole},
                    'UpstreamContainer': relevCont,
                    'ItemPath':ItemPath,
                    'filetype':filetype,
                    'ctnrootpathlist': self.ctnrootpathlist,
                    'description':description}
        else:
            return None