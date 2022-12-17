from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import lorem

headers = [ 'ContainerName', 'Rev Count', 'Container Description']

class ContainerListModel(QAbstractTableModel):
    def __init__(self, containerinfodict):
        super(ContainerListModel, self).__init__()
        containdata=[]
        containeridindex=[]
        containernametoid={}
        for containerid, containvalue in containerinfodict.items():
            containernametoid[containvalue['ContainerDescription']]=containerid
            for branch in containvalue['branches']:
                if branch['name']=='Empty':
                    continue
                row = [ containvalue['containerdict']['containerName'],
                       branch['revcount'],
                        containvalue['containerdict']['description']
                     # lorem.sentence()
                        ]
                containdata.append(row)
                containeridindex.append(containerid)
        self.containeridindex=containeridindex
        self.containernametoid=containernametoid
        self.containerinfodict = containerinfodict
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
        if len(self.containdata)==0:
            return 0
        else:
            return len(self.containdata[0])