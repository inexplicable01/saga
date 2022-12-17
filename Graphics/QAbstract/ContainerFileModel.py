from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaCore.Container import Container,ContainerFileStatus
# from SagaGuiModel.SagaGuiContainerOperations import *
from SagaCore.ContainerItem import ContainerItem, ContainerItemType
from SagaGuiModel.GuiModelConstants import CHANGEREASONORDER,sagaworkingfiles,roleRequired, roleInput, roleOutput, colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED,roleUnversioned , foregroundcolorscheme
from datetime import datetime
import os
from SagaCore.Track import FileTrack, FolderTrack
from os.path import join
import warnings
import glob
from SagaCore.Frame import Frame
# from SagaGuiModel.SagaSync import SagaSync

STATUSCOLUMNHEADER='Status'
FILENAMECOLUMNHEADER = 'FileName'

class ContainerFileModel(QAbstractTableModel):
    def __init__(self, maincontainer:Container, sagasync, sagaguimodel):

        super(ContainerFileModel, self).__init__()
        self.containerfolderstatus=[]
        self.headers = [FILENAMECOLUMNHEADER, 'Role', STATUSCOLUMNHEADER, 'Last Edited', 'Rev Committed', 'Commit Message']
        self.maincontainer = maincontainer
        self.sagasync = sagasync
        self.containidtoname = []
        self.sagaguimodel = sagaguimodel
        if self.maincontainer is not None:
            self.containerfolderstatus = self.maincontainer.containerFolderStatus()



    # def gathermodeldatafromContainer(self):
    #     # print('begin gather model data' + datetime.now().isoformat())
    #     filedir = os.listdir(self.maincontainer.containerworkingfolder)
    #     containerfiledict={roleInput:[],roleRequired:[], roleOutput:[]}
    #     refframe = self.maincontainer.refframe
    #     wf = self.maincontainer.workingFrame
    #     for citemid in self.maincontainer.containeritems.keys():
    #         if citemid in wf.filestrack.keys():
    #             filetype = wf.filestrack[citemid].connection.containeritemrole.name
    #             lastcommit, commitmessage = self.latestRevFor(self.maincontainer, citemid, refframe)
    #             filedict = {'citemid': citemid,
    #                         'fileinfo': self.maincontainer.containeritemid[citemid],
    #                         'filerole': filetype,
    #                         'change': None,
    #                         'filetrack': wf.filestrack[citemid],
    #                         'lastcommit': lastcommit, 'commitmessage': commitmessage}
    #             if wf.filestrack[citemid].entity in filedir:
    #                 filedir.remove(wf.filestrack[citemid].entity)
    #         else:
    #             filerole= self.maincontainer.containeritems[citemid].containeritemrole
    #             filedict = {'citemid': citemid,
    #                         'fileinfo': self.maincontainer.containeritems[citemid],
    #                         'filerole': filerole,
    #                         'change': None,
    #                         'filetrack': FileTrack.createMissingTrack(citemid),
    #                         'lastcommit': 'missing', 'commitmessage': 'missing'}
    #         containerfiledict[filerole].append(filedict)
    #
    #
    #     self.containerfiles = containerfiledict[roleInput] + containerfiledict[roleRequired] + containerfiledict[roleOutput]
    #     # print('should be end' + datetime.now().isoformat())
    #     for unbookedfile in filedir:
    #         if unbookedfile in sagaworkingfiles or unbookedfile.startswith('~$'):
    #             continue
    #         unversionedfiletrack=FileTrack( containerworkingfolder=self.maincontainer.containerworkingfolder,
    #                       filename=unbookedfile, containeritemid='---')
    #         self.containerfiles.append({'citemid': '---',
    #             'fileinfo': {'type':roleUnversioned, 'Container':'here'},
    #             'filerole':roleUnversioned,
    #             'change': None,
    #             'filetrack': unversionedfiletrack ,
    #             'lastcommit': None, 'commitmessage': None})
    #     # print('end gather model data' + datetime.now().isoformat())

    def data(self, index, role):
        if index.isValid():
            c = index.column()
            r = index.row()
            s:ContainerFileStatus = self.containerfolderstatus[r]
            if role == Qt.DisplayRole:
                if self.headers[c]=='Role':
                    if s.citem.containeritemrole == roleInput:
                        upstreamcontainer = self.sagaguimodel.provideContainer(s.citem.refcontainerid)
                        return roleInput + ' From ' + upstreamcontainer.containerName
                    elif s.citem.containeritemrole  == roleOutput:
                        strout = roleOutput + ' To '
                        for containerid in s.citem.refcontainerid:
                            try:
                                container = self.sagaguimodel.provideContainer(containerid)
                            except:
                                container = containerid
                            strout = strout + container.containerName + ','
                        return strout
                    elif s.citem.containeritemrole == roleRequired:
                        return roleRequired
                elif self.headers[c]==STATUSCOLUMNHEADER:
                    if s.citem.containeritemrole in [roleOutput,roleRequired]:
                        if s.change:
                            return ', '.join(s.change['reason'])
                        else:
                            return 'Added'
                    elif s.citem.containeritemrole ==roleInput:
                        return self.maincontainer.workingFrame.filestrack[s.citemid].connection.Rev
                elif self.headers[c]=='FileName':
                    pass
                elif self.headers[c]=='Last Edited':
                    if s.citem.containeritemrole in [roleOutput,roleInput,roleRequired]:
                        try:
                            return datetime.fromtimestamp(s.filetrack.lastEdited).strftime('%m/%d/%y  %H:%M')
                        except:
                            return '---'
                    else:
                        return '---'
                elif self.headers[c]=='Rev Committed':
                    return s.lastcommit
                elif self.headers[c]=='Commit Message':
                    return s.commitmessage
                return '---'
            elif role ==Qt.BackgroundColorRole:
                return QColor(colorscheme[s.citem.containeritemrole])
            elif role == Qt.ForegroundRole:
                return QColor(foregroundcolorscheme[s.citem.containeritemrole])

    def update(self, newcontainer= None):
        if newcontainer is not None:
            self.maincontainer = newcontainer
        self.containerfolderstatus = self.maincontainer.containerFolderStatus()
        for i,s in enumerate(self.containerfolderstatus):
            if s.citemid in self.sagasync.changes.keys():
                s.change  = self.sagasync.changes[s.citemid]
                # self.containerfolderstatus[i]['change'] = changes[rowdict['citemid']]
            else:
                s.change  = None
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
            # return 'Column {}'.format(section + 1)
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            s = self.containerfolderstatus[section]
            return s.citem.containeritemname
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.containerfolderstatus)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self.headers )==0:
            return 0
        else:
            return len(self.headers)

    def reset(self):
        self.containerfolderstatus=[]
        self.maincontainer=None
        self.layoutChanged.emit()



# def createBeginRect(painter, cellrect, qtbrushcolor, squaresidepx, pxlinewidth):
#     # center = cellrect.center()
#     a =  cellrect.center() - QPointF(squaresidepx/2, squaresidepx/2)
#     b =  cellrect.center() + QPointF(squaresidepx/2, squaresidepx/2)
#     painter.setPen(QPen(QBrush(Qt.black), pxlinewidth))
#     painter.setBrush(QBrush(qtbrushcolor))
#     painter.drawRect(QRectF(a,b)) # 4 by 4 rectangle
#
# def createChangedcircle(painter, cellrect, qtbrushcolor, pxradius, pxlinewidth):
#     painter.setPen(QPen(QBrush(Qt.black), pxlinewidth))
#     painter.setBrush(QBrush(qtbrushcolor))
#     painter.drawEllipse(cellrect.center(), pxradius, pxradius);
#
# def createEmptyCell(painter, cellrect):
#     painter.setPen(QPen(QBrush(Qt.transparent), 0))
#     painter.setBrush(QBrush(Qt.white))
#     painter.drawRect(cellrect)
#
# def createSmallEndLine(painter, cellrect, qtbrushcolor):
#     a = cellrect.center()+QPointF(1,4)
#     b = cellrect.center() -QPointF(1, 4)
#     rect = QRectF(a,b)
#     painter.setPen(QPen(QBrush(qtbrushcolor), 0))
#     painter.setBrush(QBrush(qtbrushcolor))
#     painter.drawRect(rect)






class ContainerFileDelegate(QStyledItemDelegate):
    def __init__(self):
        super(ContainerFileDelegate, self).__init__()
    def paint(self,painter:QPainter, option, index:QModelIndex):
        s:ContainerFileStatus = index.model().containerfolderstatus[index.row()]
        change = index.model().containerfolderstatus[index.row()].change
        header = index.model().headers[index.column()]


        if FILENAMECOLUMNHEADER==header:
            painter.setPen(QPen(QBrush(Qt.black),0.5))
            painter.setBrush(QBrush(colorscheme[s.citem.containeritemrole]))
            painter.drawRect(option.rect)
            if type(s.citem.track)==FileTrack:
                entityname = s.citem.track.entity
            elif type(s.citem.track)==FolderTrack:
                entityname = s.citem.track.entity
            else:
                entityname = 'ContainerFileDelegateMissingTrackType'
            filename, file_extension = os.path.splitext(entityname)
            if file_extension in ['.docx', '.doc']:
                qpic = QImage('Graphics/FileIcons/Word.png')
            elif file_extension in ['.pptx', '.ppt']:
                qpic = QImage('Graphics/FileIcons/ppticon.png')
            elif file_extension in ['.xls', '.xlsx']:
                qpic = QImage('Graphics/FileIcons/excelicon.png')
            elif file_extension in ['.mp4']:
                qpic = QImage('Graphics/FileIcons/mp4icon.png')
            elif file_extension in ['.txt']:
                qpic = QImage('Graphics/FileIcons/txticon.png')
            elif file_extension in ['.pdf']:
                qpic = QImage('Graphics/FileIcons/pdficon.png')
            elif file_extension =='':
                qpic = QImage('Graphics/FileIcons/foldericon.png')
            else:
                qpic = QImage('Graphics/FileIcons/genericfile.png')

            if filename=='MISSING':
                qpic = QImage('Graphics/FileIcons/questionmark.png')
            # qpic = QImage('Graphics/FileIcons/foldericon.png')


            bottomright = QPointF(option.rect.left() + option.rect.width() * 0.2, option.rect.bottom())
            picRect = QRectF(option.rect.topLeft(), bottomright)
            painter.drawImage(picRect, qpic)

            topleft = QPointF(option.rect.left()+option.rect.width()*0.2,  option.rect.top())
            textrect = QRectF(topleft, option.rect.bottomRight())

            painter.setPen(QPen(QBrush(foregroundcolorscheme[s.citem.containeritemrole]), 1))
            if type(s.citem.track) == FileTrack:
                painter.drawText(textrect, Qt.AlignCenter, s.citem.track.entity)
            else:
                painter.drawText(textrect, Qt.AlignCenter, s.citem.track.entity)
        elif STATUSCOLUMNHEADER==header:
            if change:
                # changenum = len(change['reason'])
                painter.setPen(QPen(QBrush(colorscheme[s.citem.containeritemrole]), 0.5))
                painter.setBrush(QBrush(colorscheme[s.citem.containeritemrole]))
                painter.drawRect(option.rect)

                # StatusIcons
                width = option.rect.width()
                height = option.rect.height()
                if change.conflict:
                    midpoint = QPointF(option.rect.left() + width * 3 / 4, option.rect.center().y())
                    tl = midpoint + QPointF(0.3 * height, 0.3 * height)
                    br = midpoint + QPointF(-0.3 * height, -0.3 * height)
                    painter.setPen(QPen(QBrush(Qt.red), 1))
                    painter.setBrush(QBrush(Qt.red))
                    painter.drawEllipse(QRectF(tl, br))
                elif change.noteworthy or change.md5changed:
                    midpoint = QPointF(option.rect.left() + width * 2 / 4, option.rect.center().y())
                    tl = midpoint + QPointF(0.3 * height, 0.3 * height)
                    br = midpoint + QPointF(-0.3 * height, -0.3 * height)
                    painter.setPen(QPen(QBrush(Qt.yellow), 1))
                    painter.setBrush(QBrush(Qt.yellow))
                    painter.drawEllipse(QRectF(tl, br))
                else:
                    midpoint = QPointF(option.rect.left() + width *1/4, option.rect.center().y())
                    tl = midpoint + QPointF(0.3*height, 0.3*height)
                    br = midpoint + QPointF(-0.3 * height, -0.3 * height)
                    painter.setPen(QPen(QBrush(Qt.green), 1))
                    painter.setBrush(QBrush(Qt.green))
                    painter.drawEllipse(QRectF(tl, br))
            else:
                QStyledItemDelegate.paint(self, painter, option, index)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
            # QStyledItemDelegate.paint(self, painter, option, index)
            # thisvalue = containdata[r][c]
            # if thisvalue['style'] is not None:
            #     typecolor = colorscheme[thisvalue['style']]
            #
            # ### Create Line, draw line first so symbol can go over line. Line is drawn in two parts first half and second half
            # if thisvalue['status'] in [UNCHANGED,MD5CHANGED]: ## unchanged or md5Changed implies an previous existant
            #     painter.setPen(QPen(QBrush(typecolor), 2))
            #     line = QLineF(QPointF(option.rect.topLeft().x(), option.rect.center().y()),
            #                   QPointF(option.rect.center().x(), option.rect.center().y()))
            #     painter.drawLine(line);


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

