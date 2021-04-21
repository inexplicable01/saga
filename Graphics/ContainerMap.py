from PyQt5.QtWidgets import *
from PyQt5 import uic
import math
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from SagaApp.Container import Container
from Config import typeInput,typeOutput,typeRequired, colorscheme,mapdetailstxt,RECTMARGINpx
from math import pi
import os

rectheight = 40
rectwidth = 40

class ContainerMap():
    def __init__(self, activeContainers, qtview, selecteddetail,detailedmap, mainguihandle):
        self.activeContainers = activeContainers  # contain the container objs
        self.qtview = qtview
        self.selecteddetail=selecteddetail
        self.detailedmap=detailedmap
        self.activeContainersObj={} # contain the Rect objects
        self.containerscene = QGraphicsScene()
        self.qtview.setScene(self.containerscene)
        self.containerConnections = {} # dictionary of Id: list of OD
        self.containerConnectLines={}  # dictionary of lineId:LineObject
        self.mainguihandle=mainguihandle
        self.mapdet={'containerlocations':{}}
        self.sectionid=''



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
        try:
            self.sectionid=self.mainguihandle.userdata['sectionid']
            self.mapdetailtxt = os.path.join(self.mainguihandle.guiworkingdir, 'SagaGuiData', self.sectionid,
                                             mapdetailstxt)
            with open(self.mapdetailtxt , 'r') as mapdets:
                self.mapdet = yaml.load(mapdets, Loader=yaml.FullLoader)
        except Exception as e:
            print('could not load map data for world map')
        idx,idy=1,1
        gridsize = math.ceil(math.sqrt(len(self.activeContainers.values())))
        for containerid, container in self.activeContainers.items():
            if  containerid not in  self.mapdet['containerlocations'].keys():
                xloc = idx * 100
                yloc = idy * 100
                self.mapdet['containerlocations'][containerid]={'xloc':xloc,'yloc':yloc}# initialize
            else:
                xloc=self.mapdet['containerlocations'][containerid]['xloc']
                yloc=self.mapdet['containerlocations'][containerid]['yloc']
            self.activeContainersObj[container.containerId]=containerRect(xloc,yloc,container, \
                                                                          self)
            self.containerscene.addItem(self.activeContainersObj[container.containerId])
            idx +=1
            if idx>gridsize:
                idx, idy = 1, idy + 1
        self.drawline()

    def updatemapcoord(self,containerid, QPos):
        self.mapdet['containerlocations'][containerid]['xloc']=QPos.x()
        self.mapdet['containerlocations'][containerid]['yloc']=QPos.y()
        with open(self.mapdetailtxt ,'w') as file:
            yaml.dump(self.mapdet, file)


margin =40

class containerRect(QGraphicsRectItem):
    def __init__(self, idx,idy,container:Container,containermaphandle,rectheight=rectheight, rectwidth=rectwidth):
        super().__init__(0,0, rectheight, rectwidth)
        # self.rectheight = rectheight
        # self.rectwidth = rectwidth
        self.QPos = QPointF(idx,idy)
        self.setPos(self.QPos)
        self.setBrush(QBrush(Qt.transparent))
        self.setPen(QPen(Qt.black))
        self.containerName = container.containerName
        self.containerid = container.containerId
        # self.text.setPos(self.QPos)
        self.activeContainersObj = containermaphandle.activeContainersObj
        self.drawline=containermaphandle.drawline
        self.detailedmap = containermaphandle.detailedmap
        self.selecteddetail=containermaphandle.selecteddetail
        self.updatemapcoord=containermaphandle.updatemapcoord
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def dragMoveEvent(self, event):
        print(event)

    def mousePressEvent(self,event):
        print('Pressed')

    def boundingRect(self):
        return self.rect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        rect = self.boundingRect()
        additionalwidth = 100
        textRect = QRectF(rect.topLeft().x() - additionalwidth / 2, rect.topLeft().y() + rectheight,
                          rectwidth+ additionalwidth, 20)
        picRect = QRectF(rect.topLeft().x(), rect.topLeft().y(), rectwidth , rectheight )
        # picRect.moveCenter(rect.center())

        # Draw type Background color
        painter.setPen(QPen(QBrush(Qt.white), 4))
        painter.setBrush(QBrush(Qt.white))
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
        self.QPos =QPointF(updated_cursor_x, updated_cursor_y)
        # self.QPos = QPointF(updated_cursor_position.x(), updated_cursor_position.y())
        self.setPos(self.QPos)
        self.update()
        # self.text.setPos(self.QPos)

    def mouseReleaseEvent(self,event):
        self.drawline()

        self.selecteddetail['selectedobjname']=self.containerName
        self.detailedmap.selectedobj(self.containerName)

        for containerid, rect in self.activeContainersObj.items():
            if containerid==self.containerid:
                continue
            if self.collidesWithItem(rect):
                # print('herewego')
                delta = self.pos()-rect.pos()
                xtomove = rectwidth - delta.x() if delta.x() > 0 else -1 * (rectheight + delta.x())
                ytomove= rectheight - delta.y() if delta.y()>0 else -1*(rectheight + delta.y())
                if abs(xtomove)>abs(ytomove):
                    newpos = self.pos() + QPointF(0, (abs(ytomove)+RECTMARGINpx)*abs(ytomove)/ytomove)
                else:
                    newpos = self.pos() + QPointF((abs(xtomove)+RECTMARGINpx)*abs(xtomove)/xtomove, 0)

                self.setPos(newpos)
        self.updatemapcoord(self.containerid, self.QPos)

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


    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setPen(QPen(QBrush(Qt.blue), 3))
        painter.drawLine(self.line())
        # p1 = self.line().center()
        # p2 = p1 + QPointF(0,10)
        # p3 = p1 + QPointF(10,0)
        # self.line()

        a = (self.line().angle()+90)/180.0*pi
        p1 = self.line().center() + QPointF(5*math.cos(a),-5*math.sin(a))
        b = (self.line().angle()+270)/180.0*pi
        p2 = self.line().center() + QPointF(5*math.cos(b),-5*math.sin(b))
        c = self.line().angle()/180.0*pi
        p3 = self.line().center() + QPointF(10 * math.cos(c), -10 * math.sin(c))
        # if 'ContainerC_WaichakContainer'==self.lineid:
            # print(self.lineid, self.line().angle())
        # arrowP1 = self.line().center() + QPointF(sin(angle + M_PI / 3) * arrowSize,
        #                                 cos(angle + M_PI / 3) * arrowSize);
        # QPointF
        # arrowP2 = line().p1() + QPointF(sin(angle + M_PI - M_PI / 3) * arrowSize,
        #                                 cos(angle + M_PI - M_PI / 3) * arrowSize);

        arrowcoord = QPolygonF([p1,p2,p3])
        painter.setBrush(QBrush(Qt.blue))
        painter.drawPolygon(arrowcoord)
        arrowSize = 20;
        additionalwidth = 100
    # def mouseReleaseEvent(self,event):
    #     # self.drawline()
    #     # self.selecteddetail['selectedobjname']=self.text.toPlainText()
    #     # self.detailedmap.selectedobj(self.text.toPlainText())
    #     print(self.lineid)