from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime

headers = [ 'Email', 'Active']

class ProfileListModel(QAbstractTableModel):
    def __init__(self, profilelist):
        super(ProfileListModel, self).__init__()
        profiledata = []

        for email, profile in profilelist.items():
            if profile['exptimestamp']:
                if profile['exptimestamp']>datetime.now().timestamp():
                    status = 'Click to Sign In, token valid until ' + datetime.fromtimestamp(profile['exptimestamp']).strftime('%m/%d/%y  %H:%M')
                else:
                    status = 'Please re-sign in.'
                profiledata.append([email, status])
        self.profilelist=profilelist
        self.profiledata = profiledata

    def authtokenfromemail(self, email):
        return self.profilelist[email]['authtoken']

    def exptimestampfromemail(self, email):
        return self.profilelist[email]['exptimestamp']

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.profiledata[index.row()][index.column()]


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.profiledata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self.profiledata)==0:
            return 0
        else:
            return len(self.profiledata[0])