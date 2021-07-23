import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from Config import BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,SERVERNEWREVISION,SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN
import yaml
import json
import requests
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
from SagaApp.FileObjects import FileTrack
from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from os import listdir
from os.path import isfile, join
from SagaGuiModel.SagaAPICall import SagaAPICall

from Graphics.QAbstract.ContainerFileModel import ContainerFileModel



from Graphics.QAbstract.ConflictListModel import ConflictListModel, AddedListModel, DeletedListModel, UpstreamListModel
import re


class SagaGuiModel():
    def __init__(self, desktopdir, sourcecodedir,
                 versionnumber,tokenfile,authtoken=None, userdata=None , containerwrkdir=None,):

        self.userdata= userdata
        self.containerwrkdir=containerwrkdir
        self.desktopdir = desktopdir
        self.sourcecodedir = sourcecodedir
        self.versionnumber = versionnumber
        self.guiworkingdir = os.getcwd()
        self.sagaapicall = SagaAPICall(authtoken)
        self.containernetworkkeys=[]
        self.changes = {}
        self.maincontainer = None
        self.userdata = None
        self.tokenfile = tokenfile

        guidirs= [ 'SagaGuiData','ContainerMapWorkDir']
        if not os.path.exists(self.desktopdir):
            os.mkdir(self.desktopdir)
        for guidir in guidirs:
            guidatadir = os.path.join(self.desktopdir,guidir)
            if not os.path.exists(guidatadir):
                os.mkdir(guidatadir)
            makefilehidden(guidatadir)

    @classmethod
    def loadModelFromConfig(cls):
        try:
            appdatadir = os.getenv('appdata')
            desktopdir = join(appdatadir, 'SagaDesktop')
        except Exception as e:
            warnings.warn('cannot find environmental variable appdata')
            desktopdir = ''

        try:
            with open('settings.yaml', 'r') as file:
                settingsyaml = yaml.load(file, Loader=yaml.FullLoader)
            sourcecodedir = settingsyaml['sourcecodedir']
            versionnumber= settingsyaml['versionnumber']
            tokenlocation = settingsyaml['tokenlocation']
            tokenfilename = settingsyaml['tokenfilename']
            if tokenlocation=='appdata':
                tokenfile = join(desktopdir,tokenfilename)
        except Exception as e:
            raise('unable to load settings.yaml.  Please ensure it is in program folder.')
        sagaguimodel = cls(sourcecodedir=sourcecodedir, desktopdir=desktopdir, versionnumber=versionnumber, tokenfile=tokenfile)
        return sagaguimodel

    def checkUserStatus(self):
        signinresult, self.userdata = self.sagaapicall.authUserDetails(self.tokenfile)
        if self.userdata:
            sectioniddir = join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])
            if not os.path.exists(sectioniddir):
                os.mkdir(sectioniddir)
        return signinresult


    def getWorldContainers(self):
        self.containerinfodict = self.sagaapicall.getContainerInfoDict()
        if 'EMPTY' in self.containerinfodict.keys():
            return []
        for containerID in self.containerinfodict.keys():
            newcontparentdirpath = join(self.desktopdir,'ContainerMapWorkDir')
            self.sagaapicall.downloadContainer(newcontparentdirpath, containerID)
        if not os.path.exists(join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(join(self.desktopdir, 'SagaGuiData',self.userdata['current_sectionid']))
        return self.containerinfodict

    def downloadfullframefiles(self, container:Container =None, framerev = 'latest'):
        if container is None:
            raise('Developers need to add a self.maincontainer for this model')
        wf = container.workingFrame
        for fileheader, filetrack in wf.filestrack.items():
            # print(filetrack.file_name,self.containerworkingfolder)
            self.downloadFile(filetrack, container.containerworkingfolder)

    def revertTo(self, reverttorev, fileheadertorevertto ):
        containerworkingfolder = self.maincontainer.containerworkingfolder
        framefn = os.path.join(containerworkingfolder, 'Main', reverttorev+'.yaml')
        ## Assumes Frame Exists
        revertframe = Frame.loadRefFramefromYaml(refframefullpath=framefn, containerworkingfolder = containerworkingfolder)
        if fileheadertorevertto is None:
            for fileheader, filetrack in revertframe.filestrack.items():
                self.downloadFile(filetrack, containerworkingfolder)
        else:
            if fileheadertorevertto in revertframe.filestrack.keys():
                self.downloadFile(revertframe.filestrack[fileheadertorevertto], containerworkingfolder)
            else:
                warnings.warn('This frame does not have this fileheader ' + fileheadertorevertto)

    def checkAllowedtoCommit(self):
        if self.userdata['email'] not in self.maincontainer.allowedUser:
            return {'commitstatus':'UserDenied',
                    'message':'User Not Allowed to Commit'}
        # Check if there are any conflicting files from refresh action with 'RevXCopy' in file name
        filepath = self.maincontainer.workingFrame.containerworkingfolder
        files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        searchstring = 'Rev' + str(self.newestrevnum) + 'Copy'### this might need to be refined.  Its any rev higher than current rev.
        conflictfiles = [f for f in files if searchstring in f]
        if len(conflictfiles) > 0:
            return {'commitstatus': 'ConflictedFiles',
                    'message': 'User Not Allowed to Commit',
                    'conflictfiles':conflictfiles}

    def isNewContainer(self):
        if self.maincontainer:
            return self.maincontainer.yamlfn == NEWCONTAINERFN
        else:
            raise('self.maincontainer not initatiated yet, this function should not be called')

    def loadContainer(self, containerpath):

        self.maincontainer = Container.LoadContainerFromYaml(containerpath, revnum=None)
        self.histModel = HistoryListModel(self.maincontainer .commithistory())
        self.histModel.individualfilehistory(self.maincontainer.commithistorybyfile())

        self.containerfilemodel = ContainerFileModel(self.maincontainer, self)
        return self.maincontainer, self.histModel, self.containerfilemodel

    def initiateNewContainer(self, containerworkingfolder, containername):
        os.mkdir(containerworkingfolder)
        os.mkdir(os.path.join(containerworkingfolder, 'Main'))
        self.maincontainer = Container.InitiateContainer(containerworkingfolder, containername)
        self.maincontainer.workingFrame = Frame.InitiateFrame(parentcontainerid=self.maincontainer.containerId,
                                                              parentcontainername=containername,
                                                              localdir=containerworkingfolder)
        self.histModel=HistoryListModel({})
###Calls

    def shouldModelSwitch(self,containerpath):
        goswitch, newsectionid, message = self.sagaapicall.shouldModelSwitch(containerpath)
        return goswitch, newsectionid, message

    def sectionSwitch(self, newsectionid):
        status = self.sagaapicall.sectionSwitch(newsectionid)
        return status
    def downloadFile(self, filetrack:FileTrack, filepath, newfilename=None ):
        fn=self.sagaapicall.downloadFile(filetrack, filepath, newfilename )
        return fn
    def downloadContainer(self,newcontparentdirpath,  dlcontainerid ):
        containerworkingfolder, cont = self.sagaapicall.downloadContainer(newcontparentdirpath,  dlcontainerid )
        return containerworkingfolder, cont

    def downloadbranch(self,containerworkingfolder = None, cont:Container = None, branch='Main'):
        self.sagaapicall.downloadbranch(containerworkingfolder, cont, branch )

    def commitNewContainer(self, commitmessage):
        payload, filesToUpload = self.maincontainer.prepareNewCommitCall( commitmessage)
        returncontdict,returnframedict,servermessage = self.sagaapicall.commitNewContainerToServer(payload,filesToUpload)
        if 'Container Made' == servermessage:
            self.maincontainer.allowedUser= returncontdict['allowedUser']
            self.maincontainer.workingFrame = Frame.LoadFrameFromDict(returnframedict,self.maincontainer.containerworkingfolder)
            ### Maybe put a compare function here to compare the workingFrame before the commit and the Frame that was sent back.
            ## they should be identical.
            self.maincontainer.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)# writes out TEMPFRAME
            self.maincontainer.workingFrame.writeoutFrameYaml(returnframedict['FrameName'] + '.yaml')# writes out REVX.yaml
            self.maincontainer.save(fn=CONTAINERFN)
            self.maincontainer.yamlfn = TEMPCONTAINERFN
            self.maincontainer.save()
            try:
                os.remove(self.maincontainer.containerworkingfolder, NEWCONTAINERFN)
                os.remove(self.maincontainer.containerworkingfolder, 'Main',NEWFRAMEFN)
            except:
                print('Can''t remove pre First Commit files.')
            return True
        else:
            self.maincontainer.workingFrame.FrameName = 'Rev0'
            return False

    def commitNewRevision(self, commitmessage):
        containerdictjson, framedictjson, updateinfojson, filesToUpload = self.maincontainer.prepareCommitCall()
        response = self.sagaapicall.commitToServer(containerdictjson, framedictjson, updateinfojson, filesToUpload,commitmessage, self.containerId, self.currentbranch)

        if 'commitsuccess' in response.headers.keys():
            # Updating new frame information
            yamlframefn = response.headers['file_name']
            yamlframefnfullpath = join(self.maincontainer.containerworkingfolder, 'Main', yamlframefn)
            open(yamlframefnfullpath, 'wb').write(response.content)
            makefilehidden(yamlframefn)
            self.maincontainer.setContainerForNewframe(yamlframefn)
            self.maincontainer.save()
            self.histModel.rePopulate(self.maincontainer.commithistory())
            return True, self.maincontainer.workingFrame.FrameName, 'Commit Success!'
        else:
            print('Commit Fail')
            resp = json.loads(response.content)
            print(resp)
            return  False,self.maincontainer.workingFrame.FrameName, 'Commit Failed!'



############SyncStatusStuff
    def checkUpstream(self):
        upstreamupdated = False
        workingFrame = self.maincontainer.workingFrame
        refFrame = Frame.loadRefFramefromYaml(self.maincontainer.refframefullpath,
                                              self.maincontainer.workingFrame.containerworkingfolder)
        for fileheader in self.maincontainer.filestomonitor().keys():
            if workingFrame.filestrack[fileheader].connection.connectionType.name == typeInput:
                if workingFrame.filestrack[
                    fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                    # Check to see if input file is internal to container, not referencing other containers
                    containerID = workingFrame.filestrack[fileheader].connection.refContainerId

                    upstreamcont = Container.LoadContainerFromYaml(containerfnfullpath=
                                                                   join(self.desktopdir, 'ContainerMapWorkDir', containerID, CONTAINERFN))
                    if upstreamcont is None:
                        containerworkingfolder, upstreamcont = self.downloadContainer(join(self.desktopdir, 'ContainerMapWorkDir'),
                                                                                                   containerID)
                    inputFrame = upstreamcont.getRefFrame()
                    # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                    # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.
                    # if ref frame is upstreammd5  its fine, if workingframe is upstreammd5 its fine.
                    # if upstream md5 not equal to

                    md5notsameasupstream = inputFrame.filestrack[fileheader].md5 not in [ refFrame.filestrack[fileheader].md5,workingFrame.filestrack[fileheader].md5]
                    # refnum = revNumber(refFrame.filestrack[fileheader].connection.Rev)
                    # upstreamrevnumberlarger = revNumber(inputFrame.FrameName)>refnum
                    if md5notsameasupstream:
                        if fileheader in self.changes.keys():
                            self.changes[fileheader] = {
                                'reason': [UPDATEDUPSTREAM] + self.changes[fileheader]['reason'],
                                'revision': inputFrame.FrameName,
                                'md5': inputFrame.filestrack[fileheader].md5,
                                'inputframe': inputFrame,
                                'fromcontainer':upstreamcont}
                        else:
                            self.changes[fileheader] = {'reason': [UPDATEDUPSTREAM],
                                                        'revision': inputFrame.FrameName,
                                                        'md5': inputFrame.filestrack[fileheader].md5,
                                                        'inputframe': inputFrame,
                                                        'fromcontainer':upstreamcont}
                        upstreamupdated=True
        return  upstreamupdated

    def getStatus(self):
        maincontainer = self.maincontainer
        allowcommit = False
        needtorefresh = False
        self.changes={}
        ###################ORDER IS IMPORTANT HERE..I think####
        self.changes, self.alterfiletracks = maincontainer.compareToRefFrame(self.changes)
        upstreamupdated = self.checkUpstream()
        statustext, notlatestrev = self.checkLatestRevision()
        changeisrelevant = self.checkChangeIsRelevant(maincontainer)
        containerchanged = self.checkContainerChanged(maincontainer)
        isnewcontainer = maincontainer.yamlfn == NEWCONTAINERFN
        if changeisrelevant or containerchanged:
            allowcommit=True  ## could be one line but I think this is easier to read

        if upstreamupdated or notlatestrev:
            needtorefresh=True ## could be one line but I think this is easier to read
        chgstr = ''
        for fileheader, change in self.changes.items():
            chgstr = chgstr + fileheader + '\t' + ', '.join(change['reason']) + '\n'

        return statustext,isnewcontainer, allowcommit, needtorefresh , chgstr, self.changes

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

    def checkLatestRevision(self):
        ## This is the only place that knows of a later revision.
        notlatestrev = False
        mainContainer = self.maincontainer
        self.newestframe,self.newestrevnum = self.sagaapicall.callLatestRevision(self.maincontainer)

        self.newestFiles = {}

        if mainContainer.revnum < self.newestrevnum:
            notlatestrev = True
            # self.refreshContainerBttn.setEnabled(True)
            if mainContainer.workingFrame.refreshedcheck:
                statustext='Newer Revision Exists!' + ' Current Rev: ' + mainContainer.workingFrame.refreshrevnum\
                           + ', Latest Rev: ' + str(self.newestrevnum)
            else:
                statustext = 'Newer Revision Exists!' + ' Current Rev: ' + str(mainContainer.revnum)\
                             + ', Latest Rev: ' + str(self.newestrevnum)
            # if the newest rev num is different from local rev num:
            # loop through filesttrack of both newest frame, check if file exists in current frame and compare MD5s,
            # if exists, add update message to changes, if notadd new file message
            refframe = mainContainer.getRefFrame()
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
        return statustext, notlatestrev



    # def addressAlteredInput(self):
    #     for alterfiletrack in self.alterfiletracks:
    #         dialogWindow = alteredinputFileDialog(alterfiletrack)
    #         alterinputfileinfo = dialogWindow.getInputs()
    #         if alterinputfileinfo:
    #             self.mainContainer.workingFrame.dealwithalteredInput(alterinputfileinfo,
    #                                                                  self.mainContainer.refframefullpath)
    #     self.readcontainer(os.path.join(self.mainContainer.containerworkingfolder, TEMPCONTAINERFN))
    #     self.checkdelta()


# def revNumber(fn):
#     m = re.search('Rev(\d+).yaml', fn)
#     try:
#         return int(m.group(1))
#     except:
#         return 1

sagaguimodel = SagaGuiModel.loadModelFromConfig()