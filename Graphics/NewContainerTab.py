from Graphics.Dialogs import ErrorMessage, inputFileDialog, removeFileDialog, selectFileDialog, commitDialog,alteredinputFileDialog
from functools import partial
from Frame.FrameStruct import Frame
from Frame.Container import Container
from Graphics.ContainerPlot import ContainerPlot
from Config import BASE
from Config import typeInput,typeRequired,typeOutput
import os
import copy
import random
import string

class NewContainerTab():
    def __init__(self, mainGuiHandle):
        self.index = 2
        self.inputFileButton = mainGuiHandle.inputFileButton
        self.RequiredButton = mainGuiHandle.RequiredButton
        self.outputFileButton = mainGuiHandle.outputFileButton
        self.curContainerView = mainGuiHandle.curContainerView
        self.returncontlist_2 = mainGuiHandle.returncontlist_2
        self.containerlisttable_2 = mainGuiHandle.containerlisttable_2
        self.inputFileButton = mainGuiHandle.inputFileButton
        self.removeFileButton = mainGuiHandle.removeFileButton
        self.editFileButton = mainGuiHandle.editFileButton
        self.commitNewButton = mainGuiHandle.commitNewButton
        self.refContainerView = mainGuiHandle.refContainerView
        self.containerName_lineEdit= mainGuiHandle.containerName_lineEdit
        self.descriptionText= mainGuiHandle.descriptionText
        self.messageText= mainGuiHandle.messageText
        self.GuiTab = mainGuiHandle.NewContainerTab
        self.inputFileButton = mainGuiHandle.inputFileButton
        self.editFileButton = mainGuiHandle.editFileButton
        self.removeFileButton = mainGuiHandle.removeFileButton
        self.mainGuiHandle = mainGuiHandle
        # self.tester= mainGuiHandle.tester
        # self.authtoken= mainGuiHandle.authtoken

        letters = string.ascii_letters
        self.containerName_lineEdit.setText(''.join(random.choice(letters) for i in range(10)) )
        self.descriptionText.setPlainText(''.join(random.choice(letters) for i in range(20)))
        self.messageText.setPlainText(''.join(random.choice(letters) for i in range(30)))


        self.inputFileButton.setEnabled(False)
        self.editFileButton.setEnabled(False)
        self.removeFileButton.setEnabled(False)
        self.selectedContainerId=''


        self.refContainerPlot = ContainerPlot(self, self.refContainerView, container=Container.InitiateContainer())

        self.returncontlist_2.clicked.connect(partial(mainGuiHandle.getContainerInfo, self.containerlisttable_2))
        self.containerlisttable_2.clicked.connect(self.showContainerFromList)
        self.inputFileButton.clicked.connect(self.addInputFileToTempContainer)
        self.fileheader = ''
        self.removeFileButton.clicked.connect(self.removeFileInfo)
        self.editFileButton.clicked.connect(self.editFileInfo)
        self.commitNewButton.clicked.connect(self.commitNewContainer)

        self.RequiredButton.clicked.connect(partial(self.AddToTempContainer, 'Required'))
        self.outputFileButton.clicked.connect(partial(self.AddToTempContainer, 'Output'))

    def setTab(self, tabon):
        self.GuiTab.setEnabled(tabon)

    def initiate(self, inputs):
        os.mkdir(inputs['dir'])
        os.mkdir(os.path.join(inputs['dir'], 'Main'))

        self.tempContainer = Container.InitiateContainer()
        self.tempContainer.containerName = inputs['containername']
        self.tempContainer.containerworkingfolder = inputs['dir']
        self.tempContainer.save()
        self.containerName_lineEdit.setText(inputs['containername'])

        self.workingdir = inputs['dir']

        self.tempContainer.workingFrame = Frame(localfilepath = inputs['dir'])
        self.tempContainer.workingFrame.parentcontainerid = inputs['containername']
        self.tempContainer.workingFrame.FrameName = 'Rev1'
        self.tempContainer.workingFrame.writeoutFrameYaml(os.path.join(inputs['dir'], 'Main', 'Rev1.yaml'))
        self.curContainerPlot = ContainerPlot(self, self.curContainerView, self.tempContainer) #Edit to use refContainer
        self.setTab(True)


    def AddToTempContainer(self, fileType: str):
        self.inputFileButton.setEnabled(False)
        fileInfoDialog = selectFileDialog(fileType, self.tempContainer.containerworkingfolder, self.mainGuiHandle.worldlist)
        fileInfo = fileInfoDialog.getInputs()
        if fileInfo:
            self.tempContainer.addFileObject(fileInfo['fileheader'], fileInfo['ContainerFileInfo'], fileType)
            if fileType =='Required':
                self.tempContainer.workingFrame.addFileTotrack(fileInfo['FilePath'], fileInfo['fileheader'], fileType)
            if fileType=='Output':
                self.tempContainer.workingFrame.addOutputFileTotrack(fileInfo, fileType)
            self.curContainerPlot.plot()

    def showContainerFromList(self, containerList):
        rownumber = containerList.row()
        index = containerList.model().index(rownumber, 0)
        containerId = containerList.model().data(index, 0)
        refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , 'containerstate.yaml')
        if os.path.exists(refcontainerpath):
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        else:
            refpath = os.path.join('ContainerMapWorkDir')
            Container.downloadContainerInfo(refpath,self.mainGuiHandle.authtoken, BASE, containerId)
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.changeContainer(self.selectedContainer)
        self.refContainerPlot.plot()


    def addInputFileToTempContainer(self):
        dialogWindow = inputFileDialog(self.selectedContainer.containerId, self.curfileheader)
        fileInfo = dialogWindow.getInputs()
        if fileInfo:
            branch='Main'
            fullpath, filetrack = self.selectedContainer.workingFrame.downloadInputFile(self.curfileheader,self.workingdir)
            self.tempContainer.addInputFileObject(fileheader=self.curfileheader,
                                                  reffiletrack = filetrack,
                                                  fullpath=fullpath,
                                                  refContainerId=self.selectedContainer.containerId,
                                                  branch=branch,
                                                  rev='Rev' + str(self.selectedContainer.revnum))

        # self.curContainerPlot.createInputRect()
        self.curContainerPlot.plot()
        self.inputFileButton.setEnabled(False)


    def editDeleteButtons(self,fileType: str, containerName ='', fileheader=''):
        # self.selectedContainerId = containerName
        self.curfileheader = fileheader
        self.removeFileButton.setEnabled(True)
        if fileType != 'Input':
            self.editFileButton.setEnabled(True)

    def editFileInfo(self):
        editFileDialog = selectFileDialog(self.curfiletype,self.tempContainer.containerworkingfolder)
        editFileInfo = editFileDialog.getInputs()
        if editFileInfo:
            self.editFileButton.setEnabled(False)
            self.removeFileButton.setEnabled(False)
            self.tempContainer.FileHeaders[editFileInfo['FileObjHeader']] = \
                self.tempContainer.FileHeaders.pop(self.curfileheader)
            del self.tempContainer.workingFrame.filestrack[self.curfileheader]
            self.tempContainer.workingFrame.addFileTotrack(editFileInfo['FilePath'], editFileInfo['FileObjHeader'], self.curfiletype)
            if self.curfileheader != editFileInfo['FileObjHeader']:
                self.curContainerPlot.editRect(self.curfileheader, editFileInfo['FileObjHeader'])
                self.curContainerPlot.plot()


    def removeFileInfo(self):
        fileDialog = removeFileDialog(self.curfileheader)
        fileheader = fileDialog.removeFile()
        if fileheader:
            self.editFileButton.setEnabled(False)
            self.removeFileButton.setEnabled(False)
            newTempContainer = copy.deepcopy(self.tempContainer)
            newTempFrame = copy.deepcopy(self.tempContainer.workingFrame)
            for key, value in self.tempContainer.FileHeaders.items():
                if key == fileheader:
                    del newTempContainer.FileHeaders[key]
            self.tempContainer = newTempContainer

            for key,value in self.tempContainer.workingFrame.filestrack.items():
                if key == fileheader:
                    del newTempFrame.filestrack[key]
            self.tempContainer.workingFrame = newTempFrame
            self.curContainerPlot.removeRect(fileheader)

    def commitNewContainer(self):
        if '' not in [self.containerName_lineEdit.text(), self.descriptionText.toPlainText(),
                      self.messageText.toPlainText()]:
            commitCheck = commitDialog(self.containerName_lineEdit.text(), self.descriptionText.toPlainText(),
                                       self.messageText.toPlainText())
            commited = commitCheck.commit()
            if commited:
                containerName=self.containerName_lineEdit.text()
                commitmessage= self.messageText.toPlainText()
                success = self.tempContainer.CommitNewContainer(containerName,commitmessage,self.mainGuiHandle.authtoken,BASE)
                if success:
                    self.setTab(False)
                    containeryaml = os.path.join(self.tempContainer.containerworkingfolder, 'containerstate.yaml')
                    self.mainGuiHandle.maincontainertab.readcontainer(containeryaml)
                    self.mainGuiHandle.tabWidget.setCurrentIndex(self.mainGuiHandle.maincontainertab.index)
                else:
                    print('Commit failed')
        else:
            self.errorMessage = ErrorMessage()
            self.errorMessage.showError()