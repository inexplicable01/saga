from Graphics.ContainerMap import ContainerMap
from Graphics.DetailedMap import DetailedMap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Config import BASE,  CONTAINERFN
from Graphics.GuiUtil import RotatedHeaderView
import shutil

import os
# from tester import CustomModel, CustomNode
from Graphics.QAbstract.SagaTreeDelegate import SagaTreeDelegate
from Graphics.QAbstract.SagaTreeModel import SagaTreeModel, SagaTreeNode
from Graphics.QAbstract.ContainerListModel import ContainerListModel
# from Graphics.PopUps.GanttChartPopUp import GanttChartPopUp
from Graphics.QAbstract.GanttListModel import GanttListModel, GanttListDelegate
    # GanttListDelegate
from SagaApp.Container import Container
from SagaGuiModel import sagaguimodel

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
        # self.ganttbttn=mainguihandle.ganttbttn
        self.sagatreeview=mainguihandle.sagatreeview
        self.gantttable = mainguihandle.gantttable
        self.commitmsglbl = mainguihandle.commitmsglbl


        # self.ganttChartBttn = mainguihandle.ganttChartBttn
        # self.ganttChartBttn.clicked.connect(self.showGanttChart)
        # self.generateContainerBttn.clicked.connect(self.generateContainerMap)
        self.containerlisttable.clicked.connect(self.updatecontainertodl)
        self.dlContainerBttn.clicked.connect(self.downloadcontainer)
        # self.ganttbttn.clicked.connect(self.showGanttChart)
        # self.sagatreemodel = SagaTreeModel()
        self.sagatreeviewcolumnmoved = False

        # self.sagatreeview.expandAll()
        # self.sagatreeview.setColumnWidth(0,200)
        self.sagatreeview.header().setSectionResizeMode(QHeaderView.Stretch)

        self.selecteddetail = {'selectedobjname': None}

        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap = ContainerMap({}, self.containerMapView, self.selecteddetail, self.detailedmap,self.mainguihandle)
        # self.mainguihandle.tabWidget.currentChanged.connect(self.refreshMapTab)
        self.gantttable.clicked.connect(self.updateCommitMessages)
        self.gantttable.setHorizontalHeader(RotatedHeaderView(self.gantttable))
        self.gantttable.setItemDelegate(GanttListDelegate())



    def updateCommitMessages(self, listtable):
        containerid= listtable.model().containerheaders[listtable.row()]
        weeksago= listtable.model().weeksdictlist[listtable.column()]
        # print(listtable.model().commitmessagedict[weeksago][containerid])
        str = '\n'.join(listtable.model().commitmessagedict[weeksago][containerid]['msg'])

        # columnnumber = listtable.column()
        # index = listtable.model().index(rownumber, 0)
        # containerId = listtable.model().data(index, 0)
        self.commitmsglbl.setText(str)
    # def refreshMapTab(self):
    #     if self.mainguihandle.tabWidget.currentIndex() == self.mainguihandle.tabWidget.indexOf(self.mainguihandle.Map):

    # def showGanttChart(self):
    #     self.ganttChart  = GanttChartPopUp()
    #     # self.ganttChart.showChart()

    # class GanttChartPopUp(QDialog):
    #     def __init__(self):
    #         super().__init__()
    #         # uic.loadUi("Graphics/UI/ganttchart.ui", self)
    #         # self.containerpathlbl.setText(path)
    #
    #
    #         # delegate = Delegate(self.gantttable)
    #         # self.gantttable.setItemDelegate(delegate)
    #         self.exec()

    def generateContainerMap(self,containerinfodict):
        self.containerlisttable.setModel(ContainerListModel(containerinfodict))
        self.containermap.reset()
        if 'EMPTY' in containerinfodict.keys():
            self.containermap.plot()
        else:
            for containerID in containerinfodict.keys():
                self.containermap.addActiveContainers(
                    Container.LoadContainerFromYaml(os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerID , 'containerstate.yaml'))
                )
            self.containermap.editcontainerConnections()
            self.containermap.plot()
            self.detailedmap.passobj(self.containermap)
            self.gantttable.setModel(GanttListModel(sagaguimodel.containernetworkkeys, sagaguimodel.desktopdir))


    def generateSagaTree(self, containerinfodict):
        self.sagatreeview.setModel(SagaTreeModel(containerinfodict, sagaguimodel.desktopdir))
        self.sagatreeview.setItemDelegate(SagaTreeDelegate())
        self.sagatreeview.clicked.connect(self.sagatreeclicked)
        if not self.sagatreeviewcolumnmoved:
            self.sagatreeview.header().moveSection(1, 0)
            self.sagatreeviewcolumnmoved = True
        print(self.sagatreeview.header())
        self.sagatreeview.setItemsExpandable(True)

    def sagatreeclicked(self, index):
        # print(index.row(), index.column(), index.internalPointer().data(0))
        # index.internalPointer.setSelected(True)
        index.model().setSelectedRow(index.internalPointer().data(1))
        index.model().setSelectedContainer(index.internalPointer().data(2))
        # ind = index.model().index(0,0, index.model()._root.index() )
        self.sagatreeview.collapseAll()
        self.sagatreeview.expand(index)
        # self.sagatreeview.expand(index)


    def reset(self):
        self.containermap.reset()
        self.detailedmap.reset()
        self.containerlisttable.setModel(ContainerListModel({}))

        # self.gantttable.setHorizontalHeader(RotatedHeaderView(self.gantttable))

    def updatecontainertodl(self, listtable):
        rownumber = listtable.row()
        index = listtable.model().index(rownumber, 1)
        containername = listtable.model().data(index, 0)
        self.dlContainerBttn.setEnabled(True)
        self.dlContainerBttn.setText('Click to Download Container ' + containername)
        index = listtable.model().index(rownumber, 0)
        self.dlcontainerid = listtable.model().data(index, 0)


    def downloadcontainer(self):
        openDirectoryDialog =  QFileDialog().getExistingDirectory(self.mainguihandle, 'Select Folder Space to Place ' + self.dlcontainerid
                                                                  + ' container folder.')
        if openDirectoryDialog:
            contdir = os.path.join(openDirectoryDialog, self.dlcontainerid)
            if not os.path.exists(contdir):
                os.mkdir(contdir)
            else:
                print('Container exists already...removing')
                shutil.rmtree(contdir)
            dlcontainyaml = Container.downloadContainerInfo(openDirectoryDialog, sagaguimodel.authtoken, BASE, self.dlcontainerid)
            dlcontainer = Container.LoadContainerFromYaml(containerfn=dlcontainyaml)
            dlcontainer.downloadbranch('Main', BASE, sagaguimodel.authtoken,contdir)
            dlcontainer.workingFrame.downloadfullframefiles()
            self.mainguihandle.maincontainertab.readcontainer(dlcontainyaml)
            self.mainguihandle.centralwidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
            # # print(os.path.join(openDirectoryDialog, self.dlcontainer))
            # if openDirectoryDialog:
            #     print(os.path.split(openDirectoryDialog[0]))



