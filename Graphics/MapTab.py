from Graphics.PYQTView.ContainerVerse import ContainerMap
# from Graphics.PYQTView.DetailedMap import DetailedMap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from SagaGuiModel.GuiModelConstants import TEMPCONTAINERFN
from Graphics.GuiUtil import RotatedHeaderView

import os
# from tester import CustomModel, CustomNode
from Graphics.QAbstract.SagaTreeDelegate import SagaTreeDelegate
from Graphics.QAbstract.SagaTreeModel import SagaTreeModel
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.AllowedUserListModel import AllowedUserListModel
from Graphics.PYQTView.ContainerDetailMap import ContainerDetailMap
# from Graphics.PopUps.GanttChartPopUp import GanttChartPopUp
from Graphics.QAbstract.GanttListModel import GanttListModel, GanttListDelegate
    # GanttListDelegate
from SagaGuiModel import sagaguimodel


class MapTab():
    def __init__(self, mainguihandle):
        self.index = 0
        self.detailsMapView = mainguihandle.detailsMapView
        self.containerMapView = mainguihandle.containerMapView
        # self.returncontlist = mainguihandle.returncontlist
        self.containerlisttable = mainguihandle.containerlisttable
        self.allowedusertable = mainguihandle.allowedusertable
        # self.generateContainerBttn = mainguihandle.generateContainerBttn
        self.mainguihandle = mainguihandle
        self.dlContainerBttn = mainguihandle.dlContainerBttn
        # self.ganttbttn=mainguihandle.ganttbttn
        self.sagatreeview=mainguihandle.sagatreeview
        self.gantttable = mainguihandle.gantttable
        self.commitmsglbl = mainguihandle.commitmsglbl
        self.ganttlegendview = mainguihandle.ganttlegendview
        self.networktabwidget =  mainguihandle.networktabwidget
        self.networktabwidget.setElideMode(Qt.ElideNone)
        self.containerlisttable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.allowedusertable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.ganttChartBttn = mainguihandle.ganttChartBttn
        # self.ganttChartBttn.clicked.connect(self.showGanttChart)
        # self.generateContainerBttn.clicked.connect(self.generateContainerMap)
        self.containerlisttable.clicked.connect(self.updatecontainertodl)
        self.dlContainerBttn.clicked.connect(self.downloadcontainer)
        # self.ganttbttn.clicked.connect(self.shoFwGanttChart)
        # self.sagatreemodel = SagaTreeModel()
        self.sagatreeviewcolumnmoved = False
        # self.sagatreeview.expandAll()
        # self.sagatreeview.setColumnWidth(0,200)
        self.sagatreeview.header().setSectionResizeMode(QHeaderView.Stretch)
        self.selecteddetail = {'selectedobjname': None}
        ###########Gui Variables##############
        self.detailedmap = ContainerDetailMap(self.detailsMapView, self.selecteddetail)
        self.containermap = ContainerMap({}, self.containerMapView, self.selecteddetail, self.detailedmap,self.mainguihandle)
        # self.mainguihandle.tabWidget.currentChanged.connect(self.refreshMapTab)
        self.gantttable.clicked.connect(self.updateCommitMessages)
        self.gantttable.setHorizontalHeader(RotatedHeaderView(self.gantttable))
        self.gantttable.setItemDelegate(GanttListDelegate())

        self.allowedusertable.setModel(AllowedUserListModel([]))

    def updateCommitMessages(self, listtable):
        containername= listtable.model().containerheaders[listtable.row()]
        containerid = listtable.model().containernametoid[containername]
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
        # print('generateContainerMap start ' + datetime.now().isoformat())
        self.containerlisttable.setModel(ContainerListModel(containerinfodict))
        self.containermap.reset()
        if 'EMPTY' in containerinfodict.keys():
            self.containermap.plot()
        else:
            # print('generateContainerMap loadcontstart ' + datetime.now().isoformat())
            for containerid in containerinfodict.keys():
                self.containermap.addActiveContainers(sagaguimodel.provideContainer(containerid))
            # print('generateContainerMap loadcont end  ' + datetime.now().isoformat())
            self.containermap.editcontainerConnections()
            # print('1  ' + datetime.now().isoformat())
            self.containermap.plot()
            # print('2  ' + datetime.now().isoformat())
            self.detailedmap.passobj(self.containermap)
            # print('3  ' + datetime.now().isoformat())
            self.gantttable.setModel(GanttListModel(containerinfodict, sagaguimodel))
        # print('generateContainerMap end ' + datetime.now().isoformat())


    def generateSagaTree(self, containerinfodict):
        # print('SagaTree start ' + datetime.now().isoformat())
        self.sagatreeview.setModel(SagaTreeModel(containerinfodict, sagaguimodel.appdata_saga, sagaguimodel))
        self.sagatreeview.setItemDelegate(SagaTreeDelegate())
        self.sagatreeview.clicked.connect(self.sagatreeclicked)
        if not self.sagatreeviewcolumnmoved:
            self.sagatreeview.header().moveSection(1, 0)
            self.sagatreeviewcolumnmoved = True
        # print(self.sagatreeview.header())
        self.sagatreeview.setItemsExpandable(True)
        # print('SagaTree end ' + datetime.now().isoformat())

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
        # self.allowedusertable.setModel(AllowedUserListModel({}))
        self.sagatreeview.setModel(SagaTreeModel({}, sagaguimodel.appdata_saga, sagaguimodel))
        self.sagatreeviewcolumnmoved = False
        self.gantttable.setModel(GanttListModel({}, sagaguimodel))
        # self.gantttable.setHorizontalHeader(RotatedHeaderView(self.gantttable))

    def updatecontainertodl(self, listtable):
        rownumber = listtable.row()
        index = listtable.model().index(rownumber, 0)
        containername = listtable.model().data(index, 0)
        self.dlContainerBttn.setEnabled(True)
        self.dlContainerBttn.setText('Click to Download Container ' + containername)
        index = listtable.model().index(rownumber, 0)
        # self.dlcontainerid = listtable.model().data(index, 0)
        self.dlcontainername = containername
        # listtable.model().containeridindex[rownumber]
        self.dlcontainerid = listtable.model().containernametoid[containername]
        # print(listtable.model().containeridindex[rownumber])
        containerid = listtable.model().containeridindex[rownumber]
        # print(listtable.model().containerinfodict[id])
        # print(listtable.model().containerinfodict[id]['containerdict']['containerName'])
        self.allowedusertable.model().listusers(listtable.model().containerinfodict[containerid]['containerdict']['allowedUser'])
        print(listtable.model().containerinfodict[containerid]['containerdict']['allowedUser'])
        self.dlContainerBttn.setEnabled(True)
        self.dlContainerBttn.setText('Click to Download Container ' + containername)
        self.dlcontainerid = containerid
        self.dlcontainername = containername
        self.detailedmap.selectedobj(containerid, self.containermap.containeridtoname)
        # self.allowedusertable


    def downloadcontainer(self):
        newcontparentdirpath =  QFileDialog().getExistingDirectory(self.mainguihandle, 'Select Folder Space to Place ' + self.dlcontainername
                                                                  + ' container folder.')
        if newcontparentdirpath:
            containerworkingdir = os.path.join(newcontparentdirpath, self.dlcontainername)

            if sagaguimodel.folderHasContainer(containerworkingdir) or \
                    sagaguimodel.folderHasContainer(newcontparentdirpath) or  \
                    os.path.exists(containerworkingdir):
                self.mainguihandle.errout('Container exists in location already.  Container download canceled.')
            else:
                os.mkdir(containerworkingdir)###ATTENTION, Needs better error capture.
                sagaguimodel.downloadContainer(containerworkingdir, self.dlcontainerid, ismaincontainer=True)##ATTENTION
                self.mainguihandle.maincontainertab.readcontainer(os.path.join(containerworkingdir,TEMPCONTAINERFN))  ###ATTENTION Should be calling Model and Gui ReSet
                self.mainguihandle.maintabwidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)




