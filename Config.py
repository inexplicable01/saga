from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
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


mechuser1login = {'first_name':'Bob',
                   'last_name':'Smith',
                   'email':'user1@mechdemo.com',
                    'password':'user1password',
}

mechuser2login = {'first_name':'Jane',
                   'last_name':'Doe',
                   'email':'user2@mechdemo.com',
                    'password':'user2password',
}

userclogin = {'first_name':'default',
                   'last_name':'lee',
                   'email':'usercemail@gmail.com',
                    'password':'passwordC',
}

oleglogin = {'first_name':'o',
                   'last_name':'oleg',
                   'email':'o.petrenko@gmail.com',
                    'password':'password',
}



waichak = {'first_name':'Waichak',
                   'last_name':'Luk',
                   'email':'waichak.luk@gmail.com',
                    'password':'passwordW',
}

testerlogin=waichak


colorscheme = {typeInput: QColor(124, 0, 255 ), typeOutput: QColor(0, 255, 120), typeRequired: Qt.blue, changedate: Qt.cyan,\
               changemd5: Qt.red, changenewfile: Qt.black, changeremoved: Qt.darkCyan}

TEMPCONTAINERFN='temp_containerstate.yaml'
TEMPFRAMEFN='temp_frame.yaml'
NEWCONTAINERFN='new_containerstate.yaml'
NEWFRAMEFN='new_frame.yaml'
CONTAINERFN='containerstate.yaml'


boxwidth = 40
boxheight = 40
RECTMARGINpx=5