from PyQt5.QtWidgets import *
from PyQt5 import uic


import requests
import json

# from PyQtTesting import BASE
from os.path import join
from Config import sourcecodedirfromconfig
import re
from SagaGuiModel import sagaguimodel
import random

import string
from SagaCore.Section import Section
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
class inviteUserToSectionDialog(QDialog):
    ## This might have duplicated the Sign up dialog.
    def __init__(self, mainguihandle):
        super().__init__()
        self.mainguihandle=mainguihandle
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "inviteUserToSection.ui"), self)
        self.emailfield.textChanged[str].connect(self.entrychanged)
        self.sentInviteBttn.clicked.connect(self.invite)
        self.sentInviteBttn.setEnabled(False)
        self.emailfield.setText('')
        self.exitlbl.mousePressEvent = self.exit
        self.sectionlbl.setText('Invite Users to your Section :' + sagaguimodel.usersess.current_sectionname)
        self.exec_()

    def entrychanged(self):
        emails =  self.emailfield.text().split(',')
        emailsValid = True
        for i, email in enumerate(emails):
            email = email.strip()
            if not (re.fullmatch(regex, email)):
                emailsValid = False
            emails[i] = email
        if emailsValid:
            self.sentInviteBttn.setEnabled(True)
            self.wrnlbl.setText('')
            self.emails= emails
        else:
            self.sentInviteBttn.setEnabled(False)
            self.wrnlbl.setText('Entry must be valid emails seperated by comma and/or spaces')

    # self.usersession['current_sectionid']

    def invite(self):
        success, servermessage = sagaguimodel.addEmailsToSection(self.emails)
        if success:
            self.emailfield.setText('')
            self.update()
            self.sentInviteBttn.setEnabled(False)
            self.wrnlbl.setText(self.emailfield.text() + ' Users invited!!')

        else:
            self.wrnlbl.setText('Unable to invite Users')

    def exit(self, event):
        self.accept()
    # def newSection(self):
    #     if self.exec_() == QDialog.Accepted:
    #         status, newsection , newsectionsuccess = sagaguimodel.sagaapicall.newSectionCall(newsectionname=self.newsectionedit.text(), newsectiondesp=self.sectiondescedit.text())
    #         return status, newsection , newsectionsuccess
    #     else:
    #         return None, None , False