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
import requests
import json

BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://127.0.0.1:5000/"
headers = ['ID', 'Description', 'Branch name', 'Rev Count']

class ErrorMessage(QMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('ErrorMessage')
        self.setIcon(QMessageBox.Warning)
        self.setText('Please Select File Type')
        self.setStandardButtons(QMessageBox.Ok)
    def showError(self):
        self.exec_()

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("Graphics/file_info.ui", self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.openDirButton.clicked.connect(self.openDirectory)


    def openDirectory(self):
        self.openDirectoryDialog = QFileDialog.getOpenFileName(self, "Get Dir Path")
        self.lineEdit_2.setText(self.openDirectoryDialog[0])

    def getInputs(self):
        if self.exec_() == QDialog.Accepted:
            return (self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_3.text(), self.lineEdit_4.text())
        else:
            return None



class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    # def headerData(self, section, Qt_Orientation,role):
    #     return headers[section]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

class ContainerListModel(QAbstractTableModel):
    def __init__(self, containerinfolist):
        super(ContainerListModel, self).__init__()
        containdata=[]
        for containerid, containvalue in containerinfolist.items():
            for branch in containvalue['branches']:
                row = [containerid, containvalue['ContainerDescription'] ,
                       branch['name'],
                       branch['revcount']]
                containdata.append(row)
        self.containdata = containdata

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.containdata[index.row()][index.column()]


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
            # return 'Column {}'.format(section + 1)
        # if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #     return 'Row {}'.format(section + 1)
        # return super().headerData(section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self.containdata)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.containdata[0])

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

        # Section to set up adding new file button and file type selection - Jimmy
        #Need to read and learn more about slots/events/signals, toggling of radio button won't send info to btnstate
        # without lambda function, potential memory leak?
        # self.radioButton.toggled.connect(lambda:self.btnstate(self.radioButton))
        # self.radioButton_2.toggled.connect(lambda:self.btnstate(self.radioButton_2))
        # self.radioButton_3.toggled.connect(lambda:self.btnstate(self.radioButton_3))
        # self.containerName = [self.inputCheck,self.requiredCheck,self.outputCheck]
        # print(self.containerName)
        self.radioButton.pressed.connect(self.selectFileType)
        self.radioButton_2.pressed.connect(self.selectFileType)
        self.radioButton_3.pressed.connect(self.selectFileType)
        self.newContainerInputs = []
        self.pushButton_2.clicked.connect(self.newFileInfo)

        self.navButton.clicked.connect(self.navigateTotab)


        self.counter= True
        self.resetbutton.clicked.connect(self.resetrequest)
        self.rebasebutton.clicked.connect(self.rebaserequest)

        self.commitBttn.setEnabled(False)
        self.commitBttn.clicked.connect(self.commit)

        self.commitmsgEdit.setDisabled(True)

        # self.frametextBrowser.append('here I am')
        self.show()


    def selectFileType(self):
        buttonName = self.sender()
        self.newContainerInputs = [buttonName.text()]

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
        print(response.headers['containerinfolist'])
        self.infodump.append(response.headers['response'])
        containerinfolist = json.loads(response.headers['containerinfolist'])
        self.containerlisttable.setModel(ContainerListModel(containerinfolist))

        # self.containerlisttable.setHorizontalHeaderLabels(['asd','asd','asd','df'])

    def newFileInfo(self):
        if not self.newContainerInputs:
            error = ErrorMessage()
            error.showError()
        else:
            inputwindow = InputDialog()
            inputs = inputwindow.getInputs()
            if inputs:
                self.newContainerInputs.extend(inputs)
                self.containerAddition(inputs[0])





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
        path='C:/Users/happy/Documents/GitHub/ContainerC/containerstate.yaml'
        self.Container = Container(path, 'Main', '4')
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
sys.exit(app.exec_())


