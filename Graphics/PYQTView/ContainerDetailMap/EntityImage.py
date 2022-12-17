from PyQt5.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem , QWidget

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
from os.path import join
import os
from SagaGuiModel.GuiModelConstants import roleInput,roleOutput,roleRequired, colorscheme
from SagaCore.ContainerItem import ContainerItem
from Config import sourcecodedirfromconfig
from SagaCore.Track import FileTrack, FolderTrack

class EntityImage(QGraphicsRectItem):
    # self.pos() is built in function.  This is relative to parent item.
    # In our case, the parent Item is the Scene.
    # when the RectItem is initalized below on super().__init__, the coordinates are 0,0 because these are INTERNAL coordinates for the item
    # and INTERNAL coordinates are relative to the pos().   and pos() is relative to Scene origin
    # so for example is the rect.pos() is set to 20,10 and the internal coord is set to 3,7
    # once plotted, the top left coordinate of rectangle will be at 23, 17 relative to scene origin
    # Note that when you access self.pos() you will get 20,10 and self.rect.x(), you will get 3,7
    def __init__(self, idx,idy ,width,height,parent,citem:ContainerItem):
        super().__init__(idx, idy, width,height, parent=parent)  ## this sets scenepos.  Scenepos cannot be changed.
        self.setPos(parent.rect().topLeft())
        self.citem=citem
        self.width=width
        self.height=height
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def boundingRect(self):
        return self.rect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.drawRect(self.boundingRect())
        # Painter paints everything from self.pos(), meaning that if self.pos is 20,10, and you
        # give PAINTER coordinates of 0.0
        # Painter will paint at 20,10 RELATIVE to parent(which in our case is scene origin)


        # textRect =QRectF(rect.topLeft().x(), rect.topLeft().y()+self.height*0.7, self.width,self.height*0.3)
        #
        # painter.drawText(textRect,Qt.TextWrapAnywhere, self.citem.reftrack.entity)
        #
        # filename, file_extension = os.path.splitext(self.citem.reftrack.entity)
        #
        # if file_extension in ['.docx', '.doc']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Word.png"))
        # elif file_extension in ['.pptx', '.ppt']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "ppticon.png"))
        # elif file_extension in ['.xls', '.xlsx']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "excelicon.png"))
        # elif file_extension in ['.mp4']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "mp4icon.png"))
        # elif file_extension in ['.txt']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "txticon.png"))
        # elif file_extension in ['.pdf']:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "pdficon.png"))
        # else:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "genericfile.png"))
        #
        # if type(self.citem.reftrack) == FolderTrack:
        #     qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "foldericon.png"))
        #
        # # qpic= QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "genericfile.png"))
        # painter.drawImage(picrect, qpic)
        # painter.setPen(QPen(QBrush(Qt.transparent), 4))
        # painter.setBrush(QBrush(Qt.transparent))
        # painter.drawRect(rect)