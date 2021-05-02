from Graphics.Dialogs import ErrorMessage, inputFileDialog, removeFileDialog, selectFileDialog, commitDialog,alteredinputFileDialog
from functools import partial
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from Graphics.ContainerPlot import ContainerPlot
from Config import BASE
from Config import typeInput,typeRequired,typeOutput
import os
import copy
import random
import string
from Graphics.GuiUtil import AddIndexToView

class NewContainerTab():
    def __init__(self, mainguihandle):
        self.index = 2
        self.inputFileButton = mainguihandle.inputFileButton
        self.RequiredButton = mainguihandle.RequiredButton
        self.outputFileButton = mainguihandle.outputFileButton
        self.curContainerView = mainguihandle.curContainerView
        self.returncontlist_2 = mainguihandle.returncontlist_2
        self.containerlisttable_2 = mainguihandle.containerlisttable_2

        self.removeFileButton = mainguihandle.removeFileButton
        # self.editFileButton = mainguihandle.editFileButton
        self.commitNewButton = mainguihandle.commitNewButton
        self.refContainerView = mainguihandle.refContainerView
        self.containerName_lineEdit= mainguihandle.containerName_lineEdit
        self.descriptionText= mainguihandle.descriptionText
        self.messageText= mainguihandle.messageText
        self.GuiTab = mainguihandle.NewContainerTab
        self.inputFileButton = mainguihandle.inputFileButton
        # self.editFileButton = mainguihandle.editFileButton
        self.removeFileButton = mainguihandle.removeFileButton
        self.mainguihandle = mainguihandle
        self.indexView2 = mainguihandle.indexView2
        # self.tester= mainguihandle.tester
        # self.authtoken= mainguihandle.authtoken

        letters = string.ascii_letters
        self.containerName_lineEdit.setText(''.join(random.choice(letters) for i in range(10)) )
        self.descriptionText.setPlainText(''.join(random.choice(letters) for i in range(20)))
        self.messageText.setPlainText(''.join(random.choice(letters) for i in range(30)))


        self.inputFileButton.setEnabled(False)
        # self.editFileButton.setEnabled(False)
        self.removeFileButton.setEnabled(False)
        self.selectedContainerId=''


        self.refContainerPlot = ContainerPlot(self, self.refContainerView, container=Container.InitiateContainer())

        self.returncontlist_2.clicked.connect(partial(mainguihandle.getContainerInfo, self.containerlisttable_2))
        self.containerlisttable_2.clicked.connect(self.showContainerFromList)
        self.inputFileButton.clicked.connect(self.addInputFileToTempContainer)
        self.fileheader = ''
        self.removeFileButton.clicked.connect(self.removeFileInfo)
        # self.editFileButton.clicked.connect(self.editFileInfo)
        self.commitNewButton.clicked.connect(self.commitNewContainer)

        self.RequiredButton.clicked.connect(partial(self.AddToTempContainer, 'Required'))
        self.outputFileButton.clicked.connect(partial(self.AddToTempContainer, 'Output'))
        AddIndexToView(self.indexView2)
        self.changes = {}

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
        fileInfoDialog = selectFileDialog(fileType, self.tempContainer.containerworkingfolder, self.mainguihandle.worldlist)
        fileInfo = fileInfoDialog.getInputs()
        if fileInfo:
            self.tempContainer.addFileObject(fileInfo['fileheader'], fileInfo['ContainerFileInfo'], fileType)
            if fileType =='Required':
                self.tempContainer.workingFrame.addFileTotrack(fileInfo['FilePath'], fileInfo['fileheader'], fileType)
            if fileType=='Output':
                self.tempContainer.workingFrame.addOutputFileTotrack(fileInfo, fileType)
            self.curContainerPlot.plot(self.changes)

    def showContainerFromList(self, containerList):
        rownumber = containerList.row()
        index = containerList.model().index(rownumber, 0)
        containerId = containerList.model().data(index, 0)
        index = containerList.model().index(rownumber, 3)
        revNum = containerList.model().data(index,0)
        refcontainerpath = os.path.join('ContainerMapWorkDir', containerId , 'containerstate.yaml')
        if os.path.exists(refcontainerpath):
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath, revnum = revNum)
        else:
            refpath = os.path.join('ContainerMapWorkDir')
            Container.downloadContainerInfo(refpath,self.mainGuiHandle.authtoken, BASE, containerId)
            self.selectedContainer = Container.LoadContainerFromYaml(refcontainerpath, revnum = revNum)
        # self.tester.setText(self.selectedContainer.containerName)
        self.refContainerPlot.changeContainer(self.selectedContainer)
        self.refContainerPlot.plot(self.changes)


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
        self.curContainerPlot.plot(self.changes)
        self.inputFileButton.setEnabled(False)


    def coolerRectangleFeedback(self, type, view, fileheader , curContainer):
        # self.selectedContainerId = containerName
        if view == self.refContainerView:
            if type == typeOutput:
                self.inputFileButton.setEnabled(True)
                self.removeFileButton.setEnabled(False)
                # self.editFileButton.setEnabled(False)
            else:
                self.inputFileButton.setEnabled(False)
                self.removeFileButton.setEnabled(True)
                # self.editFileButton.setEnabled(True)
            self.curfileheader = fileheader
            self.selectedContainer = curContainer
            self.curfiletype = type
            # self.guiHandle.tester.setText(self.guiHandle.filetype)
        elif view == self.curContainerView:
            self.curfileheader = fileheader
            self.removeFileButton.setEnabled(True)
            # if type == typeInput:
                # self.editFileButton.setEnabled(True)

    def editFileInfo(self):
        editFileDialog = selectFileDialog(self.curfiletype,self.tempContainer.containerworkingfolder)
        editFileInfo = editFileDialog.getInputs()
        if editFileInfo:
            # self.editFileButton.setEnabled(False)
            self.removeFileButton.setEnabled(False)
            self.tempContainer.FileHeaders[editFileInfo['FileObjHeader']] = \
                self.tempContainer.FileHeaders.pop(self.curfileheader)
            del self.tempContainer.workingFrame.filestrack[self.curfileheader]
            self.tempContainer.workingFrame.addFileTotrack(editFileInfo['FilePath'], editFileInfo['FileObjHeader'], self.curfiletype)
            if self.curfileheader != editFileInfo['FileObjHeader']:
                self.curContainerPlot.editRect(self.curfileheader, editFileInfo['FileObjHeader'])
                self.curContainerPlot.plot(self.changes)


    def removeFileInfo(self):
        fileDialog = removeFileDialog(self.curfileheader)
        fileheader = fileDialog.removeFile()
        if fileheader:
            # self.editFileButton.setEnabled(False)
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


