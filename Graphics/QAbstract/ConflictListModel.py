from PyQt5.QtWidgets import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from datetime import datetime
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
from Config import SERVERFILEADDED,SERVERNEWREVISION, colorscheme, SERVERFILEDELETED, UPDATEDUPSTREAM, typeInput,typeRequired,typeOutput
# from SagaApp.FileObjects import FileTrack
# from SagaApp.Change import Change

FILENAME = 'File Name'
# CURRENT = 'Current'
DESCRIPTION = 'Description'
CURRENT = 'Current'
CURRENTREV = 'Current Rev : {}'
NEWESTREV = 'Newest Rev: {}'
UPSTREAM = 'Upstream Info'
ACTION = 'Resolve Action'


# headersadded = ['File Name', 'Download', 'Do Not Download?']
# headersdeleted = ['File Name', 'Delete', 'Do Not Delete?']
CURRENTCOL = 2
CURRENTREVCOL = 3
NEWESTREVCOL = 4
UPSTREAMCOL = 5

filetracktypes = ['','','','wffiletrack','nffiletrack','uffiletrack']

class SyncListModel(QAbstractTableModel):
    def __init__(self, changes, newframe:Frame, maincontainer:Container, containeridtoname, option):
        super().__init__()
        self.containeridtoname = containeridtoname
        self.refframe = maincontainer.getRefFrame()
        self.changes = changes
        self.currow=[]
        self.rowheader = []
        self.conflictdata = []
        self.conflictfilenames = []
        self.checkcolumns = [CURRENTCOL, CURRENTREVCOL,NEWESTREVCOL,UPSTREAMCOL]
        self.checks = {}
        self.currentrev = self.refframe.FrameName
        self.newframe = newframe
        self.CURRENTREVX = CURRENTREV.format(self.refframe.FrameName)
        if newframe is None:
            self.NEWESTREVX = 'No newer frame'
        else:
            self.NEWESTREVX = NEWESTREV.format(newframe.FrameName)
        headers = [FILENAME, DESCRIPTION, 'No', self.CURRENTREVX, self.NEWESTREVX, UPSTREAM , ACTION]
        sortdict={}
        self.changearray=[]
        self.headers = headers
        self.actionstate = {}
        if option=='conflict':
            self.notice = False
            for fileheader, change in self.changes.items():
                if change.conflict:
                    self.actionstate[fileheader] = []
                    self.rowheader.append(fileheader)
                    self.changearray.append(change)
        elif option=='notice':
            self.notice = True
            for fileheader, change in self.changes.items():
                if change.noteworthy:
                    self.actionstate[fileheader] = []
                    self.rowheader.append(fileheader)
                    self.changearray.append(change)

            # if change.conflict:
            #     self.conflictdata.append(fileheader)
            #     self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.rowheader[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


    def checkState(self, index):
        # print('orhere?')
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            # print('goes through here right?')
            row = index.row()
            col = index.column()
            change = self.changearray[row]
            ### figure out which one is main
            if value: ## adding
                if len(self.actionstate[change.fileheader])==0:
                    self.actionstate[change.fileheader].append({'main':True,
                        'filetrack':getattr(change, filetracktypes[col]),
                                                                'header':self.headers[col],
                                                                'filetracktype': filetracktypes[col],
                                                                'filetype':change.filetype,
                                                                'change':change
                    })
                else:
                    self.actionstate[change.fileheader].append({'main':False,
                                                                'filetrack':getattr(change, filetracktypes[col]),
                                                                'filetracktype':filetracktypes[col],
                                                                'header': self.headers[col],
                                                                'filetype':change.filetype,
                                                                'change':change
                    })
            else: ## removing
                if len(self.actionstate[change.fileheader]) == 0:
                    print('there should be nothing to remove')
                else:
                    for action in self.actionstate[change.fileheader]:
                        if action['header']==self.headers[col]:
                            self.actionstate[change.fileheader].remove(action)
                    if len(self.actionstate[change.fileheader]) == 0:
                        print('resolve action should reset')
                    else:
                        self.actionstate[change.fileheader][0]['main'] = True
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)
        row = index.row()
        col = index.column()
        change = self.changearray[row]
        if index.column() in self.checkcolumns:
            if self.headers[col] == CURRENT:
                if change.md5changed:
                    fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
            elif self.headers[col] == self.CURRENTREVX:
                if change.lffiletrack or change.inputscenariono==4 or change.reqoutscenariono==4:
                    fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
            elif self.headers[col] == self.NEWESTREVX:
                # fl |= Qt.ItemIsUserCheckable
                if change.nffiletrack or change.inputscenariono==3 or change.reqoutscenariono==3:
                    fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
            elif self.headers[col] == UPSTREAM:
                if change.uffiletrack:
                    fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
                # fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
        return fl

    def data(self, index, role):
        row = index.row()
        col = index.column()
        change= self.changearray[row]
        if role == Qt.DisplayRole:
            if self.headers[col]==FILENAME:
                return change.fileheader
            elif self.headers[col]==DESCRIPTION:
                return change.description.format(change.fileheader)
            elif self.headers[col]=='No':
                if change.inputscenariono in [1,2,3,4,5,6,7,8,9,10]:
                    return 'Input Scen ' + str(change.inputscenariono)
                elif change.reqoutscenariono  in [1,2,3,4,5,6,7,8,9,10]:
                    return 'REgOut Scen ' + str(change.reqoutscenariono)

            elif self.headers[col]==self.CURRENTREVX:
                if change.conflict:
                    if change.filetype==typeInput:
                        if change.inputscenariono==3:
                            return 'Keep File Added'
                        elif change.inputscenariono==6:
                            return "Ignore Newest Frame deleted"
                        elif change.inputscenariono in [5,7]:
                            return 'Local Copy is using ' + change.wffiletrack.connection.Rev + ' from container ' + \
                                       self.containeridtoname[change.wffiletrack.connection.refContainerId]
                    else:
                        if change.reqoutscenariono == 3:
                            return 'Keep File Added'
                        elif change.reqoutscenariono ==5:
                            return 'Keep Working file as latest Commit.'
                        elif change.reqoutscenariono == 6:
                            return "Ignore Newest Frame deleted"
                        elif change.reqoutscenariono ==7:
                            if change.md5changed:
                                return 'Local Copy is edited and not committed.'
                            else:
                                return 'Local Copy is from ' + change.lffiletrack.lastupdated
                elif change.noteworthy:
                    if change.filetype==typeInput:
                        if change.inputscenariono == 1:
                            return 'New Input added to container.'
                        elif change.inputscenariono == 2:
                            return "Input deleted from container."
                        elif change.inputscenariono == 4:
                            return "Reject new File Add. (This effectively remove fileheader from newest frame)"
                        elif change.inputscenariono == 5:
                            return 'Input file added.  Using ' + change.wffiletrack.connection.Rev + ' from container ' + \
                                   self.containeridtoname[change.wffiletrack.connection.refContainerId]
                        elif change.inputscenariono == 7:
                            return 'Using ' + change.wffiletrack.connection.Rev + ' from container ' + \
                                   self.containeridtoname[change.wffiletrack.connection.refContainerId]
                        elif change.inputscenariono == 8:
                            return 'Input file {} added.  Input file synced to {} from container {}'.format(change.fileheader,
                                    change.wffiletrack.connection.Rev, self.containeridtoname[change.wffiletrack.connection.refContainerId])
                        elif change.inputscenariono ==9:
                            return 'Input {} removed'.format(change.fileheader)
                        elif change.inputscenariono == 10:
                            if change.lffiletrack.connection.Rev!=change.wffiletrack.connection.Rev:
                                return 'Input file {} synced to {} from container {}. This file has been updated in this container since last commit.'.format(change.fileheader,
                                       change.wffiletrack.connection.Rev, self.containeridtoname[change.wffiletrack.connection.refContainerId])

                            else:
                                return 'Input file {} synced to {} from container {}'.format(change.fileheader,
                                        change.wffiletrack.connection.Rev, self.containeridtoname[change.wffiletrack.connection.refContainerId])
                    else:
                        if change.reqoutscenariono == 1:
                            return 'New File added to container.'
                        elif change.reqoutscenariono == 2:
                            return "File deleted from container."
                        elif change.reqoutscenariono == 4:
                            return "Reject new File Add. (This effectively remove {} from newest frame)".format(change.fileheader)
                        elif change.reqoutscenariono == 5:
                            return "File Added.  Working Identical to newest Frame"
                        elif change.reqoutscenariono == 7:
                            return "Local File identical to file in newest Frame."
                        elif change.reqoutscenariono == 8:
                            return "File {} Added.".format(change.fileheader)
                        elif change.reqoutscenariono == 9:
                            return "File {} removed.".format(change.fileheader)
                        elif change.reqoutscenariono == 10:
                            return "File {} edited from last commit.".format(change.fileheader)
            elif self.headers[col]==self.NEWESTREVX:
                if self.newframe: ## if new frame exist
                    if change.nffiletrack:  ## if fileheader exist for this fileheader
                        if change.filetype ==typeInput:
                            return 'Newest Rev''s Input is ' + change.nffiletrack.connection.Rev + ' from container ' + \
                                   self.containeridtoname[change.wffiletrack.connection.refContainerId]
                        else:
                            return 'Latest Updated :   ' + change.nffiletrack.lastupdated
                    else:## if fileheader doesn't exist for this fileheader
                        # if change.inputscenariono==3 or change.reqoutscenariono==3:
                        #     return 'Follow Newest Frame and and Remove {}'.format(change.fileheader)
                        if change.inputscenariono==2 or change.reqoutscenariono==2:
                            return 'Newest Frame Removed {}'.format(change.fileheader)
                        elif change.inputscenariono==1 or change.reqoutscenariono==1:
                            return 'Newest Frame does not have this {} either'.format(change.fileheader)
                else:
                    return 'No Newer Frame'
            elif self.headers[col]==UPSTREAM:
                if change.uffiletrack:
                    return 'Upstream container latest rev is ' + change.uffiletrack.lastupdated
                else:
                    return 'NA'
            elif self.headers[col]==ACTION:
                if change.conflict:
                    return self.explainselected(change.fileheader, change)
                elif change.noteworthy:
                    return change.description
        elif role == Qt.CheckStateRole and col in self.checkcolumns:
            if change.conflict:
                # if self.headers[col] == CURRENT:
                #     if change.wffiletrack:
                #         # if change.md5changed or change.inputscenariono == 1 or change.reqoutscenariono == 1:
                #         return self.checkState(QPersistentModelIndex(index))
                if self.headers[col] == self.CURRENTREVX:
                    return self.checkState(QPersistentModelIndex(index))
                elif self.headers[col] == self.NEWESTREVX:
                    # if change.nffiletrack or change.inputscenariono==3 or change.reqoutscenariono==3:
                    if not change.wf_synced_nf and not change.nf_synced_uf:
                        return self.checkState(QPersistentModelIndex(index))
                elif self.headers[col] == UPSTREAM:
                    if change.uffiletrack and not change.wf_synced_uf:
                        return self.checkState(QPersistentModelIndex(index))
            if change.noteworthy:
                if self.headers[col] == self.CURRENTREVX:
                    if change.wffiletrack or change.lffiletrack or \
                            change.inputscenariono == 4 or change.reqoutscenariono == 4:
                        return self.checkState(QPersistentModelIndex(index))
                elif self.headers[col] == self.NEWESTREVX:
                    if change.nffiletrack or change.inputscenariono==3 or change.reqoutscenariono==3:
                        return self.checkState(QPersistentModelIndex(index))
                elif self.headers[col] == UPSTREAM:
                    if change.uffiletrack:
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
        return len(self.rowheader)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.headers)

    def explainselected(self, fileheader, change):
        # for col in self.checkcolumns:
        #     checkboxindex = self.index(row, col)
        #     if self.checkState(QPersistentModelIndex(checkboxindex)):
        #         self.actionstate[fileheader]
        if len(self.actionstate[fileheader])==0:
            if change.inputscenariono in [1,3,4] or change.reqoutscenariono in [1,3,4]:
                return 'Please select only one option'
            else:
                return 'Please select at least one option.'
        else:
            copies=[]
            for action in self.actionstate[fileheader]:
                if action['main']:
                    mainaction = action
                else:
                    copies.append(action)
            actionstatement = self.mainactionstatmentgenerator(mainaction, 'main')
            for copy in copies:
                actionstatement = actionstatement + self.mainactionstatmentgenerator(copy, 'copies')
            return actionstatement

    def mainactionstatmentgenerator(self, action, importance):
        filetrack = action['filetrack']
        change = action['change']
        if importance=='main':
            if action['filetracktype']=='uffiletrack':
                return 'Saga will download latest upstream version. ' \
                       'Going forward, ' +  filetrack.lastupdated  + ' will be this container''s working copy.\n\n'
            elif action['filetracktype']=='nffiletrack':
                if change.reqoutscenariono==3 or change.inputscenariono==3:
                    return 'Saga will remove this fileheader from your workingframe to be in agreement with Newest Frame'
                else:
                    return 'Saga will download the newest frames version and will be this container''s working copy\n\n'
            elif action['filetracktype']=='lffiletrack':
                if change.reqoutscenariono in [5,4] or change.inputscenariono in [5,4]:
                    return 'This effectively will remove this file from this container as the latest commit DOES have this file.'
                elif change.reqoutscenariono in [6,7] or change.inputscenariono in [6,7]:
                    return 'This effectively will revert this file from Newest Frame to this local frame''s version.'
                else:
                    return 'Saga will use the version committed in '+ self.currentrev + ' as the working copy. If youve made local changes, this may count as reverting.\n\n'
            elif action['filetracktype']=='wffiletrack':
                return 'Saga will continue to use your editted version as the working copy.  \n\n'
        else:
            if action['filetracktype']=='uffiletrack':
                return 'Create copy' + filetrack.file_name + '_' + filetrack.lastupdated  + ' .\n\n'
            elif action['filetracktype']=='nffiletrack':
                return 'Create copy' +  filetrack.file_name + '_' + filetrack.lastupdated  + ' .\n\n'
            elif action['filetracktype']=='lffiletrack':
                return 'Create ' + self.currentrev +' copy named ' + filetrack.file_name + '_' + filetrack.lastupdated  + '.\n\n'
            elif action['filetracktype']=='wffiletrack':
                return 'Create your current working file as ' + filetrack.file_name + '_' + self.currentrev +'_edited.\n\n'


# 'wffiletrack','lffiletrack','nffiletrack','uffiletrack'
# class NoticeListModel(QAbstractTableModel):
#     def __init__(self, changes, newframe:Frame, maincontainer:Container, containeridtoname):
#         super().__init__()
#
#         self.containeridtoname = containeridtoname
#         self.refframe = maincontainer.getRefFrame()
#         self.changes = changes
#         self.currow=[]
#         self.rowheader = []
#         self.conflictdata = []
#         self.conflictfilenames = []
#         self.checkcolumns = [CURRENTCOL, CURRENTREVCOL,NEWESTREVCOL,UPSTREAMCOL]
#         self.checks = {}
#         self.currentrev = self.refframe.FrameName
#         self.newframe = newframe
#         self.CURRENTREVX = CURRENTREV.format(self.refframe.FrameName)
#         if newframe is None:
#             self.NEWESTREVX = 'No newer frame'
#         else:
#             self.NEWESTREVX = NEWESTREV.format(newframe.FrameName)
#         headers = [FILENAME, DESCRIPTION, CURRENT, self.CURRENTREVX, self.NEWESTREVX, UPSTREAM]
#         sortdict={}
#         self.changearray=[]
#         self.headers = headers
#
#             # if change.conflict:
#             #     self.conflictdata.append(fileheader)
#             #     self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self.headers[section]
#         if role == Qt.DisplayRole and orientation == Qt.Vertical:
#             return self.rowheader[section]
#         return QAbstractTableModel.headerData(self, section, orientation, role)
#
#
#     def checkState(self, index):
#         if index in self.checks.keys():
#             return self.checks[index]
#         else:
#             return Qt.Unchecked
#
#     def setData(self, index, value, role=Qt.EditRole):
#
#         if not index.isValid():
#             return False
#         if role == Qt.CheckStateRole:
#             self.checks[QPersistentModelIndex(index)] = value
#             return True
#         return False
#
#     def flags(self, index):
#         fl = QAbstractTableModel.flags(self, index)
#         row = index.row()
#         col = index.column()
#         change = self.changearray[row]
#         if index.column() in self.checkcolumns:
#             if self.headers[col] == CURRENT:
#                 if change.md5changed:
#                     fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
#             elif self.headers[col] == self.CURRENTREVX:
#                 if change.lffiletrack:
#                     fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
#             elif self.headers[col] == self.NEWESTREVX:
#                 if change.nffiletrack:
#                     fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
#             elif self.headers[col] == UPSTREAM:
#                 if change.uffiletrack:
#                     fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
#                 # fl |= Qt.ItemIsUserCheckable#Qt.ItemIsEditable
#         return fl
#
#     def data(self, index, role):
#         row = index.row()
#         col = index.column()
#         change = self.changearray[row]
#         if role == Qt.DisplayRole:
#             if self.headers[col]==FILENAME:
#                 # See below for the nested-list data structure.
#                 # .row() indexes into the outer list,
#                 # .column() indexes into the sub-list
#                 return change.fileheader
#             elif self.headers[col]==DESCRIPTION:
#                 return change.description.format(change.fileheader)
#             elif self.headers[col]==CURRENT:
#                 if change.md5changed:
#                     return 'Changed from Local Frame'
#                 else:
#                     return 'Same as ' + self.currentrev
#             elif self.headers[col]==self.CURRENTREVX:
#                 if change.lffiletrack:
#                     if change.lffiletrack.connection.connectionType.name==typeInput:
#
#                         return self.CURRENTREVX +  ' uses ' + change.lffiletrack.connection.Rev + ' from container ' + \
#                                self.containeridtoname[change.lffiletrack.connection.refContainerId]
#                     else:
#                         return 'Last Updated :   ' + change.lffiletrack.lastupdated
#                 else:
#                     return 'NA'
#             elif self.headers[col]==self.NEWESTREVX:
#                 if change.nffiletrack:
#                     return 'Last Updated :   ' + change.nffiletrack.lastupdated
#                 else:
#                     return 'NA'
#             elif self.headers[col]==UPSTREAM:
#                 if change.uffiletrack:
#                     return 'Last Updated :   ' + change.uffiletrack.lastupdated
#                 else:
#                     return 'NA'
#         elif role == Qt.CheckStateRole and col in self.checkcolumns:
#             if self.headers[col] == CURRENT:
#                 if change.md5changed:
#                     return self.checkState(QPersistentModelIndex(index))
#             elif self.headers[col] == self.CURRENTREVX:
#                 if change.lffiletrack:
#                     return self.checkState(QPersistentModelIndex(index))
#             elif self.headers[col] == self.NEWESTREVX:
#                 if change.nffiletrack:
#                     return self.checkState(QPersistentModelIndex(index))
#             elif self.headers[col] == UPSTREAM:
#                 if change.uffiletrack:
#                     return self.checkState(QPersistentModelIndex(index))
#
#         elif role == Qt.BackgroundColorRole:
#             if index.row() in self.currow:
#                 return QBrush(colorscheme[self.filetype])
#             else:
#                 return QBrush(Qt.white)
#                 # if self.ganttdata[index.row()][index.column()]['outputchanged']:
#                 #     return QBrush(Qt.green)
#                 # else:
#
#     def rowCount(self, index):
#         # The length of the outer list.
#         return len(self.rowheader)
#
#     def columnCount(self, index):
#         # The following takes the first sub-list, and returns
#         # the length (only works if all rows are an equal length)
#         return len(self.headers)



# class ConflictListModel(QAbstractTableModel):
#     def __init__(self, changes, newframe):
#         super().__init__()
#         self.changes = changes
#         self.currow=[]
#         self.conflictdata = []
#         self.conflictfilenames = []
#         self.checkcolumns = [1, 2]
#         self.checks = {}
#         self.newframe = newframe
#         sortdict={}
#         self.headers = headers
#         for fileheader, change in self.changes.items():
#             if change.conflict:
#                 self.conflictdata.append(fileheader)
#                 self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self.headers[section]
#         return QAbstractTableModel.headerData(self, section, orientation, role)
#
#
#     def checkState(self, index):
#         if index in self.checks.keys():
#             return self.checks[index]
#         else:
#             return Qt.Unchecked
#
#     def setData(self, index, value, role=Qt.EditRole):
#
#         if not index.isValid():
#             return False
#         if role == Qt.CheckStateRole:
#             self.checks[QPersistentModelIndex(index)] = value
#             return True
#         return False
#
#     def flags(self, index):
#         fl = QAbstractTableModel.flags(self, index)
#         if index.column() in [1,2]:
#             fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
#         return fl
#
#     def data(self, index, role):
#         row = index.row()
#         col = index.column()
#         if role == Qt.DisplayRole and col == 0:
#             # See below for the nested-list data structure.
#             # .row() indexes into the outer list,
#             # .column() indexes into the sub-list
#             return self.conflictfilenames[row]
#         elif role == Qt.CheckStateRole and col in self.checkcolumns:
#             return self.checkState(QPersistentModelIndex(index))
#         elif role == Qt.BackgroundColorRole:
#             if index.row() in self.currow:
#                 return QBrush(colorscheme[self.filetype])
#             else:
#                 return QBrush(Qt.white)
#                 # if self.ganttdata[index.row()][index.column()]['outputchanged']:
#                 #     return QBrush(Qt.green)
#                 # else:
#
#     def rowCount(self, index):
#         # The length of the outer list.
#         return len(self.conflictdata)
#
#     def columnCount(self, index):
#         # The following takes the first sub-list, and returns
#         # the length (only works if all rows are an equal length)
#         return len(self.headers)
#
#
# class AddedListModel(QAbstractTableModel):
#     def __init__(self, changes, newframe):
#         super().__init__()
#         self.changes = changes
#         self.currow=[]
#         self.conflictdata = []
#         self.conflictfilenames = []
#         self.checkcolumns = [1,2]
#         self.checks = {}
#         self.newframe = newframe
#         sortdict={}
#         self.headers = headersadded
#         for fileheader in self.changes:
#             if SERVERFILEADDED in self.changes[fileheader]['reason']:
#                 self.conflictdata.append(fileheader)
#                 self.conflictfilenames.append(self.newframe.filestrack[fileheader].file_name)
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self.headers[section]
#         return QAbstractTableModel.headerData(self, section, orientation, role)
#
#
#     def checkState(self, index):
#         if index in self.checks.keys():
#             return self.checks[index]
#         else:
#             return Qt.Unchecked
#
#     def setData(self, index, value, role=Qt.EditRole):
#
#         if not index.isValid():
#             return False
#         if role == Qt.CheckStateRole:
#             self.checks[QPersistentModelIndex(index)] = value
#             return True
#         return False
#
#     def flags(self, index):
#         fl = QAbstractTableModel.flags(self, index)
#         if index.column() in self.checkcolumns:
#             fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
#         return fl
#
#     def data(self, index, role):
#         row = index.row()
#         col = index.column()
#         if role == Qt.DisplayRole and col == 0:
#             # See below for the nested-list data structure.
#             # .row() indexes into the outer list,
#             # .column() indexes into the sub-list
#             return self.conflictfilenames[row]
#         elif role == Qt.CheckStateRole and col in [1,2]:
#             return self.checkState(QPersistentModelIndex(index))
#         elif role == Qt.BackgroundColorRole:
#             if index.row() in self.currow:
#                 return QBrush(colorscheme[self.filetype])
#             else:
#                 return QBrush(Qt.white)
#                 # if self.ganttdata[index.row()][index.column()]['outputchanged']:
#                 #     return QBrush(Qt.green)
#                 # else:
#
#     def rowCount(self, index):
#         # The length of the outer list.
#         return len(self.conflictdata)
#
#     def columnCount(self, index):
#         # The following takes the first sub-list, and returns
#         # the length (only works if all rows are an equal length)
#         return 3
#
# class DeletedListModel(QAbstractTableModel):
#     def __init__(self, changes, newframe:Frame, workingframe:Frame):
#         super().__init__()
#         self.changes = changes
#         self.currow=[]
#         self.conflictdata = []
#         self.conflictfilenames = []
#         self.checkcolumns = [1, 2]
#         self.workingframe = workingframe
#         self.checks = {}
#         self.newframe = newframe
#         sortdict={}
#         self.headers = headersdeleted
#         for fileheader in self.changes:
#             if SERVERFILEDELETED in self.changes[fileheader]['reason']:
#                 self.conflictdata.append(fileheader)
#                 self.conflictfilenames.append(self.workingframe.filestrack[fileheader].file_name)
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self.headers[section]
#         return QAbstractTableModel.headerData(self, section, orientation, role)
#
#
#     def checkState(self, index):
#         if index in self.checks.keys():
#             return self.checks[index]
#         else:
#             return Qt.Unchecked
#
#     def setData(self, index, value, role=Qt.EditRole):
#
#         if not index.isValid():
#             return False
#         if role == Qt.CheckStateRole:
#             self.checks[QPersistentModelIndex(index)] = value
#             return True
#         return False
#
#     def flags(self, index):
#         fl = QAbstractTableModel.flags(self, index)
#         if index.column() in self.checkcolumns:
#             fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
#         return fl
#
#     def data(self, index, role):
#         row = index.row()
#         col = index.column()
#         if role == Qt.DisplayRole and col == 0:
#             # See below for the nested-list data structure.
#             # .row() indexes into the outer list,
#             # .column() indexes into the sub-list
#             return self.conflictfilenames[row]
#         elif role == Qt.CheckStateRole and col in [1,2]:
#             return self.checkState(QPersistentModelIndex(index))
#         elif role == Qt.BackgroundColorRole:
#             if index.row() in self.currow:
#                 return QBrush(colorscheme[self.filetype])
#             else:
#                 return QBrush(Qt.white)
#                 # if self.ganttdata[index.row()][index.column()]['outputchanged']:
#                 #     return QBrush(Qt.green)
#                 # else:
#
#     def rowCount(self, index):
#         # The length of the outer list.
#         return len(self.conflictdata)
#
#     def columnCount(self, index):
#         # The following takes the first sub-list, and returns
#         # the length (only works if all rows are an equal length)
#         return 3
#
# class UpstreamListModel(QAbstractTableModel):
#     def __init__(self, changes):
#         super().__init__()
#         self.changes = changes
#         self.checks = {}
#         self.checkcolumns = [4]
#         self.upstreamfileupdate=[]
#         self.conflictdata = []
#         self.headers = ['File Name','Upstream Container + Rev','Upstream Commit Message', 'Commit Time', 'ReplaceInput']
#         for fileheader in self.changes:
#
#             if UPDATEDUPSTREAM in self.changes[fileheader]['reason']:
#                 self.conflictdata.append(fileheader)
#                 self.upstreamfileupdate.append({'frame':changes[fileheader]['upstreamframe'],
#                                                 'fileheader':fileheader,
#                                                 'fromcontainer':changes[fileheader]['fromcontainer']
#                                                 })
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole and orientation == Qt.Horizontal:
#             return self.headers[section]
#         return QAbstractTableModel.headerData(self, section, orientation, role)
#
#
#     def checkState(self, index):
#         if index in self.checks.keys():
#             return self.checks[index]
#         else:
#             return Qt.Unchecked
#
#     def setData(self, index, value, role=Qt.EditRole):
#
#         if not index.isValid():
#             return False
#         if role == Qt.CheckStateRole:
#             self.checks[QPersistentModelIndex(index)] = value
#             return True
#         return False
#
#     def flags(self, index):
#         fl = QAbstractTableModel.flags(self, index)
#         if index.column() in self.checkcolumns :
#             fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
#         return fl
#
#     def data(self, index, role):
#         row = index.row()
#         col = index.column()
#
#         if role == Qt.DisplayRole:
#             upstreamframe = self.upstreamfileupdate[row]['frame']
#             fileheader = self.upstreamfileupdate[row]['fileheader']
#             fromcontainer= self.upstreamfileupdate[row]['fromcontainer']
#             # See below for the nested-list data structure.
#             # .row() indexes into the outer list,
#             # .column() indexes into the sub-list
#             if col==0:
#                 return upstreamframe.filestrack[fileheader].file_name
#             elif col==1:
#                 return fromcontainer.containerName + ' @ ' + upstreamframe.FrameName
#             elif col==2:
#                 return upstreamframe.commitMessage
#             elif col == 3:
#                 return datetime.utcfromtimestamp(upstreamframe.commitUTCdatetime).strftime('%m/%d/%y  %H:%M')
#                 # return self.upstreamupdated[row][col]
#         elif role == Qt.CheckStateRole and col in self.checkcolumns:
#             return self.checkState(QPersistentModelIndex(index))
#         elif role == Qt.BackgroundColorRole:
#             # if index.row() in self.currow:
#             #     return QBrush(colorscheme[self.filetype])
#             # else:
#             return QBrush(Qt.white)
#                 # if self.ganttdata[index.row()][index.column()]['outputchanged']:
#                 #     return QBrush(Qt.green)
#                 # else:
#
#     def rowCount(self, index):
#         # The length of the outer list.
#         return len(self.upstreamfileupdate)
#
#     def columnCount(self, index):
#         # The following takes the first sub-list, and returns
#         # the length (only works if all rows are an equal length)
#         return 5