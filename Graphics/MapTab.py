from Graphics.ContainerMap import ContainerMap
from Graphics.DetailedMap import DetailedMap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Config import BASE,  CONTAINERFN, colorscheme, typeRequired,typeInput,typeOutput, TEMPCONTAINERFN
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

def makeganttchartlegend(view):
    scene = QGraphicsScene()
    view.setScene(scene)
    # print(view.size())

    print(view.rect())
    rect = view.rect()
    w = rect.width()*1.2
    # w = option.rect.width()
    h = rect.height()*1.2

    hinternvals= h/4

    e = QGraphicsEllipseItem(0.0, 0.0, w/4, hinternvals*0.9)
    e.setBrush(QBrush(colorscheme[typeRequired], style = Qt.SolidPattern))
    scene.addItem(e)
    centertext = QGraphicsTextItem('No. of Commits')
    centertext.setPos(QPointF(w/4,0))

    scene.addItem(centertext)
    ## how many symbols

    topleft = QPointF(0,hinternvals)
    symbolrect = QRectF(QPointF(topleft),
                        QPointF(topleft+ QPointF(hinternvals * 0.9, hinternvals * 0.9)))
    r1 = QGraphicsRectItem(symbolrect)
    r1.setBrush(QBrush(colorscheme[typeOutput]))
    scene.addItem(r1)
    inputtext = QGraphicsTextItem('No. of Output Updates')
    inputtext.setPos(QPointF(w/4,hinternvals))
    scene.addItem(inputtext)

    topleft = QPointF(0,hinternvals*2)
    symbolrect = QRectF(QPointF(topleft),
                        QPointF(topleft+ QPointF(hinternvals * 0.9, hinternvals * 0.9)))
    r2 = QGraphicsRectItem(symbolrect)
    r2.setBrush(QBrush(colorscheme[typeInput]))
    scene.addItem(r2)
    outputtext = QGraphicsTextItem('No. of Input Updates')
    outputtext.setPos(QPointF(w/4,hinternvals*2))
    scene.addItem(outputtext)

    view.setBackgroundBrush(QBrush(Qt.gray, Qt.SolidPattern));

    #     w = option.rect.width()
    #     h = option.rect.height()
    #     ## how many symbols
    #
    #
    #
    #     painter.setPen(QPen(QBrush(Qt.black), 2))
    #     painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['outputchanged']))
    # painter.setPen(QPen(QBrush(Qt.transparent), 2))
    # painter.setBrush(QBrush(Qt.yellow))
    # painter.drawEllipse(symmidpoint, w * 0.4, h * 0.4)
    # painter.setPen(QPen(QBrush(Qt.black), 2))
    # painter.drawText(option.rect, Qt.AlignCenter, str(len(cellinfo['frames'])))

    # def drawoutputchangedsymbol(painter, option, cellinfo):

    #
    # def drawinputchangedsymbol(painter, option, cellinfo):
    #     w = option.rect.width()
    #     h = option.rect.height()
    #     ## how many symbols
    #     symmidpoint = option.rect.topLeft() + QPointF(w * 1 / 4, h / 2)
    #     symbolrect = QRectF(QPointF(symmidpoint + QPointF(-w * 0.08, -h * .2)),
    #                         QPointF(symmidpoint + QPointF(w * 0.08, h * 0.2)))
    #
    #     painter.setBrush(QBrush(colorscheme[typeOutput]))
    #     painter.drawRect(symbolrect)
    #     painter.setPen(QPen(QBrush(Qt.black), 2))
    #     painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['inputchanged']))
    #     # painter.drawRect(QRectF(midpoint, option.rect.topRight()))
    #
    # if len(cellinfo['frames']) > 0:



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
        self.ganttlegendview = mainguihandle.ganttlegendview
        self.networktabwidget =  mainguihandle.networktabwidget
        self.networktabwidget.setElideMode(Qt.ElideNone)
        self.containerlisttable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        makeganttchartlegend(self.ganttlegendview)



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
            self.gantttable.setModel(GanttListModel(containerinfodict, sagaguimodel.desktopdir))


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
        self.dlcontainername = containername


    def downloadcontainer(self):
        newcontparentdirpath =  QFileDialog().getExistingDirectory(self.mainguihandle, 'Select Folder Space to Place ' + self.dlcontainername
                                                                  + ' container folder.')
        if newcontparentdirpath:
            containerworkingdir = os.path.join(newcontparentdirpath, self.dlcontainername)
            if not os.path.exists(containerworkingdir):
                os.mkdir(containerworkingdir)###ATTENTION, Needs better error capture.
                containerworkingfolder, sagaguimodel.maincontainer = sagaguimodel.downloadContainer(containerworkingdir, self.dlcontainerid, 'WorkingContainer')##ATTENTION
                self.mainguihandle.maincontainertab.readcontainer(os.path.join(containerworkingdir,TEMPCONTAINERFN))  ###ATTENTION Should be calling Model and Gui ReSet
                self.mainguihandle.maintabwidget.setCurrentIndex(self.mainguihandle.maincontainertab.index)
            else:
                print('Container exists already...')
                # shutil.rmtree(contdir)



