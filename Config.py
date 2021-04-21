from PyQt5.QtCore import *
import os
BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://127.0.0.1:5000/"
WorldMapDir = 'ContainerMapWorkDir'
sagaGuiDir = os.getcwd()

# comment
typeInput='Input'
typeOutput='Output'
typeRequired='Required'
mapdetailstxt='mapdetails.txt'

ServerOrFront = 'FrontEnd'

changenewfile = 'New File Header Added'
changemd5 = 'MD5 Changed'
changedate = 'MD5 Changed'
changeremoved = 'File Header Removed'

colorscheme = {typeInput: Qt.yellow, typeOutput: Qt.green, typeRequired: Qt.blue, changedate: Qt.cyan,\
               changemd5: Qt.red, changenewfile: Qt.black, changeremoved: Qt.darkCyan}

boxwidth = 40
boxheight = 40
RECTMARGINpx=5