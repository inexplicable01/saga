from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Graphics.ContainerPlot import ContainerPlot
from Graphics.QAbstract.GanttListModel import GanttListModel
from SagaApp.FileObjects import FileTrack
from Config import typeInput,typeRequired,typeOutput
from SagaGuiModel import sagaguimodel
import os
import sys
import requests
import json
from Config import BASE

class RotatedHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super(RotatedHeaderView, self).__init__(Qt.Horizontal, parent)
        self.setMinimumSectionSize(20)

    def paintSection(self, painter, rect, logicalIndex ):
        painter.save()
        # translate the painter such that rotate will rotate around the correct point
        painter.translate(rect.x()+rect.width(), rect.y())
        painter.rotate(90)
        # and have parent code paint at this location
        # newrect = QRect(0-rect.width()/2,-20,rect.height(),rect.width())
        newrect = QRect(0 ,0, rect.height(), rect.width())
        super(RotatedHeaderView, self).paintSection(painter, newrect, logicalIndex)
        painter.restore()

    def minimumSizeHint(self):
        size = super(RotatedHeaderView, self).minimumSizeHint()
        size.transpose()
        return size

    def sectionSizeFromContents(self, logicalIndex):
        size = super(RotatedHeaderView, self).sectionSizeFromContents(logicalIndex)
        size.transpose()
        return size

class GanttChartPopUp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Graphics/UI/ganttchart.ui", self)
        # self.containerpathlbl.setText(path)


        self.ganttview.clicked.connect(self.updateCommitMessages)

        self.ganttview.setModel(GanttListModel(sagaguimodel.containernetworkkeys, sagaguimodel.desktopdir))
        self.ganttview.setHorizontalHeader(RotatedHeaderView(self.ganttview))
        # delegate = Delegate(self.ganttview)
        # self.ganttview.setItemDelegate(delegate)
        self.exec()

    def updateCommitMessages(self,listtable):
        rownumber = listtable.row()
        weeksago = listtable.model().rowheaders[rownumber]
        columnnumber = listtable.column()
        containerid = listtable.model().headers[columnnumber]
        # print(listtable.model().commitmessagedict[weeksago][containerid])
        str=''
        if weeksago in listtable.model().commitmessagedict.keys():
            if containerid in listtable.model().commitmessagedict[weeksago].keys():
                for commitsummary in listtable.model().commitmessagedict[weeksago][containerid]:
                    str = str + commitsummary['msg'] + '\n'

        # columnnumber = listtable.column()
        # index = listtable.model().index(rownumber, 0)
        # containerId = listtable.model().data(index, 0)
        self.commitmsglbl.setText(str)
