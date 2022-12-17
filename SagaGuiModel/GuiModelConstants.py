from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
from SagaCore import roleInput, roleOutput, roleRequired, roleUnversioned


TEMPCONTAINERFN='temp_containerstate.yaml'
TEMPFRAMEFN='temp_frame.yaml'
NEWCONTAINERFN='new_containerstate.yaml'
NEWFRAMEFN='new_frame.yaml'
CONTAINERFN='containerstate.yaml'

sagaworkingfiles=[CONTAINERFN,TEMPCONTAINERFN,NEWCONTAINERFN,'Main']

typeReference='Reference'
typeCommitSpecific='CommitSpecific'
typeContainer='Container'



mapdetailstxt='mapdetails.txt'

MD5CHANGED = 'MD5 Changed'
DATECHANGED = 'Date Changed'
LOCALCITEMNAMEADDED = 'New File Header Added'
LOCALCITEMNAMEREMOVED = 'File header Removed'
UPDATEDUPSTREAM = 'MD5 Updated Upstream'
SERVERNEWREVISION = 'File updated in newer Revision'
SERVERFILEDELETED = 'File deleted in newer Revision'
SERVERFILEADDED = 'New File committed in newer Revision'
CHANGEREASONORDER=[MD5CHANGED, LOCALCITEMNAMEADDED, SERVERNEWREVISION, UPDATEDUPSTREAM,DATECHANGED,SERVERFILEADDED , SERVERFILEDELETED]
NOTINSYNCREASONSET = set([])
NEEDSDOCTOR = 'NEEDSDOCTOR'
TOBECOMMITTED = 'To be Committed'




JUSTCREATED="JUSTCREATED"
UNCHANGED="UNCHANGED"

SIGNINPAGEINDEX = 0
CREATEACCINDEX = 1
LOGININDEX = 2
MAINAPPINDEX = 3


##Graphical Definitions
colorscheme = {roleInput: QColor('#D9B44A'),
               roleRequired:QColor('#75B1A9'),
                roleOutput: QColor('#4F6457'),
                roleUnversioned:QColor(Qt.gray),
               DATECHANGED: Qt.cyan,
               MD5CHANGED: Qt.red,
               UPDATEDUPSTREAM: Qt.magenta,
               LOCALCITEMNAMEADDED: Qt.yellow,
               LOCALCITEMNAMEREMOVED: Qt.darkCyan,
               SERVERNEWREVISION: QColor(255, 165, 0),
               SERVERFILEDELETED: Qt.black,
               SERVERFILEADDED: Qt.white,
                'Connection':QColor(Qt.green)
               }

foregroundcolorscheme = {roleInput: Qt.black,
               roleRequired:Qt.black,
                roleOutput: Qt.white,
                roleUnversioned:Qt.black,
               DATECHANGED: Qt.cyan,
               MD5CHANGED: Qt.red,
               UPDATEDUPSTREAM: Qt.magenta,
               LOCALCITEMNAMEADDED: Qt.yellow,
               LOCALCITEMNAMEREMOVED: Qt.darkCyan,
               SERVERNEWREVISION: QColor(255, 165, 0),
               SERVERFILEDELETED: Qt.black,
               SERVERFILEADDED: Qt.white,
               }


hexyellowshades = ['#fefcf3','#faea95','#f5d838','#c2a609','#655604']
hexinputshades = ['#F88379','#FF7F50','#F28C28','#FFAC1C','#CD7F32']
hexblueshades = ['#8cbefc', '#2383fa', '#0350ae', '#012045', '#0a233c']
RECTMARGINpx=5