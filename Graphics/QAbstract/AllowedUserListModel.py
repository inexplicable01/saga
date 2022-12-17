
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import lorem

headers = [ 'Allowed Users']

class AllowedUserListModel(QAbstractTableModel):
    def __init__(self, alloweduser):
        super(AllowedUserListModel, self).__init__()

        self.alloweduser = alloweduser

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.alloweduser[index.row()]


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.alloweduser)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 1
        # if len(self.containdata)==0:
        #     return 0
        # else:
        #     return len(self.containdata[0])

    def listusers(self, alloweduserlist):

        self.alloweduser=alloweduserlist

        self.layoutChanged.emit()