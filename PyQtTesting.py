from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrackObj
from Frame.commit import commit
import os
import sys

# Form, Window=uic.loadUiType()
class UI(QMainWindow):
    def __init__(self):
        # self.logf = open("C:\\Users\\waich\\LocalGitProjects\\saga\\error.txt", 'w+')
        super(UI, self).__init__()

        uic.loadUi("Graphics/SagaGui.ui", self)

        self.fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
        self.openContainerBttn.setText('Open Container')
        self.openContainerBttn.clicked.connect(self.readcontainer)
        # self.refreshBttn.setText('Check Button')
        self.refreshBttn.clicked.connect(self.checkdelta)

        self.commitBttn.setEnabled(False)
        self.commitBttn.clicked.connect(self.commit)

        # self.frametextBrowser.append('here I am')
        self.show()

    def checkdelta(self):
        try:
            allowCommit, changes = self.Container.checkFrame(self.cframe)
            self.commitBttn.setEnabled(allowCommit)
            # print('c',changes)
            changesarr=[]
            for change in changes:
                changesarr.append(change['ContainerObjName'])
            for ContainerObjName in self.Container.filestomonitor:
                if ContainerObjName in changesarr:
                    self.sceneObj[ContainerObjName].setPen(QPen(Qt.red, 3))
                else:
                    self.sceneObj[ContainerObjName].setPen(QPen(Qt.black, 1))

            self.printToFrameText(changes)
                # self.sceneObj[change].update()
        except Exception as err:
            print(err)

    def commit(self):
        self.cframe, committed = self.Container.commit(self.cframe)
        if committed:
            self.Container.save()
            self.framelabel.setText(self.cframe.FrameName)
            self.checkdelta()
            self.frametextBrowser.clear()

    def printToFrameText(self,changes):
        self.frametextBrowser.append(self.Container.printDelta(changes))
        # frameText

    def readcontainer(self):

        # path = QFileDialog.getOpenFileName(self, "Open")[0]
        # if path:
        #     print(path)
        path='C:/Users/waich/LocalGitProjects/saga/ExampleDIR/GroupC/GroupCContainer.yaml'

        self.Container = Container(path)

        try:
            with open(self.Container.refframe) as file:
                fyaml = yaml.load(file, Loader=yaml.FullLoader)
        except:
            print(sys.exc_info()[0])

        self.cframe = Frame(fyaml)
        # print('self.cframe.FrameName')
        self.framelabel.setText(self.cframe.FrameName)
        # self.revlabel.setText(self.cframe.FrameName)

        print(path)

        scene = QGraphicsScene()
        boxwidth= 40
        boxheight = 40
        self.sceneObj={}
        # print(self.cframe.filestrack.keys())
        colorscheme = {'inputObjs':Qt.yellow, 'outputObjs':Qt.green, 'requiredObjs':Qt.blue}

        for typeindex, fileobjtype in enumerate(self.fileobjtypes):
            # print(typeindex,fileobjtype)
            for fileindex, fileObj in enumerate(getattr(self.Container,fileobjtype)):
                # ellipse = scene.addEllipse(20, 20, 200, 70, QPen(Qt.red), QBrush(Qt.green))
                self.sceneObj[fileObj['ContainerObjName']] = scene.addRect(-100 + 100*typeindex, -200 + 100*fileindex, boxwidth, boxheight, QPen(Qt.black), QBrush(colorscheme[fileobjtype]))
                # print(inputObj['FileObjName'])
                text = scene.addText(fileObj['ContainerObjName'])
                text.setPos(-100+ 100*typeindex, -200 + 100*fileindex)
                # print(fileObj['ContainerObjName'])
                if fileObj['ContainerObjName'] in self.cframe.filestrack.keys():
                    text = scene.addText(self.cframe.filestrack[fileObj['ContainerObjName']].file_name)
                    text.setPos(-100+ 100*typeindex, -200 + 100 * fileindex +20)
                else:
                    text = scene.addText('Missing')
                    text.setPos(-100+ 100*typeindex, -200 + 100 * fileindex +20)

        self.frameView.setScene(scene)

app=QApplication([])
window = UI()
app.exec_()


