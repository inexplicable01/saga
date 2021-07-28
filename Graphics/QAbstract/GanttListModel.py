from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
import math
import os
import glob
from datetime import datetime
from Config import typeOutput,typeRequired, typeInput, colorscheme, CONTAINERFN

def weekstrfromtimestamp(commitUTCdatetime):
    weeksago = math.floor((datetime.utcnow().timestamp() - commitUTCdatetime) / (3600*4))
    return 'week -' + str(weeksago), weeksago

class GanttListModel(QAbstractTableModel):
    def __init__(self,containerinfodict , desktopdir, weekstocheck = 10):
        super(GanttListModel, self).__init__()
        containerids = containerinfodict.keys()
        self.containerheaders = []
        self.historydict={}
        self.datecommits={}

        self.commitmessagedict={}
        self.weeksdict={}
        self.containeridtoname={}
        self.containernametoid = {}

        for containerid in containerids:
                # Container.LoadContainerFromYaml(os.path.join(desktopdir, 'ContainerMapWorkDir', containerid,CONTAINERFN))##ATTENTION
            self.containerheaders.append(containerinfodict[containerid]['ContainerDescription'])
            self.containeridtoname[containerid]=containerinfodict[containerid]['ContainerDescription']
            self.containernametoid[containerinfodict[containerid]['ContainerDescription']] = containerid

        for i in range(-weekstocheck,1):
            initdict = {}
            initdictmes = {}
            ## Initiating variables
            for containerid in containerids:
                initdict[containerid] = {'cellinfo': {
                    'frames': [],
                    'status': [],
                    'cellsummary': None,
                    'outputchanged': 0,
                    'inputchanged': 0
                }}
                initdictmes[containerid] = {'msg': []}
            if i ==0:
                weekstr = 'week -0'
            else:
                weekstr = 'week '+str(i)
            self.weeksdict[weekstr]= initdict
            self.commitmessagedict[weekstr] = initdictmes

        transferpair={}
        containerframes = {}
        workingnotes=[]
        for containerid in containerids:
            # contyaml = os.path.join(desktopdir, 'ContainerMapWorkDir', containerid, 'containerstate.yaml')
            # curcont = Container.LoadContainerFromYaml(contyaml)
            # print(containerid)
            yamllist = glob.glob(os.path.join(desktopdir, 'ContainerMapWorkDir', containerid, 'Main', 'Rev*.yaml'))
            containerframes[containerid]={}
            for yamlfn in yamllist:
                pastframe = Frame.LoadFrameFromYaml(yamlfn,os.path.join(desktopdir, 'ContainerMapWorkDir', containerid))
                weekstr, weeksago = weekstrfromtimestamp(pastframe.commitUTCdatetime)
                if weeksago < weekstocheck:
                    containerframes[containerid][pastframe.commitUTCdatetime]= pastframe

            # self.sortedframes[containerid]={}
            # for revi, timestamp in enumerate(sorted(containerframes[containerid])):
            #     ## Main Action, Looping through the sorted frames of the container
            #     ## Why am I sorting through a dictionary?  Would it just make sure sense to ignore frames that have a timestamp older than X?
            #     # ATTENTION
            #     weekstr, weeksago = weekstrfromtimestamp(timestamp)
            #     if weeksago < weekstocheck:
            #         pastframe = containerframes[containerid][timestamp]
            #         self.sortedframes[containerid][timestamp] = pastframe

        ##Checking output md5 changes and adding frames to cells

        for containerid in containerids:
            sortedTimestamps = sorted(containerframes[containerid])
            for revi, timestamp in enumerate(sortedTimestamps):
                pastframe = containerframes[containerid][timestamp]

                weekstr, weeksago = weekstrfromtimestamp(pastframe.commitUTCdatetime)
                self.weeksdict[weekstr][containerid]['cellinfo']['frames'].append(pastframe)
                pstdate = datetime.fromtimestamp(pastframe.commitUTCdatetime)
                msg = pastframe.FrameName + ' : ' + pastframe.commitMessage + ':' + str(pstdate.date())
                self.commitmessagedict[weekstr][containerid]['msg'].append(msg)
                if not revi==0:
                    previoustimestamp = sortedTimestamps[revi-1]
                    prevframe = containerframes[containerid][previoustimestamp]
                    for fileheader, filetrack in pastframe.filestrack.items():
                        if containerid == 'CustomerRequirements' and fileheader=='CustomerReq':
                            a = 4
                        if filetrack.connection.connectionType.name == typeOutput:
                            if fileheader not in prevframe.filestrack.keys():
                                self.weeksdict[weekstr][containerid]['cellinfo']['outputchanged'] +=1
                                transferpair[filetrack.md5] = {'containerid':containerid,
                                                               'weekstr':weekstr,
                                                               'fileheader':fileheader,
                                                               'file_name':filetrack.file_name,
                                                               'toinput':[]}
                            elif not prevframe.filestrack[fileheader].md5 == filetrack.md5:
                                self.weeksdict[weekstr][containerid]['cellinfo']['outputchanged'] +=1
                                # workingnotes.append([])
                                transferpair[filetrack.md5] = {'containerid':containerid,
                                                               'weekstr':weekstr,
                                                               'fileheader': fileheader,
                                                               'file_name': filetrack.file_name,
                                                               'toinput':[],
                                                               'md5':filetrack.md5}
                        # elif filetrack.style !=typeInput:
                        #     if not prevframe.filestrack[fileheader].md5 == filetrack.md5:
                        #         self.weeksdict[weekstr][containerid]['cellinfo']['outputchanged']


        ### A second look is needed for the transfer pair.  Transfer pair needs to know where all the outputs are before the loop.
        ## maybe there's a smarter way tt do this.
        for containerid in containerids:
            sortedTimestamps = sorted(containerframes[containerid])
            for revi, timestamp in enumerate(sortedTimestamps):
                pastframe = containerframes[containerid][timestamp]
                weekstr, weeksago = weekstrfromtimestamp(pastframe.commitUTCdatetime)
                if not revi==0:
                    previoustimestamp = sortedTimestamps[revi-1]
                    prevframe = containerframes[containerid][previoustimestamp]
                    for fileheader, filetrack in pastframe.filestrack.items():
                        if filetrack.connection.connectionType.name == typeInput:
                            if fileheader not in prevframe.filestrack.keys():
                                if filetrack.md5 in transferpair.keys():
                                    transferpair[filetrack.md5]['toinput'].append({
                                        'containerid': containerid,
                                        'weekstr': weekstr,
                                        'md5': filetrack.md5
                                    })
                                self.weeksdict[weekstr][containerid]['cellinfo']['inputchanged']+=1
                            elif not prevframe.filestrack[fileheader].md5 == filetrack.md5:
                                self.weeksdict[weekstr][containerid]['cellinfo']['inputchanged']+=1
                                if filetrack.md5 in transferpair.keys():
                                    transferpair[filetrack.md5]['toinput'].append({
                                        'containerid': containerid,
                                        'weekstr': weekstr,
                                        'md5': filetrack.md5
                                    })


        # for workingnote in workingsnotes:
        #     [weekstr, containerid, pastframe, outputchanged, inputchanged] = workingnote
        #
        #
        #         if outputchanged: ## Only switch to True if true
        #                         transferpair[filetrack.md5] = {'containerid':containerid,
        #                                                        'weekstr':weekstr,
        #                                                        'fileheader': fileheader,
        #                                                        'file_name': filetrack.file_name,
        #                                                        'toinput':[],
        #                                                        'md5':filetrack.md5}

        for md5, pair in transferpair.items():
            if len(pair['toinput']) == 0:
               continue
            self.weeksdict[pair['weekstr']][pair['containerid']]['transfer']={
                'fromcontainerid': pair['containerid'],
                'fromweekstr': pair['weekstr'],
                'fileheader': pair['fileheader'],
                'file_name': pair['file_name'],
                'md5' : md5,
                'toinput':pair['toinput']
            }
            # print(pair)
        self.weeksdictlist = list(self.weeksdict)
        self.transferpair = transferpair

    def data(self, index, role):
        # print(role)
        if index.isValid():
            weekstr = self.weeksdictlist[index.column()]
            containername= self.containerheaders[index.row()]
            containerid = self.containernametoid[containername]
            cellinfo = self.weeksdict[weekstr][containerid]['cellinfo']
            if role == Qt.DisplayRole:
                # See below for the nested-list data structure.
                # .row() indexes into the outer list,
                # .column() indexes into the sub-list
                # self.weeksdict[weekstr][containerid]['cellinfo']
                # {'cellinfo': {
                #     'frames': [],
                #     'status': [],
                #     'cellsummary': None,
                #     'outputchanged': False,
                #     'inputchanged': False
                # }}
                # weekstr = self.weeksdictlist[index.column()]
                # containername= self.containerheaders[index.row()]
                # containerid = self.containernametoid[containername]
                # cellinfo = self.weeksdict[weekstr][containerid]['cellinfo']

                if len(cellinfo['frames'])>0:
                    return len(cellinfo['frames'])
                else:
                    return

            if role == Qt.BackgroundColorRole:
                if len(cellinfo['frames'])>0:
                    if cellinfo['outputchanged']:
                        return QBrush(Qt.green)
                    else:
                        return QBrush(Qt.blue)
                else:
                    return
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        else:
            return


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self.containerheaders[section]
            # return 'Column {}'.format(section + 1)
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.weeksdictlist[section]
        # return super().headerData(section, orientation, role)

    def columnCount(self, index):
        # The length of the outer list.
        return len(self.weeksdictlist)

    def rowCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.containerheaders)


#
class GanttListDelegate(QStyledItemDelegate):
    def __init__(self):

        super(GanttListDelegate, self).__init__()
    def paint(self,painter:QPainter, option, index:QModelIndex):
        weekstr = index.model().weeksdictlist[index.column()]
        containername = index.model().containerheaders[index.row()]
        containerid=index.model().containernametoid[containername]
        cellinfo = index.model().weeksdict[weekstr][containerid]['cellinfo']
        # {'cellinfo': {
        #     'frames': [],
        #     'status': [],
        #     'cellsummary': None,
        #     'outputchanged': False,
        #     'inputchanged': False
        # }}

        def drawoutputchangedsymbol(painter, option, cellinfo):
            w = option.rect.width()
            h = option.rect.height()
            ## how many symbols
            symmidpoint = option.rect.topLeft() + QPointF(w*3/4,h/2)
            symbolrect = QRectF(QPointF(symmidpoint+ QPointF(-w*0.08,-h*0.2)),
                                QPointF(symmidpoint+ QPointF(w*0.08,h*0.2)))

            painter.setBrush(QBrush(colorscheme[typeOutput]))
            painter.drawRect(symbolrect)
            painter.setPen(QPen(QBrush(Qt.black), 2))
            painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['outputchanged']))

        def drawinputchangedsymbol(painter, option, cellinfo):
            w = option.rect.width()
            h = option.rect.height()
            ## how many symbols
            symmidpoint = option.rect.topLeft() + QPointF(w *1/ 4, h / 2)
            symbolrect = QRectF(QPointF(symmidpoint + QPointF(-w * 0.08, -h * .2)),
                                QPointF(symmidpoint + QPointF(w * 0.08, h * 0.2)))

            painter.setBrush(QBrush(colorscheme[typeInput]))
            painter.drawRect(symbolrect)
            painter.setPen(QPen(QBrush(Qt.black), 2))
            painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['inputchanged']))
            # painter.drawRect(QRectF(midpoint, option.rect.topRight()))

        if len(cellinfo['frames'])>0:
            w = option.rect.width()
            h = option.rect.height()
            ## how many symbols
            symmidpoint = option.rect.topLeft() + QPointF(w *2/ 4, h / 2)
            painter.setPen(QPen(QBrush(Qt.transparent), 2))
            painter.setBrush(QBrush(colorscheme[typeRequired]))
            painter.drawEllipse(symmidpoint, w*0.4,h*0.4)
            painter.setPen(QPen(QBrush(Qt.black), 2))
            painter.drawText(option.rect, Qt.AlignCenter, str(len(cellinfo['frames'])))
            if cellinfo['outputchanged']:
                drawoutputchangedsymbol(painter,option,cellinfo)

            if cellinfo['inputchanged']:
                drawinputchangedsymbol(painter, option, cellinfo)
            if 'transfer' in index.model().weeksdict[weekstr][containerid].keys():
                # 'transfer'
                # {
                #     'fromcontainerid': pair['containerid'],
                #     'fromweekstr': pair['weekstr'],
                #     'fileheader': fileheader,
                #     'file_name': filetrack.file_name,
                #     'md5': md5,
                #     'tpinput': pair['toinput']
                # }
                # transferpair[filetrack.md5]['toinput'].append({
                #     'containerid': containerid,
                #     'weekstr': weekstr,
                #     'md5': filetrack.md5
                # })
                transfer = index.model().weeksdict[weekstr][containerid]['transfer']
                for toinput in transfer['toinput']:
                    c = index.model().weeksdictlist.index(toinput['weekstr'])
                    containername = index.model().containeridtoname[toinput['containerid']]
                    r = index.model().containerheaders.index(containername)

                    # print(c,r)

            # if cellinfo['outchanged']:
            #     drawchangedsymbol(painter,option,cellinfo)
            # painter.drawText(option.rect, Qt.AlignLeft, index.internalPointer().data(0))

        else:
            QStyledItemDelegate.paint(self, painter, option, index)



    def createEditor(self, parent:QWidget, option:QStyleOptionViewItem, index:QModelIndex):
        if (index.row()==0):
            lineedit = QLineEdit(parent)
            return lineedit
        elif (index.row() == 1):
            combo = QComboBox(parent)
            # connect(histeditor,HistoryEditor.editingFinished,HistoryEditor.commitAndCloseEditor)
            return combo
        return QStyledItemDelegate.createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        row=index.row()
        column = index.column()
        value = index.model().items[row][column]
        if isinstance(editor, QComboBox):
            editor.addItems(['Somewhere', 'Over', 'The Rainbow'])
            editor.setCurrentIndex(index.row())
        if isinstance(editor, QLineEdit):
            editor.setText('Somewhere over the rainbow')
#
