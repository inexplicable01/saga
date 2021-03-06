from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Config import typeInput,typeOutput,typeRequired, colorscheme
import os

containerBoxHeight = 50
containerBoxWidth = 50
fileboxHeight = 50
fileboxWidth = 50
gap=0.1

typeindex = {typeInput: 0, typeOutput: 2, typeRequired: 1}


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

    def changeContainer(self, newcontainer:Container):
        self.curContainer = newcontainer

    def plot(self, changes):
        self.scene = QGraphicsScene()
        typecounter = {typeInput: 0, typeOutput: 0, typeRequired: 0}

        for fileheader, fileinfo in self.curContainer.FileHeaders.items():
            type = fileinfo['type']
            if type=='reference' or type=='references':
                continue
            change=None
            if fileheader in changes.keys():
                change = changes[fileheader]
            self.RectBox[fileheader] = coolerRectangle(100*typeindex[type] , 200 + 100*typecounter[type],  \
                                                       containerBoxWidth, containerBoxHeight,
                                                            type,self.curContainer , fileheader, self.guiHandle, self.view, change,\
                                                       self.curContainer.workingFrame.filestrack[fileheader].file_name)
            self.RectBox[fileheader].setPen(QPen(colorscheme[type]))
            self.RectBox[fileheader].text = fileheader

            self.scene.addItem(self.RectBox[fileheader])
            # self.scene.addItem(self.title[fileheader])
            typecounter[type] += 1
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



class coolerRectangle(QGraphicsRectItem):
    def __init__(self, xpos, ypos, xwidth, ywidth, \
                 type, curContainer, fileheader, guiHandle, view, change, filename):
        super().__init__(xpos, ypos, xwidth, ywidth)
        self.type = type
        self.point=QPoint(xpos,ypos)
        self.change = change
        self.guiHandle = guiHandle
        self.fileheader = fileheader
        self.curContainer = curContainer
        self.view = view
        self.filename = filename

    def mousePressEvent(self,event):
        print('pressed ' + self.type)
        self.guiHandle.coolerRectangleFeedback(self.type, self.view, self.fileheader , self.curContainer)
        print('filename ', self.filename)
        self.update()

    def boundingRect(self):

        return self.rect()

    def paint(self, painter:QPainter, option: QStyleOptionGraphicsItem, widget:QWidget=None):

        rect = self.boundingRect()
        additionalwidth = 100
        textRect = QRectF(rect.topLeft().x()-additionalwidth/2, rect.topLeft().y()+50, fileboxWidth+additionalwidth,20)
        picRect = QRectF(rect.topLeft().x(), rect.topLeft().y(), rect.width() / 2,rect.height() / 2)
        picRect.moveCenter(rect.center())

        # Draw type Background color
        if self.change:
            painter.setPen(QPen(QBrush(Qt.red), 4))
        else:
            painter.setPen(QPen(QBrush(colorscheme[self.type]), 4))
        painter.setBrush(QBrush(colorscheme[self.type]))
        painter.drawRect(rect)
        # Draw text
        painter.setPen(QPen(QBrush(Qt.black), 6))
        painter.drawText(textRect, Qt.AlignCenter, self.fileheader)
        # Draw Picture
        filename, file_extension = os.path.splitext(self.filename)
        print('file_extension',file_extension)
        if file_extension in ['.docx','.doc']:
            qpic = QImage('Graphics/FileIcons/Word.png')
        elif file_extension in ['.pptx','.ppt']:
            qpic = QImage('Graphics/FileIcons/ppticon.png')
        elif file_extension in ['.xls','.xlsx']:
            qpic = QImage('Graphics/FileIcons/excelicon.png')
        elif file_extension in ['.mp4']:
            qpic = QImage('Graphics/FileIcons/mp4icon.png')
        elif file_extension in ['.txt']:
            qpic = QImage('Graphics/FileIcons/txticon.png')
        else:
            qpic= QImage('Graphics/FileIcons/genericfile.png')
        painter.drawImage(picRect, qpic)


