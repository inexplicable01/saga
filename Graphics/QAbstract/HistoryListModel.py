from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time

headers = ['Rev', 'Commit Msg', 'Time']

class HistoryListModel(QAbstractTableModel):
    def __init__(self, historyinfodict):
        super(HistoryListModel, self).__init__()
        containdata=[]
        sortdict={}
        if len(historyinfodict.keys()) == 0:
            containdata.append(['Rev0', 'Container Not Yet Committed', ''])
        else:
            for rev, revdetails in historyinfodict.items():
                row = [rev, revdetails['commitmessage'] , time.ctime(revdetails['timestamp'])]
                sortdict[rev] = revdetails['timestamp']
                containdata.append(row)
            def mysort(element):
                return sortdict[element[0]]
            containdata.sort(key=mysort)

        self.containdata = containdata

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.containdata[index.row()][index.column()]


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.containdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.containdata[0])