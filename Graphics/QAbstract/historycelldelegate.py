from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from Config import typeRequired, typeInput, typeOutput, colorscheme , JUSTCREATED, UNCHANGED, MD5CHANGED


def createBeginRect(painter, cellrect, qtbrushcolor, squaresidepx, pxlinewidth):
    # center = cellrect.center()
    a =  cellrect.center() - QPointF(squaresidepx/2, squaresidepx/2)
    b =  cellrect.center() + QPointF(squaresidepx/2, squaresidepx/2)
    painter.setPen(QPen(QBrush(Qt.black), pxlinewidth))
    painter.setBrush(QBrush(qtbrushcolor))
    painter.drawRect(QRectF(a,b)) # 4 by 4 rectangle

def createChangedcircle(painter, cellrect, qtbrushcolor, pxradius, pxlinewidth):
    painter.setPen(QPen(QBrush(Qt.black), pxlinewidth))
    painter.setBrush(QBrush(qtbrushcolor))
    painter.drawEllipse(cellrect.center(), pxradius, pxradius);

def createEmptyCell(painter, cellrect):
    painter.setPen(QPen(QBrush(Qt.transparent), 0))
    painter.setBrush(QBrush(Qt.white))
    painter.drawRect(cellrect)

def createSmallEndLine(painter, cellrect, qtbrushcolor):
    a = cellrect.center()+QPointF(1,4)
    b = cellrect.center() -QPointF(1, 4)
    rect = QRectF(a,b)
    painter.setPen(QPen(QBrush(qtbrushcolor), 0))
    painter.setBrush(QBrush(qtbrushcolor))
    painter.drawRect(rect)


class HistoryCellDelegate(QStyledItemDelegate):
    def __init__(self):
        super(HistoryCellDelegate, self).__init__()



    def paint(self,painter:QPainter, option, index:QModelIndex):
        # rect = self.pos()
        # a = option.rect.topLeft()+ QPointF(2,2)
        # b = option.rect.bottomRight() - QPointF(2,2)
        # innerrect = QRectF(a,b)
        r,c,containdata = index.row(),index.column(), index.model().containdata
        typecolor = Qt.red


        # if index.column()==0:
        #     QStyledItemDelegate.paint(self, painter, option, index)
        # else:
        thisvalue = containdata[r][c]
        if thisvalue['type'] is not None:
            typecolor = colorscheme[thisvalue['type']]

        ### Create Line, draw line first so symbol can go over line. Line is drawn in two parts first half and second half
        if thisvalue['status'] in [UNCHANGED,MD5CHANGED]: ## unchanged or md5Changed implies an previous existant
            painter.setPen(QPen(QBrush(typecolor), 2))
            line = QLineF(QPointF(option.rect.topLeft().x(), option.rect.center().y()),
                          QPointF(option.rect.center().x(), option.rect.center().y()))
            painter.drawLine(line);

        if thisvalue['existsInNext']:# second half
            pass
            painter.setPen(QPen(QBrush(typecolor), 2))
            line = QLineF(QPointF(option.rect.center().x(), option.rect.center().y()),
                          QPointF(option.rect.bottomRight().x(), option.rect.center().y()))
            painter.drawLine(line)
        elif thisvalue['md5'] is not None: # this means that its reaching an end.
            createSmallEndLine(painter, option.rect, Qt.black)


        if thisvalue['status'] is None:
            createEmptyCell(painter, option.rect)
        elif thisvalue['status']==JUSTCREATED:
            createBeginRect(painter, option.rect, typecolor, 12, pxlinewidth=2)
        elif thisvalue['status']==UNCHANGED:
            pass
        elif thisvalue['status'] == MD5CHANGED:
            createChangedcircle(painter, option.rect, typecolor, pxradius=6, pxlinewidth=2)
        else:
            painter.setBrush(QBrush(Qt.red))# code should never get here
            painter.drawRect(option.rect)


            # if index.model().containdata[index.row()][index.column()]==NOTEXIST:
            #     painter.setBrush(QBrush(Qt.green))
            #     painter.drawRect(option.rect)
            # elif index.column()==1 or index.model().containdata[index.row()]:
            #     painter.setBrush(QBrush(Qt.blue))


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

    # def setModelData(self, editor:QWidget, model:QAbstractItemModel,index: QModelIndex):
    #     if index.row()==0:
    #         histedtor = HistoryEditor(editor)
    #         model.setData(index,5)
    #     else:
    #         QStyledItemDelegate.setModelData(editor, model, index)

    # def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex):
    #     if index.row()==0:
    #         return 10
    #     else:
    #         return QStyledItemDelegate.sizeHint(option, index)


