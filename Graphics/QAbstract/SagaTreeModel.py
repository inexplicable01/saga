from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
import warnings
from SagaCore.Container import Container
from SagaGuiModel.GuiModelConstants import roleRequired, roleInput, roleOutput, colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED , CONTAINERFN,hexinputshades,hexblueshades
FOLDERITEMS = 'folderitems'
FOLDERNAME = 'foldername'


class SagaTreeNode(QAbstractItemModel):
    def __init__(self, data):
        QAbstractItemModel.__init__(self)
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)####is this listing the position index of the child relative to parent?
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)## ideally there should be a recusive
        ## second level child is setting the column count
        ## this is a nightmare.

headers=['FolderView','Incoming','OutGoing']

class SagaTreeModel(QAbstractItemModel):
    def __init__(self, containerinfodict, appdata_saga, sagaguimodel):
        QAbstractItemModel.__init__(self)
        self._root = SagaTreeNode(None)
        self.items=[]
        self.appdata_saga = appdata_saga
        self.sagaguimodel = sagaguimodel

        self.rowmapper = {}
        self.containerrows =[]

        def sortverticalline(fromcontainerrow, localfilerow, currentrow):
            fromcontainerbottom = fromcontainerrow > localfilerow
            if currentrow == localfilerow:
                return 'bottomhalf' if fromcontainerbottom else 'tophalf'
            elif currentrow == fromcontainerrow:
                return 'tophalf' if fromcontainerbottom else 'bottomhalf'
            else:
                return 'full'
        containers={}
        fullexpandedrow = 0
        for containerid, value in containerinfodict.items():
            icontainer = sagaguimodel.provideContainer(containerid)
            # containyaml = os.path.join(self.appdata_saga, 'ContainerMapWorkDir',containerid, CONTAINERFN)
            #
            # icontainer = Container.LoadContainerFromYaml(containyaml)
            containers[containerid] = icontainer
            self.items.append(SagaTreeNode([icontainer.containerName, fullexpandedrow, icontainer.containerId]))

            self.rowmapper[containerid] = fullexpandedrow
            # self.containerrows[fullexpandedrow] = containerid
            fullexpandedrow+=1
            for citemid, citem in icontainer.containeritems.items():
                self.items[-1].addChild(SagaTreeNode([citemid,fullexpandedrow,icontainer.containerId]))
                self.rowmapper[containerid+'_'+citemid] = fullexpandedrow
                fullexpandedrow += 1
                # self.items[-1].addChild(SagaTreeNode(['g', 'h', 'i']))
        # self.items[-1].addChild(SagaTreeNode(['there', 'is', 'hope']))
        # self.items[2]._children[1].addChild(SagaTreeNode(['d', 'e', 'f']))
        self.sectionconnection={}
        self.inputconnections={}
        self.outputconnections = {}
        for containerid, value in containerinfodict.items():
            icontainer:Container = containers[containerid]
            fileoutputs=[]
            containerinputids =[]
            for citemid, citem in icontainer.containeritems.items():
                if citem.containeritemrole== roleOutput:
                    fileoutputs.append(citemid)
                elif citem.containeritemrole== roleInput:
                    fromcontainerid = citem.refcontainerid
                    containerinputids.append(fromcontainerid)

            inputlinelength = {}
            inputlinecolor={}
            outputlinelength={}
            outputlinecolor = {}
            inputspaths = {'hori':{},'vert':{}}
            outputspaths = {'hori':{},'vert':{}}
            ipath=1
            opath=1
            # if 'Structures' == containerid:
            #     print('PartDesign')
            #     pass
            for citemid, citem in icontainer.containeritems.items():
                if citem.containeritemrole == roleInput:
                    fromcontainerid = citem.refcontainerid
                    fromcontainerrow=self.rowmapper[fromcontainerid]
                    localfilerow=self.rowmapper[containerid + '_' + citemid]
                    if fromcontainerid not in inputlinelength.keys():
                        inputlinelength[fromcontainerid]=ipath /(len(containerinputids)+1)
                        colori = 4 if (ipath-1)>4 else ipath-1
                        inputlinecolor[fromcontainerid] = hexinputshades[colori]
                        inputspaths['hori'][fromcontainerrow] = {'direc': 'left',
                                                                 'length': inputlinelength[fromcontainerid],
                                                                 'linetype': 'container',
                                                                 'hexcolor':inputlinecolor[fromcontainerid]
                                                                 }
                        ipath += 1
                    inputspaths['hori'][localfilerow] = {'direc': 'right',
                                                         'hexcolor': inputlinecolor[fromcontainerid],
                                                         'length': inputlinelength[fromcontainerid],
                                                         'linetype':'file'}
                    rowpair = [fromcontainerrow, localfilerow]
                    for row in range(min(rowpair),max(rowpair)+1):
                        if row in inputspaths['vert'].keys():
                            inputspaths['vert'][row]['xlocs'].append(inputlinelength[fromcontainerid])
                            inputspaths['vert'][row]['hexcolor'].append(inputlinecolor[fromcontainerid])
                            inputspaths['vert'][row]['length'].append(sortverticalline(fromcontainerrow, localfilerow, row))
                        else:
                            inputspaths['vert'][row] = {'xlocs': [inputlinelength[fromcontainerid]],
                                                        'length': [sortverticalline(fromcontainerrow, localfilerow, row)],
                                                        'hexcolor': [inputlinecolor[fromcontainerid]]}
                elif citem.containeritemrole == roleOutput:
                    localfilerow = self.rowmapper[containerid + '_' + citemid] ##as output, which get row number (Start of line)
                    outputlinelength[containerid+ '_' + citemid] = opath/(len(fileoutputs)+1)
                    coloro = 4 if (opath - 1) > 4 else opath-1
                    outputlinecolor[containerid + '_' + citemid] = hexblueshades[coloro]
                    outputspaths['hori'][localfilerow] = {'direc': 'right',
                                                           'length': outputlinelength[containerid+ '_' + citemid],
                                                          'hexcolor': outputlinecolor[containerid + '_' + citemid],
                                                          'linetype': 'file'}
                    if len(citem.refcontainerid)==0:
                        outputspaths['hori'][localfilerow]['length'] = 0.1
                        outputspaths['hori'][localfilerow]['direc'] = 'NoOutput'
                    for tocontainerid in citem.refcontainerid:
                        if tocontainerid not in self.rowmapper.keys():
                            continue
                        tocontainerrow = self.rowmapper[tocontainerid]
                        if tocontainerrow in outputspaths['hori'].keys():
                            if outputlinelength[containerid+ '_' + citemid] >outputspaths['hori'][tocontainerrow]['length']:
                                outputspaths['hori'][tocontainerrow]['length']=outputlinelength[containerid+ '_' + citemid]
                        else:
                            outputspaths['hori'][tocontainerrow]= {'direc': 'left',
                                                                 'length': outputlinelength[containerid+ '_' + citemid] ,
                                                                   'hexcolor':outputlinecolor[containerid+ '_' + citemid],
                                                                  'linetype': 'container'}
                        rowpair = [tocontainerrow, localfilerow]
                        for row in range(min(rowpair), max(rowpair) + 1):
                            if row in outputspaths['vert'].keys():
                                outputspaths['vert'][row]['xlocs'].append(outputlinelength[containerid+ '_' + citemid])
                                outputspaths['vert'][row]['length'].append(
                                    sortverticalline(tocontainerrow, localfilerow, row))
                                outputspaths['vert'][row]['hexcolor'].append(
                                    outputlinecolor[containerid + '_' + citemid])
                            else:
                                outputspaths['vert'][row] = {'xlocs': [outputlinelength[containerid+ '_' + citemid]],
                                                            'length': [
                                                                sortverticalline(tocontainerrow, localfilerow, row)],
                                                             'hexcolor': [outputlinecolor[containerid+ '_' + citemid]]}
                    opath+=1

            self.inputconnections[containerid] = inputspaths
            self.outputconnections[containerid] = outputspaths


        self.selectedrow = -1
        self.selectedcontainerid = None
        for node in self.items:
            self._root.addChild(node)

    def setSelectedRow(self, row:int):
        self.selectedrow = row
        self.layoutChanged.emit()

    def setSelectedContainer(self, containerid):
        self.selectedcontainerid = containerid
        self.layoutChanged.emit()
        # return self.sectionconnection[containerid]

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QModelIndex()

        child = parent.child(row)
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                # print('index',index.row(), index.column())
                # print('parent',p.row())
                return QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()### this ensures that only 2nd level child nodes set columnCount

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == Qt.DisplayRole:

            return node.data(index.column())
        return None

    # def reset(self):

