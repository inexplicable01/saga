from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtGui import *
import time

# from PyQt5.QtCore import *

import os
import sys
import requests
import json
# from Config import testerlogin

from Graphics.QAbstract.ProfileListModel import ProfileListModel
from Graphics.PopUps.NewContainerDialog import newContainerDialog
# from PyQtTesting import BASE
from SagaGuiModel import sagaguimodel
from SagaGuiModel.DevConstants import testerlogin
from datetime import datetime
from os.path import join
from Config import sourcecodedirfromconfig,chosenlogin
from SagaGuiModel.GuiModelConstants import *
from Graphics.PopUps.LoadingScreen import LoadingGif

import random
import string





def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

class LoginScreen(QDialog):
    def __init__(self, mainguihandle, sagaguimodel,widget):
        super(LoginScreen, self).__init__()
        # uic.loadUi("login.ui",self)
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "login.ui"), self)


        self.movie = QMovie('Graphics/GIFS/Spinner-1s-200px.gif')
        self.mainguihandle=mainguihandle
        self.sagaguimodel = sagaguimodel
        self.widget = widget
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        # self.error.setGeometry(QtCore.QRect(25, 25, 200, 200))
        # self.error.setMinimumSize(QtCore.QSize(250, 250))
        # self.error.setMaximumSize(QtCore.QSize(250, 250))
        # self.error.setObjectName("lb1")

        if sagaguimodel.debugmode:
            self.emailfield.setText(chosenlogin['email'])
            self.passwordfield.setText(chosenlogin['password'])
        else:
            self.emailfield.setText('')
            self.passwordfield.setText('')
        # if sagaguimodel.debugmode:
        #     self.email.setText(testerlogin['email'])
        #     self.password.setText(testerlogin['password'])
        # else:
        #     self.email.setText('')
        #     self.password.setText('')

        self.signedin=False
        # self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.signin)
        # self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        # self.profilemodel = ProfileListModel(sagaguimodel.profiledict)
        # self.profiletableview.setModel(self.profilemodel)
        # self.profiletableview.clicked.connect(self.getauthtoken)
        # self.profiletableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.login.clicked.connect(self.signin)
        self.createnewaccountlbl.mousePressEvent = self.goToCreateAccPage

    def goToCreateAccPage(self, event):
        self.widget.setCurrentIndex(CREATEACCINDEX)


    def signin(self):
        #Would really like to add a loading indicator here.
        success , respdict = sagaguimodel.signIn(self.emailfield.text(), self.passwordfield.text(),
                                                     saveprofile=self.keepprofilecheckbox.isChecked())
        # demo.stopAnimation()
        if success:
            self.signedin = True
            self.mainguihandle.adjustGuiByUserStatusChange()## It makes sense to keep it this way
            self.mainguihandle.guireset()
            self.mainguihandle.loadSection()
            self.widget.setCurrentIndex(MAINAPPINDEX)
            self.error.setText('')
            print('usertoken[status] success '  + datetime.now().isoformat())
        else:
            self.error.setText(respdict['failmessage'])
            print('ATTENTION: Need View code to deal with sign in failure')



# class SigninDialog(QDialog):
#     def __init__(self, mainguihandle, sagaguimodel,parent=None):
#         super().__init__()
#         uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","signinDialog.ui"), self)
#         self.mainguihandle=mainguihandle
#         self.sagaguimodel = sagaguimodel
#         self.password.setEchoMode(QLineEdit.Password)
#         if sagaguimodel.debugmode:
#             self.email.setText(testerlogin['email'])
#             self.password.setText(testerlogin['password'])
#         else:
#             self.email.setText('')
#             self.password.setText('')
#
#         self.signedin=False
#         self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.signin)
#         self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
#         self.profilemodel = ProfileListModel(sagaguimodel.profiledict)
#         self.profiletableview.setModel(self.profilemodel)
#         self.profiletableview.clicked.connect(self.getauthtoken)
#         self.profiletableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#
#
#     def getauthtoken(self, listtable):
#         rownumber = listtable.row()
#         index = listtable.model().index(rownumber, 0)
#         email = listtable.model().data(index,0)
#         print(listtable.model().authtokenfromemail(email))
#         self.email.setText(email)
#         if listtable.model().exptimestampfromemail(email)>datetime.now().timestamp():
#             self.sagaguimodel.sagaapicall.authtoken = listtable.model().authtokenfromemail(email)
#             self.signedin = True
#             self.accept()
#
#         # return {'signinsuccess': True}
#         # self.dlContainerBttn.setEnabled(True)
#         # self.dlContainerBttn.setText('Click to Download Container ' + containername)
#         # self.dlcontainername = containername
#         # self.dlcontainerid = listtable.model().containernametoid[containername]
#
#     def showpasswordstate(self):
#         if self.passwordcheckbox.isChecked():
#             self.password.setEchoMode(QLineEdit.Normal)
#         else:
#             self.password.setEchoMode(QLineEdit.Password)
#
#     def getInputs(self):
#         if self.exec_() == QDialog.Accepted:
#             return {'signinsuccess':self.signedin}
#         else:
#             return {'signinsuccess': False}
#
#     def signin(self):
#         status , usertokeninfo = sagaguimodel.signIn(self.email.text(), self.password.text(),
#                                                      saveprofile=self.keepprofilecheckbox.isChecked())
#         if status:
#             self.signedin = True
#             self.accept()
#             print('usertoken[status] success '  + datetime.now().isoformat())
#         else:
#             print('ATTENTION: Need View code to deal with sign in failure')