# import os
# from os.path import join, exists
# from Config import BASE
# from SagaCore.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaCore import *

# # from SagaCore.Change import Change
# from SagaCore.ContainerItem import ContainerItemType
# import warnings
# from SagaCore.Track import FileTrack
# import json
# import hashlib
from Graphics.QAbstract.ConflictListModel import SyncListModel
from SagaGuiModel.GuiModelConstants import mapdetailstxt, CONTAINERFN, NEWCONTAINERFN,SERVERNEWREVISION,\
    SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, \
    TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN,NOTINSYNCREASONSET, \
    LOCALCITEMNAMEADDED, LOCALCITEMNAMEREMOVED,MD5CHANGED,CONTAINERFN, TEMPCONTAINERFN
from SagaGuiModel.SagaAPICall import SagaAPICall
# from SagaGuiModel.SyncScenario import *



class SagaSync():
    def __init__(self, sagaguimodel):
        self.changes = {}
        self.sagaguimodel = sagaguimodel
        self.sagaapicall:SagaAPICall=sagaguimodel.sagaapicall
        self.newestframe:Frame  = None# this is the latest Server frame committed for this container.
        # self.workingframe:Frame =None
        self.upstreamframe:Frame =None
        self.localframe:Frame = None
        # self.appdata_saga = appdata_saga

    def reset(self):
        self.newestframe: Frame = None  # this is the latest Server frame committed for this container.
        # self.workingframe: Frame = None
        self.upstreamframe: Frame = None
        # self.localframe: Frame = None
        self.changes = {}

    def setUpstreamFrame(self, upstreamframe:Frame):
        self.upstreamframe = upstreamframe
    # def setWorkingFrame(self,workingframe:Frame):
    #     self.workingframe = workingframe
    def setNewestFrame(self, newestframe: Frame):
        self.newestframe = newestframe
    # def setLocalFrame(self, localframe: Frame):
    #     self.localframe = localframe

    def checkUpstream(self, container:Container):
        upstreamupdated = False
        workingFrame = container.workingFrame
        # refFrame = Frame.loadRefFramefromYaml(container.refframefullpath,
        #                                       workingFrame.containerworkingfolder)
        refFrame = container.refframe
        for citemid, citem in container.containeritems.items():
            if citem.containeritemtype == roleInput:
                upstreamcont = self.sagaguimodel.provideContainer(citem.refcontainerid)
                # containerworkingfolder, upstreamcont = self.sagaapicall.downloadContainerCall(join(self.appdata_saga, 'ContainerMapWorkDir', containerID),
                #                                                                                containerID, ismaincontainer=False)
                upstreamframe = upstreamcont.refframe
                # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.
                # if ref frame is upstreammd5  its fine, if workingframe is upstreammd5 its fine.
                # if upstream md5 not equal to
                if citem.trackname not in refFrame.filestrack.keys():
                    md5notsameasupstream = upstreamframe.filestrack[citem.trackname].md5\
                                           !=workingFrame.filestrack[citem.trackname].md5
                    ## This also means this is newly added
                    ## One explanation User just downloaded the input file and has altered it already.
                    ## Or Upstream container has already updated there
                else:
                    md5notsameasupstream = upstreamframe.filestrack[citem.trackname].md5 not in [ refFrame.filestrack[citem.trackname].md5,workingFrame.filestrack[citem.trackname].md5]
                # refnum = revNumber(refFrame.filestrack[citemid].connection.Rev)
                # upstreamrevnumberlarger = revNumber(upstreamframe.FrameName)>refnum
                if md5notsameasupstream:
                    if citemid in self.changes.keys():
                        self.changes[citemid] = {
                            'reason': [UPDATEDUPSTREAM] + self.changes[citemid]['reason'],
                            'revision': upstreamframe.FrameName,
                            'md5': upstreamframe.filestrack[citemid].md5,
                            'upstreamframe': upstreamframe,
                            'fromcontainer':upstreamcont}
                    else:
                        self.changes[citemid] = {'reason': [UPDATEDUPSTREAM],
                                                    'revision': upstreamframe.FrameName,
                                                    'md5': upstreamframe.filestrack[citem.trackname].md5,
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
            statustext = 'Newer Revision Exists!' + ' Current Rev: ' + str(maincontainer.revnum)
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
        for citemid, changedetails in self.changes.items():
            if citemid in maincontainer.containeritems.keys():
                # only set allowCommit to true if the changes involve what is in the Container's need to monitor
                changeisrelevant = True
        return changeisrelevant

    def checkContainerStatus(self, container:Container, vnewcont:Container):
        ## Crux Container Folder Status Checking.
        self.inconflict = False
        oneormore_trackchanged = False
        oneormore_upstreamupdated = False
        # self.localframe =
        # self.workingframe = container.workingFrame
        rf = container.refframe
        wf = container.workingFrame
        nf= None
        newerframeexists=False
        if container.revnum < vnewcont.revnum:
            nf = vnewcont.refframe
            newerframeexists = True

        statustext, notlatestrev = self.checkLatestRevision(container,vnewcont.revnum)

        changes = {}
        # wffileheaders =
        combinedheaders = set(rf.filestrack.keys())
        combinedheaders.update(set(container.VersionedCItemids()))
        if newerframeexists:
            combinedheaders.update(set(vnewcont.VersionedCItemids()))
        for citemid in combinedheaders:
            # if inlf:
            #     filetype = rf.filestrack[citemid].connection.containeritemrole.name
            # if inwf:
            #     filetype = wf.filestrack[citemid].connection.containeritemrole.name
            # if innf:
            #     filetype = nf.filestrack[citemid].connection.containeritemrole.name
            # if not wf.filestrack[citemid].connection.containeritemrole.name==\
            #     rf.filestrack[citemid].connection.containeritemrole.name==\
            #     nf.filestrack[citemid].connection.containeritemrole.name:
            #     raise(citemid + ' local frame, working frame and newest frame has different file types. Saga not prepared to deal with that yet')
            #Assumes users doesn't change filetype on you.
            ## ATTENTION PUT CHECKER IN TO make sure all 3 file types are the same
            c = Change(container,citemid, vnewcont, self.sagaguimodel)## inchange, it allocates track assigning
            if c.itemchanged:
                oneormore_trackchanged = True
            if c.upstreamupdated:
                oneormore_upstreamupdated = True

                # Check if Newest citemid added
            # refframefiletrackid = list(rf.filestrack.keys())
            # for citemid in wf.citemids.keys():
                ## how to manage if container and frame deviates on citemid counts

                # if citemid not in refframe.filestrack.keys() and citemid not in wf.filestrack.keys():
                #     # check if citemid is in neither refframe or current frame,
                #     raise ('somehow Container needs to track ' + citemid + 'but its not in ref frame or current frame')
            c.analysisState()
            if c.conflict:
                self.inconflict = True## If any change is in conflict
            changes[citemid] = c
        self.changes = changes
        return oneormore_upstreamupdated, statustext, notlatestrev, oneormore_trackchanged, self.changes


    def updateContainerWithUserSelection(self,combinedactionstate, container:Container):
        wf = container.workingFrame
        nf = self.newestframe
        # if combinedactionstate:
        #     wf.refreshedcheck = True
        #     for citemid, actionlist in combinedactionstate.items():
        #         copies = []
        #         for action in self.actionstate[citemid]:
        #             if action['main']:
        #                 mainaction = action
        #             else:
        #                 copies.append(action)
        #
        #         ### Main action sets to the working frame
        #         fn = self.sagaapicall.downloadFileCall(filetrack=nf.filestrack[citemid],
        #                                        containerworkingfolder=container.containerworkingfolder)
        #         wf.filestrack[citemid].md5 = nf.filestrack[citemid].md5
        #         wf.filestrack[citemid].lastEdited = nf.filestrack[citemid].lastEdited


                # if actions == 'Overwrite':
                #     fn = self.sagaapicall.downloadFileCall(filetrack=nf.filestrack[citemid],
                #                                    containerworkingfolder=container.containerworkingfolder)
                #     wf.filestrack[citemid].md5 = nf.filestrack[citemid].md5
                #     wf.filestrack[citemid].lastEdited = nf.filestrack[citemid].lastEdited
                #
                # elif filelist[citemid] == 'Download Copy':
                #     filename, ext = os.path.splitext(wf.filestrack[citemid].entity)
                #     filecopy_name = filename + '_' + nf.FrameName + 'Copy' + \
                #                     ext
                #     fn = self.sagaapicall.downloadFileCall(nf.filestrack[citemid],
                #                                    wf.containerworkingfolder, filecopy_name)
                #     print('No changes to Frame')
                # elif filelist[citemid] == 'Download':
                #     fn = self.sagaapicall.downloadFileCall(nf.filestrack[citemid],
                #                                    wf.containerworkingfolder)
                #     ft = nf.filestrack[citemid]
                #     if ft.connection.containeritemrole.name in [roleRequired, roleOutput]:
                #         wf.filestrack[citemid] = nf.filestrack[citemid]
                #     else:
                #         raise ('Under Construction')
                #     # sagaguimodel.maincontainer.addFileObject(fileinfo=newfileobj)
                # elif filelist[citemid] == 'Delete':
                #     filePath = os.path.join(
                #         wf.containerworkingfolder, wf.filestrack[citemid].ctnrootpath,
                #         wf.filestrack[citemid].entity)
                #     if os.path.exists(filePath):
                #         os.remove(filePath)
                #         container.removeContainerItem(citemid)
                #     else:
                #         print("The file does not exist")
                # elif filelist[citemid] == 'ReplaceInput':
                #     upstreamframe = self.changes[citemid]['upstreamframe']
                #     fileEditPath = self.sagaapicall.downloadFileCall(upstreamframe.filestrack[citemid],
                #                                              wf.containerworkingfolder)
                #     fileb = open(fileEditPath, 'rb')
                #     upstreammd5 = hashlib.md5(fileb.read()).hexdigest()  ## md5 shouldn't need to be reread
                #     if upstreammd5 != upstreamframe.filestrack[citemid].md5:
                #         raise (
                #             'Saga Error: upstream md5 and downloaded md5 file does not match')  # sanity check for now
                #     wf.filestrack[citemid].md5 = upstreammd5  ### IS this really necessary?
                #     wf.filestrack[citemid].connection.Rev = self.changes[citemid]['revision']
            #
            # wf.writeoutFrameYaml()

        # if mainaction['filetracktype']=='uffiletrack':

        # S1. Keep citemid
        ## S2. Remove File header
        ## S3 conflict, Keep Input, reject File removal
        ## S4 Ignore new input, reject File Adding
        ## S5 Local would mean use local Connection, Newest would mean use newest Connection, UpStream would mean use upstream
        ## S6 L would mean keep removal.  N would mean se newest connection.  Upstream would download latest Rev.
        ## S7 identical to S5.
        ## S8, L or U,
        ## S9, L or U
        ## S10, L or U

        #
        # try:
        #     filename = action['filetrack'].entity
        #     fn = os.path.join(self.maincontainer.containerworkingfolder, action['filetrack'].ctnrootpath,
        #                       filename)
        #     if os.path.exists(fn) and action['filerole'] != roleInput:
        #         filename, file_extension = os.path.splitext(action['filetrack'].entity)
        #         copiedfilename = filename + '_' + action['filetrack'].lastupdated + '+_' + file_extension
        #         copiedfn = os.path.join(self.maincontainer.containerworkingfolder,
        #                                 action['filetrack'].ctnrootpath,
        #                                 copiedfilename)
        #         os.rename(fn, copiedfn)
        # except Exception as e:
        #     print( change.citemid)
        #     print(e)
        #     print(action['filetrack'])

        # if mainaction['filetracktype']=='uffiletrack':

        # if importance == 'main':
        #     if action['filetracktype'] == 'uffiletrack':
        #         return 'Saga will download latest upstream version. ' \
        #                'Going forward, ' + filetrack.lastupdated + ' will be this container''s working copy.\n\n'
        #     elif action['filetracktype'] == 'nffiletrack':
        #         if change.reqoutscenariono == 3 or change.inputscenariono == 3:
        #             return 'Saga will remove this citemid from your workingframe to be in agreement with Newest Frame'
        #         else:
        #             return 'Saga will download the newest frames version and will be this container''s working copy\n\n'
        #     elif action['filetracktype'] == 'lffiletrack':
        #         if change.reqoutscenariono in [5, 4, 6, 7] or change.inputscenariono in [5, 4, 6, 7]:
        #             return 'This effectively will remove this file from this container as the latest commit DOES have this file.'
        #         else:
        #             return 'Saga will use the version committed in ' + self.currentrev + ' as the working copy. If youve made local changes, this may count as reverting.\n\n'
        #     elif action['filetracktype'] == 'wffiletrack':
        #         return 'Saga will continue to use your editted version as the working copy.  \n\n'
        # else:
        #     if action['filetracktype'] == 'uffiletrack':
        #         return 'Create copy' + filetrack.entity + '_' + filetrack.lastupdated + ' .\n\n'
        #     elif action['filetracktype'] == 'nffiletrack':
        #         return 'Create copy' + filetrack.entity + '_' + filetrack.lastupdated + ' .\n\n'
        #     elif action['filetracktype'] == 'lffiletrack':
        #         return 'Create ' + self.currentrev + ' copy named ' + filetrack.entity + '_' + filetrack.lastupdated + '.\n\n'
        #     elif action['filetracktype'] == 'wffiletrack':
        #         return 'Create your current working file as ' + filetrack.entity + '_' + self.currentrev + '_edited.\n\n'

    def iscontainerinsync(self):
        iscontainerinsync = True
        for citemid, change in self.changes.items():
            if change.conflict or change.needresolve:
                iscontainerinsync= False

        return iscontainerinsync


        # refframe = Frame.loadRefFramefromYaml(self.refframefullpath,self.containerworkingfolder)

    # def SyncInputFiletrack(self, upstreamupdated, wfft:FileTrack, ufft:FileTrack, upcont:Container, c:Change, nfft:FileTrack = None, newestexist=False):
    #     # UF Rev,WF Rev, NF Rev)
    #     # upstreamupdated = False
    #     wfuprevnum = numofRev(wfft.lastupdated)
    #
    #     latestframe = numofRev(upcont.refframe.FrameName)
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
    #                 print('rf!=wf!=nf Newest is updated to something else and youve updated also. So '
    #                       'conflict.  Need to resolve which version.')
    #             else:
    #                 print('rf!=wf!=nf but rf==nf  Newest hasnt changed from Lf, so you there is not really a conflict'
    #                       + 'User would simply create a new version of this file.')
    #
    #         # calculate md5 of file, if md5 has changed, update md5
    #
    #
    #     #         wf.filestrack[citemid].lastEdited = os.path.getmtime(filename)
    #     #         changes[citemid] = {'reason': [MD5CHANGED]}
    #     #         if wf.filestrack[citemid].connection.containeritemrole==roleInput:
    #     #             alterfiletracks.append(wf.filestrack[citemid])
    #     #         # if file has been updated, update last edited
    #     #         wf.filestrack[citemid].lastEdited = os.path.getmtime(filename)
    #     #         continue
    #     #     elif wf.filestrack[citemid].lastEdited != refframe.filestrack[citemid].lastEdited:
    #     #         changes[citemid] = {'reason': [DATECHANGED]}
    #     #         wf.filestrack[citemid].lastEdited = os.path.getmtime(filename)
    #     #         print('Date changed without Md5 changing')
    #     #         continue
    #     #
    #     # for removedheaders in refframefiletrackid:
    #     #     changes[removedheaders] = {'reason': [LOCALCITEMNAMEREMOVED]}
    #     # self.changes = gatherfileheaders(self.localframe, self.workingframe, self.newestframe)
    #     # self.changes, self.alterfiletracks = container.compareToRefFrame(self.changes)
    #     # upstreamupdated = self.checkUpstream(container)
    #     # statustext, notlatestrev = self.checkLatestRevision(container,newestrevnum)
    #     # containerchanged = self.checkContainerChanged(container)
    #     # changeisrelevant = self.checkChangeIsRelevant(container)
    #     #
    #     # return upstreamupdated, statustext, notlatestrev, containerchanged ,changeisrelevant, self.changes


