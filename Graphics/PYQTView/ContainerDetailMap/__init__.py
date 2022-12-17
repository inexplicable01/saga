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
import os
import sys
import requests
import json
from os.path import join
import math
from Config import sourcecodedirfromconfig
from .ViewDefinitions import *


from Graphics.PYQTView.ContainerDetailMap.ConnectionBox import ConnectionBox
from Graphics.PYQTView.ContainerDetailMap.ContainerFlowBox import ContainerFlowBox

class ContainerDetailMap():
    def __init__(self,detailsMapView, selecteddetail):
        self.detailsMapView=detailsMapView
        self.selecteddetail= selecteddetail
        self.containerscene = QGraphicsScene()
        self.textholder = self.containerscene.addText('Select a Container or Connection')
        self.textholder.setDefaultTextColor(Qt.black)
        self.textholder.setPos(QPointF(0,0))
        self.viewitems={}

        self.detailsMapView.setScene(self.containerscene)

    def reset(self):
        self.containerscene = QGraphicsScene()
        self.detailsMapView.setScene(self.containerscene)

    def selectedobj(self,selectedobjname, containeridtoname):
        self.containerscene = QGraphicsScene()
        self.selecteddetail['selectedobjname'] = selectedobjname

        if '_' in selectedobjname:
            [containerId_in, containerId_out] = selectedobjname.split('_')
            # print(containerId_in,containerId_out)
            ConnectionBox(self.containerscene,\
                             self.activeContainers[containerId_in],self.activeContainers[containerId_out], containeridtoname)
            # containerupstream = self.activeContainers[containerId_in]
            # containerdownstream = self.activeContainers[containerId_out]
            #
            # # self.containInBox = QGraphicsRectItem(containerBoxWidth * -1.0, 0, containerBoxWidth,
            # #                                       containeritemrectheight)
            # # self.containInBox.setPen(Qt.black)
            # self.containerscene.addItem(self.containInBox)
            # containerintext = QGraphicsTextItem(containerupstream.containerName, parent=self.containInBox)
            # containerintext.setPos(self.containInBox.rect().topLeft())
            # containerintext.setDefaultTextColor(Qt.black)
        else:
            # print(selectedobjname)
            self.containerscene.addItem( \
                ContainerFlowBox(self.containerscene,self.activeContainers[selectedobjname], containeridtoname))
        self.detailsMapView.setScene(self.containerscene)

    def passobj(self, containmap):
        self.activeContainers=containmap.activeContainers