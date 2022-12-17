from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QStyleOptionGraphicsItem, QWidget

from PyQt5.QtGui import *
from PyQt5.QtCore import *

import math
from SagaGuiModel.GuiModelConstants import roleInput,roleOutput,roleRequired, colorscheme
from SagaCore.ContainerItem import ContainerItem
from Graphics.PYQTView.ContainerDetailMap.EntityImage import EntityImage
from .ViewDefinitions import *
from os.path import join,splitext
from Config import sourcecodedirfromconfig
from SagaCore.Track import FileTrack, FolderTrack

class FileRect(QGraphicsRectItem):
    ##This is the Rect of the file.  In Container mode,  it shows input and out.
    ## In connection mode, it shows out to in.
    def __init__(self, parent, locF,idx,citem:ContainerItem, role, containeridtoname, flip = False):

        if role=='Connection':
            boxgap = 0.1
            # self.boxgap = 0.1
        else:
            boxgap = 0
            # self.boxgap = 0
        super().__init__(locF,70 + idx*filerectboxheight,containerBoxWidth * (1 + boxgap),100,parent)

        if role=='Connection':
            grad = QLinearGradient(self.rect().topLeft(), self.rect().topRight())
            grad.setColorAt(1, colorscheme['Input'])
            grad.setColorAt(0, colorscheme['Output'])

            # self.setBrush(QBrush(grad))
            # self.setPen(QPen(QBrush(grad), 2))
            offset = 0.25 #print('')#nothing yet
        self.role = role
        self.citem = citem
        # EntityImage(containerBoxWidth*0.1,10,150,40,self,citem)
        self.containeridtoname = containeridtoname
        self.flip = flip

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        # qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Container_Read.png"))

        # draw border
        # borderect = QRectF(self.boundingRect().x(), self.boundingRect().y(), self.boundingRect().width(), filerectcolourboxheight)
        # painter.drawImage(picrect, qpic)

        def producedotdotdotstring(text, pxlimit, fontfamily, fontsize):
            pxwidthoftext = QFontMetrics(QFont(fontfamily, fontsize)).width(text)
            indx=-1
            if QFontMetrics(QFont("times", fontsize)).width('...') > pxlimit:
                print('fontsize for knowledge network container text is set too large.  Str ... functionality failed.')
                return text
            if pxwidthoftext>pxlimit:
                while pxwidthoftext>pxlimit:
                    dottext = text[0:indx] + '...'#needs to add dots to string
                    pxwidthoftext = QFontMetrics(QFont("times", fontsize)).width(dottext)
                    indx+=-1
                return dottext
            else:
                return text


        borderpx = 2
        painter.setPen(QPen(QBrush(colorscheme[self.role]), borderpx))
        painter.drawRect(self.boundingRect())
        c = colorscheme[self.role]
        # c.lighter()
        qtrans = QColor(c.red(),c.green(),c.blue(),133)
        if self.role=='Connection':
            painter.fillRect(self.boundingRect(), QBrush(QColor(Qt.transparent)))
        else:
            painter.fillRect(self.boundingRect(), QBrush(qtrans))

        # define citemimagerect
        citemimgx_px = 50
        citemimgy_px = 50
        if self.flip:
            picmargin = self.boundingRect().width() - 60 - citemimgx_px
        else:
            picmargin = 60

        x = self.boundingRect().x() + picmargin
        y = self.boundingRect().y()+ self.boundingRect().height()/2 - citemimgy_px/2

        citemimgrect = QRectF(x,y , citemimgx_px, citemimgy_px)

        filename, file_extension = splitext(self.citem.reftrack.entity)

        if file_extension in ['.docx', '.doc']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "Word.png"))
        elif file_extension in ['.pptx', '.ppt']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "ppticon.png"))
        elif file_extension in ['.xls', '.xlsx']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "excelicon.png"))
        elif file_extension in ['.mp4']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "mp4icon.png"))
        elif file_extension in ['.txt']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "txticon.png"))
        elif file_extension in ['.pdf']:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "pdficon.png"))
        else:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "genericfile.png"))

        if type(self.citem.reftrack) == FolderTrack:
            qpic = QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "foldericon.png"))

        # qpic= QImage(join(sourcecodedirfromconfig, "Graphics", "FileIcons", "genericfile.png"))
        painter.drawImage(citemimgrect, qpic)

        #draw Text
        textmargin = 10
        x = self.boundingRect().x() +textmargin
        y = self.boundingRect().y()+ fileboxtitletextheight+10+borderpx +citemimgy_px
        textwidth = (picmargin+citemimgx_px/2 - textmargin)*2
        textheight = 20
        # citemimgrect = QRectF(x,y , citemimgx_px, citemimgy_px)
        textRect =QRectF(x, y,  textwidth,textheight)
        painter.setPen(QPen(QBrush(Qt.black), borderpx))

        entitydisplayname = producedotdotdotstring(self.citem.reftrack.entity, textRect.width(), "times", fontsize)
        painter.drawText(textRect,Qt.AlignCenter, entitydisplayname)


        ###DrawLine and triagle
        # arrowlength
        if self.role=='Connection':
            arrowlength = 200
        else:
            arrowlength = 80
        if self.flip:
            x1 = self.boundingRect().x() + picmargin
        else:
            x1 = self.boundingRect().x() + picmargin + citemimgx_px
        y1 = self.boundingRect().y()+ self.boundingRect().height()/2
        Q1 = QPointF(x1, y1)
        if self.flip:
            Q2 = QPointF(x1 - arrowlength,y1)
        else:
            Q2 = QPointF(x1 + arrowlength,y1)

        painter.setBrush(QBrush(Qt.black))
        painter.drawLine(QLineF(Q1,Q2))
        ###DrawTriangleonLine
        pi = math.pi

        tri_px=10
        a = (90)/180.0*pi
        p1 = Q2 + QPointF(tri_px*math.cos(a),-tri_px*math.sin(a))
        b = (270)/180.0*pi
        p2 = Q2 + QPointF(tri_px*math.cos(b),-tri_px*math.sin(b))
        c = 0/180.0*pi
        if self.flip:
            p3 = Q2 - QPointF(tri_px*2 * math.cos(c), -2*tri_px * math.sin(c))
        else:
            p3 = Q2 + QPointF(tri_px*2 * math.cos(c), -2*tri_px * math.sin(c))

        arrowcoord = QPolygonF([p1,p2,p3])
        # painter.setBrush(QBrush(Qt.blue))
        painter.drawPolygon(arrowcoord)



        if self.role==roleInput:
            painter.setPen(QPen(Qt.black, 4))
            x1 = self.boundingRect().x() + 10
            y1 = self.boundingRect().y() + 10
            inputtextrect = QRectF(x1,y1,100,12)
            painter.drawText(inputtextrect, Qt.AlignCenter, 'From Container :' + self.containeridtoname[self.citem.refcontainerid])
            # self.containertext.setDefaultTextColor(Qt.black)
        # For generating Output specific boxes
        elif self.role==roleOutput:
            outputtextrectheight = 10
            outputboxwidth= 150
            y1 = self.boundingRect().y() + 10
            outputtextrect = QRectF(p3.x(),y1,outputboxwidth,outputtextrectheight)
            painter.drawText(outputtextrect, Qt.AlignCenter, 'To Containers: ')

            borderpx = 2
            outputboxheight = 50
            painter.setPen(QPen(QBrush(colorscheme[self.role]), borderpx))
            outputcontainerrect = QRectF(p3.x(), y1 + outputtextrectheight + 5, outputboxwidth, outputboxheight)
            painter.setBrush(QBrush(Qt.transparent))
            painter.drawRect(outputcontainerrect)
            painter.fillRect(outputcontainerrect, QBrush(Qt.transparent))
            for idx,outputcontainerid in enumerate(self.citem.refcontainerid):
                if outputcontainerid in self.containeridtoname:
                    y1 = y1 + 20
                    outputtextrect = QRectF(p3.x(), y1, outputboxwidth, outputtextrectheight)
                    painter.drawText(outputtextrect, Qt.AlignCenter, self.containeridtoname[outputcontainerid])
        # elif self.role == "Connection":
        #     painter.setPen(QPen(Qt.black, 4))
        #     x1 = self.boundingRect().x() + 10
        #     y1 = self.boundingRect().y() + 10
        #     inputtextrect = QRectF(x1,y1,100,12)
        #     painter.drawText(inputtextrect, Qt.AlignCenter, self.containeridtoname[self.citem.refcontainerid])
                    # containername =
                    # self.containertext = QGraphicsTextItem(containername, parent=self)
                    # self.containertext.setDefaultTextColor(Qt.black)
                    # self.containertext.setPos(self.rect().topRight()+QPoint(-50, -20 -idx*15))
