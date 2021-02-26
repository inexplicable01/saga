from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Config import typeInput,typeOutput,typeRequired
from Frame.FileObjects import FileTrack
from Frame.commit import commit
import os
import sys
import requests
import json
import copy

colorscheme = {typeInput: Qt.yellow, typeOutput: Qt.green, typeRequired: Qt.blue}

containerBoxHeight = 250
containerBoxWidth = 300
gap=0.1

class DetailedMap():
    def __init__(self,detailsMapView, selecteddetail):
        self.detailsMapView=detailsMapView
        self.selecteddetail= selecteddetail
        self.containerscene = QGraphicsScene()
        self.textholder = self.containerscene.addText('clicktoinitiate')
        self.textholder.setPos(QPointF(0,0))
        self.viewitems={}
        self.detailsMapView.setScene(self.containerscene)

    def selectedobj(self,selectedobjname):
        self.containerscene = QGraphicsScene()

        self.selecteddetail['selectedobjname'] = selectedobjname

        if '_' in selectedobjname:
            [containerId_in, containerId_out] = selectedobjname.split('_')
            # print(containerId_in,containerId_out)
            ConnectionBox(self.containerscene,\
                             self.activeContainers[containerId_in],self.activeContainers[containerId_out])
        else:
            # print(selectedobjname)
            self.viewitems[selectedobjname] = self.containerscene.addItem( \
                containerBox(self.containerscene,self.activeContainers[selectedobjname]))
        self.detailsMapView.setScene(self.containerscene)

    def passobj(self, containmap):
        self.activeContainers=containmap.activeContainers


class containerBox(QGraphicsRectItem):
    def __init__(self, containerscene,container,containerBoxHeight=containerBoxHeight, containerBoxWidth=containerBoxWidth):
        super().__init__(0, 0,  containerBoxWidth,containerBoxHeight)
        self.containerBoxHeight = containerBoxHeight
        self.containerBoxWidth = containerBoxWidth
        # self.QPos = QPointF(50,50)
        self.setBrush(QBrush(Qt.transparent))
        self.setPen(QPen(Qt.black))
        self.containertitle=container.containerId
        self.containerscene = containerscene
        self.titletext = self.containerscene.addText(container.containerId)
        self.titletext.setPos(QPointF(10,10))
        self.titletext.setFont(QFont("Times",16))
        self.inputlbl = self.containerscene.addText('Input')
        self.inputlbl.setPos(QPointF(15,40))
        self.outputlbl = self.containerscene.addText('Output')
        self.outputlbl.setPos(QPointF(self.rect().width()/2+ 15,40))
        self.crossbox={}
        # self.outputbox = {}
        typecounter = {typeInput: 0, typeOutput: 0}
        loc = {typeInput: -1, typeOutput: 1}
        if container.FileHeaders:

            for fileheader, fileinfo in container.FileHeaders.items():
                type = fileinfo['type']
                if type in [typeInput, typeOutput]:
                    # print(fileheader)
                    self.crossbox[fileheader]=FileRect(parent=self, locF= (containerBoxWidth+40)*loc[type]/2, idx= typecounter[type],\
                                                       fileinfo=fileinfo,fileheader=fileheader,type=type)
                    typecounter[type]+=1


class ConnectionBox():
    def __init__(self, containerscene,containerIn:Container, containerOut:Container,containerBoxHeight=containerBoxHeight, containerBoxWidth=containerBoxWidth):
        self.containInBox = QGraphicsRectItem(containerBoxWidth*-1.0, 0,  containerBoxWidth,containerBoxHeight)
        containerscene.addItem(self.containInBox)
        containerintext = QGraphicsTextItem(containerIn.containerId, parent=self.containInBox)
        containerintext.setPos(self.containInBox.rect().topLeft())

        self.containoutBox = QGraphicsRectItem(containerBoxWidth * gap, 0, containerBoxWidth, containerBoxHeight)
        containerscene.addItem(self.containoutBox)
        containerouttext = QGraphicsTextItem(containerOut.containerId, parent=self.containoutBox)
        containerouttext.setPos(self.containoutBox.rect().topLeft())

        self.fileObj = []

        idx=0
        for upfileheader, upfileinfo in containerIn.FileHeaders.items():
            if upfileinfo['type']==typeOutput and set([containerOut.containerId]).issubset(set(upfileinfo['Container'])):
                if containerOut.FileHeaders[upfileheader] and containerOut.FileHeaders[upfileheader]['type']==typeInput:
                    self.fileObj.append(FileRect(None, containerBoxWidth*-0.5, idx, fileinfo=upfileinfo, fileheader=upfileheader, type='Connection'))
                    containerscene.addItem(self.fileObj[-1])
                    idx +=1


class FileRect(QGraphicsRectItem):
    def __init__(self, parent, locF,idx,fileinfo,fileheader, type):

        if type=='Connection':
            boxgap = 0.1
        else:
            boxgap = 0
        super().__init__(locF,60 + idx*100,containerBoxWidth * (1 + boxgap),60,parent)

        self.setPen(QPen(Qt.black))
        if type==typeInput:
            self.setBrush(QBrush(colorscheme[type]))
            self.containertext = QGraphicsTextItem(fileinfo['Container'], parent=self)
            self.containertext.setPos(self.rect().topLeft()+QPoint(0,-20))
        elif type==typeOutput:
            self.setBrush(QBrush(colorscheme[type]))
            for idx,outputcontainer in enumerate(fileinfo['Container']):
                self.containertext = QGraphicsTextItem(outputcontainer, parent=self)
                self.containertext.setPos(self.rect().topRight()+QPoint(-50, -20 -idx*15))
        elif type=='Connection':
            grad = QLinearGradient(self.rect().topLeft(), self.rect().topRight())
            grad.setColorAt(1, Qt.yellow)
            grad.setColorAt(0, Qt.green)
            self.setBrush(QBrush(grad))
            offset = 0.25 #print('')#nothing yet
        self.upbox = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
        self.upbox.setPos(self.rect().topLeft())
        self.upboxtext =QGraphicsTextItem(fileheader, parent=self.upbox)
        self.upboxtext.setPos(self.upbox.rect().topLeft())


        self.downbox = QGraphicsRectItem(containerBoxWidth*(1-0.1-0.25+boxgap),10 ,containerBoxWidth*0.25,40,self)
        self.downbox.setPos(self.rect().topLeft())
        self.downboxtext = QGraphicsTextItem(fileheader, parent=self.downbox)
        self.downboxtext.setPos(self.downbox.rect().topLeft())

        Q1 = self.upbox.rect().center()
        Q2 = self.downbox.rect().center()
        self.connectionline = QGraphicsLineItem(QLineF(Q1,Q2),self)
        self.connectionline.setPen(QPen(Qt.red))
        self.connectionline.setPos(self.rect().topLeft())



    def dragMoveEvent(self, event):
        print(event)

    def mousePressEvent(self, event):
        print('pressed')

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x()- orig_cursor_position.x()+ orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))
        # self.text.setPos(self.QPos)
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)