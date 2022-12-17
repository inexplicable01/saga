from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaCore.Container import Container
from SagaGuiModel.GuiModelConstants import CHANGEREASONORDER,sagaworkingfiles,roleRequired, roleInput, roleOutput, colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED,roleUnversioned
from datetime import datetime
import os
from SagaCore.Track import FileTrack
from os.path import join
import warnings
import glob
from SagaCore.Frame import Frame
# from SagaGuiModel.SagaSync import SagaSync

UPSTREAMCONTAINER='Output Container'
CITEMCOLUMN = 'CItemName'
UPSTREAMCOMMITMSG = 'Upstream Commit Msg'
STATUSCOLUMNHEADER='Status'
DOWNSTREAMCONTAINER = 'Downstream Container'
DOWNSTREAMCOMMITMSG='Downstream Commit Msg'


class SectionSyncFileModel(QAbstractTableModel):
    def __init__(self, sagaguimodel):

        super(SectionSyncFileModel, self).__init__()
        self.sagaguimodel = sagaguimodel

        self.headers = [CITEMCOLUMN, UPSTREAMCOMMITMSG, STATUSCOLUMNHEADER, DOWNSTREAMCONTAINER, DOWNSTREAMCOMMITMSG]
        self.gatherdatafrommodel()


    def gatherdatafrommodel(self):
        self.modeldata = []
        self.containernames = []
        inputsoutputsperfile={}
        if self.sagaguimodel.containerinfodict:
            for containerid, containerinfo in self.sagaguimodel.containerinfodict.items():

                curcontainer:Container = self.sagaguimodel.provideContainer(containerid)
                self.containernames.append(curcontainer.containerName)
                ## Looping through every single Container Item that is an input
                for citemid, citem in curcontainer.containeritems.items():
                    if citem.containeritemrole == roleInput:
                        # Is citem already reviewed?
                        if citemid in inputsoutputsperfile.keys():
                            if citem.refcontainerid != inputsoutputsperfile[citemid]['upstreaminfo']['containerid']:
                                raise('something is wrong')
                            inputsoutputsperfile[citemid]['downstreaminfo'].append(
                                {'containerid': curcontainer.containerId,
                                 'rev': citem.reftrack.Rev}
                            )
                        else:
                            upstreamcont = self.sagaguimodel.provideContainer(citem.refcontainerid)
                            if upstreamcont.refframe.filestrack[citemid].lastupdated is None:
                                raise('wtf')
                            inputsoutputsperfile[citemid] = \
                                {'upstreaminfo': {'containerid':citem.refcontainerid,
                                                  'rev':upstreamcont.refframe.filestrack[citemid].lastupdated},
                                 'downstreaminfo': [
                                     {'containerid': curcontainer.containerId,
                                      'rev': citem.reftrack.Rev}]
                                 }
                        # rowdict = {'outputcontname':curcontainer.containerName, 'citemid':fileheader}
                        # self.modeldata.append(rowdict)

            # for fileheader, connectioninfo in inputsoutputsperfile.items():
            #
            #     for downstreaminfo in connectioninfo['downstreaminfo']:
            #         self.modeldata.append({'upstreamid':connectioninfo['upstreaminfo']['containerid'],
            #                                'upstreamrev': connectioninfo['upstreaminfo']['rev'],
            #                                'citemid':fileheader,
            #                                'downstreamid': downstreaminfo['containerid'],
            #                                'downstreamrev': downstreaminfo['rev'],
            #                                })

            ### Reorder and Format.   Probably should use some sort of sorting algor but....MVP
            # def mysort(element):
            #     return sortdict[element]  ## sortdict[element] returns timestamp

            # revheaders.sort loops through each element.  element1 goes into mysort. key takes in a method.
            # mysort accepts element1 and returns timestamp1, e2 timestamp2 etc.   and sorts in roder the timestamps.
            # This way, you can through in some complex functions to tailer to the sorting.
            # self.containernames.sorted
            for containername in sorted(self.containernames): ### Attnetion this is super inefficient.
                upstreamcontainerheaderline = True
                for citemid, connectioninfo in inputsoutputsperfile.items():
                    upstreamcont = self.sagaguimodel.provideContainer(connectioninfo['upstreaminfo']['containerid'])
                    fileheaderheaderline = True
                    if containername ==upstreamcont.containerName:
                        for downstreaminfo in connectioninfo['downstreaminfo']:
                            self.modeldata.append({'upstreamid': connectioninfo['upstreaminfo']['containerid'],
                                                   'upstreamcontainerheaderline': upstreamcontainerheaderline,
                                                   'upstreamrev': connectioninfo['upstreaminfo']['rev'],
                                                   'citemid': citemid,
                                                   'fileheaderheaderline': fileheaderheaderline,
                                                   'downstreamid': downstreaminfo['containerid'],
                                                   'downstreamrev': downstreaminfo['rev'],
                                                   })
                            upstreamcontainerheaderline=False
                            fileheaderheaderline = False

                # self.modeldata.append({'upstreamid': '',
                #                        'upstreamrev': '',
                #                        'citemid': '',
                #                        'downstreamid': '',
                #                        'downstreamrev': '',
                #                        })



    def data(self, index, role):
        if index.isValid():
            c = index.column()
            r = index.row()
            rowdict = self.modeldata[r]
            # fileheader = rowdict['citemid']
            if role == Qt.DisplayRole:
                # if self.headers[c]=='citemid':

                if self.headers[c]==CITEMCOLUMN:
                    if rowdict['fileheaderheaderline']:
                        return rowdict['citemid'] + ' ' + rowdict['upstreamrev']
                elif self.headers[c]==UPSTREAMCOMMITMSG:
                    if rowdict['fileheaderheaderline']:
                        upstreamcont:Container= self.sagaguimodel.provideContainer(rowdict['upstreamid'])
                        return upstreamcont.refframe.commitMessage
                elif self.headers[c]==STATUSCOLUMNHEADER:
                    pass
                elif self.headers[c]==DOWNSTREAMCONTAINER:
                    downstreamcont = self.sagaguimodel.provideContainer(rowdict['downstreamid'])

                    ##ATTENTION Fix this
                    if rowdict['downstreamrev']:
                        downstreamrev = rowdict['downstreamrev']
                    else:
                        downstreamrev = 'Missing'
                    return downstreamcont.containerName + '  ' + downstreamrev
                elif self.headers[c]==DOWNSTREAMCOMMITMSG:
                    downstreamcont = self.sagaguimodel.provideContainer(rowdict['downstreamid'])
                    return downstreamcont.refframe.commitMessage

                return ''

            elif role ==Qt.BackgroundColorRole:
                # filetype = self.containerfiles[index.row()]['filerole']
                # return QColor(colorscheme[filetype])
                pass
            elif role == Qt.ForegroundRole:
                pass
                # if self.containerfiles[index.row()]['filerole'] == roleOutput:
                #     return QColor(Qt.white)
                # else:
                #     return QColor(Qt.black)

    def update(self):
        self.gatherdatafrommodel()
        self.layoutChanged.emit()
        # if newcontainer is not None:
        #     self.maincontainer = newcontainer
        # self.gathermodeldatafromContainer()
        # for i,rowdict in enumerate(self.containerfiles):
        #     if rowdict['citemid'] in self.sagasync.changes.keys():
        #         rowdict['change']  = self.sagasync.changes[rowdict['citemid']]
        #         # self.containerfiles[i]['change'] = changes[rowdict['citemid']]
        #     else:
        #         rowdict['change'] = None
        # self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
            # return 'Column {}'.format(section + 1)
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            rowdict = self.modeldata[section]
            # rowdict = self.containerfiles[section]
            if rowdict['upstreamcontainerheaderline']:
                upstreamcont = self.sagaguimodel.provideContainer(rowdict['upstreamid'])
                return upstreamcont.containerName
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.modeldata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self.headers)==0:
            return 0
        else:
            return len(self.headers)

class SectionSyncDelegate(QStyledItemDelegate):
    def __init__(self):
        super(SectionSyncDelegate, self).__init__()
    def paint(self,painter:QPainter, option, index:QModelIndex):
        rowdict = index.model().modeldata[index.row()]
        header = index.model().headers[index.column()]



        if STATUSCOLUMNHEADER==header:
            currentfileheader = rowdict['citemid']
            tophalfline = False
            bottomhalfline = False
            if index.row() > 0:
                lastrowdict = index.model().modeldata[index.row() - 1]
                lastrowfileheader = lastrowdict['citemid']
                if lastrowfileheader == currentfileheader:
                    tophalfline = True

            if index.row() < (index.model().rowCount(index) - 1):
                nextrowdict = index.model().modeldata[index.row() + 1]
                nextrowfileheader = nextrowdict['citemid']
                if nextrowfileheader == currentfileheader:
                    bottomhalfline = True
            if rowdict['fileheaderheaderline']:
                tophalfline = False
                painter.setPen(QPen(QBrush(Qt.black),0.5))
                painter.setBrush(QBrush(Qt.black))
                line = QLineF(QPointF(option.rect.left(), option.rect.center().y()),
                              QPointF(option.rect.center().x(), option.rect.center().y()))
                painter.drawLine(line);
            if tophalfline:
                painter.setPen(QPen(QBrush(Qt.black),0.5))
                painter.setBrush(QBrush(Qt.black))
                line = QLineF(QPointF(option.rect.center().x(), option.rect.top()),
                              QPointF(option.rect.center().x(), option.rect.center().y()))
                painter.drawLine(line);
            if bottomhalfline:
                painter.setPen(QPen(QBrush(Qt.black),0.5))
                painter.setBrush(QBrush(Qt.black))
                line = QLineF(QPointF(option.rect.center().x(), option.rect.center().y()),
                              QPointF(option.rect.center().x(), option.rect.bottom()))
                painter.drawLine(line);

            if  rowdict['upstreamrev']==rowdict['downstreamrev']:
                painter.setPen(QPen(QBrush(Qt.green), 1.5))
                painter.setBrush(QBrush(Qt.green))
                line = QLineF(QPointF(option.rect.center().x(), option.rect.center().y()),
                              QPointF(option.rect.right(), option.rect.center().y()))
                painter.drawLine(line);
            else:
                painter.setPen(QPen(QBrush(Qt.red), 2.0))
                painter.setBrush(QBrush(Qt.red))
                width = option.rect.width()
                crossPt = QPointF(option.rect.left() + 0.75*width, option.rect.center().y())
                bottomleft = crossPt + QPointF(5,-10)
                topright = crossPt + QPointF(-5, 10)
                line = QLineF(bottomleft,topright)
                painter.drawLine(line);

                line = QLineF(QPointF(option.rect.center().x(), option.rect.center().y()),
                              QPointF(option.rect.right(), option.rect.center().y()))
                painter.drawLine(line);

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

