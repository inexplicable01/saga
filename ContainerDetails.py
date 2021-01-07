from PyQt5.QtWidgets import *
# from PyQt5 import uic
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

containerBoxHeight = 50
containerBoxWidth = 50
gap=0.1

class containerPlot():
    def __init__(self, mainGuiHandle, view, frame:Frame, containerName = ''):

        self.containerName = containerName
        # self.path = framePath
        self.scene = QGraphicsScene()
        self.mainGuiHandle = mainGuiHandle
        self.view = view
        self.curFrame = frame
        self.inputRectBox = {}
        self.inputTitle = {}
        self.reqRectBox = {}
        self.reqTitle = {}
        self.outputRectBox = {}
        self.outputTitle = {}
        self.newFileInfo = mainGuiHandle.newFileInfo


        # self.inputRect = self.createInputRect()



        rectItem = QGraphicsRectItem
        rectItem.origMousePress = rectItem.mousePressEvent

        # def addFileMousePressA(self, event:QMouseEvent):
        #     print("TestA")
        #     # self.mousePressEvent

        # def addFileMousePressB(event:QMouseEvent):
        #     print("TestB")
        #     # self.mousePressEvent()


        # rectItem.mousePressEvent = addFileMousePressA
    def plot(self):
        for key, rectBox in self.inputRectBox.items():
            self.scene.addItem(rectBox)

        # for key, rectBox in self.reqRectBox.items():
        #     self.scene.addItem(rectBox)
        #
        # for key, rectBox in self.outputRectBox.items():
        #     # rectBox.mousePressEvent= addFileMousePressB
        #     self.scene.addItem(rectBox)

        for key, rectBox in self.inputTitle.items():
            self.scene.addItem(rectBox)

        # for key, rectBox in self.reqTitle.items():
        #     self.scene.addItem(rectBox)
        #
        # for key, rectBox in self.outputTitle.items():
        #     self.scene.addItem(rectBox)

        self.view.setScene(self.scene)

    def removeRect(self, header):
        self.scene.removeItem(self.inputRectBox[header])
        self.scene.removeItem(self.inputTitle[header])
        del self.inputRectBox[header]
        del self.inputTitle[header]
        self.view.setScene(self.scene)

    def editRect(self, headerOrig, headerNew):
        self.scene.removeItem(self.inputRectBox[headerOrig])
        self.scene.removeItem(self.inputTitle[headerOrig])
        self.inputRectBox[headerNew] = self.inputRectBox.pop(headerOrig)
        self.inputRectBox[headerNew].text = headerNew
        self.inputTitle[headerNew] = self.inputTitle.pop(headerOrig)
        pos = self.inputTitle[headerNew].pos()
        self.inputTitle[headerNew] = QGraphicsTextItem(headerNew)
        self.inputTitle[headerNew].setPos(pos)



    def createInputRect(self):
        typeindex = {'Input': 0, 'Output': 2, 'Required': 1}
        typecounter = {'Input': 0, 'Output': 0, 'Required': 0}
        colorscheme = {'Input': Qt.yellow, 'Output': Qt.green, 'Required': Qt.blue}
        for header, fileinfo in self.curFrame.filestrack.items():
            type = fileinfo.style
            if type=='reference' or type=='references':
                continue
            self.inputRectBox[header] = coolerRectangle(100*typeindex[type] , 200 + 75*typecounter[type],  containerBoxWidth, containerBoxHeight,
                                                            type,self.containerName , header, self.mainGuiHandle, self.view)
            self.inputRectBox[header].setPen(QPen(colorscheme[type]))
            self.inputRectBox[header].text = header
            self.inputTitle[header] = QGraphicsTextItem(header)
            self.inputTitle[header].setPos(QPoint(100*typeindex[type] , 200 + 75*typecounter[type]))
            typecounter[type] += 1
        # if self.curcontainer.requiredObjs:
        #     position = 0
        #     for inputs in self.curcontainer.requiredObjs:
        #         self.reqRectBox[inputs['ContainerObjName']] = coolerRectangle(0, 200 + 75*position,  containerBoxWidth, containerBoxHeight, 'refRequired',self.containername ,inputs['ContainerObjName'], self.mainGuiHandle)
        #         self.reqRectBox[inputs['ContainerObjName']].setPen(QPen(Qt.blue))
        #         self.reqTitle[inputs['ContainerObjName']] = QGraphicsTextItem(inputs['ContainerObjName'])
        #         self.reqTitle[inputs['ContainerObjName']].setPos(QPoint(0, 200 + 75*position))
        #         position += 1
        # if self.curcontainer.outputObjs:
        #     position = 0
        #     for inputs in self.curcontainer.outputObjs:
        #         self.outputRectBox[inputs['ContainerObjName']] = coolerRectangle(100, 200 + 75 * position,  containerBoxWidth, containerBoxHeight,'refOutput', self.containername ,inputs['ContainerObjName'], self.mainGuiHandle)
        #         self.outputRectBox[inputs['ContainerObjName']].setPen(QPen(Qt.green))
        #
        #         self.outputTitle[inputs['ContainerObjName']] = QGraphicsTextItem(inputs['ContainerObjName'])
        #         self.outputTitle[inputs['ContainerObjName']].setPos(QPoint(100, 200 + 75*position))
        #         position += 1

class coolerRectangle(QGraphicsRectItem):
    def __init__(self, xpos, ypos, xwidth, ywidth, type, containerName, containerObjName, mainGuiHandle, view):
        super().__init__(xpos, ypos, xwidth, ywidth)
        self.type = type
        self.qtext = QGraphicsTextItem(type)
        self.qtext.setPos(QPoint(xpos,ypos))
        self.mainGuiHandle = mainGuiHandle
        self.newFileInfo = mainGuiHandle.newFileInfo
        self.containerObjName = containerObjName
        self.containerName = containerName
        self.view = view

    def mousePressEvent(self,event):
        print('pressed ' + self.type)
        if self.view == self.mainGuiHandle.refContainerView:
            if self.type == 'Output':
                self.newFileInfo('Input', self.containerName, self.containerObjName)
        elif self.view == self.mainGuiHandle.curContainerView:
            self.mainGuiHandle.editDeleteButtons(self.type, self.containerName, self.containerObjName)


