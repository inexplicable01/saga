from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.CGuiControls import ContainerMap
from Graphics.DetailedMap import DetailedMap
from Graphics.TrayActions import SignIn, SignOut
from Graphics.Dialogs import ErrorMessage, inputFileDialog, selectFileDialog
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrackObj
from Frame.commit import commit
import os
import sys
import requests
import json
from functools import partial
from Config import BASE
from ContainerDetails import refContainer
from NewContainerGraphics import newContainerGraphics

if os.path.exists("token.txt"):
  os.remove("token.txt")






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
        self.returncontlist_2.clicked.connect(self.getContainerInfo2)
        self.generateContainerBttn.clicked.connect(self.generateContainerMap)

        # Section to set up adding new file button and file type selection - Jimmy
        #Need to read and learn more about slots/events/signals, toggling of radio button won't send info to btnstate
        # without lambda function, potential memory leak?
        # self.radioButton.toggled.connect(lambda:self.btnstate(self.radioButton))
        # self.radioButton_2.toggled.connect(lambda:self.btnstate(self.radioButton_2))
        # self.radioButton_3.toggled.connect(lambda:self.btnstate(self.radioButton_3))
        # self.containerName = [self.inputCheck,self.requiredCheck,self.outputCheck]
        # print(self.containerName)

        # Add File Button Connections:
        self.inputFileButton.setEnabled(False)
        self.removeFileButton.setEnabled(False)
        self.tempContainer = Container()
        self.tempFrame = Frame()
        self.outputFrame = Frame()      #frame from Output container where input file is taken
        self.inputFileButton.clicked.connect(self.newFileInfoInputs)
        self.requiredFileButton.clicked.connect(partial(self.newFileInfo, 'Required'))
        self.outputFileButton.clicked.connect(partial(self.newFileInfo, 'Output'))

        self.commitNewButton.clicked.connect(self.createNewContainer)

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

        self.userdata=None

        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap =ContainerMap({}, self.containerMapView, self.selecteddetail,self.detailedmap)

        ###########Tray Actions #############
        self.actionSign_In.triggered.connect(partial(SignIn,self))
        self.actionSign_Out.triggered.connect(partial(SignOut,self))

        self.checkUserStatus()

    # def selectFileType(self):
    #     buttonName = self.sender()
    #     self.newContainerInputs = [buttonName.text()]

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


    def getContainerInfo2(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        # print(response.headers['containerinfolist'])
        self.infodump.append(response.headers['response'])
        containerinfolist = json.loads(response.headers['containerinfolist'])
        self.containerlisttable_2.setModel(ContainerListModel(containerinfolist))
        self.containerlisttable_2.clicked.connect(partial(refContainer, self))

    def newFileInfoInputs(self):
        dialogWindow = inputFileDialog(self.containerName,self.containerObjName)
        fileInfo = dialogWindow.getInputs()
        if fileInfo:
            self.tempContainer.addFileObject(fileInfo, self.fileType)
            outputYaml = self.outputFrame.downloadFrame('ContainerC')
            self.outputFrame = Frame(outputYaml)
            self.downloadInputFile(self.outputFrame, self.outputFrame.parentContainerId, self.containerObjName)
            # self.tempFrame.addFileTotrack('',self.containerObjName,'')
            # print(self.tempFrame.filestrack['ContainerObjName'])
        newContainerGraphics(self.tempContainer,self)
        self.inputFileButton.setEnabled(False)

    def downloadInputFile(self, outputFrame: Frame, outputContainerID, containerObjName):
        # with open(FrameYaml, 'r') as file:
        #     fnyaml = yaml.load(file, Loader=yaml.FullLoader)
        ## load the yaml file as a yaml object.
        # curframe = Frame(fnyaml, outputContainerID)
        ## frame uses the yaml object to make a frame object.

        response = requests.get(BASE + 'FILES',
                                data={'file_id': outputFrame.filestrack[containerObjName].file_id, 'file_name': outputFrame.filestrack[containerObjName].file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join('testingDownloads', response.headers['file_name'])
        # fn = os.path.join(containerID, response.headers['file_name'])
        open(fn, 'wb').write(response.content)
        # saves the content into file.
        os.utime(fn, (outputFrame.filestrack[containerObjName].lastEdited, outputFrame.filestrack[containerObjName].lastEdited))

    def newFileInfo(self, fileType:str, containerName="", containerObjName=""):
        self.fileType = fileType
        if fileType in ['refOutput','Input']:
            self.inputFileButton.setEnabled(True)
            self.containerObjName = containerObjName
            self.containerName = containerName
            # inputWindow = InputDialog(fileType)
            # inputs = inputWindow.getInputs()
            # if inputs:
            #     self.newContainerInputs.extend(inputs)
            #     self.containerAddition(inputs[0])
            # if output file selected:
            # self.newContainerInputs.extend(inputs)
            # self.containerAddition(inputs[0])
        else:
            self.inputFileButton.setEnabled(False)
            fileInfoDialog = selectFileDialog(self.fileType)
            fileInfo = fileInfoDialog.getInputs()
            if fileInfo:
                self.tempContainer.addFileObject(fileInfo, self.fileType)
                newContainerGraphics(self.tempContainer,self)

    def createNewContainer(self):
        print(self.descriptionText.toPlainText())
        if '' not in [self.containerName_lineEdit.text(), self.descriptionText.toPlainText(), self.messageText.toPlainText()]:
            self.tempContainer.containerName = self.containerName_lineEdit.text()
            self.tempContainer.containerId = self.containerName_lineEdit.text()
            self.tempContainer.save(self.tempContainer.containerName)
        else:
            self.errorMessage = ErrorMessage()
            self.errorMessage.showError()



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

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                authtoken = json.load(json_file)
                response = requests.get(
                    BASE + '/auth/status',
                    headers={"Authorization": 'Bearer ' + authtoken['auth_token']}
                )
                usertoken = response.json()
                if usertoken['status'] == 'success':
                    self.userstatuslbl.setText('User ' + usertoken['data']['email'] + ' Signed in')
                    self.userdata = usertoken['data']
                else:
                    self.userstatuslbl.setText('Please sign in')
                    self.userdata = None

        except Exception as e:
            print('No User Signed in yet')

    # def containerMapView(self, title):
    #     filemap = QGraphicsScene()
    #     filemap.addRect(-100, -200, 40, 40, QPen(Qt.black), QBrush(Qt.yellow))
    #     text = filemap.addText(title)
    #     text.setPos(-100, -200)
    #     self.graphicsView_3.setScene(filemap)



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


