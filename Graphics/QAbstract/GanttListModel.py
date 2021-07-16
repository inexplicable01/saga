from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
import os
import glob
from datetime import datetime
from Config import typeOutput,typeRequired

class GanttListModel(QAbstractTableModel):
    def __init__(self, containerids, desktopdir):
        super(GanttListModel, self).__init__()
        self.headers = []
        self.historydict={}
        self.datecommits={}
        ganttdata=[]
        self.commitmessagedict={}

        for containerid in containerids:
            self.headers.append(containerid)
            # self.historydict[containerid] = []

        for containerid in containerids:
            # contyaml = os.path.join(desktopdir, 'ContainerMapWorkDir', containerid, 'containerstate.yaml')
            # curcont = Container.LoadContainerFromYaml(contyaml)
            # print(containerid)
            yamllist = glob.glob(os.path.join(desktopdir, 'ContainerMapWorkDir', containerid, 'Main', '*.yaml'))
            containerframes={}
            for yamlfn in yamllist:
                pastframe = Frame(os.path.join(desktopdir, 'ContainerMapWorkDir', containerid, 'Main'),yamlfn)
                containerframes[pastframe.commitUTCdatetime]= pastframe
            for revi, timestamp in enumerate(sorted(containerframes)):

                # self.historydict[containerid].append({'commitmessage': pastframe.commitMessage,
                #                                     'timestamp': pastframe.commitUTCdatetime})
                pastframe = containerframes[timestamp]
                outputchanged = False
                if not revi==0:
                    previoustimestamp = sorted(containerframes)[revi-1]
                    prevframe = containerframes[previoustimestamp]
                    for fileheader, filetrack in pastframe.filestrack.items():
                        if filetrack.style == typeOutput:
                            if fileheader not in prevframe.filestrack.keys():
                                outputchanged=True
                            elif not prevframe.filestrack[fileheader].md5 == filetrack.md5:
                                outputchanged=True


                pstdate = datetime.fromtimestamp(pastframe.commitUTCdatetime)
                weeksago = round((datetime.now().timestamp() - pastframe.commitUTCdatetime) / (3600 * 24 *7))

                msg = pastframe.FrameName + ' : ' + pastframe.commitMessage + ':' + str(pstdate.date())
                if weeksago not in self.historydict.keys():
                    self.historydict[weeksago]=[containerid]

                elif containerid not in self.historydict[weeksago]:
                    self.historydict[weeksago].append(containerid)

                if weeksago not in self.commitmessagedict.keys():
                    self.commitmessagedict[weeksago] = {containerid: [{'msg':msg,'outputchanged':outputchanged}]}
                else:
                    if containerid not in self.commitmessagedict[weeksago].keys():
                        self.commitmessagedict[weeksago][containerid]= [{'msg':msg,'outputchanged':outputchanged}]
                    else:
                        self.commitmessagedict[weeksago][containerid].append({'msg':msg,'outputchanged':outputchanged})
        check = 4



        for weeksago in sorted(self.historydict):
            row = []
            for containerid in containerids:
                if containerid in self.historydict[weeksago]:
                    outputchanged = False
                    for commit in self.commitmessagedict[weeksago][containerid]:
                        if commit['outputchanged']:
                            outputchanged=True
                    row.append(
                        {'text':'⃤',
                         'outputchanged':outputchanged})
                else:
                    row.append({'text':'', 'outputchanged':False
                                })
            ganttdata.append(row)

        self.rowheaders = sorted(self.historydict)
        self.ganttdata = ganttdata



    def data(self, index, role):
        # print(role)
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.ganttdata[index.row()][index.column()]['text']

        if role == Qt.BackgroundColorRole:
            if self.ganttdata[index.row()][index.column()]['text'] is not '':
                if self.ganttdata[index.row()][index.column()]['outputchanged']:
                    return QBrush(Qt.green)
                else:
                    return QBrush(Qt.blue)


        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
            # return 'Column {}'.format(section + 1)
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return 'Week {}'.format(sorted(self.historydict)[section])
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.ganttdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.headers)