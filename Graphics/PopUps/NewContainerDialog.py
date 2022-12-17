from PyQt5.QtWidgets import *
from PyQt5 import uic
import random
import string
import os
from os.path import join
from Config import sourcecodedirfromconfig
# uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","newContainer.ui"), self)

class newContainerDialog(QDialog):
    def __init__(self, path):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","newContainer.ui"), self)
        self.containerpathlbl.setText(path)
        self.dir=''
        self.openDirButton.clicked.connect(self.openDirectory)
        # self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        res = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k=7))
        self.containername=''
        self.containernameEdit.setText(res)
        self.containerdesc=''
        # self.containerpathlbl.setText(os.path.join(self.dir, res))
        self.containernameEdit.textChanged[str].connect(self.textChanged)
        self.lineEdit.textChanged[str].connect(self.textChanged)

    def openDirectory(self):
        dialog = QFileDialog()
        self.dir = os.path.normpath(dialog.getExistingDirectory(self, 'Select a dir to making your container'))
        if os.path.exists(self.dir):
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.containernameEdit.setEnabled(True)
            self.containerpathlbl.setText(os.path.join(self.dir,self.containername))

    def textChanged(self,str:str):
        # print(ttext)
        containername = self.containernameEdit.text()
        containerdesc = self.lineEdit.text()
        # print(containername, containerdesc)
        if len(containername)>4 and len(containerdesc)>7:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.containername = containername.replace(" ","")
            self.containernameEdit.setText(self.containername)
            self.containerpathlbl.setText(os.path.join(self.dir,self.containername))
            self.advicelabel.setText('')
            self.containerdesc = containerdesc
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.containerpathlbl.setText(self.dir)
            self.advicelabel.setText('Container Name needs to be at least 4 charaters long and description needs to be at least 7 characters long')




    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'dir':self.containerpathlbl.text(), 'containername':self.containername, 'containerdesc':self.containerdesc}
            # print()
        else:
            return None

