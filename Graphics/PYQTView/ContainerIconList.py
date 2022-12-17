from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaCore.Frame import Frame
from SagaCore.Track import FileTrack,FolderTrack
from SagaCore.Container import Container
from SagaGuiModel.GuiModelConstants import roleInput,roleOutput,roleRequired, colorscheme, UPDATEDUPSTREAM, MD5CHANGED, DATECHANGED
from Config import  sourcecodedirfromconfig
import os
from os.path import join

containerBoxHeight = 50
containerBoxWidth = 50
fileboxHeight = 50
fileboxWidth = 50
gap=0.1
cont_imgheight=50
cont_imgwidth=50


typeindex = {roleInput: 0, roleOutput: 2, roleRequired: 1}


class ContainerPlot():
    def __init__(self, guiHandle, view, container:Container=None,  rectmousepressmethod=''):

        # self.containerName = containerName
        # self.path = framePath
        self.scene = QGraphicsScene()
        self.guiHandle = guiHandle
        self.view = view
        self.curContainer = container
        self.RectBox = {}
        self.title = {}
        self.rectmousepressmethod = rectmousepressmethod
        self.view.setScene(self.scene)

        rectItem = QGraphicsRectItem
        rectItem.origMousePress = rectItem.mousePressEvent
        # rectItem.mousePressEvent = addFileMousePressA

    def setContainer(self, curContainer:Container):
        self.curContainer = curContainer

    def reset(self):
        self.view.setScene(QGraphicsScene())

    def plot(self, changes):
        self.scene.clear()
        rolecounter = {roleInput: 0, roleOutput: 0, roleRequired: 0}
        for citemid, citem in self.curContainer.containeritems.items():
            role = citem.containeritemrole
            type = citem.containeritemtype
            if role=='reference' or role=='references':
                continue
            change=None
            if citemid in changes.keys():
                change = changes[citemid]
            self.RectBox[citemid] = FileViewItemRect(150*typeindex[role] , 200 + 150*rolecounter[role],  \
                                                       containerBoxWidth, containerBoxHeight,
                                                            role, type, self.curContainer , citemid, citem, self.guiHandle, self.view, change,\
                                                       self.curContainer.refframe.filestrack[citemid])
            # self.RectBox[fileheader].setPen(QPen(colorscheme[type]))
            # self.RectBox[fileheader].text = fileheader
            self.scene.addItem(self.RectBox[citemid])
            rolecounter[role] += 1


        self.view.setScene(self.scene)

    def removeRect(self, header):
        self.scene.removeItem(self.RectBox[header])
        self.scene.removeItem(self.title[header])
        del self.RectBox[header]
        del self.title[header]
        self.view.setScene(self.scene)

    def editRect(self, headerOrig, headerNew):
        self.scene.removeItem(self.RectBox[headerOrig])
        self.scene.removeItem(self.title[headerOrig])
        self.RectBox[headerNew] = self.RectBox.pop(headerOrig)
        self.RectBox[headerNew].text = headerNew
        self.title[headerNew] = self.title.pop(headerOrig)
        pos = self.title[headerNew].pos()
        self.title[headerNew] = QGraphicsTextItem(headerNew)
        self.title[headerNew].setPos(pos)


class FileViewItemRect(QGraphicsRectItem):
    # self.pos() is built in function.  This is relative to parent item.
    # In our case, the parent Item is the Scene.
    # when the RectItem is initalized below on super().__init__, the coordinates are 0,0 because these are INTERNAL coordinates for the item
    # and INTERNAL coordinates are relative to the pos().   and pos() is relative to Scene origin
    # so for example is the rect.pos() is set to 20,10 and the internal coord is set to 3,7
    # once plotted, the top left coordinate of rectangle will be at 23, 17 relative to scene origin
    # Note that when you access self.pos() you will get 20,10 and self.rect.x(), you will get 3,7
    def __init__(self, xpos, ypos, xwidth, ywidth, \
                 role, type, curContainer, citemid, citem ,guiHandle, view, change, filetrack):
        # cont_imgheight = 50
        # cont_imgwidth = 50
        # + 2 * cont_imgheight+ 2 * cont_imgwidth
        super().__init__(xpos, ypos, 2.5*xwidth, 1.8*ywidth)
        self.role = role
        self.type = type
        self.citem = citem
        self.point=QPoint(xpos,ypos)
        self.change = change
        self.guiHandle = guiHandle
        self.citemid = citemid
        self.curContainer = curContainer
        self.view = view
        self.xwidth=xwidth
        self.ywidth = ywidth
        # self.entity = filetrack.entity
        self.filetrack = filetrack
        # print(filetrack.ctnrootpath)

    def mousePressEvent(self,event):
        self.guiHandle.FileViewItemRectFeedback(self.role, self.view, self.citemid,self.citem, self.curContainer, self.type)
        self.update()

    def boundingRect(self):
        return self.rect()

##Paint handles the actual drawing of the rect
    def paint(self, painter:QPainter, option: QStyleOptionGraphicsItem, widget:QWidget=None):
        # xmargin = 10% of xwidth  , xwidth and ywidth are dimensions of picrect
        # left of picrect is center - 1/2 of ywidth
        # the FileViewItemRect is 1.2x xwdith and 2x ywidth
        rect = self.boundingRect()
        # additionalwidth = 100
        textRect = QRectF(rect.topLeft().x()+self.xwidth*0.1, rect.topLeft().y()+self.ywidth*1.1, self.xwidth*2.5,self.ywidth*0.7)
        picRect = QRectF(rect.center().x()-self.xwidth*0.5,
                         rect.topLeft().y()+self.ywidth*0.1, self.xwidth,self.ywidth)
        # picRect.moveCenter(rect.center())

        # Draw role Background color
        if self.change:
            if len(self.change['reason'])==1:
                painter.setPen(QPen(QBrush(colorscheme[self.change['reason'][0]]), 4))
            else:
                painter.setPen(QPen(QBrush(Qt.yellow), 4))
        else:
            painter.setPen(QPen(QBrush(colorscheme[self.role]), 4))
        painter.setBrush(QBrush(colorscheme[self.role]))
        painter.drawRect(rect)
        # Draw text
        if self.role==roleOutput:
            painter.setPen(QPen(QBrush(Qt.white), 6))
        else:
            painter.setPen(QPen(QBrush(Qt.black), 6))
        painter.drawText(textRect, Qt.TextWrapAnywhere, self.filetrack.entity)
        # Draw Picture
        filename, file_extension = os.path.splitext(self.filetrack.entity)

        if file_extension in ['.docx','.doc']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Word.png"))
        elif file_extension in ['.pptx','.ppt']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "ppticon.png"))
        elif file_extension in ['.xls','.xlsx']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "excelicon.png"))
        elif file_extension in ['.mp4']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "mp4icon.png"))
        elif file_extension in ['.txt']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "txticon.png"))
        elif file_extension in ['.pdf']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "pdficon.png"))
        else:
            qpic= QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "genericfile.png"))

        if type(self.filetrack)==FolderTrack:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "foldericon.png"))
        painter.drawImage(picRect, qpic)




