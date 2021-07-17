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