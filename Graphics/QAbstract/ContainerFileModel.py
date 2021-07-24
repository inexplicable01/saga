from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.Container import Container
from Config import CHANGEREASONORDER,sagaworkingfiles,typeRequired, typeInput, typeOutput, colorscheme,  JUSTCREATED, UNCHANGED, MD5CHANGED,typeUnversioned
from datetime import datetime
import os
from SagaApp.FileObjects import FileTrack
from os.path import join
import warnings
import glob
from SagaApp.FrameStruct import Frame
# from SagaGuiModel.SagaSync import SagaSync

STATUSCOLUMNHEADER='Status'

class ContainerFileModel(QAbstractTableModel):
    def __init__(self, maincontainer:Container, sagasync):

        super(ContainerFileModel, self).__init__()

        self.headers = ['FileHeader', 'Role', 'Status','FileName', 'Last Edited', 'Rev Committed', 'Commit Message']
        self.maincontainer = maincontainer
        self.sagasync = sagasync
        self.gathermodeldatafromContainer()

    def latestRevFor(self,maincontainer:Container,fileheader):
        if fileheader not in maincontainer.getRefFrame().filestrack.keys():
            return 'Rev Next', 'Not Committed Yet'
        curmd5 = maincontainer.getRefFrame().filestrack[fileheader].md5
        # print(self.revnum, self.workingFrame.FrameName)
        lastsamerevnum = maincontainer.revnum
        while lastsamerevnum > 1:
            lastsamerevnum -= 1
            revyaml = 'Rev' + str(lastsamerevnum) + '.yaml'

            if revyaml in maincontainer.memoryframesdict.keys():
                pastframe = maincontainer.memoryframesdict[revyaml]
            else:
                warnings.warn('Rev' + str(lastsamerevnum) + '.yaml  cannot be found. Incomplete history')
                continue
            if fileheader in pastframe.filestrack.keys():
                if curmd5 != pastframe.filestrack[fileheader].md5:
                    return 'Rev' + str(lastsamerevnum + 1), maincontainer.memoryframesdict['Rev' + str(lastsamerevnum + 1)+ '.yaml'].commitMessage
                    # returns Rev where md5 was still the same which is one Rev(this+1)
                if lastsamerevnum == 1:
                    return 'Rev' + str(lastsamerevnum), pastframe.commitMessage
            else:
                return 'Rev'+str(lastsamerevnum+1), pastframe.commitMessage
        return 'Rev0', 'work in progress'



    def gathermodeldatafromContainer(self):
        filedir = os.listdir(self.maincontainer.containerworkingfolder)
        containerfiledict={typeInput:[],typeRequired:[], typeOutput:[]}
        for fileheader, fileinfo in self.maincontainer.FileHeaders.items():
            wf = self.maincontainer.workingFrame
            # lastcommit, commitmessage = maincontainer.latestRevFor(fileheader)
            lastcommit, commitmessage = self.latestRevFor(self.maincontainer,fileheader)
            filedict = {'fileheader': fileheader,
                'fileinfo': fileinfo,
                'change': None,
                'filetrack': None ,
                'lastcommit': lastcommit, 'commitmessage': commitmessage}
            if fileheader in wf.filestrack.keys():
                filedict['filetrack']=wf.filestrack[fileheader]
            else:
                missingfiletrack = FileTrack(FileHeader='---',
                                             containerworkingfolder=self.maincontainer.containerworkingfolder,
                                             file_name='---', style=None)
                filedict['filetrack'] = missingfiletrack

            containerfiledict[fileinfo['type']].append(filedict)

            if wf.filestrack[fileheader].file_name in filedir:
                filedir.remove(wf.filestrack[fileheader].file_name)
        self.containerfiles = containerfiledict[typeInput] + containerfiledict[typeRequired] + containerfiledict[typeOutput]
        for unbookedfile in filedir:
            if unbookedfile in sagaworkingfiles:
                continue
            unversionedfiletrack=FileTrack(FileHeader='---', containerworkingfolder=self.maincontainer.containerworkingfolder,
                          file_name=unbookedfile, style=typeUnversioned)
            self.containerfiles.append({'fileheader': '---',
                'fileinfo': {'type':typeUnversioned, 'Container':'here'},
                'change': None,
                'filetrack': unversionedfiletrack ,
                'lastcommit': None, 'commitmessage': None})


    def data(self, index, role):

        if index.isValid():
            c = index.column()
            r = index.row()
            rowdict = self.containerfiles[r]
            if role == Qt.DisplayRole:
                if self.headers[c]=='FileHeader':
                    return rowdict['fileheader']
                elif self.headers[c]=='Role':
                    if rowdict['fileinfo']['type'] == typeInput:
                        return typeInput + ' From ' + rowdict['fileinfo']['Container']
                    elif rowdict['fileinfo']['type'] == typeOutput:
                        return typeOutput + ' To ' +  ','.join(rowdict['fileinfo']['Container'])
                    elif rowdict['fileinfo']['type'] == typeRequired:
                        return typeRequired
                elif self.headers[c]==STATUSCOLUMNHEADER:
                    if rowdict['fileinfo']['type'] in [typeOutput,typeInput,typeRequired]:
                        if rowdict['change']:
                            return ', '.join(rowdict['change']['reason'])
                        else:
                            return 'Up To Date'
                elif self.headers[c]=='FileName':
                    pass
                # elif self.headers[c]=='From':
                #     if rowdict['fileinfo']['type']==typeInput:
                #         return rowdict['fileinfo']['Container']
                #     else:
                #         return None
                # elif self.headers[c]=='To':
                #     if rowdict['fileinfo']['type'] == typeOutput:
                #         return ', '.join(rowdict['fileinfo']['Container'])
                #     else:
                #         return None
                elif self.headers[c]=='Last Edited':
                    if rowdict['fileinfo']['type'] in [typeOutput,typeInput,typeRequired]:
                        return datetime.fromtimestamp(rowdict['filetrack'].lastEdited).strftime('%m/%d/%y  %H:%M')
                    else:
                        return '---'
                elif self.headers[c]=='Rev Committed':
                    return rowdict['lastcommit']
                elif self.headers[c]=='Commit Message':
                    return rowdict['commitmessage']
                return '---'
            elif role ==Qt.BackgroundColorRole:

                filetype = self.containerfiles[index.row()]['fileinfo']['type']
                return QColor(colorscheme[filetype])

    def update(self):
        self.gathermodeldatafromContainer()
        for i,rowdict in enumerate(self.containerfiles):
            if rowdict['fileheader'] in self.sagasync.changes.keys():
                rowdict['change']  = self.sagasync.changes[rowdict['fileheader']]
                # self.containerfiles[i]['change'] = changes[rowdict['fileheader']]
            else:
                rowdict['change'] = None
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.containerfiles)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self.headers )==0:
            return 0
        else:
            return len(self.headers)



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
        filetrack = index.model().containerfiles[index.row()]['filetrack']
        change = index.model().containerfiles[index.row()]['change']
        header = index.model().headers[index.column()]


        if 'FileName'==header:
            painter.setPen(QPen(QBrush(Qt.black),1))
            painter.setBrush(QBrush(colorscheme[filetrack.connection.connectionType.name]))
            painter.drawRect(option.rect)

            file_name, file_extension = os.path.splitext(filetrack.file_name)

            bottomright = QPointF(option.rect.left() + option.rect.width() * 0.2, option.rect.bottom())
            picRect = QRectF(option.rect.topLeft(), bottomright)
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
            else:
                qpic = QImage('Graphics/FileIcons/genericfile.png')

            if not filetrack.ctnrootpath == '.':
                qpic = QImage('Graphics/FileIcons/foldericon.png')
            painter.drawImage(picRect, qpic)

            topleft = QPointF(option.rect.left()+option.rect.width()*0.2,  option.rect.top())
            textrect = QRectF(topleft, option.rect.bottomRight())
            painter.setPen(QPen(QBrush(Qt.white), 1))
            painter.drawText(textrect, Qt.AlignCenter, filetrack.file_name)
        elif STATUSCOLUMNHEADER==header:
            if change:
                # changenum = len(change['reason'])
                for ic, changereason in enumerate(change['reason']):
                    reasonnum = CHANGEREASONORDER.index(changereason)
                    intv = option.rect.width()/len(CHANGEREASONORDER)
                    tl = QPointF(option.rect.left() +  intv * reasonnum + intv*0.1, option.rect.top()+0.2*option.rect.height())
                    br = QPointF(option.rect.left() + intv * (reasonnum+1)- intv*0.1, option.rect.bottom()-0.2*option.rect.height())
                    textrect = QRectF(tl, br)
                    painter.setPen(QPen(QBrush(colorscheme[changereason]), 1))
                    painter.setBrush(QBrush(colorscheme[changereason]))
                    painter.drawRect(textrect)
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

