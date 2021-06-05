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
from os.path import join, normpath
import os
from shutil import copyfile

class selectFileDialog(QDialog):
    def __init__(self, fileType:str, containerworkdir, containerlist=None):
        super().__init__()
        self.fileType = fileType
        self.ctnrootpathlist = []
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

            if normpath(self.containerworkdir)==normpath(path):#root folder
                self.filePathEdit.setText(join(self.containerworkdir, file_name))
                # self.ctnrootpath='.'
            elif normpath(self.containerworkdir) in normpath(path):# Subfolder
                print('sub Folder')
                self.filePathEdit.setText(join(normpath(path), file_name))
                remainingpath = normpath(path).split(normpath(self.containerworkdir))[1]
                # l = []
                for folder in remainingpath.split(os.path.sep):
                    if len(folder)>0 and not folder=='.' and not folder=='..':
                        self.ctnrootpathlist.append(folder)
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
                # self.ctnrootpath = '.'



    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            if self.fileType == typeRequired or self.fileType == typeOutput:
                containerFileInfo = {'Container': 'here', 'type':self.fileType}
                return {'fileheader': self.fileObjHeaderEdit.text(), 'FilePath':self.filePathEdit.text(),
                        'Owner': self.ownerEdit.text(), 'Description': self.descriptionEdit.text(),
                        'ContainerFileInfo': containerFileInfo, 'ctnrootpathlist':self.ctnrootpathlist}
        else:
            return None