from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from Config import *

headers = ['File Name', 'Download?', 'Do Not Download?']

class AddedListModel(QAbstractTableModel):
    def __init__(self, changes, newframe):
        super(ConflictListModel, self).__init__()
        self.changes = changes
        self.currow=[]
        self.conflictdata = []
        self.conflictfilenames = []
        self.checks = {}
        self.newframe = newframe
        sortdict={}
        self.headers = headers
        for fileheader in self.changes:
            if fileadded in self.changes[fileheader]['reason']:
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