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
            print(containerId_in,containerId_out)
            ConnectionBox(self.containerscene,\
                             self.activeContainers[containerId_in],self.activeContainers[containerId_out])
        else:
            print(selectedobjname)
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
        self.inputbox={}
        self.outputbox = {}
        if container.inputObjs:
            idx =0
            for fileobj in container.inputObjs:
                print(fileobj['ContainerObjName'])
                self.inputbox[fileobj['ContainerObjName']]=FileRect(parent=self, locF= -containerBoxWidth/2-25, idx= idx,fileobj=fileobj,type='Input')
                idx+=1
        if container.outputObjs:
            idx = 0
            for fileobj in container.outputObjs:
                self.outputbox[fileobj['ContainerObjName']]=FileRect(parent=self, locF= containerBoxWidth/2+25, idx= idx,fileobj=fileobj, type='Output')
                idx += 1
        # self.subrect = FileRect(self)

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

        if containerIn.outputObjs and containerOut.inputObjs:
            idx=0
            for infileobj in containerIn.outputObjs:
                # print(infileobj['ContainerObjName'])
                for outfileobj in containerOut.inputObjs:
                    if infileobj['ContainerObjName']==outfileobj['ContainerObjName']:
                        # self.fileObj.append(QGraphicsRectItem(containerBoxWidth*-0.5, 100 +idx*100,  containerBoxWidth*1.1,60))
                        # containerscene.addItem(self.fileObj[-1])
                        self.fileObj.append(FileRect(None, containerBoxWidth*-0.5, idx, fileobj=infileobj, type='Connection'))
                        containerscene.addItem(self.fileObj[-1])
                        idx +=1


        # self.containoutBox = QGraphicsRectItem(containerBoxWidth * 0.1, 0, containerBoxWidth, containerBoxHeight)



class FileRect(QGraphicsRectItem):
    def __init__(self, parent, locF,idx,fileobj, type):

        if type=='Connection':
            boxgap = 0.1
        else:
            boxgap = 0
        super().__init__(locF,50 + idx*100,containerBoxWidth * (1 + boxgap),60,parent)
        self.setBrush(QBrush(Qt.green))
        self.setPen(QPen(Qt.black))
        if type=='Input':
            self.containertext = QGraphicsTextItem(fileobj['Container'], parent=self)
            self.containertext.setPos(self.rect().topLeft()+QPoint(0,-20))
        elif type=='Output':
            self.containertext = QGraphicsTextItem(fileobj['Container'], parent=self)
            self.containertext.setPos(self.rect().topRight()+QPoint(-50, -20))
        elif type=='Connection':
            offset = 0.25 #print('')#nothing yet
        self.upbox = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
        self.upbox.setPos(self.rect().topLeft())
        self.upboxtext =QGraphicsTextItem(fileobj['ContainerObjName'], parent=self.upbox)
        self.upboxtext.setPos(self.upbox.rect().topLeft())

        self.downbox = QGraphicsRectItem(containerBoxWidth*(1-0.1-0.25+boxgap),10 ,containerBoxWidth*0.25,40,self)
        self.downbox.setPos(self.rect().topLeft())
        self.downboxtext = QGraphicsTextItem(fileobj['ContainerObjName'], parent=self.downbox)
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