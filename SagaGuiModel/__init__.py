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
from SagaGuiModel.SagaSync import SagaSync


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
        self.sagaapicall:SagaAPICall = SagaAPICall(authtoken)
        self.sagasync:SagaSync = SagaSync(self.sagaapicall,desktopdir)

        self.maincontainer:Container = None
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
            self.downloadContainer(join(self.desktopdir,'ContainerMapWorkDir'), containerID)
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
                    'message':'User Not Allowed to Commit',
                    'conflictfiles': None}
        # Check if there are any conflicting files from refresh action with 'RevXCopy' in file name
        filepath = self.maincontainer.workingFrame.containerworkingfolder
        files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        searchstring = 'Rev' + str(self.newestrevnum) + 'Copy'### this might need to be refined.  Its any rev higher than current rev.
        conflictfiles = [f for f in files if searchstring in f]
        if len(conflictfiles) > 0:
            return {'commitstatus': 'ConflictedFiles',
                    'message': 'User Not Allowed to Commit',
                    'conflictfiles':conflictfiles}
        return {'commitstatus': 'GreenLight',
                'message': 'User Allowed To Commit',
                'conflictfiles': []}

    def isNewContainer(self):
        if self.maincontainer:
            return self.maincontainer.yamlfn == NEWCONTAINERFN
        else:
            raise('self.maincontainer not initatiated yet, this function should not be called')

    def loadContainer(self, containerpath):

        self.maincontainer = Container.LoadContainerFromYaml(containerpath, revnum=None, ismaincontainer=True)
        self.histModel = HistoryListModel(self.maincontainer .commithistory())
        self.histModel.individualfilehistory(self.maincontainer.commithistorybyfile())

        self.containerfilemodel = ContainerFileModel(self.maincontainer, self.sagasync)
        return self.maincontainer, self.histModel, self.containerfilemodel

    def initiateNewContainer(self, containerworkingfolder, containername):
        os.mkdir(containerworkingfolder)
        os.mkdir(os.path.join(containerworkingfolder, 'Main'))
        self.maincontainer = Container.InitiateContainer(containerworkingfolder, containername)
        self.maincontainer.workingFrame = Frame.InitiateFrame(parentcontainerid=self.maincontainer.containerId,
                                                              parentcontainername=containername,
                                                              localdir=containerworkingfolder)
        self.containerfilemodel = ContainerFileModel(self.maincontainer, self.sagasync)
        self.histModel=HistoryListModel({})
        return self.containerfilemodel
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
    def downloadContainer(self,newcontparentdirpath,  dlcontainerid, use = 'NetworkContainer' ):
        containerworkingfolder, cont = self.sagaapicall.downloadContainerCall(newcontparentdirpath,  dlcontainerid, use )
        return containerworkingfolder, cont

    def downloadbranch(self,containerworkingfolder = None, cont:Container = None, branch='Main'):
        self.sagaapicall.downloadbranch(self.maincontainer.containerworkingfolder, self.maincontainer, branch )

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
        response = self.sagaapicall.commitToServer(containerdictjson, framedictjson, updateinfojson,
                                                   filesToUpload,commitmessage,
                                                   self.maincontainer.containerId,
                                                   self.maincontainer.currentbranch)

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
    #
    #
    # def checkState

    # def syncModels(self):
    #     syncmodels
    #     return
    def getRefreshPopUpModels(self):
        return self.sagasync.syncStatusModels()

    def dealWithUserSelection(self,filelist):
        self.sagasync.updateContainerWithUserSelection(filelist, self.maincontainer)

    def getStatus(self):
        # maincontainer = self.maincontainer
        allowcommit = False
        needtorefresh = False
        if self.maincontainer is None:
            return '', False, False, {}

        self.newestframe, self.newestrevnum = self.sagaapicall.callLatestRevision(self.maincontainer)
        notlatestrev = False
        if self.maincontainer.revnum < self.newestrevnum:
            self.sagasync.setNewestFrame(self.newestframe)
        upstreamupdated, statustext, notlatestrev, containerchanged, changeisrelevant, changes =self.sagasync.checkContainerStatus(self.maincontainer, self.newestrevnum)

        if changeisrelevant or containerchanged:
            allowcommit=True  ## could be one line but I think this is easier to read

        if upstreamupdated or notlatestrev:
            needtorefresh=True ## could be one line but I think this is easier to read

        return statustext, allowcommit, needtorefresh ,  changes




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