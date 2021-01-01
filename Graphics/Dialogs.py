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
        self.fileName_label.setText(containerObjName)
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'Container': self.containerName, 'ContainerObjName': self.containerObjName}
        else:
            return None


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
        self.lineEdit_2.setText(self.openDirectoryDialog[0])

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.fileType == 'Required':
                return {'ContainerObjName': self.lineEdit.text()}
            elif self.fileType == 'Output':
                return{'Container': self.lineEdit_5.text(), 'ContainerObjName': self.lineEdit.text()}
            # Need to add space for path, owner, directory, etc.
        else:
            return None

