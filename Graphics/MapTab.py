from Graphics.ContainerMap import ContainerMap
from Graphics.DetailedMap import DetailedMap
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import requests
from Config import BASE
import shutil
import json

import os
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from SagaApp.SagaUtil import getContainerInfo
from Graphics.PopUps.GanttChartPopUp import GanttChartPopUp
from SagaApp.Container import Container
from Graphics.Dialogs import ganttChartProject

class MapTab():
    def __init__(self, mainguihandle):
        self.index = 0

        self.detailsMapView = mainguihandle.detailsMapView
        self.containerMapView = mainguihandle.containerMapView
        # self.returncontlist = mainguihandle.returncontlist
        self.containerlisttable = mainguihandle.containerlisttable
        # self.generateContainerBttn = mainguihandle.generateContainerBttn
        self.mainguihandle = mainguihandle
        self.dlContainerBttn = mainguihandle.dlContainerBttn
        self.ganttbttn=mainguihandle.ganttbttn
        # self.ganttChartBttn = mainguihandle.ganttChartBttn

        # self.ganttChartBttn.clicked.connect(self.showGanttChart)
        # self.generateContainerBttn.clicked.connect(self.generateContainerMap)
        self.containerlisttable.clicked.connect(self.updatecontainertodl)
        self.dlContainerBttn.clicked.connect(self.downloadcontainer)
        self.ganttbttn.clicked.connect(self.showGanttChart)

        self.selecteddetail = {'selectedobjname': None}
        # self.returncontlist.clicked.connect(partial( mainguihandle.getContainerInfo,self.containerlisttable))

        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap = ContainerMap({}, self.containerMapView, self.selecteddetail, self.detailedmap,self.mainguihandle)
        # self.mainguihandle.tabWidget.currentChanged.connect(self.refreshMapTab)

    # def refreshMapTab(self):
    #     if self.mainguihandle.tabWidget.currentIndex() == self.mainguihandle.tabWidget.indexOf(self.mainguihandle.Map):

    def showGanttChart(self):
        self.ganttChart  = GanttChartPopUp(mainguihandle=self.mainguihandle)
        # self.ganttChart.showChart()

    def generateContainerMap(self,containerinfolist):
        self.containerlisttable.setModel(ContainerListModel(containerinfolist))
        self.containermap.reset()
        if 'EMPTY' in containerinfolist.keys():
            self.containermap.plot()
        else:
            for containerID in containerinfolist.keys():
                self.containermap.addActiveContainers(
                    Container.LoadContainerFromYaml(os.path.join('ContainerMapWorkDir', containerID , 'containerstate.yaml'))
                )

            self.containermap.editcontainerConnections()
            self.containermap.plot()
            self.detailedmap.passobj(self.containermap)

    def reset(self):
        self.containermap.reset()
        self.detailedmap.reset()
        self.containerlisttable.setModel(ContainerListModel({}))


    def updatecontainertodl(self, listtable):
        rownumber = listtable.row()
        index = listtable.model().index(rownumber, 0)
        containerId = listtable.model().data(index, 0)
        self.dlContainerBttn.setEnabled(True)
        self.dlContainerBttn.setText('Click to Download Container ' + containerId)
        self.dlcontainer = containerId

    def downloadcontainer(self):
        openDirectoryDialog =  QFileDialog().getExistingDirectory(self.mainguihandle, 'Select Folder Space to Place ' + self.dlcontainer
                                                                  + ' container folder.')
        if openDirectoryDialog:
            contdir = os.path.join(openDirectoryDialog, self.dlcontainer)
            if not os.path.exists(contdir):
                os.mkdir(contdir)
            else:
                print('Container exists already...removing')
                shutil.rmtree(contdir)
            dlcontainyaml = Container.downloadContainerInfo(openDirectoryDialog, self.mainguihandle.authtoken, BASE, self.dlcontainer)
            dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
            dlcontainer.downloadbranch('Main', BASE, self.mainguihandle.authtoken,contdir)
            dlcontainer.workingFrame.downloadfullframefiles()
            self.mainguihandle.maincontainertab.readcontainer(dlcontainyaml)
            self.mainguihandle.tabWidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
            # print(os.path.join(openDirectoryDialog, self.dlcontainer))
            if openDirectoryDialog:
                print(os.path.split(openDirectoryDialog[0]))


