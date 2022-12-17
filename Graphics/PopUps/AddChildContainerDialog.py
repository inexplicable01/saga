from PyQt5.QtWidgets import *
from PyQt5 import uic
import random
import string
import os
from os.path import join
from Config import sourcecodedirfromconfig
from SagaGuiModel.GuiModelConstants import roleOutput, roleRequired
# uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","newContainer.ui"), self)

class AddChildContainerDialog(QDialog):
    def __init__(self, path):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","newChildContainer.ui"), self)
        self.containerpathlbl.setText(path)
        self.dir=''
        self.openDirButton.clicked.connect(self.openDirectory)
        # self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        res = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k=7))
        self.containernameEdit.setText(res)
        # self.containerpathlbl.setText(os.path.join(self.dir, res))
        self.containernameEdit.textChanged[str].connect(self.textChanged)

        self.fileroleradiogroup = QButtonGroup(self)
        self.fileroleradiogroup.addButton(self.workingradiobttn)
        self.fileroleradiogroup.addButton(self.outputradiobttn)
        self.fileroleradiogroup.buttonToggled.connect(self.rolechanged)

    def openDirectory(self):
        dialog = QFileDialog()
        self.dir = os.path.normpath(dialog.getExistingDirectory(self, 'Select a dir to making your container'))
        if os.path.exists(self.dir):
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.containernameEdit.setEnabled(True)
            self.containerpathlbl.setText(os.path.join(self.dir,self.containernameEdit.text()))

    def textChanged(self,containername):
        # print(ttext)
        if len(containername)>4:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.containerpathlbl.setText(os.path.join(self.dir,containername))
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.containerpathlbl.setText(self.dir)
            self.advicelabel.setText('Container Name needs to be at least 4 charaters long')

    def rolechanged(self, clickedbutton):
        # print(button.text())
        if 'Output' in clickedbutton.text():
            self.filerole= roleOutput
        elif 'Working' in clickedbutton.text():
            self.filerole=roleRequired
        # self.okpermissions()

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'dir':self.containerpathlbl.text(),
                    'filerole':self.filerole,
                    'containerName':self.containernameEdit.text()}
            # print()
        else:
            return None

