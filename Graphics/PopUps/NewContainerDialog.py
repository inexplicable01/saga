from PyQt5.QtWidgets import *
from PyQt5 import uic
import random
import string
import os

class newContainerDialog(QDialog):
    def __init__(self, path):
        super().__init__()
        uic.loadUi("Graphics/UI/newContainer.ui", self)
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


    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return {'dir':self.containerpathlbl.text(), 'containername':self.containernameEdit.text()}
            # print()
        else:
            return None

