from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Graphics.ContainerPlot import ContainerPlot
from SagaApp.FileObjects import FileTrack
from Config import typeInput,typeRequired,typeOutput, TEMPCONTAINERFN, TEMPFRAMEFN, CONTAINERFN
import os
from os.path import join, normpath
from shutil import copyfile
import sys
import requests
import json
from Config import BASE
# from SagaApp.SagaUtil import getContainerInfo
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from SagaGuiModel import sagaguimodel

class AddFileToContainerPopUp(QDialog):
    def __init__(self, mainguihandle, containerworkdir,maincontainer:Container,filetype=typeInput):
        super().__init__()
        uic.loadUi("Graphics/UI/AddFileToContainer.ui", self)
        # self.containerpathlbl.setText(path)
        containerinfodict = sagaguimodel.getContainerInfo()

        if maincontainer.containerId in containerinfodict: del containerinfodict[maincontainer.containerId]### self container should not show up in input.

        self.filetyperadiogroup = QButtonGroup(self)
        # self.filetyperadiogroup.addButton(self.inputradiobttn)
        # self.inputradiobttn.setText(typeInput)
        # self.inputradiobttn.setChecked(True)
        self.filetyperadiogroup.addButton(self.workingradiobttn)
        # self.workingradiobttn.setText(typeRequired)
        self.filetyperadiogroup.addButton(self.outputradiobttn)
        # self.outputradiobttn.setText(typeOutput)
        self.filetyperadiogroup.buttonToggled.connect(self.typechanged)
        # self.tabs.currentChanged.connect(self.onChange)  # changed!

        self.containerlisttable.setModel(ContainerListModel(containerinfodict))
        self.containerlisttable.clicked.connect(self.showContainerFromList)

        self.refContainerPlot = ContainerPlot(self, self.refContainerView)
        self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox1.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox1.button(QDialogButtonBox.Ok).clicked.connect(self.accept)

        self.filetype = filetype
        self.ctnrootpathlist = []
        self.openDirButton.clicked.connect(self.openDirectory)
        self.containerworkdir=containerworkdir

        # self.tabWidget.currentChanged.connect(self.ontabchanged)

        self.fileheader = None
        self.curContainer = None
        self.descriptionEdit.setText('Description for how this file behaves for the larger project')
        self.navtotab()

    # def ontabchanged(self, tabindex):

    def typechanged(self, clickedbutton):
        # print(button.text())
        if 'Output' in clickedbutton.text():
            self.filetype= typeOutput
        elif 'Working' in clickedbutton.text():
            self.filetype=typeRequired
        self.navtotab()

    def navtotab(self):
        if self.filetype==typeInput:
            self.tabWidget.setCurrentIndex(0)
            if self.curContainer and self.fileheader:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        if self.filetype in [typeRequired,typeOutput]:
            self.tabWidget.setCurrentIndex(1)
            if os.path.exists(self.filePathEdit.text()):
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)

    def FileViewItemRectFeedback(self, filetype, view, fileheader, curContainer:Container):
        self.fileheader = fileheader
        self.filetype = filetype
        self.curContainer = curContainer
        if filetype==typeOutput:
            self.fileheaderlbl.setText("FileHeader: " + fileheader)
            self.fromcontainerlbl.setText("From Container: " + curContainer.containerName)
            self.revlbl.setText("Rev: " + curContainer.workingFrame.FrameName)
            self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.fileheaderlbl.setText("FileHeader: ")
            self.fromcontainerlbl.setText("From Container: ")
            self.revlbl.setText("Rev: ")
            self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)

    def showContainerFromList(self, containerList):
        rownumber = containerList.row()
        index = containerList.model().index(rownumber, 0)
        containerId = containerList.model().data(index, 0)
        refcontainerpath = os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerId , CONTAINERFN)
        if os.path.exists(refcontainerpath):
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        else:
            refpath = os.path.join(sagaguimodel.desktopdir,'ContainerMapWorkDir')
            Container.downloadContainerInfo(refpath,sagaguimodel.authtoken, BASE, containerId)
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.setContainer(self.selectedContainer)
        self.refContainerPlot.plot({})

    def openDirectory(self):

        openDirectoryDialog = QFileDialog.getOpenFileName(self, "Get Dir Path", self.containerworkdir)
        if openDirectoryDialog:
            [path, file_name] = os.path.split(openDirectoryDialog[0])

            if normpath(self.containerworkdir)==normpath(path):#root folder
                self.filePathEdit.setText(join(self.containerworkdir, file_name))
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            elif normpath(self.containerworkdir) in normpath(path):# Subfolder
                print('sub Folder')
                self.filePathEdit.setText(join(normpath(path), file_name))
                remainingpath = normpath(path).split(normpath(self.containerworkdir))[1]
                # l = []
                for folder in remainingpath.split(os.path.sep):
                    if len(folder)>0 and not folder=='.' and not folder=='..':
                        self.ctnrootpathlist.append(folder)
                self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                choice = QMessageBox.question(self, 'File not in Container',
                                                    "Copy file into Container folder?",
                                                    QMessageBox.Ok | QMessageBox.No)
                if choice==QMessageBox.Ok:
                    newfilepath = join(self.containerworkdir,file_name)
                    copyfile(join(path,file_name), newfilepath)
                    lastedited = os.path.getmtime(join(path,file_name))
                    os.utime(newfilepath, (lastedited, lastedited))
                    self.filePathEdit.setText(join(self.containerworkdir,file_name))
                    self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(True)

                # self.ctnrootpath = '.'

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.filetype == typeRequired:
                return {'fileheader': self.fileObjHeaderEdit.text(),
                        'filetype': self.filetype,
                        'FilePath': self.filePathEdit.text(),
                        'containerfileinfo': {'Container': 'here', 'type': self.filetype},
                        'description': self.descriptionEdit.text(),
                        'ctnrootpathlist': self.ctnrootpathlist,
                        }
            elif self.filetype == typeOutput:
                return {'fileheader': self.fileObjHeaderEdit.text(),
                        'filetype': self.filetype,
                        'FilePath':self.filePathEdit.text(),
                        'containerfileinfo': {'Container': [], 'type':self.filetype},
                        'description':self.descriptionEdit.text(),
                        'ctnrootpathlist':self.ctnrootpathlist,
                        }
            elif self.filetype == typeInput:
                return {'fileheader': self.fileheader,
                        'filetype': self.filetype,
                        'containerfileinfo': {'Container': self.curContainer.containerId, 'type':self.filetype},
                        'UpstreamContainer': self.curContainer,
                        'ctnrootpathlist': self.ctnrootpathlist,
                        'description':self.descriptionEdit.text()}
        else:
            return None