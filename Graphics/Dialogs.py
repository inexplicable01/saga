from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrack
from Frame.commit import commit
import os
import sys
import requests
import json
import copy
from Frame.Container import Container

class ErrorMessage(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ErrorMessage')
        self.setIcon(QMessageBox.Warning)
        self.setText('Please Fill In All Container Information First')
        self.setStandardButtons(QMessageBox.Ok)
    def showError(self):
        self.exec_()

class inputFileDialog(QDialog):
    def __init__(self, containerName, containerObjName):
        super().__init__()
        # self.fileName = fileName
        uic.loadUi("Graphics/inputFileDialog.ui", self)
        self.containerName = containerName
        self.containerObjName = containerObjName
        self.containerName_label.setText(self.containerName)
        self.fileNameLabel.setText(containerObjName)
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'Container': self.containerName, 'type': 'Input'}
        else:
            return None

class removeFileDialog(QDialog):
    def __init__(self, containerObjName):
        super().__init__()
        uic.loadUi("Graphics/removeFileDialog.ui", self)
        self.containerObjName = containerObjName
        self.fileNameLabel.setText(self.containerObjName)
    def removeFile(self):
        if self.exec_() == QDialog.Accepted:
            return self.containerObjName
        else:
            return None
class commitDialog(QDialog):
    def __init__(self, containerName, description, commitMessage):
        super().__init__()
        uic.loadUi("Graphics/commitContainerDialog.ui", self)
        self.containerName = containerName
        self.containerNameLabel.setText(self.containerName)
    def commit(self):
        if self.exec_() == QDialog.Accepted:
            return True
        else:
            return False

class selectFileDialog(QDialog):
    def __init__(self, fileType:str):
        super().__init__()
        self.fileType = fileType
        if self.fileType == 'Required':
            uic.loadUi("Graphics/file_info.ui", self)
        elif self.fileType == 'Output':
            uic.loadUi("Graphics/file_info_outputs.ui", self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.openDirButton.clicked.connect(self.openDirectory)

    def openDirectory(self):
        self.openDirectoryDialog = QFileDialog.getOpenFileName(self, "Get Dir Path")
        self.filePathEdit.setText(self.openDirectoryDialog[0])

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.fileType == 'Required':
                containerFileInfo = {'Container': 'here', 'type':'Required'}
                return {'FileObjHeader': self.fileObjHeaderEdit.text(), 'FilePath':self.filePathEdit.text(),
                        'Owner': self.ownerEdit.text(), 'Description': self.descriptionEdit.text(),
                        'ContainerFileInfo': containerFileInfo}
            elif self.fileType == 'Output':
                containerFileInfo = {'Container': 'here', 'type': 'Required'}
                return {'FileObjHeader': self.fileObjHeaderEdit.text(), 'FilePath': self.filePathEdit.text(),
                        'Owner': self.ownerEdit.text(), 'Description': self.descriptionEdit.text(),
                        'ContainerFileInfo': containerFileInfo, 'ContainerDestination':self.destinationEdit}
        else:
            return None

class alteredinputFileDialog(QDialog):
    def __init__(self, alterfiletrack:FileTrack):
        super().__init__()
        # self.fileName = fileName
        uic.loadUi("Graphics/alteredinputFileDialog.ui", self)
        self.alterfiletrack = alterfiletrack
        self.old_filename_lbl.setText(alterfiletrack.file_name)
        self.old_fileheader_lbl.setText(alterfiletrack.FileHeader)

        linkstr= alterfiletrack.connection.refContainerId+'_'+alterfiletrack.connection.branch + '_'+ alterfiletrack.connection.Rev
        self.nfilename_edit.setText(linkstr + '_' + alterfiletrack.file_name)
        self.nfileheader_edit.setText(linkstr + '_' + alterfiletrack.FileHeader)
        # self.containerName_label.setText(self.containerName)
        # self.fileName_label.setText(containerObjName)
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:

            return { 'alterfiletrack':self.alterfiletrack,
                    'nfileheader': self.nfileheader_edit.text(),
                    'nfilename': self.nfilename_edit.text(),
                    'persist': self.persist_cb.checkState()}
        else:
            return None

