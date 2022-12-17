from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

import re
import requests
# Make a regular expression
# for validating an Email
from SagaGuiModel import sagaguimodel
from SagaGuiModel.SagaGuiUtility import *
from os.path import join
from Config import sourcecodedirfromconfig
from Graphics.QAbstract.SectionSyncFileModel import SectionSyncDelegate
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

class sectionSynchDialog(QDialog):
    def __init__(self, mainguihandle):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "SectionSychronizationStatus.ui"), self)
        self.mainguihandle= mainguihandle
        # self.mainContainer = mainContainer
        updateEveryContainerInSection(sagaguimodel)
        self.synctableview.setModel(sagaguimodel.sectionsyncmodel)
        sagaguimodel.sectionsyncmodel.update()
        self.synctableview.setItemDelegate(SectionSyncDelegate())
        self.synctableview.clicked.connect(self.setPingButton)
        self.exitbttn.clicked.connect(self.accept)
        self.pingbttn.clicked.connect(self.pingdownstream)
        self.pingbttn.setEnabled(False)
        self.pingdownstreamcontainerid = None
        self.pingdownstreamrev = None
        self.pingupstreamcontainerid = None
        self.pringcitemid= None
        self.synctableview.horizontalHeader().setStretchLastSection(True)
        self.exec_()


    def pingdownstream(self):
        # print('go Ping Downstream ' + self.pingcontainerid + '')
        sagaguimodel.pingDownstream(downstreamcontainerid=self.pingdownstreamcontainerid,
                                    citemid=self.pringcitemid,
                                    upstreamcontainerid= self.pingupstreamcontainerid)

    def setPingButton(self, index):
        rowdict = sagaguimodel.sectionsyncmodel.modeldata[index.row()]
        if rowdict['upstreamrev']==rowdict['downstreamrev']:
            self.pingdownstreamcontainerid = None
            self.pingdownstreamrev = None
            self.pringcitemid = None
            self.pingupstreamcontainerid = None
            self.pingbttn.setEnabled(False)
        else:
            self.pringcitemid = rowdict['citemid']
            self.pingdownstreamcontainerid = rowdict['downstreamid']
            self.pingupstreamcontainerid = rowdict['upstreamid']
            self.pingdownstreamrev = rowdict['downstreamrev']
            self.pingbttn.setEnabled(True)
        print(index.row())
        print(index.column())

    def adduser(self):
        permissionsresponse, allowedUsers  = sagaguimodel.addUserToContainer(self.emailedit.text())
        print(permissionsresponse['ServerMessage'])
        if permissionsresponse['result']:
            self.emailedit.setText('')
            self.usermodel.listusers(allowedUsers)
            self.usermodel.layoutChanged.emit()
        else:
            self.errorlbl.setText(permissionsresponse['ServerMessage'])

    def textChanged(self, email):
        # print(ttext)
        if re.search(regex, email):
            self.adduserbttn.setEnabled(True)
        else:
            self.adduserbttn.setEnabled(False)

    def setemailedit(self, selectedIndex):
        # rownumber = emailList.row()
        email = self.sectionUser.getemail(selectedIndex)
        self.emailedit.setText(email)

        # containerId = containerList.model().data(index, 0)
        # refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , CONTAINERFN)
        # if os.path.exists(refcontainerpath):
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # else:
        #     refpath = os.path.join(sagaguimodel.appdata_saga,'ContainerMapWorkDir')
        #     Container.sagaguimodel.downloadContainerState(refpath,sagaguimodel.authtoken, BASE, containerId)
        #     self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # # self.tester.setText(self.selectedContainer.containerName)
        # self.refContainerPlot.changeContainer(self.selectedContainer)
        # self.refContainerPlot.plot({})

    # def getInputs(self):
    #     if self.exec_() == QDialog.Accepted:
    #         return {'userlist':self.usermodel.userlist()}
    #         # print()
    #     else:
    #         return None

