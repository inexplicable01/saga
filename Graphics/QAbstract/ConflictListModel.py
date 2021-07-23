from PyQt5.QtWidgets import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from datetime import datetime
from SagaApp.FrameStruct import Frame
from Config import SERVERFILEADDED,SERVERNEWREVISION, colorscheme, SERVERFILEDELETED, UPDATEDUPSTREAM

headers = ['File Name', 'Overwrite', 'Download Copy']
headersadded = ['File Name', 'Download', 'Do Not Download?']
headersdeleted = ['File Name', 'Delete', 'Do Not Delete?']

class ConflictListModel(QAbstractTableModel):
    def __init__(self, changes, newframe):
        super().__init__()
        self.changes = changes
        self.currow=[]
        self.conflictdata = []
        self.conflictfilenames = []
        self.checkcolumns = [1, 2]
        self.checks = {}
        self.newframe = newframe
        sortdict={}
        self.headers = headers
        for fileheader in self.changes:
            if SERVERNEWREVISION in self.changes[fileheader]['reason']:
                self.conflictdata.append(fileheader)
                self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)
        if index.column() in [1,2]:
            fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return fl

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole and col == 0:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.conflictfilenames[row]
        elif role == Qt.CheckStateRole and col in self.checkcolumns:
            return self.checkState(QPersistentModelIndex(index))
        elif role == Qt.BackgroundColorRole:
            if index.row() in self.currow:
                return QBrush(colorscheme[self.filetype])
            else:
                return QBrush(Qt.white)
                # if self.ganttdata[index.row()][index.column()]['outputchanged']:
                #     return QBrush(Qt.green)
                # else:

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.conflictdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 3


class AddedListModel(QAbstractTableModel):
    def __init__(self, changes, newframe):
        super().__init__()
        self.changes = changes
        self.currow=[]
        self.conflictdata = []
        self.conflictfilenames = []
        self.checkcolumns = [1,2]
        self.checks = {}
        self.newframe = newframe
        sortdict={}
        self.headers = headersadded
        for fileheader in self.changes:
            if SERVERFILEADDED in self.changes[fileheader]['reason']:
                self.conflictdata.append(fileheader)
                self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)
        if index.column() in self.checkcolumns:
            fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return fl

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole and col == 0:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.conflictfilenames[row]
        elif role == Qt.CheckStateRole and col in [1,2]:
            return self.checkState(QPersistentModelIndex(index))
        elif role == Qt.BackgroundColorRole:
            if index.row() in self.currow:
                return QBrush(colorscheme[self.filetype])
            else:
                return QBrush(Qt.white)
                # if self.ganttdata[index.row()][index.column()]['outputchanged']:
                #     return QBrush(Qt.green)
                # else:

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.conflictdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 3

class DeletedListModel(QAbstractTableModel):
    def __init__(self, changes, newframe:Frame, workingframe:Frame):
        super().__init__()
        self.changes = changes
        self.currow=[]
        self.conflictdata = []
        self.conflictfilenames = []
        self.checkcolumns = [1, 2]
        self.workingframe = workingframe
        self.checks = {}
        self.newframe = newframe
        sortdict={}
        self.headers = headersdeleted
        for fileheader in self.changes:
            if SERVERFILEDELETED in self.changes[fileheader]['reason']:
                self.conflictdata.append(fileheader)
                self.conflictfilenames.append(self.workingframe.filestrack[fileheader].file_name)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)
        if index.column() in self.checkcolumns:
            fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return fl

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole and col == 0:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.conflictfilenames[row]
        elif role == Qt.CheckStateRole and col in [1,2]:
            return self.checkState(QPersistentModelIndex(index))
        elif role == Qt.BackgroundColorRole:
            if index.row() in self.currow:
                return QBrush(colorscheme[self.filetype])
            else:
                return QBrush(Qt.white)
                # if self.ganttdata[index.row()][index.column()]['outputchanged']:
                #     return QBrush(Qt.green)
                # else:

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.conflictdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 3

class UpstreamListModel(QAbstractTableModel):
    def __init__(self, changes):
        super().__init__()
        self.changes = changes
        self.checks = {}
        self.checkcolumns = [4]
        self.upstreamfileupdate=[]
        self.conflictdata = []
        self.headers = ['File Name','Upstream Container + Rev','Upstream Commit Message', 'Commit Time', 'ReplaceInput']
        for fileheader in self.changes:

            if UPDATEDUPSTREAM in self.changes[fileheader]['reason']:
                self.conflictdata.append(fileheader)
                self.upstreamfileupdate.append({'frame':changes[fileheader]['inputframe'],
                                                'fileheader':fileheader,
                                                'fromcontainer':changes[fileheader]['fromcontainer']
                                                })

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)
        if index.column() in self.checkcolumns :
            fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return fl

    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            upstreamframe = self.upstreamfileupdate[row]['frame']
            fileheader = self.upstreamfileupdate[row]['fileheader']
            fromcontainer= self.upstreamfileupdate[row]['fromcontainer']
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            if col==0:
                return upstreamframe.filestrack[fileheader].file_name
            elif col==1:
                return fromcontainer.containerName + ' @ ' + upstreamframe.FrameName
            elif col==2:
                return upstreamframe.commitMessage
            elif col == 3:
                return datetime.utcfromtimestamp(upstreamframe.commitUTCdatetime).strftime('%m/%d/%y  %H:%M')
                # return self.upstreamupdated[row][col]
        elif role == Qt.CheckStateRole and col in self.checkcolumns:
            return self.checkState(QPersistentModelIndex(index))
        elif role == Qt.BackgroundColorRole:
            # if index.row() in self.currow:
            #     return QBrush(colorscheme[self.filetype])
            # else:
            return QBrush(Qt.white)
                # if self.ganttdata[index.row()][index.column()]['outputchanged']:
                #     return QBrush(Qt.green)
                # else:

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.upstreamfileupdate)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 5