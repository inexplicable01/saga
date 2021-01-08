from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Graphics.QAbstract.ContainerListModel import ContainerListModel
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.CGuiControls import ContainerMap
from Graphics.DetailedMap import DetailedMap
from Graphics.TrayActions import SignIn, SignOut
from Graphics.FixInput import fixInput
from Graphics.Dialogs import ErrorMessage, inputFileDialog, removeFileDialog, selectFileDialog, commitDialog,alteredinputFileDialog
import yaml
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Frame.FileObjects import FileTrack
from Frame.commit import commit
import os
import sys
import requests
import json
import copy
from functools import partial
from Config import BASE
from ContainerDetails import containerPlot
from NewContainerGraphics import newContainerGraphics
# from hackpatch import downloadedFrames

boxwidth = 40
boxheight = 40

if os.path.exists("token.txt"):
    os.remove("token.txt")


# Form, Window=uic.loadUiType()
class UI(QMainWindow):
    def __init__(self):
        # self.logf = open("C:\\Users\\waich\\LocalGitProjects\\saga\\error.txt", 'w+')
        super(UI, self).__init__()
        uic.loadUi("Graphics/SagaGui.ui", self)

        self.openContainerBttn.setText('Open Container')
        self.openContainerBttn.clicked.connect(self.readcontainer)
        # self.refreshBttn.setText('Check Button')
        self.refreshBttn.clicked.connect(self.checkdelta)
        self.returncontlist.clicked.connect(self.getContainerInfo)
        self.returncontlist_2.clicked.connect(self.getContainerInfo2)
        self.generateContainerBttn.clicked.connect(self.generateContainerMap)
        self.enterEvent=self.blah
        # Section to set up adding new file button and file type selection - Jimmy
        # Need to read and learn more about slots/events/signals, toggling of radio button won't send info to btnstate
        # Add File Button Connections:
        self.inputFileButton.setEnabled(False)
        self.editFileButton.setEnabled(False)
        self.removeFileButton.setEnabled(False)
        self.tempContainer = Container()
        self.tempFrame = Frame()
        self.outputFrame = Frame()  # frame from Output container where input file is taken
        self.inputFileButton.clicked.connect(self.newFileInfoInputs)
        self.requiredFileButton.clicked.connect(partial(self.newFileInfo, 'Required'))
        self.outputFileButton.clicked.connect(partial(self.newFileInfo, 'Output'))
        self.containerObjName = ''
        self.removeFileButton.clicked.connect(self.removeFileInfo)
        self.editFileButton.clicked.connect(self.editFileInfo)

        self.commitNewButton.clicked.connect(self.commitNewContainer)

        self.counter = True
        self.resetbutton.clicked.connect(self.resetrequest)
        self.rebasebutton.clicked.connect(self.rebaserequest)
        # self.fixInputBttn.clicked.connect(self.addressAlteredInput)
        # self.fixInputBttn.setEnabled(False)
        self.sceneObj = {}
        self.revertbttn.clicked.connect(self.revert)
        self.revertbttn.setEnabled(False)

        self.commitBttn.setEnabled(False)
        self.commitBttn.clicked.connect(self.commit)

        self.commitmsgEdit.setDisabled(True)
        self.selecteddetail = {'selectedobjname': None}
        # self.frametextBrowser.append('here I am')
        self.show()

        self.userdata = None

        self.authtoken = None
        self.tabWidget.setEnabled(False)
        self.alterfiletracks=[]

        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap = ContainerMap({}, self.containerMapView, self.selecteddetail, self.detailedmap)

        ###########History Info####
        self.commithisttable.clicked.connect(self.alterRevertButton)

        ###########Tray Actions #############
        self.actionSign_In.triggered.connect(partial(SignIn, self))
        self.actionSign_Out.triggered.connect(partial(SignOut, self))

        self.checkUserStatus()
        self.startingcheck = False

    def blah(self, event):
        if self.startingcheck:
            self.checkdelta()
        # print(event)

    def alterRevertButton(self,histtable):
        rownumber = histtable.row()
        index = histtable.model().index(rownumber, 0)
        self.reverttorev = histtable.model().data(index, 0)
        self.revertbttn.setText('Revert back to ' + self.reverttorev)
        self.revertbttn.setEnabled(True)

    def revert(self):
        self.cframe.revertTo(self.reverttorev)
        self.commitmsgEdit.setText('Revert back to ' + self.reverttorev)
        self.commit()
        self.checkdelta()
        self.commithisttable.setModel(HistoryListModel(self.Container.commithistory()))

    def resetrequest(self):
        response = requests.get(BASE + 'RESET')
        print(response.content)

    def rebaserequest(self):
        response = requests.post(BASE + 'RESET')
        print(response.content)

    # def navigateTotab(self):
    #     self.tabWidget.setCurrentIndex(2)

    def getContainerInfo(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        # print(response.headers['containerinfolist'])
        self.infodump.append(response.headers['response'])
        containerinfolist = json.loads(response.headers['containerinfolist'])
        self.containerlisttable.setModel(ContainerListModel(containerinfolist))

    def getContainerInfo2(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        # print(response.headers['containerinfolist'])
        self.infodump.append(response.headers['response'])
        containerinfolist = json.loads(response.headers['containerinfolist'])
        self.containerlisttable_2.setModel(ContainerListModel(containerinfolist))
        # self.containerlisttable_2.clicked.connect(partial(refContainer, self))
        self.containerlisttable_2.clicked.connect(self.showContainerFromList)


    def showContainerFromList(self, containerList):
        rownumber = containerList.row()
        self.index = containerList.model().index(rownumber, 0)
        self.containerID = containerList.model().data(self.index, 0)
        self.refFrame = Frame(self.tempFrame.downloadFrame(self.authtoken,self.containerID))
        rownumber = containerList.row()
        index = containerList.model().index(rownumber, 0)
        containerName = containerList.model().data(index, 0)
        self.refContainerPlot = containerPlot(self, self.refContainerView, self.refFrame, containerName)
        self.refContainerPlot.createInputRect()
        self.refContainerPlot.plot()

    # def getFrameInfo(self, containerID, branch='Main'):
    #     payload = {'containerID': containerID,
    #                'branch': branch}
    #     files = [
    #     ]
    #     headers = {
    #         'Authorization': 'Bearer ' + self.authtoken['auth_token']
    #     }
    #     response = requests.get(BASE + 'FRAMES', headers=headers, data=payload, files=files)
    #     fd = os.path.join(downloadedFrames, containerID, branch)
    #     fn = os.path.join(fd, response.headers['file_name'])
    #     if not os.path.exists(fd):
    #         if not os.path.exists(os.path.join(downloadedFrames,containerID)):
    #             if not os.path.exists(downloadedFrames):
    #                 os.mkdir(downloadedFrames)
    #             os.mkdir(os.path.join(downloadedFrames,containerID))
    #         os.mkdir(fd)
    #     open(fn, 'wb').write(response.content)
    #     return Frame(fn)


    def newFileInfoInputs(self):
        dialogWindow = inputFileDialog(self.containerName, self.containerObjName)
        fileInfo = dialogWindow.getInputs()
        if fileInfo:
            self.tempContainer.addFileObject(self.containerObjName, fileInfo, self.fileType)
            outputFrameYaml = self.outputFrame.downloadFrame(self.authtoken,'ContainerC')
            self.outputFrame = Frame(outputFrameYaml)
            inputFilePath = self.downloadInputFile(self.outputFrame, self.outputFrame.parentContainerId, self.containerObjName)
            self.tempFrame.addFileTotrack(inputFilePath, self.containerObjName, self.fileType)
            # self.tempFrame.addFileTotrack('',self.containerObjName,'')
            # print(self.tempFrame.filestrack['ContainerObjName'])
        self.curContainerPlot = containerPlot(self, self.curContainerView, self.tempFrame) #Edit to use refContainer
        self.curContainerPlot.createInputRect()
        self.curContainerPlot.plot()
        self.inputFileButton.setEnabled(False)

    def downloadInputFile(self, outputFrame: Frame, outputContainerID, containerObjName):
        # with open(FrameYaml, 'r') as file:
        #     fnyaml = yaml.load(file, Loader=yaml.FullLoader)
        ## load the yaml file as a yaml object.
        # curframe = Frame(fnyaml, outputContainerID)
        ## frame uses the yaml object to make a frame object.

        response = requests.get(BASE + 'FILES',
                                data={'file_id': outputFrame.filestrack[containerObjName].file_id,
                                      'file_name': outputFrame.filestrack[containerObjName].file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join('testingDownloads', response.headers['file_name'])
        # fn = os.path.join(containerID, response.headers['file_name'])
        open(fn, 'wb').write(response.content)
        # saves the content into file.
        os.utime(fn, (
        outputFrame.filestrack[containerObjName].lastEdited, outputFrame.filestrack[containerObjName].lastEdited))
        return fn

    def newFileInfo(self, fileType: str, containerName="", containerObjName=""):
        self.fileType = fileType
        if fileType == 'Input':
            self.inputFileButton.setEnabled(True)
            self.removeFileButton.setEnabled(False)
            self.editFileButton.setEnabled(False)
            self.containerObjName = containerObjName
            self.containerName = containerName
        else:
            self.inputFileButton.setEnabled(False)
            fileInfoDialog = selectFileDialog(self.fileType)
            fileInfo = fileInfoDialog.getInputs()
            if fileInfo:
                self.tempContainer.addFileObject(fileInfo['FileObjHeader'], fileInfo['ContainerFileInfo'], self.fileType)
                self.tempFrame.addFileTotrack(fileInfo['FilePath'], fileInfo['FileObjHeader'], self.fileType)
                self.curContainerPlot = containerPlot(self, self.curContainerView, self.tempFrame)
                self.curContainerPlot.createInputRect()
                self.curContainerPlot.plot()

# <<<<<<< HEAD
#
#     def createNewContainer(self):
#         print(self.descriptionText.toPlainText())
#         if '' not in [self.containerName_lineEdit.text(), self.descriptionText.toPlainText(), self.messageText.toPlainText()]:
#             # print('working?')
#             self.tempContainer.containerName = self.containerName_lineEdit.text()
#             self.tempContainer.containerId = self.containerName_lineEdit.text()
#             self.tempContainer.save(self.tempContainer.containerName)
# =======
    def editDeleteButtons(self,fileType: str, containerName ='', containerObjName=''):
        self.fileType = fileType
        self.containerName = containerName
        self.containerObjName = containerObjName
        self.removeFileButton.setEnabled(True)
        if self.fileType != 'Input':
            self.editFileButton.setEnabled(True)

    def editFileInfo(self):
        editFileDialog = selectFileDialog(self.fileType)
        editFileInfo = editFileDialog.getInputs()
        if editFileInfo:
            self.editFileButton.setEnabled(False)
            self.removeFileButton.setEnabled(False)
            self.tempContainer.FileHeaders[editFileInfo['FileObjHeader']] = \
                self.tempContainer.FileHeaders.pop(self.containerObjName)
            del self.tempFrame.filestrack[self.containerObjName]
            self.tempFrame.addFileTotrack(editFileInfo['FilePath'], editFileInfo['FileObjHeader'], self.fileType)
            if self.containerObjName != editFileInfo['FileObjHeader']:
                self.curContainerPlot.editRect(self.containerObjName, editFileInfo['FileObjHeader'])
                self.curContainerPlot.plot()
            print('working?')
            # self.tempFrame.filestrack[editFileInfo['FileObjHeader']] = \
            #     self.tempFrame.filestrack.pop(self.containerObjName)
            # self.tempFrame.filestrack

    def removeFileInfo(self):
        fileDialog = removeFileDialog(self.containerObjName)
        self.containerObjName = fileDialog.removeFile()
        if self.containerObjName:
            self.editFileButton.setEnabled(False)
            self.removeFileButton.setEnabled(False)
            newTempContainer = copy.deepcopy(self.tempContainer)
            newTempFrame = copy.deepcopy(self.tempFrame)
            for key, value in self.tempContainer.FileHeaders.items():
                if key == self.containerObjName:
                    del newTempContainer.FileHeaders[key]
            self.tempContainer = newTempContainer

            for key,value in self.tempFrame.filestrack.items():
                if key == self.containerObjName:
                    del newTempFrame.filestrack[key]
            self.tempFrame = newTempFrame
            self.curContainerPlot.removeRect(self.containerObjName)

    def commitNewContainer(self):
        if '' not in [self.containerName_lineEdit.text(), self.descriptionText.toPlainText(),
                      self.messageText.toPlainText()]:
            commitCheck = commitDialog(self.containerName_lineEdit.text(), self.descriptionText.toPlainText(),
                                       self.messageText.toPlainText())
            commited = commitCheck.commit()
            if commited:
                self.tempContainer.containerName = self.containerName_lineEdit.text()
                self.tempContainer.containerId = self.containerName_lineEdit.text()
                self.tempContainer.save(self.tempContainer.containerName)
                self.tempFrame.parentContainerId = self.containerName_lineEdit.text()
                self.tempFrame.FrameName = 'Rev0'
                # self.tempFrame.description = self.descriptionText.toPlainText()
                self.tempFrame.commitMessage = self.messageText.toPlainText()
                self.tempFrame.writeoutFrameYaml(self.tempFrame.FrameName + '.yaml')
                commitContainer = self.tempContainer.dictify()
                commitFrame = self.tempFrame.dictify()
                url = BASE + 'CONTAINERS/newContainer'
                payload = {'containerdictjson': json.dumps(commitContainer), 'framedictjson': json.dumps(commitFrame)}
                files = [

                ]
                headers = {
                    'Authorization': 'Bearer ' + self.authtoken['auth_token']
                }
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
        else:
            self.errorMessage = ErrorMessage()
            self.errorMessage.showError()

    def generateContainerMap(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        containerinfolist = json.loads(response.headers['containerinfolist'])
        for containerID in containerinfolist.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID})
            open(os.path.join('ContainerMapWorkDir', containerID + '_' + response.headers['file_name']), 'wb').write(
                response.content)
            self.containermap.addActiveContainers(
                Container(os.path.join('ContainerMapWorkDir', containerID + '_' + response.headers['file_name'])))
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
                    self.authtoken = authtoken
                    self.tabWidget.setEnabled(True)
                else:
                    self.authtoken = None
                    self.userstatuslbl.setText('Please sign in')
                    self.userdata = None

                    self.tabWidget.setEnabled(False)

        except Exception as e:
            print('No User Signed in yet')

    def checkdelta(self):
        allowCommit = False
        fixInput = False
        # allowCommit, changes, fixInput , self.alterfiletracks= self.Container.checkFrame(self.cframe)
        changes, self.alterfiletracks = self.cframe.compareToRefFrame()
        if len(changes) > 0:
            allowCommit = True

        self.commitBttn.setEnabled(allowCommit)
        self.commitmsgEdit.setDisabled(not allowCommit)
        # self.fixInputBttn.setEnabled(fixInput)

        changesarr=[change['fileheader'] for change in changes]
        for fileheader in self.Container.FileHeaders.keys():
            if fileheader in changesarr:
                self.sceneObj[fileheader].setPen(QPen(Qt.red, 3))
            else:
                self.sceneObj[fileheader].setPen(QPen(Qt.black, 1))
        chgstr = ''
        for change in changes:
            chgstr = chgstr + change['fileheader'] + '\t' + change['reason'] + '\n'
        self.frametextBrowser.setText(chgstr)

    def addressAlteredInput(self):
        for alterfiletrack in self.alterfiletracks:
            dialogWindow = alteredinputFileDialog(alterfiletrack)
            alterinputfileinfo = dialogWindow.getInputs()
            if alterinputfileinfo:
                self.cframe.dealwithalteredInput(alterinputfileinfo)
        self.readcontainer()
        self.checkdelta()


    def commit(self):
        # print(self.commitmsgEdit.toPlainText() + str())
        error_dialog = QErrorMessage()
        # print()
        if len(self.commitmsgEdit.toPlainText()) <= 7:
            error_dialog.showMessage('You need to put in a commit message longer than 8 characters')
            error_dialog.exec_()
            return
            # return
        if self.userdata['email'] not in self.Container.allowedUser:
            error_dialog.showMessage('You do not have the privilege to commit to this container')
            error_dialog.exec_()
            return

        self.addressAlteredInput()
        self.cframe, committed = self.Container.commit(self.cframe,self.commitmsgEdit.toPlainText(), self.authtoken, BASE)

        if committed:
            self.Container.save()
            self.framelabel.setText(self.cframe.FrameName)
            self.checkdelta()
            self.commithisttable.setModel(HistoryListModel(self.Container.commithistory()))

    def printToFrameText(self, changes):
        self.frametextBrowser.append(self.Container.printDelta(changes))
        # frameText

    def readcontainer(self):
        path = 'C:/Users/waich/LocalGitProjects/saga/ContainerC/containerstate.yaml'
        self.Container = Container(path, revnum=None)
        self.cframe = Frame(self.Container.refframe, self.Container.filestomonitor,
                            self.Container.containerworkingfolder)
        print('self.cframe.FrameName')
        self.startingcheck=True
        self.framelabel.setText(self.cframe.FrameName)
        self.commithisttable.setModel(HistoryListModel(self.Container.commithistory()))
        self.commithisttable.setColumnWidth(0, self.commithisttable.width()*0.1)
        self.commithisttable.setColumnWidth(1, self.commithisttable.width() * 0.6)
        self.commithisttable.setColumnWidth(2, self.commithisttable.width() * 0.29)
        self.plotcontainer()

    def plotcontainer(self):
        scene = QGraphicsScene()

        colorscheme = {'input': Qt.yellow, 'output': Qt.green, 'required': Qt.blue}
        typeindex = {'input': 0, 'output': 1, 'required': 2}
        typecounter = {'input': 0, 'output': 0, 'required': 0}

        for fileheader, fileinfo in self.Container.FileHeaders.items():
            type = fileinfo['type']
            if type == 'references':
                continue
            self.sceneObj[fileheader] = scene.addRect(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type], \
                                                      boxwidth, boxheight, QPen(Qt.black), QBrush(colorscheme[type]))
            text = scene.addText(fileheader)
            text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type])
            if fileheader in self.cframe.filestrack.keys():
                text = scene.addText(self.cframe.filestrack[fileheader].file_name)
                text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type] + 20)
            else:
                text = scene.addText('Missing')
                text.setPos(-100 + 100 * typeindex[type], -200 + 100 * typecounter[type] + 20)
            typecounter[type] += 1
        self.frameView.setScene(scene)


app = QApplication([])
window = UI()
sys.exit(app.exec_())
