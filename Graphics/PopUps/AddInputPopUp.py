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
import sys
import requests
import json
from Config import BASE, sourcefolder
from SagaApp.SagaUtil import getContainerInfo
from Graphics.QAbstract.ContainerListModel import ContainerListModel

class AddInputPopUp(QDialog):
    def __init__(self, mainguihandle):
        super().__init__()
        uic.loadUi(sourcefolder + "Graphics/UI/AddInput.ui", self)
        # self.containerpathlbl.setText(path)
        containerinfolist = getContainerInfo(mainguihandle.authtoken)

        self.containerlisttable.setModel(ContainerListModel(containerinfolist))
        self.containerlisttable.clicked.connect(self.showContainerFromList)

        self.refContainerPlot = ContainerPlot(self, self.refContainerView)
        self.buttonBox1.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox1.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox1.button(QDialogButtonBox.Ok).clicked.connect(self.accept)

        self.fileheader = None
        self.type = None
        self.curContainer = None

    def coolerRectangleFeedback(self, type, view, fileheader, curContainer:Container):
        self.fileheader = fileheader
        self.type = type
        self.curContainer = curContainer
        if type==typeOutput:
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
        refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , CONTAINERFN)
        if os.path.exists(refcontainerpath):
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        else:
            refpath = os.path.join(self.mainGuiHandle.guiworkingdir,'ContainerMapWorkDir')
            Container.downloadContainerInfo(refpath,self.mainGuiHandle.authtoken, BASE, containerId)
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.changeContainer(self.selectedContainer)
        self.refContainerPlot.plot({})

    def getInputs(self):
        print('working')
        if self.exec_() == QDialog.Accepted:
            return {'fileheader': self.fileheader , 'type': self.type, 'UpstreamContainer': self.curContainer}
        else:
            return None