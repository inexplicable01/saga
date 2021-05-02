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