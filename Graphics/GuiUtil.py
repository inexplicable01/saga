from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaGuiModel.GuiModelConstants import colorscheme, CONTAINERFN , TEMPCONTAINERFN  , roleRequired,roleInput,roleOutput

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
    with open(os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'qttab.stylesheet'), 'r') as txth:
        tabstylesheet = txth.read()
    tabstylesheet=tabstylesheet.replace("TABCOLOR","#505160")
    tabstylesheet = tabstylesheet.replace("TEXTCOLOR", "white")
    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'table.stylesheet')
    with open(txt, 'r') as txth:
        tablestylesheet = txth.read()
    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'tree.stylesheet')
    with open(txt, 'r') as txth:
        treestylesheet = txth.read()
    # mainguihandle.sagatreeview.setStyleSheet(treestylesheet)
    with open(os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'textedit.stylesheet'), 'r') as txth:
        textedit = txth.read()
    txt = os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'qpushbutton.stylesheet')
    with open(txt, 'r') as txth:
        qpushbuttonstylesheet = txth.read()
    with open(os.path.join(sourcecodedir, 'Graphics', 'StyleSheet', 'qheader.stylesheet'), 'r') as txth:
        qheader = txth.read()
    # mainguihandle.centralwidget.setStyleSheet(tabstylesheet)
    mainguihandle.setStyleSheet(tabstylesheet +qpushbuttonstylesheet + textedit +qheader)
    mainguihandle.ContainerTab.setStyleSheet(tabstylesheet+qpushbuttonstylesheet +textedit+qheader)
    mainguihandle.networktabwidget.setStyleSheet(tabstylesheet+qpushbuttonstylesheet +textedit+qheader)
    mainguihandle.containerfiletable.setStyleSheet(qheader)
    mainguihandle.maintabwidget.setCursor(QCursor(Qt.ArrowCursor))
    # mainguihandle.container_subtab.setStyleSheet(tabstylesheet)
    # # mainguihandle.container_subtab.setCursor(QCursor(Qt.ArrowCursor))
    # mainguihandle.networktabwidget.setStyleSheet(tabstylesheet)
    # mainguihandle.container_subtab.setStyleSheet(tabstylesheet)
    # mainguihandle.Map.setStyleSheet(tabstylesheet)
    # mainguihandle.ContainerTab.setStyleSheet(tabstylesheet)

    # mainguihandle.containerfiletable.setStyleSheet(tablestylesheet)
    # mainguihandle.gantttable.setStyleSheet(tablestylesheet)
    # mainguihandle.commithisttable.setStyleSheet(tablestylesheet)
    # mainguihandle.containerlisttable.setStyleSheet(tablestylesheet)

    # mainguihandle.commitBttn.setStyleSheet(specificstylesheet)
    # mainguihandle.commitmsgEdit.setStyleSheet(specificstylesheet)
    # mainguihandle.newcontaineredit.setStyleSheet(specificstylesheet)

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

def makeganttchartlegend(view):
    scene = QGraphicsScene()
    print(view.event)
    view.setScene(scene)
    # print(view.size())

    print(view.sceneRect())
    rect = view.rect()
    w = rect.width()*1.2
    # w = option.rect.width()
    h = rect.height()*1.2

    borderrect = QGraphicsRectItem(QRectF(rect))
    borderrect.setBrush(QBrush(Qt.darkYellow))
    scene.addItem(borderrect)

    hinternvals= h/4

    e = QGraphicsEllipseItem(0.0, 0.0, w/4, hinternvals*0.9)
    e.setBrush(QBrush(colorscheme[roleRequired], style = Qt.SolidPattern))
    scene.addItem(e)
    centertext = QGraphicsTextItem('No. of Commits')
    centertext.setPos(QPointF(w/4,0))

    scene.addItem(centertext)
    ## how many symbols

    topleft = QPointF(0,hinternvals)
    symbolrect = QRectF(QPointF(topleft),
                        QPointF(topleft+ QPointF(hinternvals * 0.9, hinternvals * 0.9)))
    r1 = QGraphicsRectItem(symbolrect)
    r1.setBrush(QBrush(colorscheme[roleOutput]))
    scene.addItem(r1)
    inputtext = QGraphicsTextItem('No. of Output Updates')
    inputtext.setPos(QPointF(w/4,hinternvals))
    scene.addItem(inputtext)

    topleft = QPointF(0,hinternvals*2)
    symbolrect = QRectF(QPointF(topleft),
                        QPointF(topleft+ QPointF(hinternvals * 0.9, hinternvals * 0.9)))
    r2 = QGraphicsRectItem(symbolrect)
    r2.setBrush(QBrush(colorscheme[roleInput]))
    scene.addItem(r2)
    outputtext = QGraphicsTextItem('No. of Input Updates')
    outputtext.setPos(QPointF(w/4,hinternvals*2))
    scene.addItem(outputtext)

    view.setBackgroundBrush(QBrush(Qt.black, Qt.SolidPattern));
    # view.set
    #     w = option.rect.width()
    #     h = option.rect.height()
    #     ## how many symbols
    #
    #
    #
    #     painter.setPen(QPen(QBrush(Qt.black), 2))
    #     painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['outputchanged']))
    # painter.setPen(QPen(QBrush(Qt.transparent), 2))
    # painter.setBrush(QBrush(Qt.yellow))
    # painter.drawEllipse(symmidpoint, w * 0.4, h * 0.4)
    # painter.setPen(QPen(QBrush(Qt.black), 2))
    # painter.drawText(option.rect, Qt.AlignCenter, str(len(cellinfo['frames'])))

    # def drawoutputchangedsymbol(painter, option, cellinfo):

    #
    # def drawinputchangedsymbol(painter, option, cellinfo):
    #     w = option.rect.width()
    #     h = option.rect.height()
    #     ## how many symbols
    #     symmidpoint = option.rect.topLeft() + QPointF(w * 1 / 4, h / 2)
    #     symbolrect = QRectF(QPointF(symmidpoint + QPointF(-w * 0.08, -h * .2)),
    #                         QPointF(symmidpoint + QPointF(w * 0.08, h * 0.2)))
    #
    #     painter.setBrush(QBrush(colorscheme[roleOutput]))
    #     painter.drawRect(symbolrect)
    #     painter.setPen(QPen(QBrush(Qt.black), 2))
    #     painter.drawText(symbolrect, Qt.AlignCenter, str(cellinfo['inputchanged']))
    #     # painter.drawRect(QRectF(midpoint, option.rect.topRight()))
    #
    # if len(cellinfo['frames']) > 0: