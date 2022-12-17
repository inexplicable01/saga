from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from SagaGuiModel.GuiModelConstants import  colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED
from SagaCore import roleInput, roleOutput,roleRequired



class HistoryListModel(QAbstractTableModel):
    ## Model for Main Container Gannt chart,
    def __init__(self, historyinfodict):
        super(HistoryListModel, self).__init__()
        self.currow=[]
        self.filetype=roleRequired
        if len(historyinfodict.keys()) == 0:
            self.initiatilized = False
            self.containdata= []
            self.citemnamelist=[]
            self.revheaders=[]
        else:
            self.initiatilized = True
            self.revheaders, self.containdata, self.citemnamelist = self.sorthistory(historyinfodict)

    def load(self, historyinfodict):
        self.currow = []
        self.filetype = roleRequired
        if len(historyinfodict.keys()) == 0:
            self.initiatilized = False
            self.containdata= []
            self.citemnamelist=[]
            self.revheaders=[]
        else:
            self.initiatilized = True
            self.revheaders, self.containdata, self.citemnamelist = self.sorthistory(historyinfodict)
        self.layoutChanged.emit()




    def sorthistory(self,historyinfodict):
        sortdict = {}
        revheaders = []
        containdata=[]
        for rev, revdetails in historyinfodict.items():
            sortdict[rev] = revdetails['timestamp']
            revheaders.append(rev)
        self.commitmsg = []
        citemidlist = []


        def mysort(element):
            return sortdict[element]  ## sortdict[element] returns timestamp
        # revheaders.sort loops through each element.  element1 goes into mysort. key takes in a method.
        # mysort accepts element1 and returns timestamp1, e2 timestamp2 etc.   and sorts in roder the timestamps.
        # This way, you can through in some complex functions to tailer to the sorting.

        revheaders.sort(key=mysort)
        citemnamelist=[]
        for revs in historyinfodict.keys():
            # citemidlist =  historyinfodict[revs]['frame'].filestrack.keys() + citemidlist
            citemidlist = citemidlist + list(
                set(historyinfodict[revs]['frame'].filestrack.keys()) - set(citemidlist))
            citemnamelist = citemnamelist + list(
                set(historyinfodict[revs]['frame'].provideEntityNames()) - set(citemnamelist))
        blahdict = {}

        for citemid in citemidlist:
            blahdict[citemid] = []
            for revi, rev in enumerate(revheaders):  ## Rev headers already sorted by timestamp
                self.commitmsg.append(historyinfodict[rev]['frame'].commitMessage)
                if citemid in historyinfodict[rev]['frame'].filestrack.keys():
                    ## if rev has citemid,  we need to find out whether it was just created
                    if revi == 0:  ## assumes first rev is history dict is rev1
                        status = JUSTCREATED
                    else:  ## if it exists, and not Rev1, first check if it exists in last rev
                        if citemid in historyinfodict[revheaders[revi - 1]][
                            'frame'].filestrack.keys():  ## if citemid exists in last rev
                            previousmd5 = historyinfodict[revheaders[revi - 1]]['frame'].filestrack[citemid].md5
                            thismd5 = historyinfodict[rev]['frame'].filestrack[citemid].md5
                            if thismd5 != previousmd5:
                                status = MD5CHANGED
                            else:
                                status = UNCHANGED
                        else:  # Doesn't exist in last rev, so just created
                            status = JUSTCREATED
                    if revi == (len(revheaders) - 1):  ## latest rev
                        existsInNext = True  ## just assumes it exists in the next rev.
                    else:  ### not latest rev
                        if citemid in historyinfodict[revheaders[revi + 1]]['frame'].filestrack.keys():
                            existsInNext = True
                        else:
                            existsInNext = False
                    md5 = historyinfodict[rev]['frame'].filestrack[citemid].md5
                    type = historyinfodict[rev]['frame'].filestrack[citemid].containeritemrole
                    entity = historyinfodict[rev]['frame'].filestrack[citemid].entity
                else:
                    md5 = None
                    type = None
                    status = None
                    existsInNext = None
                blahdict[citemid].append({"md5": md5, "type": type, "status": status, "existsInNext": existsInNext, 'entity':entity})

        for citemid in citemidlist:
            row = blahdict[citemid]
            containdata.append(row)

        return revheaders, containdata, citemnamelist

    def individualfilehistory(self,changesbyfile):
        filestatus={}
        for citemname, changearr in changesbyfile.items():
            status='missing'
            filestatus[citemname]=[]
            for irow, change in enumerate(changearr):
                if change['md5']=='missing':
                    continue
                else:
                    if status=='missing':
                        filestatus[citemname].append(irow)
                        status = change['md5']
                    elif not status == change['md5']:
                        filestatus[citemname].append(irow)
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


    def edithighlight(self, citemname, type):

        if citemname not in self.filestatus.keys():
            self.currow = []
        else:
            self.currow = self.filestatus[citemname]
        self.filetype=type


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.revheaders[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self.citemnamelist[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        if self.initiatilized:
            return len(self.containdata)
        else:
            return 0

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self.containdata)>0:
            return len(self.containdata[0])
        else:
            return 0

    def reset(self):

        self.containdata = []
        self.citemidlist = []
        self.revheaders = []
        self.layoutChanged.emit()
