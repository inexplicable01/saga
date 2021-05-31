from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
# from SagaApp.FrameStruct import Frame
# from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack
from Config import typeInput,typeRequired,typeOutput
import os
from shutil import copyfile

import sys
import requests
import json
import copy
# from SagaApp.Container import Container

class ganttChartFiles(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Graphics/UI/fileChart.ui", self)
    def showChart(self):
        self.exec()

class ganttChartProject(QDialog):
    def __init__(self):
        super().__init__()
        # uic.loadUi("Graphics/UI/projectChart.ui", self)
        uic.loadUi("Graphics/UI/projectChart.ui", self)
        self.actualButton.clicked.connect(self.showActualChart)
        self.scheduledButton.clicked.connect(self.showScheduledChart)
    def showChart(self):
        self.exec()
    def showActualChart(self):
        self.titleLabel.setText("Actual Gantt Chart")
        self.chartPic.setPixmap(QPixmap("Graphics/UI/Demo_Project_Gantt_Completed.png"))
    def showScheduledChart(self):
        self.chartPic.setPixmap(QPixmap("Graphics/UI/Demo_Project_Gantt.png"))
        self.titleLabel.setText("Scheduled Gantt Chart")

# class errorPopUp(QDialog):
#     def __init__(self):
#         super().__init__()
#         uic.loadUi("Graphics/UI/errorMessage.ui",self)
#     def showMessage(self, text):
#         self.errorText.setText(text)
#         self.exec()

class downloadProgressBar(QWidget):
    def __init__(self, fileId):
        super().__init__()
        uic.loadUi("Graphics/UI/downloadProgressBar.ui", self)
        self.fileNameLabel.setText(fileId)
    def updateProgress(self, value):
        self.progressBar.setValue(value)
        self.show()
        # self.progressBar.setProperty("value", percent)

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
    def __init__(self, ContainerId, fileheader):
        super().__init__()
        # self.fileName = fileName
        uic.loadUi("Graphics/UI/inputFileDialog.ui", self)
        self.ContainerId, = ContainerId,
        self.fileheader = fileheader
        self.containerName_label.setText(self.ContainerId,)
        self.fileNameLabel.setText(fileheader)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'Container': self.ContainerId, 'type': typeInput}
        else:
            return None

class removeFileDialog(QDialog):
    def __init__(self, fileheader,candelete, candeletemesssage):
        super().__init__()
        uic.loadUi("Graphics/UI/removeFileDialog.ui", self)
        self.fileheader = fileheader
        self.fileNameLabel.setText(self.fileheader)

        if not candelete:
            self.deletewarninglbl.setText(candeletemesssage)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def removeFile(self):
        if self.exec_() == QDialog.Accepted:
            return self.fileheader
        else:
            return None
class commitDialog(QDialog):
    def __init__(self, containerName, description, commitMessage):
        super().__init__()
        uic.loadUi("Graphics/UI/commitContainerDialog.ui", self)
        self.containerName = containerName
        self.containerNameLabel.setText(self.containerName)
    def commit(self):
        if self.exec_() == QDialog.Accepted:
            return True
        else:
            return False

class selectFileDialog(QDialog):
    def __init__(self, fileType:str, containerworkdir, containerlist=None):
        super().__init__()
        self.fileType = fileType
        if self.fileType == typeRequired:
            uic.loadUi("Graphics/UI/file_info.ui", self)
            self.ownerEdit.setText('OwnerRequired')
            self.descriptionEdit.setText('DescrtiptionRequired')
        elif self.fileType == typeOutput:
            uic.loadUi("Graphics/UI/file_info_outputs.ui", self)
            self.ownerEdit.setText('Owneroutput')
            self.descriptionEdit.setText('Descrtiptionoutpu')
            # for container in containerlist:
            #     self.downcontainerbox.addItem(container)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.openDirButton.clicked.connect(self.openDirectory)
        self.containerworkdir=containerworkdir

    def openDirectory(self):

        openDirectoryDialog = QFileDialog.getOpenFileName(self, "Get Dir Path", self.containerworkdir)
        if openDirectoryDialog:
            [path, file_name] = os.path.split(openDirectoryDialog[0])

            if os.path.normpath(self.containerworkdir)==os.path.normpath(path):#root folder
                self.filePathEdit.setText(os.path.join(self.containerworkdir, file_name))
            elif os.path.normpath(self.containerworkdir) in os.path.normpath(path):# Subfolder
                print('sub Folder')
            else:
                choice = QMessageBox.question(self, 'File not in Container',
                                                    "Copy file into Container folder?",
                                                    QMessageBox.Ok | QMessageBox.No)
                if choice==QMessageBox.Ok:
                    newfilepath = os.path.join(self.containerworkdir,file_name)
                    copyfile(os.path.join(path,file_name), newfilepath)
                    lastedited = os.path.getmtime(os.path.join(path,file_name))
                    os.utime(newfilepath, (lastedited, lastedited))
                    self.filePathEdit.setText(os.path.join(self.containerworkdir,file_name))



    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.fileType == typeRequired:
                containerFileInfo = {'Container': 'here', 'type':typeRequired}
                return {'fileheader': self.fileObjHeaderEdit.text(), 'FilePath':self.filePathEdit.text(),
                        'Owner': self.ownerEdit.text(), 'Description': self.descriptionEdit.text(),
                        'ContainerFileInfo': containerFileInfo}
            elif self.fileType == typeOutput:
                containerFileInfo = {'Container': [], 'type': typeOutput}
                return {'fileheader': self.fileObjHeaderEdit.text(), 'FilePath': self.filePathEdit.text(),
                        'Owner': self.ownerEdit.text(), 'Description': self.descriptionEdit.text(),
                        'ContainerFileInfo': containerFileInfo}
        else:
            return None

class alteredinputFileDialog(QDialog):
    def __init__(self, alterfiletrack:FileTrack):
        super().__init__()
        # self.fileName = fileName
        uic.loadUi("Graphics/UI/alteredinputFileDialog.ui", self)
        self.alterfiletrack = alterfiletrack
        self.old_filename_lbl.setText(alterfiletrack.file_name)
        self.old_fileheader_lbl.setText(alterfiletrack.FileHeader)

        linkstr= alterfiletrack.connection.refContainerId+'_'+alterfiletrack.connection.branch + '_'+ alterfiletrack.connection.Rev
        self.nfilename_edit.setText(linkstr + '_' + alterfiletrack.file_name)
        self.nfileheader_edit.setText(linkstr + '_' + alterfiletrack.FileHeader)
        # self.containerName_label.setText(self.containerName)
        # self.fileName_label.setText(fileheader)
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:

            return { 'alterfiletrack':self.alterfiletrack,
                    'nfileheader': self.nfileheader_edit.text(),
                    'nfilename': self.nfilename_edit.text(),
                    'persist': self.persist_cb.checkState()}
        else:
            return None

