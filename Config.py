from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
import os
import sys
BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://10.0.0.227:9500/"
# BASE = "http://127.0.0.1:5000/"
sourcecodedirfromconfig = os.path.abspath(os.path.dirname(__file__))
# comment
typeInput='Input'
typeOutput='Output'
typeRequired='Required'
typeReference='Reference'
typeCommitSpecific='CommitSpecific'
typeContainer='Container'
typeUnversioned='Unversioned'

mapdetailstxt='mapdetails.txt'

ServerOrFront = 'FrontEnd'


MD5CHANGED = 'MD5 Changed'
DATECHANGED = 'Date Changed'
LOCALFILEHEADERADDED = 'New File Header Added'
LOCALFILEHEADERREMOVED = 'File Header Removed'
UPDATEDUPSTREAM = 'MD5 Updated Upstream'
SERVERNEWREVISION = 'File updated in newer Revision'
SERVERFILEDELETED = 'File deleted in newer Revision'
SERVERFILEADDED = 'New File committed in newer Revision'
CHANGEREASONORDER=[MD5CHANGED, LOCALFILEHEADERADDED, SERVERNEWREVISION, UPDATEDUPSTREAM,DATECHANGED,SERVERFILEADDED , SERVERFILEDELETED]
NOTINSYNCREASONSET = set([])


colorscheme = {typeInput: QColor('#D0F0C0'),
               typeRequired:QColor('#03DAC6'),
                typeOutput: QColor('#3700B3'),
                typeUnversioned:QColor(Qt.gray),
               DATECHANGED: Qt.cyan,
               MD5CHANGED: Qt.red,
               UPDATEDUPSTREAM: Qt.magenta,
               LOCALFILEHEADERADDED: Qt.yellow,
               LOCALFILEHEADERREMOVED: Qt.darkCyan,
               SERVERNEWREVISION: QColor(255, 165, 0),
               SERVERFILEDELETED: Qt.black,
               SERVERFILEADDED: Qt.white,
               }

JUSTCREATED="JUSTCREATED"
UNCHANGED="UNCHANGED"


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

testerlogin={
                    'first_name':'',
                   'last_name':'',
                   'email':'',
                    'password':'',
}

debugmode=False
if len(sys.argv)>1:
    if 'debug' ==sys.argv[1]:
        if sys.argv[2]=='waichak':
            testerlogin=waichak
        elif sys.argv[2]=='userc':
            testerlogin=userclogin
        elif sys.argv[2]=='jimmy':
            testerlogin=jimmy




TEMPCONTAINERFN='temp_containerstate.yaml'
TEMPFRAMEFN='temp_frame.yaml'
NEWCONTAINERFN='new_containerstate.yaml'
NEWFRAMEFN='new_frame.yaml'
CONTAINERFN='containerstate.yaml'


# boxwidth = 40
# boxheight = 40
RECTMARGINpx=5

BANNEDNAMES=['EMPTY']

sagaworkingfiles=[CONTAINERFN,TEMPCONTAINERFN,NEWCONTAINERFN,'Main']

hexyellowshades = ['#fefcf3','#faea95','#f5d838','#c2a609','#655604']
hexblueshades = ['#8cbefc', '#2383fa', '#0350ae', '#012045', '#0a233c']