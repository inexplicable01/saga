from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

headers = ['Email']

class UserListModel(QAbstractTableModel):
    def __init__(self, allowedUser):
        super(UserListModel, self).__init__()
        userdata=[]
        for email in allowedUser:
            userdata.append([email])
        self.userdata = userdata

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.userdata[index.row()][index.column()]

    def adduser(self, newemail):
        self.userdata.append([newemail])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
            # return 'Column {}'.format(section + 1)
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.userdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.userdata[0])

    def userlist(self):
        userlist=[]
        for line in self.userdata:
            userlist.append(line[0])
        return userlist