from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Config import colorscheme

def AddIndexToView(view):
    scene = QGraphicsScene()
    offset = 7
    indexheight = view.height() / 2
    indexwidth = view.width()

    text = scene.addText('Input')
    text.setPos(-indexwidth+15, indexheight)
    scene.addRect(0, indexheight + offset, indexwidth * 0.8, indexheight , QPen(Qt.black), QBrush(colorscheme['Input']))

    text = scene.addText('Working')
    text.setPos(-indexwidth+15, indexheight * 2)
    scene.addRect(0, indexheight * 2 + offset, indexwidth * 0.8, indexheight , QPen(Qt.black), QBrush(Qt.blue))

    text = scene.addText('Output')
    text.setPos(-indexwidth+15, indexheight * 3)
    scene.addRect(0, indexheight * 3 + offset, indexwidth * 0.8, indexheight, QPen(Qt.black), QBrush(colorscheme['Output']))
    view.setScene(scene)

class RotatedHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super(RotatedHeaderView, self).__init__(Qt.Horizontal, parent)
        self.setMinimumSectionSize(20)

    def paintSection(self, painter, rect, logicalIndex ):
        painter.save()
        # translate the painter such that rotate will rotate around the correct point
        painter.translate(rect.x()+rect.width(), rect.y())
        painter.rotate(90)
        # and have parent code paint at this location
        # newrect = QRect(0-rect.width()/2,-20,rect.height(),rect.width())
        newrect = QRect(0 ,0, rect.height(), rect.width())
        super(RotatedHeaderView, self).paintSection(painter, newrect, logicalIndex)
        painter.restore()

    def minimumSizeHint(self):
        size = super(RotatedHeaderView, self).minimumSizeHint()
        size.transpose()
        return size

    def sectionSizeFromContents(self, logicalIndex):
        size = super(RotatedHeaderView, self).sectionSizeFromContents(logicalIndex)
        size.transpose()
        return size
import os
def setStyle(mainguihandle, sourcecodedir):
    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'cst.stylesheet')
    with open(txt, 'r') as txth:
        tabstylesheet = txth.read()
    mainguihandle.maintabwidget.setStyleSheet(tabstylesheet)
    mainguihandle.maintabwidget.setCursor(QCursor(Qt.ArrowCursor))
    # mainguihandle.container_subtab.setStyleSheet(tabstylesheet)
    # # mainguihandle.container_subtab.setCursor(QCursor(Qt.ArrowCursor))
    mainguihandle.networktabwidget.setStyleSheet(tabstylesheet)
    mainguihandle.container_subtab.setStyleSheet(tabstylesheet)
    # mainguihandle.Map.setStyleSheet(tabstylesheet)
    # mainguihandle.ContainerTab.setStyleSheet(tabstylesheet)

    # mainguihandle.container_subtab.setCursor(QCursor(Qt.ArrowCursor))

    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'table.stylesheet')
    with open(txt, 'r') as txth:
        tablestylesheet = txth.read()
    mainguihandle.containerfiletable.setStyleSheet(tablestylesheet)
    mainguihandle.gantttable.setStyleSheet(tablestylesheet)
    mainguihandle.commithisttable.setStyleSheet(tablestylesheet)
    mainguihandle.containerlisttable.setStyleSheet(tablestylesheet)

    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'tree.stylesheet')
    with open(txt, 'r') as txth:
        treestylesheet = txth.read()
    mainguihandle.sagatreeview.setStyleSheet(treestylesheet)

    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'specific.stylesheet')
    with open(txt, 'r') as txth:
        specificstylesheet = txth.read()
    # mainguihandle.commitBttn.setStyleSheet(specificstylesheet)
    mainguihandle.commitmsgEdit.setStyleSheet(specificstylesheet)
    mainguihandle.newcontaineredit.setStyleSheet(specificstylesheet)

    #
    # txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'view.stylesheet')
    # with open(txt, 'r') as txth:
    #     viewstylesheet = txth.read()
    # mainguihandle.containerMapView.setStyleSheet(viewstylesheet)
    #
    # txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'view.stylesheet')
    # with open(txt, 'r') as txth:
    #     viewstylesheet = txth.read()
    # mainguihandle.containerMapView.setStyleSheet(viewstylesheet)


def setstyleoflabel(color, label):
    alpha = 140
    values = "{r}, {g}, {b}, {a}".format(r=color.red(),
                                         g=color.green(),
                                         b=color.blue(),
                                         a=alpha
                                         )
    label.setStyleSheet("QLabel { background-color: rgba(" + values + "); }")