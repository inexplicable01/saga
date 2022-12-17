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
from Config import sourcecodedirfromconfig
from Graphics.PYQTView.ContainerDetailMap.FileRect import FileRect
from .ViewDefinitions  import *
from os.path import join

class ConnectionBox():

    # ConnectionBox is currently a generic class while containerBox inherits from QRects
# This is rather confusing and just not a very good structure  They should either both inherit from Qrects or both are just generic classes

    def __init__(self, containerscene, containerupstream:Container, containerdownstream:Container,containeridtoname,containerBoxHeight=containerBoxHeight, containerBoxWidth=containerBoxWidth):

        self.fileObj = []
        containerscene.addItem(ContainerBox(containerupstream, containerBoxWidth*-1.0, 0))
        containerscene.addItem(ContainerBox(containerdownstream, containerBoxWidth*gap , 0))
        idx=0
        for upcitemid, upcitem in containerupstream.containeritems.items():
            if upcitem.containeritemrole==roleOutput and set([containerdownstream.containerId]).issubset(set(upcitem.refcontainerid)):
                if containerdownstream.containeritems[upcitemid] and containerdownstream.containeritems[upcitemid].containeritemrole==roleInput:
                    self.fileObj.append(FileRect(None,
                                                 containerBoxWidth*-0.5,
                                                 idx,
                                                 citem=upcitem,
                                                 role='Connection',
                                                 containeridtoname= containeridtoname))
                    containerscene.addItem(self.fileObj[-1])
                    idx +=1
            if upcitem.containeritemrole == roleInput and upcitem.refcontainerid==containerdownstream.containerId:
                self.fileObj.append(FileRect(None,
                                             containerBoxWidth * -0.5,
                                             idx,
                                             citem=upcitem,
                                             role='Connection',
                                             containeridtoname=containeridtoname,
                                             flip=True))
                containerscene.addItem(self.fileObj[-1])
                idx += 1

        # self.containInBox.setRect(containerBoxWidth*-1.0, 0,  containerBoxWidth, 70 + idx * 100)

        # self.containoutBox.setRect(containerBoxWidth * gap, 0, containerBoxWidth, 70 + idx * 100)
        ##Quick Hack to size height of Container Box
        # self.setRect(0, 0, containerBoxWidth, 70 + idx * 100)

class ContainerBox(QGraphicsRectItem):
    def __init__(self, container:Container, topleftx, toplefty,
                 containerBoxHeight=containerBoxHeight,
                 containerBoxWidth=containerBoxWidth):
        super().__init__(topleftx, toplefty,  containerBoxWidth,containerBoxHeight)
        self.container=container

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        ##Draw Container Pic
        qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Container_Read.png"))
        picrect = QRectF(self.boundingRect().x(), self.boundingRect().y()+50, containerBoxWidth, containerBoxHeight-50)
        painter.drawImage(picrect, qpic)

        ##Draw Border
        painter.setPen(QPen(QBrush(Qt.black),4))
        painter.drawRect(self.boundingRect())

        ## Draw Container Text
        textrect = QRectF(self.boundingRect().x(), self.boundingRect().y()+10, containerBoxWidth, 24)
        painter.setFont(QFont("Helvetica",14))
        painter.drawText(textrect, Qt.AlignCenter, "Container : " + self.container.containerName)
