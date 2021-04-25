from PyQt5.QtCore import *

# BASE = "http://fatpanda1985.pythonanywhere.com/"
BASE = "http://127.0.0.1:5000/"
import os
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

testerlogin=userclogin

colorscheme = {typeInput: Qt.yellow, typeOutput: Qt.green, typeRequired: Qt.blue, changedate: Qt.cyan,\
               changemd5: Qt.red, changenewfile: Qt.black, changeremoved: Qt.darkCyan}

boxwidth = 40
boxheight = 40
RECTMARGINpx=5