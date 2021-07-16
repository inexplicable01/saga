from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import os
import glob
from Config import typeRequired, typeInput, typeOutput, colorscheme , JUSTCREATED, UNCHANGED, MD5CHANGED


def arrowpolygon(rect: QRectF, xlocpct, direc):
    # All x pixels are measured from left of rect
    width = rect.bottomRight().x() - rect.topLeft().x()
    midp =  xlocpct*width + rect.topLeft().x()##
    p1 = QPointF(midp, rect.top())
    p2 = QPointF(midp, rect.bottom())
    if direc == 'right':
        p3 = QPointF(midp + 10, rect.center().y())
    elif direc == 'left':
        p3 = QPointF(midp - 10, rect.center().y())
    elif direc=='NoOutput':
        midcoord = QPointF(rect.topLeft().x()+2*xlocpct*width, rect.center().y())
        p1 = midcoord + QPoint(-4,4)
        p2 = midcoord + QPoint(4, 4)
        p3 = midcoord + QPoint(4, -4)
        p4 = midcoord + QPoint(-4, -4)
        return QPolygonF([p1,p2,p3,p4])
    else:
        raise ('direc not well set in SagaTree Model')
    return QPolygonF([p1, p2, p3])

class SagaTreeDelegate(QStyledItemDelegate):
    def __init__(self):
        super(SagaTreeDelegate, self).__init__()

    def paint(self,painter:QPainter, option, index:QModelIndex):
        # rect = self.pos()
        # a = option.rect.topLeft()+ QPointF(2,2)
        # b = option.rect.bottomRight() - QPointF(2,2)
        # innerrect = QRectF(a,b)
        # r,c,containdata = index.row(),index.column(), index.model().containdata
        # typecolor = Qt.red
        # self.sectionconnection[containerid]
        selectedcontainerid = index.model().selectedcontainerid
        if selectedcontainerid:
            inputspaths = index.model().inputconnections[selectedcontainerid]
            outputspaths = index.model().outputconnections[selectedcontainerid]
            selectedcontainerrownum = index.model().rowmapper[selectedcontainerid]
        else:
            inputspaths = {'hori': {}, 'vert': {}}
            outputspaths = {'hori': {}, 'vert': {}}
            selectedcontainerrownum =0



        currow = index.internalPointer().data(1)


        if index.column()==0:
            if selectedcontainerrownum==currow:
                # print(index.model().data[0])
                cellleftmid = QPointF(option.rect.topLeft().x(),option.rect.center().y())
                cellrightmid = QPointF(option.rect.bottomRight().x(), option.rect.center().y())
                painter.setPen(QPen(QBrush(Qt.red), 4))
                painter.setBrush(QBrush(Qt.red))
                painter.drawRect(option.rect)
                painter.setPen(QPen(QBrush(Qt.white), 4))
                painter.drawText(option.rect, Qt.AlignLeft, index.internalPointer().data(0))
            elif currow in inputspaths['hori'].keys():
                if inputspaths['hori'][currow]['linetype']=='file':
                    painter.setPen(QPen(QBrush(Qt.white), 1))
                    painter.setBrush(QBrush(Qt.yellow))
                    painter.drawRect(option.rect)
                    painter.setPen(QPen(QBrush(Qt.black), 4))
                    painter.drawText(option.rect, Qt.AlignLeft, index.internalPointer().data(0))
                    ## this is container maybe a faded block instead
                else:
                    QStyledItemDelegate.paint(self, painter, option, index)
            elif currow in outputspaths['hori'].keys():
                if outputspaths['hori'][currow]['linetype'] == 'file':
                    painter.setPen(QPen(QBrush(Qt.white), 1))
                    painter.setBrush(QBrush(Qt.cyan))
                    painter.drawRect(option.rect)
                    painter.setPen(QPen(QBrush(Qt.black), 4))
                    painter.drawText(option.rect, Qt.AlignLeft, index.internalPointer().data(0))
                else:
                    ## this is container maybe a faded block instead
                    QStyledItemDelegate.paint(self, painter, option, index)
            else:
                QStyledItemDelegate.paint(self, painter, option, index)
        elif index.column()==1:

            # for fromcontainerid, pathdetails in inputspaths.items():

            # print('currow', currow)
            # print('kryd', inputspaths.keys())
            if len(inputspaths['hori'].keys())>0:
                if currow in inputspaths['hori'].keys():

                    length = inputspaths['hori'][currow]['length']## misnomer? length here means fraction of gap from left
                    direc = inputspaths['hori'][currow]['direc']
                    width = option.rect.bottomRight().x() -option.rect.topLeft().x()
                    startpoint = QPointF(option.rect.topLeft().x() + width*length,option.rect.center().y())
                    cellrightmid = QPointF(option.rect.bottomRight().x(), option.rect.center().y())
                    painter.setPen(QPen(QBrush(Qt.yellow), 1))
                    painter.drawLine(QLineF(startpoint, cellrightmid))
                    xlocpct = (1-length)/2 + length
                    arrowcoord = arrowpolygon(option.rect, xlocpct, direc)
                    painter.setBrush(QBrush(Qt.yellow))
                    painter.drawPolygon(arrowcoord)
                # print('kryd', inputspaths.keys())

                if currow in inputspaths['vert'].keys():
                    for i, xloc in enumerate(inputspaths['vert'][currow]['xlocs']): # could probanly use zip:
                        width = option.rect.bottomRight().x() - option.rect.topLeft().x()
                        length = inputspaths['vert'][currow]['length'][i]
                        if length=='full':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.top())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.bottom())
                        elif length=='bottomhalf':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.center().y())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.bottom())
                        elif length=='tophalf':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.top())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.center().y())
                        painter.setPen(QPen(QBrush(Qt.yellow), 1))
                        painter.drawLine(QLineF(celltop, cellbottom))
            else:
                painter.setPen(QPen(QBrush(Qt.transparent), 2))
                painter.setBrush(QBrush(Qt.green))
                painter.drawRect(option.rect)
        elif index.column() == 2:
            if len(outputspaths['hori'].keys()) > 0:
                if currow in outputspaths['hori'].keys():

                    length = outputspaths['hori'][currow]['length']  ## misnomer? length here means fraction of gap from left
                    direc = outputspaths['hori'][currow]['direc']
                    width = option.rect.bottomRight().x() - option.rect.topLeft().x()
                    startpoint = QPointF(option.rect.topLeft().x(), option.rect.center().y())
                    cellrightmid = QPointF(option.rect.topLeft().x() +  width*length, option.rect.center().y())
                    painter.setPen(QPen(QBrush(Qt.cyan), 1))
                    painter.drawLine(QLineF(startpoint, cellrightmid))
                    xlocpct= length/2
                    arrowcoord = arrowpolygon(option.rect, xlocpct, direc)
                    painter.setBrush(QBrush(Qt.cyan))
                    painter.drawPolygon(arrowcoord)

                if currow in outputspaths['vert'].keys():
                    for i, xloc in enumerate(outputspaths['vert'][currow]['xlocs']): # could probanly use zip:
                        width = option.rect.bottomRight().x() - option.rect.topLeft().x()
                        length = outputspaths['vert'][currow]['length'][i]
                        if length=='full':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.top())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.bottom())
                        elif length=='bottomhalf':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.center().y())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.bottom())
                        elif length=='tophalf':
                            celltop = QPointF(option.rect.topLeft().x() + width *xloc,option.rect.top())
                            cellbottom = QPointF(option.rect.topLeft().x() + width *xloc, option.rect.center().y())
                        painter.setPen(QPen(QBrush(Qt.cyan), 1))
                        painter.drawLine(QLineF(celltop, cellbottom))
            else:
                painter.setPen(QPen(QBrush(Qt.transparent), 2))
                painter.setBrush(QBrush(Qt.green))
                painter.drawRect(option.rect)


            # if index.model().containdata[index.row()][index.column()]==NOTEXIST:
            #     painter.setBrush(QBrush(Qt.green))
            #     painter.drawRect(option.rect)
            # elif index.column()==1 or index.model().containdata[index.row()]:
            #     painter.setBrush(QBrush(Qt.blue))

