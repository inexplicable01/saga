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

rectheight = 40
rectwidth = 40

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

    def drawline(self):
        for containerId_in, containerId_outlist in self.containerConnections.items():
            for containerId_out in containerId_outlist:
                lineid = containerId_in + '_' + containerId_out
                if lineid not in self.containerConnectLines:
                    Q1 = copy.deepcopy(self.activeContainersObj[containerId_in].QPos)
                    Q2 = copy.deepcopy(self.activeContainersObj[containerId_out].QPos)
                    Q1 += QPointF(rectheight/2, rectwidth/2)
                    Q2 += QPointF(rectheight/2, rectwidth/2)

                    self.containerConnectLines[lineid] = containerLine(Q1,Q2,lineid, self.detailedmap)
                    self.containerscene.addItem(self.containerConnectLines[lineid])
                    # self.containerConnectLines[lineid] = self.containerscene.addLine(QLineF(Q1, Q2), QPen(Qt.green))
                else:
                    Q1 = copy.deepcopy(self.activeContainersObj[containerId_in].QPos)
                    Q2 = copy.deepcopy(self.activeContainersObj[containerId_out].QPos)
                    Q1 += QPointF(rectheight/2, rectwidth/2)
                    Q2 += QPointF(rectheight/2, rectwidth/2)
                    self.containerConnectLines[lineid].setLine(QLineF(Q1, Q2))


    def editcontainerConnections(self):
        for container in self.activeContainers.values():
            # print(container.containerId)
            if container.inputObjs:
                for input in container.inputObjs:
                    # print('in' + input['Container'] + ' to '  + container.containerId + 'for file' + input['ContainerObjName'])
                    if input['Container'] in self.containerConnections.keys():
                        if container.containerId not in self.containerConnections[input['Container']]:
                            self.containerConnections[input['Container']].append(container.containerId)
                    else:
                        self.containerConnections[input['Container']]=[container.containerId]
            if container.outputObjs:
                if container.containerId not in self.containerConnections.keys():
                    self.containerConnections[container.containerId]=[]
                for output in container.outputObjs:
                    # print('out' + container.containerId + ' to '  + output['Container'] + 'for file' + output['ContainerObjName'])
                    if output['Container'] not in self.containerConnections[container.containerId]:
                        self.containerConnections[container.containerId].append(output['Container'])
        print(self.containerConnections)

    def addActiveContainers(self, container:Container):
        self.activeContainers[container.containerId]=container

    def plot(self):
        idx=0
        for container in self.activeContainers.values():
            # print(container.containerName)
            text = self.containerscene.addText(container.containerName)
            self.activeContainersObj[container.containerName]=containerRect(idx, text, self.drawline, self.detailedmap,self.selecteddetail)
            self.containerscene.addItem(self.activeContainersObj[container.containerName])
            idx +=1
        self.drawline()



class containerRect(QGraphicsRectItem):
    def __init__(self, idx,text,drawline, detailedmap,selecteddetail,rectheight=rectheight, rectwidth=rectwidth):
        super().__init__(0, 0, rectheight, rectwidth)
        self.rectheight = rectheight
        self.rectwidth = rectwidth
        self.QPos = QPointF(-100+idx*100,-200)
        self.setPos(self.QPos)
        self.setBrush(QBrush(Qt.transparent))
        self.setPen(QPen(Qt.black))
        self.text = text
        self.text.setPos(self.QPos)
        self.drawline=drawline
        self.detailedmap = detailedmap
        self.selecteddetail=selecteddetail
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def dragMoveEvent(self, event):
        print(event)

    def mousePressEvent(self,event):
        print('pressed')

    def mouseMoveEvent(self,event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x()- orig_cursor_position.x()+ orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.QPos = QPointF(updated_cursor_x, updated_cursor_y)
        self.setPos(self.QPos)
        self.text.setPos(self.QPos)

    def mouseReleaseEvent(self,event):
        self.drawline()
        self.selecteddetail['selectedobjname']=self.text.toPlainText()
        self.detailedmap.selectedobj(self.text.toPlainText())

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