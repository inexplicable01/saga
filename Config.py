from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
import os

BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://10.0.0.227:9500/"
# BASE = "http://127.0.0.1:5000/"

#
JimmyDict = {'Whatever': 999}

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
changedate = 'Date Changed'
changeremoved = 'File Header Removed'
updatedupstream = 'MD5 Updated Upstream'
newrevision = 'File updated in newer Revision'
filedeleted = 'File deleted in newer Revision'
fileadded = 'New File committed in newer Revision'

colorscheme = {typeInput: QColor(124, 0, 255 ), typeOutput: QColor(0, 255, 120), typeRequired: Qt.blue, changedate: Qt.cyan,
                changemd5: Qt.red, updatedupstream: Qt.magenta, changenewfile: Qt.black, changeremoved: Qt.darkCyan,
               newrevision: QColor(255, 165, 0), filedeleted: Qt.black, fileadded: Qt.black}



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

jimmy = {'first_name':'Jimmy',
                   'last_name':'Leong',
                   'email':'jimmyleong113@gmail.com',
                    'password':'passwordJ',
}


privatepackagejohnlee = {'first_name':'John',
                   'last_name':'Lee',
                   'email':'member@example.com',
                    'password':'Password1',
}

privatepackageadmin = {'first_name':'Simon',
                   'last_name':'Genius',
                   'email':'admin@example.com',
                    'password':'PasswordS',
}
privatepackagejames = {'first_name':'James',
                   'last_name':'Bond',
                   'email':'agent@example.com',
                    'password':'Password007',
}

privatepackagechris = {'first_name':'Chris',
                   'last_name':'Everyman',
                   'email':'usercemail@gmail.com',
                    'password':'passwordC',
}
privatepackagedennis = {'first_name':'Dennis',
                   'last_name':'Wong',
                   'email':'userdemail@gmail.com',
                    'password':'passwordD',
}

privatepackageaaron = {'first_name':'aaron',
                   'last_name':'Jones',
                   'email':'useraemail@gmail.com',
                    'password':'passwordA',
}

privatepackagebeth = {'first_name':'beth',
                   'last_name':'asdf',
                   'email':'userbemail@gmail.com',
                    'password':'passwordB',
}
privatepackageevan = {'first_name':'Evan',
                   'last_name':'Port',
                   'email':'usereemail@gmail.com',
                    'password':'passwordE',
}

privatepackageman = {'first_name':'Mr',
                   'last_name':'Manager',
                   'email':'manager@gmail.com',
                    'password':'passwordM',
}
privatepackagecustomer = {'first_name':'Good',
                   'last_name':'Customer',
                   'email':'customer@gmail.com',
                    'password':'passwordCust',
}



testerlogin=userclogin



# Read a input file
sourcefolder = ''

TEMPCONTAINERFN='temp_containerstate.yaml'
TEMPFRAMEFN='temp_frame.yaml'
NEWCONTAINERFN='new_containerstate.yaml'
NEWFRAMEFN='new_frame.yaml'
CONTAINERFN='containerstate.yaml'


boxwidth = 40
boxheight = 40
RECTMARGINpx=5

BANNEDNAMES=['EMPTY']