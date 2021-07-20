from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from Config import typeRequired, typeInput, typeOutput, colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED



class HistoryListModel(QAbstractTableModel):
    def __init__(self, historyinfodict):
        super(HistoryListModel, self).__init__()
        self.currow=[]
        self.fileheaderlist=[]
        containdata=[]
        sortdict={}
        self.filetype=typeRequired
        if len(historyinfodict.keys()) == 0:
            containdata.append([ 'Container Not Yet Committed'])
            self.fileheaderlist=['Null']
            self.revheaders=['Null']
        else:
            revheaders = []
            for rev, revdetails  in historyinfodict.items():
                sortdict[rev] = revdetails['timestamp']
                revheaders.append(rev)
            def mysort(element):
                return sortdict[element]
            revheaders.sort(key=mysort)
            self.revheaders = revheaders
            # sortdict[rev] = revdetails['timestamp']
            # containdata.append(row)
            # def mysort(element):
            #     return sortdict[element[0]]
            # containdata.sort(key=mysort)
            self.commitmsg=[]
            fileheaderlist = []
            for revs in historyinfodict.keys():
                # fileheaderlist =  historyinfodict[revs]['frame'].filestrack.keys() + fileheaderlist
                fileheaderlist = fileheaderlist + list(set(historyinfodict[revs]['frame'].filestrack.keys() )-set(fileheaderlist))
            blahdict={}
            for fileheader in fileheaderlist:
                blahdict[fileheader] = []
                for revi,rev in enumerate(revheaders):  ## Rev headers already sorted by timestamp
                    self.commitmsg.append(historyinfodict[rev]['frame'].commitMessage)
                    if fileheader in historyinfodict[rev]['frame'].filestrack.keys():
                        ## if rev has fileheader,  we need to find out whether it was just created
                        if revi==0: ## assumes first rev is history dict is rev1
                            status = JUSTCREATED
                        else:  ## if it exists, and not Rev1, first check if it exists in last rev
                            if fileheader in historyinfodict[revheaders[revi-1]]['frame'].filestrack.keys(): ## if fileheader exists in last rev
                                previousmd5 =historyinfodict[revheaders[revi-1]]['frame'].filestrack[fileheader].md5
                                thismd5=historyinfodict[rev]['frame'].filestrack[fileheader].md5
                                if thismd5!=previousmd5:
                                    status = MD5CHANGED
                                else:
                                    status=UNCHANGED
                            else:# Doesn't exist in last rev, so just created
                                status = JUSTCREATED
                        if revi==(len(revheaders)-1):## latest rev
                            existsInNext = True  ## just assumes it exists in the next rev.
                        else:### not latest rev
                            if fileheader in historyinfodict[revheaders[revi+1]]['frame'].filestrack.keys():
                                existsInNext=True
                            else:
                                existsInNext=False
                        md5 = historyinfodict[rev]['frame'].filestrack[fileheader].md5
                        type = historyinfodict[rev]['frame'].filestrack[fileheader].connection.connectionType.name
                    else:
                        md5 = None
                        type = None
                        status = None
                        existsInNext = None
                    blahdict[fileheader].append({"md5":md5, "type":type, "status":status, "existsInNext":existsInNext})

            for fileheader in  fileheaderlist:
                row = [fileheader]
                self.fileheaderlist.append(fileheader)
                row = blahdict[fileheader]
                containdata.append(row)
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
            return self.revheaders[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self.fileheaderlist[section]
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