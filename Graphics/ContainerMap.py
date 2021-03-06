from PyQt5.QtWidgets import *
from PyQt5 import uic
import math
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import yaml
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack
from Config import typeInput,typeOutput,typeRequired, colorscheme


import os
import sys
import requests
import json
import copy

rectheight = 40
rectwidth = 40
# fileboxHeight = 50
# fileboxWidth = 50

class ContainerMap():
    def __init__(self, activeContainers, qtview, selecteddetail,detailedmap):
        self.activeContainers = activeContainers  # contain the container objs
        self.qtview = qtview
        self.selecteddetail=selecteddetail
        self.detailedmap=detailedmap
        self.activeContainersObj={} # contain the Rect objects
        self.containerscene = QGraphicsScene()
        self.qtview.setScene(self.containerscene)
        self.containerConnections = {} # dictionary of Id: list of OD
        self.containerConnectLines={}  # dictionary of lineId:LineObject

    def reset(self):
        self.containerscene = QGraphicsScene()
        self.qtview.setScene(self.containerscene)
        self.containerConnections = {} # dictionary of Id: list of OD
        self.containerConnectLines={}  # dictionary of lineId:LineObject
        self.activeContainersObj = {}

    def drawline(self):
        for containerId_in, containerId_outlist in self.containerConnections.items():
            for containerId_out in containerId_outlist:
                lineid = containerId_in + '_' + containerId_out
                if lineid not in self.containerConnectLines:
                    Q1 = self.activeContainersObj[containerId_in].QPos + QPointF(rectheight/2, rectwidth/2)
                    Q2 = self.activeContainersObj[containerId_out].QPos + QPointF(rectheight/2, rectwidth/2)
                    self.containerConnectLines[lineid] = containerLine(Q1,Q2,lineid, self.detailedmap)
                    self.containerscene.addItem(self.containerConnectLines[lineid])
                else:
                    Q1 = self.activeContainersObj[containerId_in].QPos + QPointF(rectheight/2, rectwidth/2)
                    Q2 = self.activeContainersObj[containerId_out].QPos + QPointF(rectheight/2, rectwidth/2)
                    self.containerConnectLines[lineid].setLine(QLineF(Q1, Q2))


    def editcontainerConnections(self):
        for container in self.activeContainers.values():
            ##Loops through all containers and build connection by looping through each FileHeaders to build map.
            ## Doesn't care so much about individual FileHeader, just cares about Container to Container
            for FileHeader, FileInfo in container.FileHeaders.items():
                ##Identify upstream and downstream containerId
                upstreamContainerId=None
                downstreamContainerId=None
                if FileInfo['type']=='Input':
                    upstreamContainerId = FileInfo['Container']
                    downstreamContainerId = container.containerId
                elif FileInfo['type'] in ['Output']:
                    upstreamContainerId = container.containerId
                    downstreamContainerId = FileInfo['Container']

                if type(downstreamContainerId) is list:
                    downstreamContaineridList = downstreamContainerId
                    for downstreamContainerId in downstreamContaineridList:
                        if downstreamContainerId not in self.activeContainers.keys() or upstreamContainerId is None:
                            continue  # if containerID not in current map or if type isn't input or output
                        if upstreamContainerId in self.containerConnections.keys():
                            if downstreamContainerId not in self.containerConnections[upstreamContainerId]:
                                self.containerConnections[upstreamContainerId].append(downstreamContainerId)
                        else:
                            self.containerConnections[upstreamContainerId] = [downstreamContainerId]
                else:
                    if FileInfo['Container'] not in self.activeContainers.keys() or upstreamContainerId is None:
                        continue # if containerID not in current map or if type isn't input or output
                    if upstreamContainerId in self.containerConnections.keys():
                        if downstreamContainerId not in self.containerConnections[upstreamContainerId]:
                            self.containerConnections[upstreamContainerId].append(downstreamContainerId)
                    else:
                        self.containerConnections[upstreamContainerId] = [downstreamContainerId]


    def addActiveContainers(self, container:Container):
        self.activeContainers[container.containerId]=container

    def plot(self):
        idx,idy=1,1
        gridsize = math.ceil(math.sqrt(len(self.activeContainers.values())))
        for container in self.activeContainers.values():
            # print(container.containerName)
            # text = self.containerscene.addText(container.containerName)
            self.activeContainersObj[container.containerId]=containerRect(idx,idy, container.containerName, \
                                                                          self.drawline, self.detailedmap,self.selecteddetail)
            self.containerscene.addItem(self.activeContainersObj[container.containerId])
            idx +=1
            if idx>gridsize:
                idx, idy = 1, idy + 1
        self.drawline()



class containerRect(QGraphicsRectItem):
    def __init__(self, idx,idy,containerName,drawline, detailedmap,selecteddetail,rectheight=rectheight, rectwidth=rectwidth):
        super().__init__(0, 0, rectheight, rectwidth)
        self.rectheight = rectheight
        self.rectwidth = rectwidth
        self.QPos = QPointF(idx*100,idy*100)
        self.setPos(self.QPos)
        self.setBrush(QBrush(Qt.transparent))
        self.setPen(QPen(Qt.black))
        self.containerName = containerName
        # self.text.setPos(self.QPos)
        self.drawline=drawline
        self.detailedmap = detailedmap
        self.selecteddetail=selecteddetail
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def dragMoveEvent(self, event):
        print(event)

    def mousePressEvent(self,event):
        print('pressed')

    def boundingRect(self):
        return self.rect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        rect = self.boundingRect()
        additionalwidth = 100
        textRect = QRectF(rect.topLeft().x() - additionalwidth / 2, rect.topLeft().y() + rectheight,
                          rectwidth+ additionalwidth, 20)
        picRect = QRectF(rect.topLeft().x(), rect.topLeft().y(), rect.width() , rect.height() )
        # picRect.moveCenter(rect.center())

        # Draw type Background color
        painter.setPen(QPen(QBrush(Qt.black), 4))
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(rect)
        # Draw text
        painter.setPen(QPen(QBrush(Qt.black), 6))
        painter.drawText(textRect, Qt.AlignCenter, self.containerName)
        # Draw Picture
        qpic = QImage('Graphics/FileIcons/Container.png')
        painter.drawImage(picRect, qpic)


    def mouseMoveEvent(self,event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x()- orig_cursor_position.x()+ orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.QPos = QPointF(updated_cursor_x, updated_cursor_y)
        self.setPos(self.QPos)
        self.update()
        # self.text.setPos(self.QPos)

    def mouseReleaseEvent(self,event):
        self.drawline()
        self.selecteddetail['selectedobjname']=self.containerName
        self.detailedmap.selectedobj(self.containerName)

class containerLine(QGraphicsLineItem):
    def __init__(self, Q1,Q2,lineid,detailedmap):
        # self.containerConnectLines[lineid] = self.containerscene.addLine(QLineF(Q1, Q2), QPen(Qt.green))
        super().__init__(QLineF(Q1, Q2))
        self.setPen(QPen(QBrush(Qt.green), 6))
        self.lineid=lineid
        self.detailedmap=detailedmap



        # self.setFlag(QGraphicsItem.ItemIsMovable, True)
    def mousePressEvent(self,event):
        print(self.lineid)
        self.detailedmap.selectedobj(self.lineid)


    # def mouseReleaseEvent(self,event):
    #     # self.drawline()
    #     # self.selecteddetail['selectedobjname']=self.text.toPlainText()
    #     # self.detailedmap.selectedobj(self.text.toPlainText())
    #     print(self.lineid)