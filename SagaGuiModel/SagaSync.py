import os
from os.path import join, exists
from Config import BASE, CONTAINERFN, TEMPCONTAINERFN
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack
import json
import hashlib
from Graphics.QAbstract.ConflictListModel import ConflictListModel, AddedListModel, DeletedListModel, UpstreamListModel
from Config import BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,SERVERNEWREVISION,\
    SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN,NOTINSYNCREASONSET
from SagaGuiModel.SagaAPICall import SagaAPICall
class SagaSync():
    def __init__(self, sagaapicall, desktopdir):
        self.changes = {}
        self.sagaapicall:SagaAPICall=sagaapicall
        self.newestframe:Frame  = None# this is the latest Server frame committed for this container.
        self.workingframe:Frame =None
        self.upstreamframe:Frame =None
        self.localframe:Frame = None
        self.desktopdir = desktopdir

    def setUpstreamFrame(self, upstreamframe:Frame):
        self.upstreamframe = upstreamframe
    def setWorkingFrame(self,workingframe:Frame):
        self.workingframe = workingframe
    def setNewestFrame(self, newestframe: Frame):
        self.newestframe = newestframe
    def setLocalFrame(self, localframe: Frame):
        self.localframe = localframe

    def checkUpstream(self, container:Container):
        upstreamupdated = False
        workingFrame = container.workingFrame
        refFrame = Frame.loadRefFramefromYaml(container.refframefullpath,
                                              workingFrame.containerworkingfolder)
        for fileheader in container.filestomonitor().keys():
            if workingFrame.filestrack[fileheader].connection.connectionType.name == typeInput:
                if workingFrame.filestrack[
                    fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                    # Check to see if input file is internal to container, not referencing other containers
                    containerID = workingFrame.filestrack[fileheader].connection.refContainerId

                    upstreamcont = Container.LoadContainerFromYaml(containerfnfullpath=
                                                                   join(self.desktopdir, 'ContainerMapWorkDir', containerID, CONTAINERFN))
                    if upstreamcont is None:
                        containerworkingfolder, upstreamcont = self.sagaapicall.downloadContainer(join(self.desktopdir, 'ContainerMapWorkDir'),
                                                                                                   containerID, 'NetworkContainer')
                    upstreamframe = upstreamcont.getRefFrame()
                    # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                    # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.
                    # if ref frame is upstreammd5  its fine, if workingframe is upstreammd5 its fine.
                    # if upstream md5 not equal to

                    md5notsameasupstream = upstreamframe.filestrack[fileheader].md5 not in [ refFrame.filestrack[fileheader].md5,workingFrame.filestrack[fileheader].md5]
                    # refnum = revNumber(refFrame.filestrack[fileheader].connection.Rev)
                    # upstreamrevnumberlarger = revNumber(upstreamframe.FrameName)>refnum
                    if md5notsameasupstream:
                        if fileheader in self.changes.keys():
                            self.changes[fileheader] = {
                                'reason': [UPDATEDUPSTREAM] + self.changes[fileheader]['reason'],
                                'revision': upstreamframe.FrameName,
                                'md5': upstreamframe.filestrack[fileheader].md5,
                                'upstreamframe': upstreamframe,
                                'fromcontainer':upstreamcont}
                        else:
                            self.changes[fileheader] = {'reason': [UPDATEDUPSTREAM],
                                                        'revision': upstreamframe.FrameName,
                                                        'md5': upstreamframe.filestrack[fileheader].md5,
                                                        'upstreamframe': upstreamframe,
                                                        'fromcontainer':upstreamcont}
                        upstreamupdated=True
        return  upstreamupdated

    def syncStatusModels(self):
        self.conflictlistmodel = ConflictListModel(self.changes, self.newestframe)
        self.addedlistmodel = AddedListModel(self.changes, self.newestframe)
        self.deletedlistmodel = DeletedListModel(self.changes, self.newestframe,
                                                 self.workingframe)
        self.upstreamlistmodel = UpstreamListModel(self.changes)
        return self.conflictlistmodel, self.addedlistmodel, self.deletedlistmodel, self.upstreamlistmodel, self.changes

    def checkLatestRevision(self, maincontainer:Container, newestrevnum):
        ## This is the only place that knows of a later revision.
        self.newestFiles = {}
        notlatestrev = maincontainer.revnum < newestrevnum
        if notlatestrev:
            # self.refreshContainerBttn.setEnabled(True)
            # if maincontainer.workingframe.refreshedcheck:
            #     statustext='Newer Revision Exists!' + ' Current Rev: ' + maincontainer.workingframe.refreshrevnum\
            #                + ', Latest Rev: ' + str(self.newestrevnum)
            # else:
            statustext = 'Newer Revision Exists!' + ' Current Rev: ' + str(maincontainer.revnum)\
                         + ', Latest Rev: ' + str(newestrevnum)
            # if the newest rev num is different from local rev num:
            # loop through filesttrack of both newest frame, check if file exists in current frame and compare MD5s,
            # if exists, add update message to changes, if notadd new file message
            refframe = maincontainer.getRefFrame()
            for fileheader in self.newestframe.filestrack.keys():
                if fileheader in refframe.filestrack.keys():
                    if self.newestframe.filestrack[fileheader].md5 != refframe.filestrack[fileheader].md5:
                        if fileheader in self.changes.keys():
                            self.changes[fileheader]['reason'].append(SERVERNEWREVISION)
                        else:
                            self.changes[fileheader] = {'reason': [SERVERNEWREVISION]}
                        # if 'File updated....' is within changes reason dictionary, display delta in GUI
                else:
                    self.changes[fileheader] = {'reason': [SERVERFILEADDED]}

            # Loop through working frame to check if any files have been deleted in new revision
            for fileheader in refframe.filestrack.keys():
                if fileheader not in self.newestframe.filestrack.keys():
                    if fileheader in self.changes.keys():
                        self.changes[fileheader]['reason'].append(SERVERFILEDELETED)
                    else:
                        self.changes[fileheader] = {'reason': [SERVERFILEDELETED]}
        else:
            statustext='This is the latest revision'
        return statustext , notlatestrev

    def checkContainerChanged(self, maincontainer:Container):
        refContainer = Container.LoadContainerFromYaml(maincontainer.yamlpath())
        identical, diff = Container.compare(refContainer, maincontainer)
        containerchanged = not identical ## just for readablity
        return containerchanged

    def checkChangeIsRelevant(self,maincontainer:Container):
        changeisrelevant=False
        for fileheader, changedetails in self.changes.items():
            if fileheader in maincontainer.filestomonitor().keys():
                # only set allowCommit to true if the changes involve what is in the Container's need to monitor
                changeisrelevant = True
        return changeisrelevant

    def checkContainerStatus(self, container, newestrevnum):
        ###################ORDER IS IMPORTANT HERE..I think####
        self.localframe = container.getRefFrame()
        self.workingframe = container.workingFrame


        self.changes = {}
        self.changes, self.alterfiletracks = container.compareToRefFrame(self.changes)
        upstreamupdated = self.checkUpstream(container)
        statustext, notlatestrev = self.checkLatestRevision(container,newestrevnum)
        containerchanged = self.checkContainerChanged(container)
        changeisrelevant = self.checkChangeIsRelevant(container)

        return upstreamupdated, statustext, notlatestrev, containerchanged ,changeisrelevant, self.changes

    def updateContainerWithUserSelection(self,filelist, container:Container):
        wf = container.workingFrame
        nf = self.newestframe
        if filelist:
            wf.refreshedcheck = True
            for fileheader in filelist.keys():
                if filelist[fileheader] == 'Overwrite':
                    fn = self.sagaapicall.downloadFileCall(filetrack=nf.filestrack[fileheader],
                                                   filepath=container.containerworkingfolder)
                    wf.filestrack[fileheader].md5 = nf.filestrack[fileheader].md5
                    wf.filestrack[fileheader].lastEdited = nf.filestrack[fileheader].lastEdited

                elif filelist[fileheader] == 'Download Copy':
                    filename, ext = os.path.splitext(wf.filestrack[fileheader].file_name)
                    filecopy_name = filename + '_' + nf.FrameName + 'Copy' + \
                                    ext
                    fn = self.sagaapicall.downloadFileCall(nf.filestrack[fileheader],
                                                   wf.containerworkingfolder, filecopy_name)
                    print('No changes to Frame')
                elif filelist[fileheader] == 'Download':
                    fn = self.sagaapicall.downloadFileCall(nf.filestrack[fileheader],
                                                   wf.containerworkingfolder)
                    ft = nf.filestrack[fileheader]
                    if ft.connection.connectionType.name in [typeRequired, typeOutput]:
                        wf.filestrack[fileheader] = nf.filestrack[fileheader]
                    else:
                        raise ('Under Construction')
                    # sagaguimodel.maincontainer.addFileObject(fileinfo=newfileobj)
                elif filelist[fileheader] == 'Delete':
                    filePath = os.path.join(
                        wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                        wf.filestrack[fileheader].file_name)
                    if os.path.exists(filePath):
                        os.remove(filePath)
                        container.removeFileHeader(fileheader)
                    else:
                        print("The file does not exist")
                elif filelist[fileheader] == 'ReplaceInput':
                    upstreamframe = self.changes[fileheader]['upstreamframe']
                    fileEditPath = self.sagaapicall.downloadFileCall(upstreamframe.filestrack[fileheader],
                                                             wf.containerworkingfolder)
                    fileb = open(fileEditPath, 'rb')
                    upstreammd5 = hashlib.md5(fileb.read()).hexdigest()  ## md5 shouldn't need to be reread
                    if upstreammd5 != upstreamframe.filestrack[fileheader].md5:
                        raise (
                            'Saga Error: upstream md5 and downloaded md5 file does not match')  # sanity check for now
                    wf.filestrack[fileheader].md5 = upstreammd5  ### IS this really necessary?
                    wf.filestrack[fileheader].connection.Rev = self.changes[fileheader]['revision']

            wf.writeoutFrameYaml()

    def iscontainerinsync(self):
        iscontainerinsync = True
        for fileheader, change in self.changes.items():
            if len(set(change['reason']).intersection(NOTINSYNCREASONSET))>0:
                iscontainerinsync= False

        return iscontainerinsync
