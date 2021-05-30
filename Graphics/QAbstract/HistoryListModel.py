from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from Config import typeRequired, typeInput, typeOutput, colorscheme

headers = ['Rev', 'Commit Msg', 'Time']

class HistoryListModel(QAbstractTableModel):
    def __init__(self, historyinfodict):
        super(HistoryListModel, self).__init__()
        self.currow=[]
        containdata=[]
        sortdict={}
        self.filetype=typeRequired
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

    def individualfilehistory(self,changesbyfile):
        filestatus={}
        for fileheader, changearr in changesbyfile.items():
            status='missing'
            filestatus[fileheader]=[]
            for irow, change in enumerate(changearr):
                if change['md5']=='missing':
                    continue
                else:
                    if status=='missing':
                        filestatus[fileheader].append(irow)
                        status = change['md5']
                    elif not status == change['md5']:
                        filestatus[fileheader].append(irow)
                        status = change['md5']

        self.filestatus=filestatus




    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.containdata[index.row()][index.column()]

        if role == Qt.BackgroundColorRole:
            if index.row() in self.currow:
                return QBrush(colorscheme[self.filetype])
            else:
                return QBrush(Qt.white)
                # if self.ganttdata[index.row()][index.column()]['outputchanged']:
                #     return QBrush(Qt.green)
                # else:


    def edithighlight(self, fileheader, type):

        if fileheader not in self.filestatus.keys():
            self.currow = []
        else:
            self.currow = self.filestatus[fileheader]
        self.filetype=type


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