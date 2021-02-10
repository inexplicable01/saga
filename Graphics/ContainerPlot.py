from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Config import typeInput,typeOutput,typeRequired


containerBoxHeight = 50
containerBoxWidth = 50
gap=0.1

class ContainerPlot():
    def __init__(self, guiHandle, view, container:Container,  rectmousepressmethod=''):

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

    def plot(self):
        self.scene = QGraphicsScene()
        typeindex = {typeInput: 0, typeOutput: 2, typeRequired: 1}
        typecounter = {typeInput: 0, typeOutput: 0, typeRequired: 0}
        colorscheme = {typeInput: Qt.yellow, typeOutput: Qt.green, typeRequired: Qt.blue}
        for fileheader, fileinfo in self.curContainer.FileHeaders.items():
            type = fileinfo['type']
            if type=='reference' or type=='references':
                continue
            self.RectBox[fileheader] = coolerRectangle(100*typeindex[type] , 200 + 75*typecounter[type],  \
                                                       containerBoxWidth, containerBoxHeight,
                                                            type,self.curContainer , fileheader, self.guiHandle, self.view)
            self.RectBox[fileheader].setPen(QPen(colorscheme[type]))
            self.RectBox[fileheader].text = fileheader
            self.title[fileheader] = QGraphicsTextItem(fileheader)
            self.title[fileheader].setPos(QPoint(100*typeindex[type] , 200 + 75*typecounter[type]))
            self.scene.addItem(self.RectBox[fileheader])
            self.scene.addItem(self.title[fileheader])
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
                 type, curContainer, fileheader, guiHandle, view):
        super().__init__(xpos, ypos, xwidth, ywidth)
        self.type = type
        self.qtext = QGraphicsTextItem(type)
        self.qtext.setPos(QPoint(xpos,ypos))
        self.guiHandle = guiHandle
        self.fileheader = fileheader
        self.curContainer = curContainer
        self.view = view
        # self.mainGuiHandle=mainGuiHandle

    def mousePressEvent(self,event):
        print('pressed ' + self.type)
        if self.view == self.guiHandle.refContainerView:
            if self.type == typeOutput:
                # self.definefiletype('Input', self.containerName, self.fileheader)
                self.guiHandle.inputFileButton.setEnabled(True)
                self.guiHandle.removeFileButton.setEnabled(False)
                self.guiHandle.editFileButton.setEnabled(False)
            else:
                self.guiHandle.inputFileButton.setEnabled(False)
                self.guiHandle.removeFileButton.setEnabled(True)
                self.guiHandle.editFileButton.setEnabled(True)
            self.guiHandle.curfileheader = self.fileheader
            self.guiHandle.selectedContainer = self.curContainer
            self.guiHandle.curfiletype=self.type
            # self.guiHandle.tester.setText(self.guiHandle.filetype)
        elif self.view == self.guiHandle.curContainerView:
            self.guiHandle.editDeleteButtons(self.type, self.curContainer.containername, self.fileheader)