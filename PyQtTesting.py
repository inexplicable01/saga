from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.CGuiControls import ContainerMap
from Graphics.DetailedMap import DetailedMap
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrackObj
from Frame.commit import commit
import os
import sys
import requests
import json

# BASE = "http://fatpanda1985.pythonanywhere.com/"
BASE = "http://127.0.0.1:5000/"



class ErrorMessage(QMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('ErrorMessage')
        self.setIcon(QMessageBox.Warning)
        self.setText('Please Select File Type')
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_()

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('File Information')
        self.setMinimumSize(500,100)
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        self.third = QLineEdit(self)
        self.fourth = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("File Name", self.first)
        layout.addRow("File Path", self.second)
        layout.addRow("Owner", self.third)
        layout.addRow("Description", self.fourth)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return (self.first.text(), self.second.text(), self.third.text(), self.fourth.text())



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
        self.returncontlist.clicked.connect(self.getContainerInfo)


        self.generateContainerBttn.clicked.connect(self.generateContainerMap)

        # Section to set up adding new file button and file type selection - Jimmy
        #Need to read and learn more about slots/events/signals, toggling of radio button won't send info to btnstate
        # without lambda function, potential memory leak?
        # self.radioButton.toggled.connect(lambda:self.btnstate(self.radioButton))
        # self.radioButton_2.toggled.connect(lambda:self.btnstate(self.radioButton_2))
        # self.radioButton_3.toggled.connect(lambda:self.btnstate(self.radioButton_3))
        # self.containerName = [self.inputCheck,self.requiredCheck,self.outputCheck]
        # print(self.containerName)

        # if self.containerName == [False,False,False]:
        #     self.pushButton_2.clicked.connect(ErrorMessage)
        # else:
        self.newContainerInputs = []
        self.pushButton_2.clicked.connect(self.newFileInfo)

        self.navButton.clicked.connect(self.navigateTotab)




        self.counter= True
        self.resetbutton.clicked.connect(self.resetrequest)
        self.rebasebutton.clicked.connect(self.rebaserequest)

        self.commitBttn.setEnabled(False)
        self.commitBttn.clicked.connect(self.commit)

        self.commitmsgEdit.setDisabled(True)
        self.selecteddetail={'selectedobjname':None}
        # self.frametextBrowser.append('here I am')
        self.show()


        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap =ContainerMap({}, self.containerMapView, self.selecteddetail,self.detailedmap)

    def btnstate(self,b):
        if b.text() == 'Input':
            print('Checked')
        if b.text() == 'Required':
            print('Checked')
        if b.text() == 'Output':
            print('Checked')


    def resetrequest(self):
        response = requests.get(BASE + 'RESET')
        print(response.content)

    def rebaserequest(self):
        response = requests.post(BASE + 'RESET')
        print(response.content)

    def navigateTotab(self):
        self.tabWidget.setCurrentIndex(2)

    def getContainerInfo(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        # print(response.headers['containerinfolist'])
        self.infodump.append(response.headers['response'])
        containerinfolist = json.loads(response.headers['containerinfolist'])
        self.containerlisttable.setModel(ContainerListModel(containerinfolist))

        # self.containerlisttable.setHorizontalHeaderLabels(['asd','asd','asd','df'])


    def newFileInfo(self):
        inputwindow = InputDialog()
        inputs = inputwindow.getInputs()
        self.newContainerInputs = inputs
        self.containerAddition(inputs[1])

    def generateContainerMap(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        containerinfolist = json.loads(response.headers['containerinfolist'])
        for containerID in containerinfolist.keys():
            response = requests.get(BASE+'CONTAINERS/containerID', data={'containerID':containerID})
            open(os.path.join('ContainerMapWorkDir',containerID+'_'+response.headers['file_name']), 'wb').write(response.content)
            self.containermap.addActiveContainers(Container(os.path.join('ContainerMapWorkDir',containerID+'_'+response.headers['file_name'])))
        self.containermap.editcontainerConnections()
        self.containermap.plot()
        self.detailedmap.passobj(self.containermap)

    # def containerMapView(self, title):
    #     filemap = QGraphicsScene()
    #     filemap.addRect(-100, -200, 40, 40, QPen(Qt.black), QBrush(Qt.yellow))
    #     text = filemap.addText(title)
    #     text.setPos(-100, -200)
    #     self.graphicsView_3.setScene(filemap)

    def containerAddition(self, title):
        filemap = QGraphicsScene()
        filemap.addRect(-100, -200, 40, 40, QPen(Qt.black), QBrush(Qt.yellow))
        text = filemap.addText(title)
        text.setPos(-100, -200)
        self.graphicsView_3.setScene(filemap)



    def checkdelta(self):
        try:
            allowCommit, changes = self.Container.checkFrame(self.cframe)
            self.commitBttn.setEnabled(allowCommit)
            self.commitmsgEdit.setDisabled(not allowCommit)
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
        # print(self.commitmsgEdit.toPlainText() + str())
        error_dialog = QErrorMessage()
        # print()
        if len(self.commitmsgEdit.toPlainText())<=7:
            error_dialog.showMessage('You need to put in a commit message longer than 8 characters')
            error_dialog.exec_()
            return
            # return
        self.cframe, committed = self.Container.commit(self.cframe,self.commitmsgEdit.toPlainText(), BASE)
        if committed:
            self.Container.save()
            self.framelabel.setText(self.cframe.FrameName)
            self.checkdelta()
            self.frametextBrowser.clear()
            self.commithist.clear()
            self.commithist.append(self.Container.commithistory())

    def printToFrameText(self,changes):
        self.frametextBrowser.append(self.Container.printDelta(changes))
        # frameText

    def readcontainer(self):

        # path = QFileDialog.getOpenFileName(self, "Open")[0]
        # if path:
        #     print(path)
        path='C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.Container = Container(path, 'Main', '2')
        # refframe = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/Main/Rev3.yaml'
        try:
            with open(self.Container.refframe) as file:
                fyaml = yaml.load(file, Loader=yaml.FullLoader)
        except:
            print(sys.exc_info()[0])
        print(self.Container.containerworkingfolder)
        self.cframe = Frame(fyaml, self.Container.containerworkingfolder)
        print('self.cframe.FrameName')
        self.framelabel.setText(self.cframe.FrameName)

        # self.commithist.setText(self.Container.commitMessage)
        # self.Container.commithistory()
        self.commithist.append(self.Container.commithistory())
        # print()

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


