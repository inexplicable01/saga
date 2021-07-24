from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Config import typeInput,typeOutput,typeRequired, colorscheme
from SagaApp.FileObjects import FileTrack

import os
import sys
import requests
import json
import copy



containerBoxHeight = 61
containerBoxWidth = 300
gap=0.1

class DetailedMap():
    def __init__(self,detailsMapView, selecteddetail):
        self.detailsMapView=detailsMapView
        self.selecteddetail= selecteddetail
        self.containerscene = QGraphicsScene()
        self.textholder = self.containerscene.addText('Select a Container or Connection')
        self.textholder.setDefaultTextColor(Qt.white)
        self.textholder.setPos(QPointF(0,0))
        self.viewitems={}

        self.detailsMapView.setScene(self.containerscene)

    def reset(self):
        self.containerscene = QGraphicsScene()
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
            self.containerscene.addItem( \
                containerBox(self.containerscene,self.activeContainers[selectedobjname]))
        self.detailsMapView.setScene(self.containerscene)

    def passobj(self, containmap):
        self.activeContainers=containmap.activeContainers


class containerBox(QGraphicsRectItem):
    def __init__(self, containerscene,container,containerBoxHeight=containerBoxHeight, containerBoxWidth=containerBoxWidth):
        super().__init__(0, 0,  containerBoxWidth,containerscene.height())
        # self.containerBoxHeight = containerBoxHeight
        # self.containerBoxWidth = containerBoxWidth
        # self.QPos = QPointF(50,50)
        self.setBrush(QBrush(Qt.transparent))
        self.setPen(QPen(Qt.white))
        self.containertitle=container.containerId
        self.containerscene = containerscene
        self.titletext = self.containerscene.addText(container.containerId)
        self.titletext.setPos(QPointF(10,10))
        self.titletext.setFont(QFont("Times",16))
        self.titletext.setDefaultTextColor(Qt.white)
        self.inputlbl = self.containerscene.addText('Input')
        self.inputlbl.setDefaultTextColor(Qt.white)
        self.inputlbl.setPos(QPointF(15,40))
        self.outputlbl = self.containerscene.addText('Output')
        self.outputlbl.setDefaultTextColor(Qt.white)
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
                    self.crossbox[fileheader] = FileRect(parent=self, locF=(containerBoxWidth + 40) * loc[type] / 2,
                                                         idx=typecounter[type], \
                                                         fileinfo=fileinfo, fileheader=fileheader, type=type)
                    # if type == 'Output':
                    #     for containerName in fileinfo['Container']:
                    #         if containerName in self.crossbox:
                    #             self.crossbox[containerName].addFile(parent=self, fileheader=fileheader)
                    #         else:
                    #             self.crossbox[containerName] = FileRect(parent=self,
                    #                                                             locF=(containerBoxWidth + 40) * loc[
                    #                                                                 type] / 2, idx=typecounter[type], \
                    #                                                             fileinfo=fileinfo,
                    #                                                             fileheader=fileheader, type=type)
                    # else:
                    #     if fileinfo['Container'] in self.crossbox:
                    #         self.crossbox[fileinfo['Container']].addFile(parent=self, fileheader = fileheader)
                    #     else:
                    #         self.crossbox[fileinfo['Container']]=FileRect(parent=self, locF= (containerBoxWidth+40)*loc[type]/2, idx= typecounter[type],\
                    #                                            fileinfo=fileinfo,fileheader=fileheader,type=type)
                    typecounter[type]+=1

        ##Quick Hack to size height of Container Box
        self.setRect(0, 0,  containerBoxWidth,70 + max(typecounter.values())*100)
        self.setPen(QPen(QBrush(Qt.white),4))


class ConnectionBox():

    # ConnectionBox is currently a generic class while containerBox inherits from QRects
# This is rather confusing and just not a very good structure  They should either both inherit from Qrects or both are just generic classes

    def __init__(self, containerscene,containerIn:Container, containerOut:Container,containerBoxHeight=containerBoxHeight, containerBoxWidth=containerBoxWidth):
        self.containInBox = QGraphicsRectItem(containerBoxWidth*-1.0, 0,  containerBoxWidth,containerBoxHeight)
        self.containInBox.setPen(Qt.white)
        containerscene.addItem(self.containInBox)
        containerintext = QGraphicsTextItem(containerIn.containerId, parent=self.containInBox)
        containerintext.setPos(self.containInBox.rect().topLeft())
        containerintext.setDefaultTextColor(Qt.white)

        self.containoutBox = QGraphicsRectItem(containerBoxWidth * gap, 0, containerBoxWidth, containerBoxHeight)
        containerscene.addItem(self.containoutBox)
        containerouttext = QGraphicsTextItem(containerOut.containerId, parent=self.containoutBox)
        containerouttext.setPos(self.containoutBox.rect().topLeft())
        containerouttext.setDefaultTextColor(Qt.white)

        self.fileObj = []

        idx=0
        for upfileheader, upfileinfo in containerIn.FileHeaders.items():
            if upfileinfo['type']==typeOutput and set([containerOut.containerId]).issubset(set(upfileinfo['Container'])):
                if containerOut.FileHeaders[upfileheader] and containerOut.FileHeaders[upfileheader]['type']==typeInput:
                    self.fileObj.append(FileRect(None, containerBoxWidth*-0.5, idx, fileinfo=upfileinfo, fileheader=upfileheader, type='Connection'))
                    containerscene.addItem(self.fileObj[-1])
                    idx +=1

        self.containInBox.setRect(containerBoxWidth*-1.0, 0,  containerBoxWidth, 70 + idx * 100)
        self.containoutBox.setRect(containerBoxWidth * gap, 0, containerBoxWidth, 70 + idx * 100)
        ##Quick Hack to size height of Container Box
        # self.setRect(0, 0, containerBoxWidth, 70 + idx * 100)


class FileRect(QGraphicsRectItem):
    def __init__(self, parent, locF,idx,fileinfo,fileheader, type):

        if type=='Connection':
            boxgap = 0.1
            # self.boxgap = 0.1
        else:
            boxgap = 0
            # self.boxgap = 0
        super().__init__(locF,70 + idx*100,containerBoxWidth * (1 + boxgap),60,parent)
        # self.setParentItem(parent)
        # self.setRect(locF, 60 + idx * 100, containerBoxWidth * (1 + boxgap), containerBoxHeight)
        # self.fileCount = 1
        # self.locF = locF
        # self.idx = idx
        # super().__init__(locF,60 + idx*100,containerBoxWidth * (1 + self.boxgap),60,parent)



        if type==typeInput:
            self.setPen(QPen(colorscheme[type], 4))
            # self.setBrush(QBrush(colorscheme[type]))
            self.containertext = QGraphicsTextItem(fileinfo['Container'], parent=self)
            self.containertext.setPos(self.rect().topLeft()+QPoint(0,-20))
            self.containertext.setDefaultTextColor(Qt.white)
        elif type==typeOutput:
            # self.setBrush(QBrush(colorscheme[type]))
            self.setPen(QPen(colorscheme[type], 4))
            for idx,outputcontainer in enumerate(fileinfo['Container']):
                self.containertext = QGraphicsTextItem(outputcontainer, parent=self)
                self.containertext.setDefaultTextColor(Qt.white)
                self.containertext.setPos(self.rect().topRight()+QPoint(-50, -20 -idx*15))
        elif type=='Connection':
            grad = QLinearGradient(self.rect().topLeft(), self.rect().topRight())
            grad.setColorAt(1, colorscheme['Input'])
            grad.setColorAt(0, colorscheme['Output'])

            self.setBrush(QBrush(grad))
            self.setPen(QPen(QBrush(grad), 2))
            offset = 0.25 #print('')#nothing yet

        self.upbox = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
        self.upbox.setPen(QPen(QBrush(Qt.white),3))
        self.upbox.setPos(self.rect().topLeft())
        self.upboxtext =QGraphicsTextItem(fileheader, parent=self.upbox)
        self.upboxtext.setPos(self.upbox.rect().topLeft())
        self.upboxtext.setDefaultTextColor(Qt.white)


    #     self.upbox = {}
    #     self.upboxtext = {}
    #     self.upbox[fileheader] = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
    #     self.upbox[fileheader].setPos(self.rect().topLeft())
    #     self.upboxtext[fileheader] =QGraphicsTextItem(fileheader, parent=self.upbox[fileheader])
    #     self.upboxtext[fileheader].setPos(self.upbox[fileheader].rect().topLeft())
    #
    #
    #     # self.downbox = QGraphicsRectItem(containerBoxWidth*(1-0.1-0.25+boxgap),10 ,containerBoxWidth*0.25,40,self)
    #     # self.downbox.setPos(self.rect().topLeft())
    #     # self.downboxtext = QGraphicsTextItem(fileheader, parent=self.downbox)
    #     # self.downboxtext.setPos(self.downbox.rect().topLeft())
    #
    #     Q1 = self.upbox[fileheader].rect().center()
    #     # Q2 = self.downbox.rect().center()
    #     # self.connectionline = QGraphicsLineItem(QLineF(Q1,Q2),self)
    #     # self.connectionline.setPen(QPen(Qt.red))
    #     # self.connectionline.setPos(self.rect().topLeft())
    #
    # def addFile(self, parent, fileheader):
    #     self.fileCount += 1
    #     self.setRect(self.locF, 60 + self.idx * 100, containerBoxWidth * (1 + self.boxgap), containerBoxHeight * self.fileCount)
    #     self.upbox[fileheader] = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
    #     self.upbox[fileheader].setPos(self.rect().topLeft())
    #     self.upbox[fileheader].moveBy(0,(containerBoxHeight/2 * self.fileCount))
    #     self.upboxtext[fileheader] =QGraphicsTextItem(fileheader, parent=self.upbox[fileheader])
    #     self.upboxtext[fileheader].setPos(self.upbox[fileheader].rect().topLeft())
    # def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
    #     QPainter.drawRoundedRect()

    def dragMoveEvent(self, event):
        print(event)

    def mousePressEvent(self, event):
        print('List')

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x()- orig_cursor_position.x()+ orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))
        # self.text.setPos(self.QPos)
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)