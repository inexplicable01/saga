from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Config import typeInput,typeRequired,typeOutput, CONTAINERFN
from os.path import join, normpath
import os
from os.path import join
from Config import sourcecodedirfromconfig
from shutil import copyfile


class SagaFolderDelegate(QStyledItemDelegate):
    def __init__(self):
        super(SagaFolderDelegate, self).__init__()

    def paint(self,painter:QPainter, option, index:QModelIndex):
        filepath = index.model().filePath(index)
        if os.path.isdir(filepath) and index.column()==0:
            if os.path.exists(join(filepath, CONTAINERFN)):
                baseindex = index.model().index('C:/')
                print(baseindex.data())
                print(index.model().rowCount(baseindex))
                tl = option.rect.topLeft()
                br = tl + QPointF(option.rect.height(), option.rect.height())
                iconrect = QRectF(tl, br)

                qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Container.png"))
                painter.drawImage(iconrect, qpic)

                tl2 = tl + QPointF(option.rect.height(), 0)
                textrect = QRectF(tl2, option.rect.bottomRight())
                painter.drawText(textrect, Qt.AlignLeft, index.model().data(index))
            else:
                return QStyledItemDelegate.paint(self, painter, option, index)
        else:
            return QStyledItemDelegate.paint(self, painter, option, index)


class SagaFolderDialog(QDialog):
    def __init__(self, dir_path):
        super().__init__()

        self.model = SagaFileSystemModel()
        self.model.setRootPath(dir_path)

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "sagafolderDialog.ui"), self)
        self.sagafolderstreeview.setModel(self.model)

        self.sagafolderstreeview.setItemDelegate(SagaFolderDelegate())
        self.sagafolderstreeview.clicked.connect(self.treeclicked)
        self.containerselected = False
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        path = dir_path


        folders = []
        while 1:
            path, folder = os.path.split(path)

            if folder != "":
                folders.append(folder)
            elif path != "":
                folders.append(path)

                break
        folders.reverse()

        # for ele in folders:
        print(folders)
        if self.model.index(folders[0]).isValid():
            baseindex = self.model.index(folders[0])
            # print(baseindex.data())
            # print(self.model.rowCount(baseindex))
            curindex = baseindex
            self.sagafolderstreeview.expand(curindex)
            for ele in folders[1:]:
                # print(ele)
                curindex = curindex.child(0,0)
                self.sagafolderstreeview.expand(curindex)
                # print('indexdata' + curindex.data())
        self.sagafolderstreeview.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sagafolderstreeview.header().resizeSection(1, 100)
        self.sagafolderstreeview.header().resizeSection(2, 100)
        self.sagafolderstreeview.header().resizeSection(3, 100)

    def treeclicked(self, index):
        # print(index.row(), index.column(), index.internalPointer().data(0))
        # index.internalPointer.setSelected(True)
        filepath = index.model().filePath(index)
        if os.path.exists(join(filepath, CONTAINERFN)):
            self.containerselected = True
            self.containeryaml  = join(filepath, CONTAINERFN)
        else:
            self.containerselected = False
            self.containeryaml = None

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.containerselected)


    def getfilepath(self):
        if self.exec_() == QDialog.Accepted:
            return self.containeryaml
        else:
            None

# counter = 1
class SagaFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        # self.counter=1

    def hasChildren(self, parent=None, *args, **kwargs):

        filepath = self.filePath(parent)
        if os.path.isdir(filepath):
            if os.path.exists(join(filepath, CONTAINERFN)):
                return False
        return QDirIterator(self.filePath(parent)).hasNext()


