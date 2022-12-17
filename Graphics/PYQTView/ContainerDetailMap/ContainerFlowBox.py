from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from SagaCore.Frame import Frame
from SagaCore.Container import Container
from SagaGuiModel.GuiModelConstants import roleInput,roleOutput,roleRequired, colorscheme
from SagaCore.Track import FileTrack, FolderTrack
from SagaCore.ContainerItem import ContainerItem
from .FileRect import FileRect
from .ViewDefinitions import *
from os.path import join
from Config import sourcecodedirfromconfig

# containeritemrectheight = 61
# containerBoxWidth = 300
# gap=0.1


class ContainerFlowBox(QGraphicsRectItem):
    def __init__(self, containerscene,container:Container,containeridtoname,
                 containeritemrectheight=containeritemrectheight,
                 containerBoxWidth=containerBoxWidth):
        super().__init__(0, 0,  containerBoxWidth,containeritemrectheight)
        # self.containeritemrectheight = containeritemrectheight
        # self.containerBoxWidth = containerBoxWidth
        # self.QPos = QPointF(50,50)
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black))
        self.containertitle=container.containerId
        self.containerscene = containerscene

        titletext = QGraphicsTextItem('Container : ' + container.containerName,parent=self)
        titletext.setTextWidth(self.boundingRect().width())
        titletext.document().setDefaultTextOption(QTextOption(Qt.AlignCenter))
        titletext.setFont(QFont("Times",16))
        titletext.setDefaultTextColor(Qt.black)

        inputlbl = QGraphicsTextItem('Input', parent=self)
        inputlbl.setDefaultTextColor(Qt.black)
        inputlbl.setPos(QPointF(15,40))

        outputlbl = QGraphicsTextItem('Output', parent=self)
        outputlbl.setDefaultTextColor(Qt.black)
        outputlbl.setPos(QPointF(self.rect().width()/2+ 15,40))


        self.crossbox={}
        # self.outputbox = {}
        rolecounter = {roleInput: 0, roleOutput: 0}
        loc = {roleInput: -1, roleOutput: 1}
        if container.containeritems:
            for citemid, citem in container.containeritems.items():
                role = citem.containeritemrole
                if role in [roleInput, roleOutput]:
                    # print(fileheader)
                    self.crossbox[citemid] = FileRect(parent=self, locF=(containerBoxWidth + 40) * loc[role] / 2,
                                                         idx=rolecounter[role], \
                                                         citem=citem, role=role, containeridtoname=containeridtoname)

                    rolecounter[role]+=1

        ##Quick Hack to size height of Container Box
        if max(rolecounter.values()) * filerectboxheight<containerBoxWidth:
            boxheight = containerBoxWidth
        else:
            boxheight = max(rolecounter.values()) * filerectboxheight
        self.boxheight = boxheight
        self.setRect(0, 0,  containerBoxWidth, boxheight+70)


    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Container_Read.png"))
        picrect = QRectF(self.boundingRect().x(), self.boundingRect().y()+70, self.boundingRect().width(), containerBoxWidth)
        painter.drawImage(picrect, qpic)
        painter.setPen(QPen(QBrush(Qt.black),4))
        painter.drawRect(self.boundingRect())










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
#     self.setRect(self.locF, 60 + self.idx * 100, containerBoxWidth * (1 + self.boxgap), containeritemrectheight * self.fileCount)
#     self.upbox[fileheader] = QGraphicsRectItem(containerBoxWidth*0.1,10 ,containerBoxWidth*0.25,40,self)
#     self.upbox[fileheader].setPos(self.rect().topLeft())
#     self.upbox[fileheader].moveBy(0,(containeritemrectheight/2 * self.fileCount))
#     self.upboxtext[fileheader] =QGraphicsTextItem(fileheader, parent=self.upbox[fileheader])
#     self.upboxtext[fileheader].setPos(self.upbox[fileheader].rect().topLeft())
# def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
#     QPainter.drawRoundedRect()

# def dragMoveEvent(self, event):
#     print(event)
#
# def mousePressEvent(self, event):
#     print('List')
#
# def mouseMoveEvent(self, event):
#     orig_cursor_position = event.lastScenePos()
#     updated_cursor_position = event.scenePos()
#     orig_position = self.scenePos()
#     updated_cursor_x = updated_cursor_position.x()- orig_cursor_position.x()+ orig_position.x()
#     updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
#     self.setPos(QPointF(updated_cursor_x, updated_cursor_y))
    # self.text.setPos(self.QPos)
    # self.setFlag(QGraphicsItem.ItemIsMovable, True)