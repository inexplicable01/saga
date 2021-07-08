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

containerRectWidth=100
containerRectHeight=100
cont_imgheight=50
cont_imgwidth=50
fontsize=10
contmargin = 25
textmargin = 2

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
        self.activeContainers={}

    def drawline(self):
        for containerId_in, containerId_outlist in self.containerConnections.items():
            for containerId_out in containerId_outlist:
                lineid = containerId_in + '_' + containerId_out
                if lineid not in self.containerConnectLines:
                    Q1 = self.activeContainersObj[containerId_in].containercenter()
                    Q2 = self.activeContainersObj[containerId_out].containercenter()
                    self.containerConnectLines[lineid] = containerLine(Q1,Q2,lineid, self.detailedmap)
                    self.containerscene.addItem(self.containerConnectLines[lineid])
                else:
                    Q1 = self.activeContainersObj[containerId_in].containercenter()
                    Q2 = self.activeContainersObj[containerId_out].containercenter()
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
            self.sectionid=self.mainguihandle.userdata['current_sectionid']
            self.mapdetailtxt = os.path.join(self.mainguihandle.guiworkingdir, 'SagaGuiData', self.sectionid,
                                             mapdetailstxt)
            with open(self.mapdetailtxt , 'r') as mapdets:
                self.mapdet = yaml.load(mapdets, Loader=yaml.FullLoader)
        except Exception as e:
            print('could not load map data for world map')
        idx,idy=0,0
        gridsize = math.ceil(math.sqrt(len(self.activeContainers.values())))
        for containerid, container in self.activeContainers.items():
            if  containerid not in  self.mapdet['containerlocations'].keys():
                xloc = idx * containerRectWidth ## this number should be related to the size of the containericon instead of hard coded
                yloc = idy * containerRectHeight
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

        ##Setting a 0,0 for understanding.  Delete this for production
        self.containerscene.addRect(QRectF(-2,-2,4,4),QPen(Qt.black),QBrush(Qt.black))


    def updatemapcoord(self,containerid, QPos):
        self.mapdet['containerlocations'][containerid]['xloc']=QPos.x()
        self.mapdet['containerlocations'][containerid]['yloc']=QPos.y()
        with open(self.mapdetailtxt ,'w') as file:
            yaml.dump(self.mapdet, file)


margin =40


## Need to set the containerRect to emcompass both the container image and the text
## Setting the Text to only reach two letters beyond the container img.
##

class containerRect(QGraphicsRectItem):
    # self.pos() is built in function.  This is relative to parent item.
    # In our case, the parent Item is the Scene.
    # when the RectItem is initalized below on super().__init__, the coordinates are 0,0 because these are INTERNAL coordinates for the item
    # and INTERNAL coordinates are relative to the pos().   and pos() is relative to Scene origin
    # so for example is the rect.pos() is set to 20,10 and the internal coord is set to 3,7
    # once plotted, the top left coordinate of rectangle will be at 23, 17 relative to scene origin
    # Note that when you access self.pos() you will get 20,10 and self.rect.x(), you will get 3,7
    def __init__(self, idx,idy,container:Container,containermaphandle,cont_imgheight=cont_imgheight, cont_imgwidth=cont_imgwidth):
        super().__init__(0,0, cont_imgheight+2*contmargin, cont_imgwidth+2*contmargin) ## this sets scenepos.  Scenepos cannot be changed.
        self.cont_imgheight = cont_imgheight
        self.cont_imgwidth = cont_imgwidth
        # self.QPos = QPointF(idx,idy)  #self.scenePos() or is it pos().... built in function does same thing
        self.setPos(QPointF(idx,idy))
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

    def containercenter(self):
        return QPointF(self.pos().x() + containerRectWidth/2,self.pos().y() + containerRectHeight/2)


    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        # Painter paints everything from self.pos(), meaning that if self.pos is 20,10, and you
        # give PAINTER coordinates of 0.0
        # Painter will paint at 20,10 RELATIVE to parent(which in our case is scene origin)
        rect = self.boundingRect()
        textRect = QRectF(textmargin, contmargin+cont_imgheight,containerRectWidth-textmargin*2, 15)
        contRect = QRectF(contmargin, contmargin, cont_imgwidth , cont_imgheight )
        # contRect = self.boundingRect()
        # Draw type Background color
        painter.setPen(QPen(QBrush(Qt.transparent), 4))
        painter.setBrush(QBrush(Qt.transparent))
        painter.drawRect(rect)

        # Draw text
        # pxwidth = QFontMetrics(QFont("times", fontsize)).width()
        def producedotdotdotstring(text, pxlimit, fontfamily, fontsize):
            pxwidthoftext = QFontMetrics(QFont(fontfamily, fontsize)).width(text)
            indx=-1
            if QFontMetrics(QFont("times", fontsize)).width('...') > pxlimit:
                print('fontsize for knowledge network container text is set too large.  Str ... functionality failed.')
                return text
            if pxwidthoftext>pxlimit:
                while pxwidthoftext>pxlimit:
                    dottext = text[0:indx] + '...'#needs to add dots to string
                    pxwidthoftext = QFontMetrics(QFont("times", fontsize)).width(dottext)
                    indx+=-1
                return dottext
            else:
                return text

        containerdisplayname= producedotdotdotstring(self.containerName, textRect.width(), "times", fontsize)
        painter.setPen(QPen(QBrush(Qt.black), 1))
        painter.drawText(textRect, Qt.AlignCenter, containerdisplayname)
        painter.setBrush(QBrush(Qt.transparent))
        # painter.drawRect(textRect)
        # Draw Picture
        qpic = QImage('Graphics/FileIcons/Container.png')
        # print(contRect)
        painter.drawImage(contRect, qpic)


    def mouseMoveEvent(self,event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        deltamoved = updated_cursor_position- orig_cursor_position  #this measured how much the item has been moved
        ## the reason why it has to be delta instead of straight on using event point is because you don't know where on the item you clicked
        ##  You COULD calculated the delta between item 0,0 versus here you clicked but see, a delta is needed
        # deltamoved_y = updated_cursor_position.y() - orig_cursor_position.y()#+ orig_position.y()
        self.setPos(deltamoved+self.pos())
        # self.mapFromScene
        self.update()
        # self.text.setPos(self.QPos)

    def mouseReleaseEvent(self,event):
        self.selecteddetail['selectedobjname']=self.containerName
        self.detailedmap.selectedobj(self.containerName)
        for containerid, rectitem in self.activeContainersObj.items():
            if containerid==self.containerid:
                continue
            if self.collidesWithItem(rectitem):
                delta = self.pos()-rectitem.pos()
                xtomove = containerRectWidth - delta.x() if delta.x() > 0 else -1 * (containerRectWidth + delta.x())
                ytomove= containerRectHeight - delta.y() if delta.y()>0 else -1*(containerRectHeight + delta.y())
                if abs(xtomove)>abs(ytomove):
                    newpos = self.pos() + QPointF(0, (abs(ytomove)+RECTMARGINpx)*abs(ytomove)/ytomove)
                else:
                    newpos = self.pos() + QPointF((abs(xtomove)+RECTMARGINpx)*abs(xtomove)/xtomove, 0)

                self.setPos(newpos)
        self.updatemapcoord(self.containerid, self.pos())
        self.drawline()
        self.update()

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
        painter.setPen(QPen(QBrush(QColor(92, 85, 233)), 3))
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