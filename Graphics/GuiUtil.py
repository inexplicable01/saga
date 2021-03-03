from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def AddIndexToView(view):
    scene = QGraphicsScene()
    offset = 7
    indexheight = view.height() / 5
    indexwidth = view.width() / 2

    text = scene.addText('Input')
    text.setPos(-indexwidth+20, indexheight)
    scene.addRect(0, indexheight + offset, indexwidth * 0.8, indexheight , QPen(Qt.black), QBrush(Qt.yellow))

    text = scene.addText('Required')
    text.setPos(-indexwidth+20, indexheight * 2)
    scene.addRect(0, indexheight * 2 + offset, indexwidth * 0.8, indexheight , QPen(Qt.black), QBrush(Qt.blue))

    text = scene.addText('Output')
    text.setPos(-indexwidth+20, indexheight * 3)
    scene.addRect(0, indexheight * 3 + offset, indexwidth * 0.8, indexheight, QPen(Qt.black), QBrush(Qt.green))
    view.setScene(scene)