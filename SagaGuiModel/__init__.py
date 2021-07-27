import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from Config import sourcecodedirfromconfig,BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,SERVERNEWREVISION,SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN
import yaml
import json

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
from subprocess import Popen
import sys


from Graphics.QAbstract.ContainerFileModel import ContainerFileModel



from Graphics.QAbstract.ConflictListModel import ConflictListModel, AddedListModel, DeletedListModel, UpstreamListModel
import re


class SagaGuiModel():
    def __init__(self, desktopdir, sourcecodedir,
                 versionnumber,tokenfile,authtoken=None, userdata=None , containerwrkdir=None,):

        self.userdata= userdata
        self.containerwrkdir=containerwrkdir
        self.desktopdir = desktopdir
        self.sourcecodedir = sourcecodedirfromconfig
        self.versionnumber = versionnumber
        self.guiworkingdir = os.getcwd()
        self.sagaapicall:SagaAPICall = SagaAPICall(authtoken)
        self.sagasync:SagaSync = SagaSync(self.sagaapicall,desktopdir)
        self.mainguihandle = None

        self.maincontainer:Container = None
        self.userdata = None
        self.tokenfile = tokenfile
        self.histModel = HistoryListModel({})  ### Attention, this should probalby be init at init
        self.containerfilemodel = ContainerFileModel(None, self.sagasync, self)### Attention, ### Attention, this should probalby be init at init

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
        userdetailsresult, self.userdata = self.sagaapicall.authUserDetails(self.tokenfile)
        if self.userdata:
            sectioniddir = join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])
            if not os.path.exists(sectioniddir):
                os.mkdir(sectioniddir)
        return userdetailsresult

    def signOut(self):
        self.maincontainer: Container = None
        self.userdata = None
        self.modelreset()



    def newUserSignUp(self, formentry):
        signupresponse = self.sagaapicall.newUserSignUpCall(formentry)

        if signupresponse['status'] == 'success':###ATTENTION, MAIN MODEL SHOULD SET THE APICALL AUTHTOKEN
            self.sagaapicall.authtoken = signupresponse['auth_token']
            with open(sagaguimodel.tokenfile, 'w') as tokenfile:
                json.dump(signupresponse, tokenfile)
            return True
        return False


    def getWorldContainers(self):
        self.containerinfodict = self.sagaapicall.getContainerInfoDict()### Get list of containers by authtoken.
        if 'EMPTY' in self.containerinfodict.keys():
            return {}
        for containerID in self.containerinfodict.keys():
            print(containerID, self.containerinfodict[containerID]['ContainerDescription'])
            self.containeridtoname[containerID] = self.containerinfodict[containerID]['ContainerDescription']
            self.downloadContainer(join(self.desktopdir,'ContainerMapWorkDir',containerID), containerID)
        if not os.path.exists(join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(join(self.desktopdir, 'SagaGuiData',self.userdata['current_sectionid']))
        return self.containerinfodict

    # def downloadfullframefiles(self, container:Container =None, framerev = 'latest'):
    #     if container is None:
    #         raise('Developers need to add a self.maincontainer for this model')
    #     wf = container.workingFrame
    #     for fileheader, filetrack in wf.filestrack.items():
    #         # print(filetrack.file_name,self.containerworkingfolder)
    #         self.downloadFile(filetrack, container.containerworkingfolder)

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
            warnings.warn ('self.maincontainer not initatiated yet')
            return False


    def loadContainer(self, containerpath):
        # raise('WRITE THIS GODDAMN Error')
        self.maincontainer = Container.LoadContainerFromYaml(containerpath, revnum=None, ismaincontainer=True)
        # self.histModel = HistoryListModel(self.maincontainer .commithistory())### Attention, this should probalby be init at init
        self.histModel.load(self.maincontainer.commithistory())
        self.histModel.individualfilehistory(self.maincontainer.commithistorybyfile())
        self.containerfilemodel.update(self.maincontainer)### Attention,
        return self.maincontainer, self.histModel, self.containerfilemodel

    def initiateNewContainer(self, containerworkingfolder, containername):
        ensureFolderExist(os.path.join(containerworkingfolder, 'Main', 'anything'))#### ATTENTION Need to fix ensureFolderExists
        self.maincontainer = Container.InitiateContainer(containerworkingfolder, containername)
        self.containerfilemodel.update(self.maincontainer)#
        self.histModel.load(self.maincontainer.commithistory())
        return self.containerfilemodel, self.histModel


    def getAvailableSections(self):
        sectiondict = self.sagaapicall.getAvailableSectionsCall()
        return sectiondict

    def shouldModelSwitch(self,containerpath):
        loadingcontainer = Container.LoadContainerFromYaml(containerpath, revnum=None)
        if loadingcontainer.yamlfn == NEWCONTAINERFN:
            return False, self.userdata['current_sectionid'],'This is a new container'
        goswitch, newsectionid, message = self.sagaapicall.shouldModelSwitchCall(loadingcontainer.containerId)
        return goswitch, newsectionid, message

    def sectionSwitch(self, newsectionid=None):
        if newsectionid is None:
            if self.userdata['current_sectionid'] is None:
                return None, None
            else:
                newsectionid = self.userdata['current_sectionid']
        report, usersection = self.sagaapicall.sectionSwitchCall(newsectionid)
        if report['status'] == 'User Current Section successfully changed':
            self.modelreset()
            self.mainguihandle.loadSection()
        else:
            print('Error Occured.  Your current section has not change')
        return report , usersection

    def modelreset(self):
        self.maincontainer = None
        self.containeridtoname= {}
        ## Sagatree, Network and Gantt models???
        self.histModel.reset()
        self.containerfilemodel.reset()

    def downloadFile(self, filetrack:FileTrack, containerworkingfolder, newfilename=None ):
        fn=self.sagaapicall.downloadFileCall(filetrack, containerworkingfolder, newfilename )
        return fn
    def downloadContainer(self,containerworkingfolder,  dlcontainerid, use = 'NetworkContainer' ):
        containerworkingfolder, cont = self.sagaapicall.downloadContainerCall(containerworkingfolder,  dlcontainerid, use )
        if use=='WorkingContainer':
            for fileheader, filetrack in cont.workingFrame.filestrack.items():
                self.downloadFile(filetrack, containerworkingfolder)
        return containerworkingfolder, cont

    def downloadbranch(self, branch='Main'):
        self.sagaapicall.downloadbranch(self.maincontainer.containerworkingfolder, self.maincontainer, branch )
        self.maincontainer.updatememorydict()

    def addUserToContainer(self,emailtoadd):
        permissionsresponse = self.sagaapicall.addUserToContainerCall(self.userdata,emailtoadd,self.userdata['current_sectionid'],self.maincontainer.containerId)
        print(permissionsresponse['ServerMessage'])
        if permissionsresponse['result']:
            self.maincontainer.setAllowedUser(permissionsresponse['allowedUser'])
        return permissionsresponse, self.maincontainer.allowedUser

    def commitNewContainer(self, commitmessage):
        payload, filesToUpload = self.maincontainer.prepareNewCommitCall( commitmessage)
        returncontdict,returnframedict,servermessage = self.sagaapicall.commitNewContainerToServer(payload,filesToUpload)
        if 'Container Made' == servermessage:
            self.maincontainer.allowedUser= returncontdict['allowedUser']
            self.maincontainer.workingFrame = Frame.LoadFrameFromDict(returnframedict,self.maincontainer.containerworkingfolder)
            ### Maybe put a compare function here to compare the workingFrame before the commit and the Frame that was sent back.
            ## they should be identical.
            self.maincontainer.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)# writes out TEMPFRAME
            yamlframefnfullpath = self.maincontainer.workingFrame.writeoutFrameYaml(returnframedict['FrameName'] + '.yaml')# writes out REVX.yaml
            self.maincontainer.setContainerForNextframe(yamlframefnfullpath)
            self.maincontainer.yamlfn = TEMPCONTAINERFN
            self.maincontainer.save()
            # self.maincontainer.memoryframesdict[returnframedict['FrameName'] + '.yaml'] = Frame.LoadFrameFromYaml(yamlframefnfullpath, self.maincontainer.containerworkingfolder)
            try:
                os.remove(join(self.maincontainer.containerworkingfolder, NEWCONTAINERFN))
                os.remove(join(self.maincontainer.containerworkingfolder, 'Main',NEWFRAMEFN))
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
            self.maincontainer.setContainerForNextframe(yamlframefnfullpath)
            # self.maincontainer.save(fn=CONTAINERFN, commitprocess=True)
            self.histModel.load(self.maincontainer.commithistory())
            self.containerfilemodel.update()
            return True, self.maincontainer.workingFrame.FrameName, 'Commit Success!'
        else:
            print('Commit Fail')
            resp = json.loads(response.content)
            print(resp)
            return  False,self.maincontainer.workingFrame.FrameName, 'Commit Failed!'
############SyncStatusStuff

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
        if self.isNewContainer():
            if len(self.maincontainer.FileHeaders.keys())>0:
                allowcommit = True
            return 'New Container', allowcommit, False, {}
        self.newestframe, self.newestrevnum = self.sagaapicall.callLatestRevision(self.maincontainer)
        filesupdated, wffilesupdated = self.maincontainer.updateworkframe()
        notlatestrev = False
        if self.maincontainer.revnum < self.newestrevnum:
            self.sagasync.setNewestFrame(self.newestframe)
        upstreamupdated, statustext, notlatestrev, containerchanged, changeisrelevant, changes =self.sagasync.checkContainerStatus(self.maincontainer, self.newestrevnum)

        if changeisrelevant or containerchanged:
            allowcommit=True  ## could be one line but I think this is easier to read

        if upstreamupdated or notlatestrev:
            needtorefresh=True ## could be one line but I think this is easier to read

        return statustext, allowcommit, needtorefresh ,  changes

    def getNewVersionInstaller(self, app):
        # response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
        #                         headers={"Authorization": 'Bearer ' + self.authtoken})
        installPath = os.path.join(self.desktopdir, 'Saga.exe')
        # open(installPath, 'wb').write(response.content)
        self.sagaapicall.getNewVersionCall(installPath)
        Popen(installPath, shell=True)
        sys.exit(app.exec_())




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