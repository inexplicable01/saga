from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrackObj
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

class newContainerGraphics():
    def __init__(self, tempContainer:Container, mainGuiHandle ):
        self.tempContainer = tempContainer
        self.scene = QGraphicsScene()
        self.mainGuiHandle = mainGuiHandle
        self.view = mainGuiHandle.graphicsView_3
        self.inputRectBox = {}
        self.inputTitle = {}
        self.reqRectBox = {}
        self.reqTitle = {}
        self.outputRectBox = {}
        self.outputTitle = {}

        self.inputRect = self.createInputRect()

        for key, rectBox in self.inputRectBox.items():
            self.scene.addItem(rectBox)

        for key, rectBox in self.reqRectBox.items():
            self.scene.addItem(rectBox)

        for key, rectBox in self.outputRectBox.items():
            # rectBox.mousePressEvent= addFileMousePressB
            self.scene.addItem(rectBox)

        for key, rectBox in self.inputTitle.items():
            self.scene.addItem(rectBox)

        for key, rectBox in self.reqTitle.items():
            self.scene.addItem(rectBox)

        for key, rectBox in self.outputTitle.items():
            self.scene.addItem(rectBox)

        self.view.setScene(self.scene)

        rectItem = QGraphicsRectItem
        rectItem.origMousePress = rectItem.mousePressEvent

        # def addFileMousePressA(self, event:QMouseEvent):
        #     print("TestA")
        #     # self.mousePressEvent

        # def addFileMousePressB(event:QMouseEvent):
        #     print("TestB")
        #     # self.mousePressEvent()


        # rectItem.mousePressEvent = addFileMousePressA

    def createInputRect(self):
        if self.tempContainer.inputObjs:
            position = 0
            for inputs in self.tempContainer.inputObjs:
                self.inputRectBox[inputs['ContainerObjName']] = coolerRectangle(-100, 200 + 75*position,  containerBoxWidth, containerBoxHeight,'refInput',self.tempContainer.containerName , inputs['ContainerObjName'], self.mainGuiHandle)
                self.inputRectBox[inputs['ContainerObjName']].setPen(QPen(Qt.yellow))
                self.inputRectBox[inputs['ContainerObjName']].text = inputs['ContainerObjName']
                self.inputTitle[inputs['ContainerObjName']] = QGraphicsTextItem(inputs['ContainerObjName'])
                self.inputTitle[inputs['ContainerObjName']].setPos(QPoint(-100, 200 + 75*position))
                position += 1
        if self.tempContainer.requiredObjs:
            position = 0
            for inputs in self.tempContainer.requiredObjs:
                self.reqRectBox[inputs['ContainerObjName']] = coolerRectangle(0, 200 + 75*position,  containerBoxWidth, containerBoxHeight, 'refRequired',self.tempContainer.containerName ,inputs['ContainerObjName'], self.mainGuiHandle)
                self.reqRectBox[inputs['ContainerObjName']].setPen(QPen(Qt.blue))
                self.reqTitle[inputs['ContainerObjName']] = QGraphicsTextItem(inputs['ContainerObjName'])
                self.reqTitle[inputs['ContainerObjName']].setPos(QPoint(0, 200 + 75*position))
                position += 1
        if self.tempContainer.outputObjs:
            position = 0
            for inputs in self.tempContainer.outputObjs:
                self.outputRectBox[inputs['ContainerObjName']] = coolerRectangle(100, 200 + 75 * position,  containerBoxWidth, containerBoxHeight,'refOutput', self.tempContainer.containerName ,inputs['ContainerObjName'], self.mainGuiHandle)
                self.outputRectBox[inputs['ContainerObjName']].setPen(QPen(Qt.green))
                self.outputTitle[inputs['ContainerObjName']] = QGraphicsTextItem(inputs['ContainerObjName'])
                self.outputTitle[inputs['ContainerObjName']].setPos(QPoint(100, 200 + 75*position))
                position += 1




class coolerRectangle(QGraphicsRectItem):
    def __init__(self, xpos, ypos, xwidth, ywidth, text, containerName, containerObjName, mainGuiHandle):
        super().__init__(xpos, ypos, xwidth, ywidth)
        self.title = text
        self.qtext = QGraphicsTextItem(text)
        self.qtext.setPos(QPoint(xpos,ypos))
        self.newFileInfo = mainGuiHandle.newFileInfo
        self.containerObjName = containerObjName
        self.containerName = containerName


