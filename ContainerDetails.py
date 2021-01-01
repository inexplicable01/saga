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

class refContainer():
    def __init__(self, mainGuiHandle, containerlist ):
        rownumber = containerlist.row()
        self.index = containerlist.model().index(rownumber, 0)
        self.containername = containerlist.model().data(self.index, 0)

        self.path = 'ContainerMapWorkDir/' + str(self.containername) + '_containerstate.yaml'
        self.scene = QGraphicsScene()
        self.mainGuiHandle = mainGuiHandle
        self.view = mainGuiHandle.graphicsView
        self.curcontainer = Container(self.path)
        self.inputRectBox = {}
        self.inputTitle = {}
        self.reqRectBox = {}
        self.reqTitle = {}
        self.outputRectBox = {}
        self.outputTitle = {}
        self.newFileInfo = mainGuiHandle.newFileInfo


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
        typeindex = {'input': 0, 'output': 2, 'required': 1}
        typecounter = {'input': 0, 'output': 0, 'required': 0}
        colorscheme = {'input': Qt.yellow, 'output': Qt.green, 'required': Qt.blue}
        for fileheader, fileinfo in self.curcontainer.FileHeaders.items():
            type=fileinfo['type']
            if type=='reference' or type=='references' :
                continue
            self.inputRectBox[fileheader] = coolerRectangle(100*typeindex[type] , 200 + 75*typecounter[type],  containerBoxWidth, containerBoxHeight,\
                                                            type,self.containername , fileheader, self.mainGuiHandle)
            self.inputRectBox[fileheader].setPen(QPen(colorscheme[type]))
            self.inputRectBox[fileheader].text = fileheader
            self.inputTitle[fileheader] = QGraphicsTextItem(fileheader)
            self.inputTitle[fileheader].setPos(QPoint(100*typeindex[type] , 200 + 75*typecounter[type]))
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
    def __init__(self, xpos, ypos, xwidth, ywidth, type, containerName, containerObjName, mainGuiHandle):
        super().__init__(xpos, ypos, xwidth, ywidth)
        self.type = type
        self.qtext = QGraphicsTextItem(type)
        self.qtext.setPos(QPoint(xpos,ypos))
        self.newFileInfo = mainGuiHandle.newFileInfo
        self.containerObjName = containerObjName
        self.containerName = containerName

    def mousePressEvent(self,event):
        print('pressed ' + self.type)
        if self.type == 'output':
            self.newFileInfo(self.type, self.containerName, self.containerObjName)
        # self.handle.setText(self.title)

