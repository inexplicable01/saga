from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Graphics.ContainerPlot import ContainerPlot
from Frame.FileObjects import FileTrack
from Config import typeInput,typeRequired,typeOutput
import os
import sys
import requests
import json
from Config import BASE

class AddInputPopUp(QDialog):
    def __init__(self, mainguihandle):
        super().__init__()
        uic.loadUi("Graphics/UI/AddInput.ui", self)
        # self.containerpathlbl.setText(path)
        mainguihandle.getContainerInfo(self.containerlisttable)
        self.containerlisttable.clicked.connect(self.showContainerFromList)

        self.refContainerPlot = ContainerPlot(self, self.refContainerView, container=Container.InitiateContainer())
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
        refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , 'containerstate.yaml')
        if os.path.exists(refcontainerpath):
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        else:
            refpath = os.path.join('ContainerMapWorkDir')
            Container.downloadContainerInfo(refpath,self.mainGuiHandle.authtoken, BASE, containerId)
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.changeContainer(self.selectedContainer)
        self.refContainerPlot.plot()

    def getInputs(self):
        print('working')
        if self.exec_() == QDialog.Accepted:
            return {'fileheader': self.fileheader , 'type': self.type, 'UpstreamContainer': self.curContainer}
        else:
            return None