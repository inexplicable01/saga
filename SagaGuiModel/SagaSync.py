import os
from os.path import join, exists
from Config import BASE, CONTAINERFN, TEMPCONTAINERFN
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.Change import Change
import warnings
from SagaApp.FileObjects import FileTrack
import json
import hashlib
from Graphics.QAbstract.ConflictListModel import SyncListModel
from Config import BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,SERVERNEWREVISION,\
    SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, \
    TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN,NOTINSYNCREASONSET, \
    LOCALFILEHEADERADDED, LOCALFILEHEADERREMOVED,MD5CHANGED
from SagaGuiModel.SagaAPICall import SagaAPICall
from SagaGuiModel.SyncScenario import *


class SagaSync():
    def __init__(self, sagaguimodel, desktopdir):
        self.changes = {}
        self.sagaguimodel = sagaguimodel
        self.sagaapicall:SagaAPICall=sagaguimodel.sagaapicall
        self.newestframe:Frame  = None# this is the latest Server frame committed for this container.
        self.workingframe:Frame =None
        self.upstreamframe:Frame =None
        self.localframe:Frame = None
        self.desktopdir = desktopdir

    def reset(self):
        self.newestframe: Frame = None  # this is the latest Server frame committed for this container.
        self.workingframe: Frame = None
        self.upstreamframe: Frame = None
        self.localframe: Frame = None
        self.changes = {}

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

                    # upstreamcont = Container.LoadContainerFromYaml(containerfnfullpath=
                    #                                                join(self.desktopdir, 'ContainerMapWorkDir', containerID, CONTAINERFN))
                    # if upstreamcont is None:
                    containerworkingfolder, upstreamcont = self.sagaapicall.downloadContainerCall(join(self.desktopdir, 'ContainerMapWorkDir', containerID),
                                                                                                   containerID, ismaincontainer=False)
                    upstreamframe = upstreamcont.getRefFrame()
                    # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                    # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.
                    # if ref frame is upstreammd5  its fine, if workingframe is upstreammd5 its fine.
                    # if upstream md5 not equal to
                    if fileheader not in refFrame.filestrack.keys():
                        md5notsameasupstream = upstreamframe.filestrack[fileheader].md5!=workingFrame.filestrack[fileheader].md5
                        ## This also means this is newly added
                        ## One explanation User just downloaded the input file and has altered it already.
                        ## Or Upstream container has already updated there
                    else:
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

    # def syncStatusModels(self):
    #     self.conflictlistmodel = ConflictListModel(self.changes, self.newestframe)
    #     self.addedlistmodel = AddedListModel(self.changes, self.newestframe)
    #     self.deletedlistmodel = DeletedListModel(self.changes, self.newestframe,
    #                                              self.workingframe)
    #     self.upstreamlistmodel = UpstreamListModel(self.changes)
    #     return self.conflictlistmodel, self.addedlistmodel, self.deletedlistmodel, self.upstreamlistmodel, self.changes

    def syncStatusModels2(self, maincontainer:Container, containeridtoname):
        self.conflictlistmodel = SyncListModel(self.changes, self.newestframe, maincontainer, containeridtoname, option='conflict')
        self.noticelistmodel = SyncListModel(self.changes, self.newestframe, maincontainer, containeridtoname, option='notice')
        # self.attentionmodel= AttentionModel(self.changes, self.newestframe)
        # self.deletedlistmodel = DeletedListModel(self.changes, self.newestframe,
        #                                          self.workingframe)
        # self.upstreamlistmodel = UpstreamListModel(self.changes)
        return self.conflictlistmodel, self.noticelistmodel

    def checkLatestRevision(self, maincontainer:Container, newestrevnum):
        ## This is the only place that knows of a later revision.
        # self.newestFiles = {}
        notlatestrev = maincontainer.revnum < newestrevnum
        if notlatestrev:
            # self.refreshContainerBttn.setEnabled(True)
            # if maincontainer.workingframe.refreshedcheck:
            #     statustext='Newer Revision Exists!' + ' Current Rev: ' + maincontainer.workingframe.refreshrevnum\
            #                + ', Latest Rev: ' + str(self.newestrevnum)
            # else:
            statustext = 'Newer Revision Exists!' + ' Current Rev: ' + str(maincontainer.revnum)\
                         + ', Latest Rev: ' + str(newestrevnum)
            # # if the newest rev num is different from local rev num:
            # # loop through filesttrack of both newest frame, check if file exists in current frame and compare MD5s,
            # # if exists, add update message to changes, if notadd new file message
            # refframe = maincontainer.getRefFrame()
            # for fileheader in self.newestframe.filestrack.keys():
            #     if fileheader in refframe.filestrack.keys():
            #         if self.newestframe.filestrack[fileheader].md5 != refframe.filestrack[fileheader].md5:
            #             if fileheader in self.changes.keys():
            #                 self.changes[fileheader]['reason'].append(SERVERNEWREVISION)
            #             else:
            #                 self.changes[fileheader] = {'reason': [SERVERNEWREVISION]}
            #             # if 'File updated....' is within changes reason dictionary, display delta in GUI
            #     else:
            #         self.changes[fileheader] = {'reason': [SERVERFILEADDED]}
            #
            # # Loop through working frame to check if any files have been deleted in new revision
            # for fileheader in refframe.filestrack.keys():
            #     if fileheader not in self.newestframe.filestrack.keys():
            #         if fileheader in self.changes.keys():
            #             self.changes[fileheader]['reason'].append(SERVERFILEDELETED)
            #         else:
            #             self.changes[fileheader] = {'reason': [SERVERFILEDELETED]}
        else:
            statustext='This is the latest revision'
        return statustext , notlatestrev

    # def checkContainerChanged(self, maincontainer:Container):
    #     refContainer = Container.LoadContainerFromYaml(maincontainer.yamlpath())
    #     identical, diff = Container.compare(refContainer, maincontainer)
    #     containerchanged = not identical ## just for readablity
    #     return containerchanged

    def checkChangeIsRelevant(self,maincontainer:Container):
        changeisrelevant=False
        for fileheader, changedetails in self.changes.items():
            if fileheader in maincontainer.filestomonitor().keys():
                # only set allowCommit to true if the changes involve what is in the Container's need to monitor
                changeisrelevant = True
        return changeisrelevant

    # def checkContainerStatus(self, container, newestrevnum):
    #     ###################ORDER IS IMPORTANT HERE..I think####
    #     self.localframe = container.getRefFrame()
    #     self.workingframe = container.workingFrame
    #
    #     self.changes = {}
    #     self.changes, self.alterfiletracks = container.compareToRefFrame(self.changes)
    #     upstreamupdated = self.checkUpstream(container)
    #     statustext, notlatestrev = self.checkLatestRevision(container,newestrevnum)
    #     containerchanged = self.checkContainerChanged(container)
    #     changeisrelevant = self.checkChangeIsRelevant(container)
    #
    #     return upstreamupdated, statustext, notlatestrev, containerchanged ,changeisrelevant, self.changes

    def checkContainerStatus(self, container:Container, newestrevnum):
        self.inconflict = False

        upstreamupdated = False
        containerchanged = False
        self.localframe = container.getRefFrame()
        self.workingframe = container.workingFrame
        lf = self.localframe
        wf = self.workingframe
        nf = self.newestframe

        statustext, notlatestrev = self.checkLatestRevision(container,newestrevnum)

        changes = {}
        if nf is None:
            newestframefileheaders = set([])
        else:
            newestframefileheaders = set(nf.filestrack.keys())

        wffileheaders = set(wf.filestrack.keys())
        combinedheaders = set(lf.filestrack.keys())
        combinedheaders.update(wffileheaders)
        combinedheaders.update(newestframefileheaders)
        for fileheader in combinedheaders:
            inlf = fileheader in lf.filestrack.keys()
            inwf = fileheader in wf.filestrack.keys()
            innf = fileheader in newestframefileheaders
            if inlf:
                filetype = lf.filestrack[fileheader].connection.connectionType.name
            if inwf:
                filetype = wf.filestrack[fileheader].connection.connectionType.name
            if innf:
                filetype = nf.filestrack[fileheader].connection.connectionType.name
            # if not wf.filestrack[fileheader].connection.connectionType.name==\
            #     lf.filestrack[fileheader].connection.connectionType.name==\
            #     nf.filestrack[fileheader].connection.connectionType.name:
            #     raise(fileheader + ' local frame, working frame and newest frame has different file types. Saga not prepared to deal with that yet')
            #
            #

            #Assumes users doesn't change filetype on you.
            ## ATTENTION PUT CHECKER IN TO make sure all 3 file types are the same
            c = Change(fileheader, filetype, container)

            if inlf:
                c.lffiletrack = lf.filestrack[fileheader]
            if inwf:
                c.wffiletrack = wf.filestrack[fileheader]
            if innf:
                c.nffiletrack = nf.filestrack[fileheader]

            if inwf and inlf:
                c.md5changed = lf.filestrack[fileheader].md5!=wf.filestrack[fileheader].md5# check for md5 change
                containerchanged = True

            ## Fileheaders h
            if not inlf and inwf:
                c.reason.append(LOCALFILEHEADERADDED)
                containerchanged = True
            elif inlf and not inwf:
                c.reason.append(LOCALFILEHEADERADDED)
                containerchanged = True

            if container.revnum < newestrevnum:
                if not inlf and innf:
                    c.reason.append(SERVERFILEADDED)
                elif inlf and not innf:
                    c.reason.append(SERVERFILEDELETED)
                c.newerframeexists = True
                if innf:
                    c.nffiletrack = nf.filestrack[fileheader]
                    c.needtoregardnewest = True

            if c.filetype==typeInput:
                if fileheader=='AnaylsisReport':
                    b= 4
                # containerID =
                # upstreamcontyaml = join(self.desktopdir, 'ContainerMapWorkDir', containerID, CONTAINERFN)
                # # containerworkingfolder, upstreamcont = self.sagaapicall.downloadContainerCall(
                # #     join(self.desktopdir, 'ContainerMapWorkDir', containerID),
                # #     containerID, ismaincontainer=False)
                upstreamcont = self.sagaguimodel.provideContainer(wf.filestrack[fileheader].connection.refContainerId)
                uf = upstreamcont.getRefFrame()
                c.upcont = upstreamcont
                upstreamframefileheaderset = set(uf.filestrack.keys())
                if fileheader not in upstreamframefileheaderset:
                    warnings.warn('Somethings broken.  Upstream frame should have this fileheader. ')
                    c.missinginput=True## in uf?
                    # if wf.filestrack[fileheader].md5 in upstreamcont.filemd5history[fileheader].keys():
                    #     uf.filestrack[fileheader].lastupdated
                    #     c.wffiletrack = wf.filestrack[fileheader]
                    #     c.uffiletrack = uf.filestrack[fileheader]
                    #     # c.wffiletrack = wf.filestrack[fileheader]
                    # else:
                    #     c.needdecisionfromuser = True
                    #     c.description(USERCREATEDALTEREDINPUT)
                else:
                    if wf.filestrack[fileheader].md5 not in upstreamcont.filemd5history[fileheader].keys():
                        c.alterinput = True  ## in uf?
                    else:
                        c.uffiletrack = uf.filestrack[fileheader]
                        if c.uffiletrack.lastupdated!= wf.filestrack[fileheader].lastupdated:
                            upstreamupdated=True
                    inuf=True
                if c.newerframeexists:
                    c.inputscenariono = 4 * innf + 2 * inlf + inwf
                else:
                    c.inputscenariono = 2 * inlf + inwf + 7

                # if container.revnum < newestrevnum:## Need to sync, lf, wf, nf, uf
                #     c.newerframeexists = True
                #  # if 7,6,5 and 15,14,13,12


            if c.newerframeexists:
                c.reqoutscenariono = 4*innf + 2*inlf + inwf
            else:
                c.reqoutscenariono =  2 * inlf + inwf + 7
                # Check if Newest fileheader added
            # refframefileheaders = list(lf.filestrack.keys())
            # for fileheader in wf.FileHeaders.keys():
                ## how to manage if container and frame deviates on fileheader counts

                # if fileheader not in refframe.filestrack.keys() and fileheader not in wf.filestrack.keys():
                #     # check if fileheader is in neither refframe or current frame,
                #     raise ('somehow Container needs to track ' + fileheader + 'but its not in ref frame or current frame')
            c.analysisState()
            if c.conflict:
                self.inconflict = True## If any change is in conflict
            changes[fileheader] = c
        self.changes = changes
        return upstreamupdated, statustext, notlatestrev, containerchanged, self.changes
        # refframe = Frame.loadRefFramefromYaml(self.refframefullpath,self.containerworkingfolder)

    # def SyncInputFiletrack(self, upstreamupdated, wfft:FileTrack, ufft:FileTrack, upcont:Container, c:Change, nfft:FileTrack = None, newestexist=False):
    #     # UF Rev,WF Rev, NF Rev)
    #     # upstreamupdated = False
    #     wfuprevnum = numofRev(wfft.lastupdated)
    #
    #     latestframe = numofRev(upcont.getRefFrame().FrameName)
    #     ufrevnum = numofRev(ufft.lastupdated)
    #     if nfft:
    #         nfuprevnum = numofRev(nfft.lastupdated)
    #         if wfuprevnum == ufrevnum:
    #             if wfuprevnum == nfuprevnum:  # tri1
    #                 c.needrefresh = False
    #                 c.description = INPUT_NEWFRAME_SCENARIO15A
    #                 # c.nffiletrack = nfft   No Conflict
    #             else:  # NF is out of sync although wrking frame is in sync.
    #                 c.needrefresh = False
    #                 c.description = INPUT_NEWFRAME_SCENARIO15B
    #
    #         else:  # wfuprevnum != ufrevnum:
    #             upstreamupdated = True
    #             if wfuprevnum==nfuprevnum:
    #                 c.reason.append('NFFILEHEADEROUTDATED')
    #                 c.description = INPUT_NEWFRAME_SCENARIO15C
    #                 c.needdecisionfromuser = True
    #                 pass  # WF and NF are at the same frame but not the same with upstream, no conflict.  Does WF want to update?
    #             elif ufrevnum == nfuprevnum:# WF not eual to UF and NF same as UF means that NEwest frame is updated.   most likely newest frame has updated sync.
    #                 c.needdecisionfromuser = True
    #                 c.reason.append('NFFILEHEADEROUTDATED')
    #                 c.description = INPUT_NEWFRAME_SCENARIO15D
    #             else:
    #                 c.needdecisionfromuser = True
    #                 c.description = INPUT_NEWFRAME_SCENARIO15E
    #                 # c.reason.append('NFFILEHEADEROUTDATED')
    #     # else:
    #     #     if wfuprevnum == ufrevnum:
    #     #         c.needdecisionfromuser = False
    #     #         c.description = INPUT_NEWFRAME_SCENARIO7A if newestexist else INPUT_LOCALFRAME_SCENARIO7A
    #     #     else:
    #     #         upstreamupdated = True
    #     #         c.needdecisionfromuser = True
    #     #         c.description = INPUT_NEWFRAME_SCENARIO7B if newestexist else INPUT_LOCALFRAME_SCENARIO7B
    #     return c , upstreamupdated
    # #
    # def md5comparison(self):
    #     if c.lffiletrack.md5 == c.wffiletrack.md5:
    #         if c.wffiletrack.md5 == c.nffiletrack.md5:
    #             print('everything is in sync')
    #         else:
    #             print('nf is updated.  Need to Refresh/Conflict')
    #     else:
    #         if c.wffiletrack.md5 == c.nffiletrack.md5:
    #             print('somehow wf file is same as newest and different from local')
    #         else:
    #             if c.lffiletrack.md5 != c.nffiletrack.md5:
    #                 print('lf!=wf!=nf Newest is updated to something else and youve updated also. So '
    #                       'conflict.  Need to resolve which version.')
    #             else:
    #                 print('lf!=wf!=nf but lf==nf  Newest hasnt changed from Lf, so you there is not really a conflict'
    #                       + 'User would simply create a new version of this file.')
    #
    #         # calculate md5 of file, if md5 has changed, update md5
    #
    #
    #     #         wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
    #     #         changes[fileheader] = {'reason': [MD5CHANGED]}
    #     #         if wf.filestrack[fileheader].connection.connectionType==typeInput:
    #     #             alterfiletracks.append(wf.filestrack[fileheader])
    #     #         # if file has been updated, update last edited
    #     #         wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
    #     #         continue
    #     #     elif wf.filestrack[fileheader].lastEdited != refframe.filestrack[fileheader].lastEdited:
    #     #         changes[fileheader] = {'reason': [DATECHANGED]}
    #     #         wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
    #     #         print('Date changed without Md5 changing')
    #     #         continue
    #     #
    #     # for removedheaders in refframefileheaders:
    #     #     changes[removedheaders] = {'reason': [LOCALFILEHEADERREMOVED]}
    #     # self.changes = gatherfileheaders(self.localframe, self.workingframe, self.newestframe)
    #     # self.changes, self.alterfiletracks = container.compareToRefFrame(self.changes)
    #     # upstreamupdated = self.checkUpstream(container)
    #     # statustext, notlatestrev = self.checkLatestRevision(container,newestrevnum)
    #     # containerchanged = self.checkContainerChanged(container)
    #     # changeisrelevant = self.checkChangeIsRelevant(container)
    #     #
    #     # return upstreamupdated, statustext, notlatestrev, containerchanged ,changeisrelevant, self.changes

    def updateContainerWithUserSelection(self,combinedactionstate, container:Container):
        wf = container.workingFrame
        nf = self.newestframe
        # if combinedactionstate:
        #     wf.refreshedcheck = True
        #     for fileheader, actionlist in combinedactionstate.items():
        #         copies = []
        #         for action in self.actionstate[fileheader]:
        #             if action['main']:
        #                 mainaction = action
        #             else:
        #                 copies.append(action)
        #
        #         ### Main action sets to the working frame
        #         fn = self.sagaapicall.downloadFileCall(filetrack=nf.filestrack[fileheader],
        #                                        containerworkingfolder=container.containerworkingfolder)
        #         wf.filestrack[fileheader].md5 = nf.filestrack[fileheader].md5
        #         wf.filestrack[fileheader].lastEdited = nf.filestrack[fileheader].lastEdited


                # if actions == 'Overwrite':
                #     fn = self.sagaapicall.downloadFileCall(filetrack=nf.filestrack[fileheader],
                #                                    containerworkingfolder=container.containerworkingfolder)
                #     wf.filestrack[fileheader].md5 = nf.filestrack[fileheader].md5
                #     wf.filestrack[fileheader].lastEdited = nf.filestrack[fileheader].lastEdited
                #
                # elif filelist[fileheader] == 'Download Copy':
                #     filename, ext = os.path.splitext(wf.filestrack[fileheader].file_name)
                #     filecopy_name = filename + '_' + nf.FrameName + 'Copy' + \
                #                     ext
                #     fn = self.sagaapicall.downloadFileCall(nf.filestrack[fileheader],
                #                                    wf.containerworkingfolder, filecopy_name)
                #     print('No changes to Frame')
                # elif filelist[fileheader] == 'Download':
                #     fn = self.sagaapicall.downloadFileCall(nf.filestrack[fileheader],
                #                                    wf.containerworkingfolder)
                #     ft = nf.filestrack[fileheader]
                #     if ft.connection.connectionType.name in [typeRequired, typeOutput]:
                #         wf.filestrack[fileheader] = nf.filestrack[fileheader]
                #     else:
                #         raise ('Under Construction')
                #     # sagaguimodel.maincontainer.addFileObject(fileinfo=newfileobj)
                # elif filelist[fileheader] == 'Delete':
                #     filePath = os.path.join(
                #         wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                #         wf.filestrack[fileheader].file_name)
                #     if os.path.exists(filePath):
                #         os.remove(filePath)
                #         container.removeFileHeader(fileheader)
                #     else:
                #         print("The file does not exist")
                # elif filelist[fileheader] == 'ReplaceInput':
                #     upstreamframe = self.changes[fileheader]['upstreamframe']
                #     fileEditPath = self.sagaapicall.downloadFileCall(upstreamframe.filestrack[fileheader],
                #                                              wf.containerworkingfolder)
                #     fileb = open(fileEditPath, 'rb')
                #     upstreammd5 = hashlib.md5(fileb.read()).hexdigest()  ## md5 shouldn't need to be reread
                #     if upstreammd5 != upstreamframe.filestrack[fileheader].md5:
                #         raise (
                #             'Saga Error: upstream md5 and downloaded md5 file does not match')  # sanity check for now
                #     wf.filestrack[fileheader].md5 = upstreammd5  ### IS this really necessary?
                #     wf.filestrack[fileheader].connection.Rev = self.changes[fileheader]['revision']
            #
            # wf.writeoutFrameYaml()

    def iscontainerinsync(self):
        iscontainerinsync = True
        for fileheader, change in self.changes.items():
            if change.conflict or change.needresolve:
                iscontainerinsync= False

        return iscontainerinsync



