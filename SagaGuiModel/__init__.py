import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from Config import sourcecodedirfromconfig,BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,SERVERNEWREVISION,SERVERFILEADDED, SERVERFILEDELETED,UPDATEDUPSTREAM, TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN
import yaml
import json
import shutil

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
from datetime import datetime


from Graphics.QAbstract.ContainerFileModel import ContainerFileModel



# from Graphics.QAbstract.ConflictListModel import ConflictListModel2, NoticeListModel
#     # AddedListModel, DeletedListModel, UpstreamListModel
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
        self.sagasync:SagaSync = SagaSync(self,desktopdir)
        self.mainguihandle = None
        self.networkcontainers={}

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
            with open(join(sourcecodedirfromconfig, 'settings.yaml'), 'r') as file:
                settingsyaml = yaml.load(file, Loader=yaml.FullLoader)
            sourcecodedir = sourcecodedirfromconfig
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

    def signIn(self, email, password):
        signinstatus = self.sagaapicall.signInCall(email, password)

        if signinstatus['status'] == 'success':
            with open(self.tokenfile, 'w') as tokenfilefh:
                json.dump(signinstatus['usertokeninfo'], tokenfilefh)    #ATTENTION, MAY NOT NEED THIS ANYMORE POtentail security issue?
        return {'status': signinstatus['status']}

    def signOut(self):
        self.maincontainer: Container = None
        self.userdata = None
        self.container_reset()



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
        self.networkcontainers={}
        self.containeridtoname={}
        for containerID in self.containerinfodict.keys():
            print(containerID, self.containerinfodict[containerID]['ContainerDescription'])
            self.containeridtoname[containerID] = self.containerinfodict[containerID]['ContainerDescription']
            self.provideContainer(containerID)
        self.updatecontainerbylastframecheck()
        if not os.path.exists(join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(join(self.desktopdir, 'SagaGuiData',self.userdata['current_sectionid']))
        return self.containerinfodict

    def provideContainer(self, containerid):
        if containerid not in self.networkcontainers.keys():
            containyaml = os.path.join(self.desktopdir, 'ContainerMapWorkDir',containerid, CONTAINERFN)
            if os.path.exists(containyaml):
                self.networkcontainers[containerid] = Container.LoadContainerFromYaml(containyaml)
            else:
                containerworkingfolder = os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerid)
                containerworkingfolder, self.networkcontainers[containerid]  = sagaguimodel.downloadContainer(containerworkingfolder,
                                                                                                containerid)
        return self.networkcontainers[containerid]
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


    def loadContainer(self, containerpath, ismaincontainer=False):
        # raise('WRITE THIS GODDAMN Error')
        goswitch, newsectionid = self.shouldModelSwitch(containerpath)
        if goswitch:
            report, usersection = self.sectionSwitch(newsectionid)
        self.container_reset()
        print('start of loadcontainer' + datetime.now().isoformat())
        self.maincontainer = Container.LoadContainerFromYaml(containerpath, revnum=None, ismaincontainer=ismaincontainer)
        self.histModel.load(self.maincontainer.commithistory())
        self.histModel.individualfilehistory(self.maincontainer.commithistorybyfile())
        self.containerfilemodel.update(self.maincontainer)### Attention,
        # print('hist and container model end' + datetime.now().isoformat())
        return self.maincontainer

    def initiateNewContainer(self, containerworkingfolder, containername):
        ensureFolderExist(os.path.join(containerworkingfolder, 'Main', 'anything'))#### ATTENTION Need to fix ensureFolderExists
        self.maincontainer = Container.InitiateContainer(containerworkingfolder, containername)
        self.containerfilemodel.update(self.maincontainer)#
        self.histModel.load(self.maincontainer.commithistory())
        # return self.containerfilemodel, self.histModel


    def getAvailableSections(self):
        sectiondict = self.sagaapicall.getAvailableSectionsCall()
        return sectiondict

    def shouldModelSwitch(self,containerpath):
        loadingcontainer = Container.LoadContainerFromYaml(containerpath, revnum=None, lightload=True)
        # print('damn loading' + datetime.now().isoformat())
        if loadingcontainer is None:
            raise('Could not load container with file ' + containerpath)###Attention feed to gui error box.
        if loadingcontainer.yamlfn == NEWCONTAINERFN:
            return False, self.userdata['current_sectionid'],'This is a new container'
        goswitch, newsectionid = self.sagaapicall.shouldModelSwitchCall(loadingcontainer.containerId)
        return goswitch, newsectionid

    def sectionSwitch(self, newsectionid=None):
        # print('sectionstart' + datetime.now().isoformat())
        if newsectionid is None:
            if self.userdata['current_sectionid'] is None:
                return None, None
            else:
                newsectionid = self.userdata['current_sectionid']
        report, usersection = self.sagaapicall.sectionSwitchCall(newsectionid)
        if report['status'] == 'User Current Section successfully changed':
            self.container_reset()
            self.mainguihandle.loadSection()
        else:
            print('Error Occured.  Your current section has not change')
        return report , usersection

    def container_reset(self):
        self.maincontainer = None
        # self.containeridtoname= {}
        ## Sagatree, Network and Gantt models???
        self.histModel.reset()
        self.containerfilemodel.reset()
        self.sagasync.reset()
        # self.networkcontainers={}

    def downloadFile(self, filetrack:FileTrack, containerworkingfolder, newfilename=None ):
        fn=self.sagaapicall.downloadFileCall(filetrack, containerworkingfolder, newfilename )
        return fn

    def downloadContainer(self,containerworkingfolder,  dlcontainerid, ismaincontainer=False ):
        containerworkingfolder, cont = self.sagaapicall.downloadContainerCall(containerworkingfolder,  dlcontainerid, ismaincontainer )
        if ismaincontainer:
            for fileheader, filetrack in cont.workingFrame.filestrack.items():
                self.downloadFile(filetrack, containerworkingfolder)
        return containerworkingfolder, cont

    def downloadbranch(self, branch='Main'):
        self.sagaapicall.downloadbranch(self.maincontainer.containerworkingfolder, self.maincontainer, branch )
        self.maincontainer.updatememorydict()
        self.maincontainer.updateRevNum()

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
            # self.maincontainer.memoryframesdict[returnframedict['FrameName'] + '.yaml'] = Frame.loadRefFramefromYaml(yamlframefnfullpath, self.maincontainer.containerworkingfolder)
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
        return self.sagasync.syncStatusModels2(self.maincontainer, self.containeridtoname)

    def dealWithUserSelection(self,combinedactionstate):
        # self.sagasync.updateContainerWithUserSelection(combinedactionstate, self.maincontainer)
        wf = self.maincontainer.workingFrame
        alldownloaded = True
            # wf.refreshedcheck = True

        def makesurenotoverwrite(ft:FileTrack, containerworkingfolder, append):

            filefullpath = join(containerworkingfolder, ft.ctnrootpath,ft.file_name)
            filename, file_extension = os.path.splitext(ft.file_name)
            # edited = '_wk'
            newfilename = filefullpath
            while os.path.exists(newfilename):
                newfile_name = filename + append + file_extension
                newfilename = join(containerworkingfolder, ft.ctnrootpath,newfile_name)
                append = append + '+'
            shutil.copyfile(filefullpath, newfilename)
            return newfilename

        for fileheader, actionlist in combinedactionstate.items():
            for action in actionlist:       ### Main action sets to the working frame
                change = action['change']
                if action['main']:
                    if change.alterinput:
                        newfilename = makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder, 'altered_'+change.wffiletrack.connection.Rev)
                        self.maincontainer.addFileTrack(action['filetrack'])
                        newfileheader = action['newfileheader']
                        self.maincontainer.FileHeaders[newfileheader] = {'Container': 'here', 'type': typeRequired}
                        # filepath =
                        self.maincontainer.workingFrame.addFileTotrack(newfileheader, newfilename, typeRequired,
                                                         action['filetrack'].rootpathlist())
                        # revyaml = change.wffiletrack.connection.Rev + '.yaml'
                        # pastframe = change.upcont.memoryframesdict[revyaml]
                        referencefiletrack = self.maincontainer.getRefFrame().filestrack[change.fileheader]
                        self.maincontainer.workingFrame.filestrack[change.fileheader] = self.maincontainer.getRefFrame().filestrack[change.fileheader]
                        self.sagaapicall.downloadFileCall(filetrack=referencefiletrack,
                                                          containerworkingfolder=self.maincontainer.containerworkingfolder)

                    if change.filetype == typeInput:
                        ## what are the choices  There are 3
                        ## If user selected Local  It might mean
                        if action['filetracktype']=='wffiletrack':
                            if change.wffiletrack:
                                pass
                            else:
                                self.maincontainer.removeFileHeader(change.fileheader)
                        elif action['filetracktype']=='nffiletrack':
                            if change.nffiletrack:
                                try:
                                    # makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                                    fn = self.sagaapicall.downloadFileCall(filetrack=action['filetrack'],
                                                                           containerworkingfolder=self.maincontainer.containerworkingfolder)
                                except:

                                    alldownloaded = False
                            else:
                                self.maincontainer.removeFileHeader(change.fileheader)
                            ## use newesttrack
                            ## download newest
                        elif action['filetracktype']=='uffiletrack':
                            ## download upstream
                            try:
                                # makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                                fn = self.sagaapicall.downloadFileCall(filetrack=action['filetrack'],
                                                                       containerworkingfolder=self.maincontainer.containerworkingfolder)
                            except:
                                alldownloaded = False
                    elif change.filetype in  [typeOutput, typeRequired]:
                        if action['filetracktype']=='wffiletrack':
                            if change.wffiletrack:
                                pass
                            else:
                                self.maincontainer.removeFileHeader(change.fileheader)
                        elif action['filetracktype']=='nffiletrack':
                            if change.nffiletrack:
                                try:
                                    if change.md5changed:
                                        makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder, action['filetrack'].lastupdated )
                                    fn = self.sagaapicall.downloadFileCall(filetrack=action['filetrack'],
                                                                           containerworkingfolder=self.maincontainer.containerworkingfolder)
                                except:
                                    alldownloaded = False
                            else:
                                self.maincontainer.removeFileHeader(change.fileheader)

                    if fileheader not in wf.filestrack.keys():
                        if action['filetracktype'] == 'uffiletrack':
                            self.maincontainer.addFileObject(
                                {'fileheader': fileheader,
                                 'filetype': typeInput,
                                 'containerfileinfo': {'Container': change.upcont.containerId,
                                                       'type': typeInput},
                                 'UpstreamContainer': change.upcont,
                                 'ctnrootpathlist': action['filetrack'].ctnrootpathlist}
                            )
                        else:
                            self.maincontainer.addFileTrack(action['filetrack'])

                    if action['filetracktype']=='wffiletrack':
                        pass
                    else:
                        if action['filetype'] == typeInput:
                            wf.filestrack[fileheader].md5 = action['filetrack'].md5
                            if action['filetracktype'] == 'uffiletrack':
                                wf.filestrack[fileheader].connection.Rev = action['filetrack'].lastupdated
                            else:
                                wf.filestrack[fileheader].connection.Rev = action['filetrack'].connection.Rev
                            wf.filestrack[fileheader].lastEdited = action['filetrack'].lastEdited
                        else:
                            wf.filestrack[fileheader].md5 = action['filetrack'].md5
                            wf.filestrack[fileheader].lastupdated = action['filetrack'].lastupdated
                            wf.filestrack[fileheader].lastEdited = action['filetrack'].lastEdited
                else:
                    if action['filetracktype']=='wffiletrack':
                        makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                    else:
                        fn, file_extension = os.path.splitext(action['filetrack'].file_name)
                        file_name = fn + '_' + action['filetrack'].lastupdated + file_extension
                        fn = self.sagaapicall.downloadFileCall(filetrack=action['filetrack'],
                                                               containerworkingfolder=self.maincontainer.containerworkingfolder,
                                                               newfilename=file_name)
                # if mainaction['filetracktype']=='uffiletrack':

                # S1. Keep Fileheader
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
                #     file_name = action['filetrack'].file_name
                #     fn = os.path.join(self.maincontainer.containerworkingfolder, action['filetrack'].ctnrootpath,
                #                       file_name)
                #     if os.path.exists(fn) and action['filetype'] != typeInput:
                #         filename, file_extension = os.path.splitext(action['filetrack'].file_name)
                #         copiedfile_name = filename + '_' + action['filetrack'].lastupdated + '+_' + file_extension
                #         copiedfn = os.path.join(self.maincontainer.containerworkingfolder,
                #                                 action['filetrack'].ctnrootpath,
                #                                 copiedfile_name)
                #         os.rename(fn, copiedfn)
                # except Exception as e:
                #     print( change.fileheader)
                #     print(e)
                #     print(action['filetrack'])

                # if mainaction['filetracktype']=='uffiletrack':

            # if importance == 'main':
            #     if action['filetracktype'] == 'uffiletrack':
            #         return 'Saga will download latest upstream version. ' \
            #                'Going forward, ' + filetrack.lastupdated + ' will be this container''s working copy.\n\n'
            #     elif action['filetracktype'] == 'nffiletrack':
            #         if change.reqoutscenariono == 3 or change.inputscenariono == 3:
            #             return 'Saga will remove this fileheader from your workingframe to be in agreement with Newest Frame'
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
            #         return 'Create copy' + filetrack.file_name + '_' + filetrack.lastupdated + ' .\n\n'
            #     elif action['filetracktype'] == 'nffiletrack':
            #         return 'Create copy' + filetrack.file_name + '_' + filetrack.lastupdated + ' .\n\n'
            #     elif action['filetracktype'] == 'lffiletrack':
            #         return 'Create ' + self.currentrev + ' copy named ' + filetrack.file_name + '_' + filetrack.lastupdated + '.\n\n'
            #     elif action['filetracktype'] == 'wffiletrack':
            #         return 'Create your current working file as ' + filetrack.file_name + '_' + self.currentrev + '_edited.\n\n'
        wf.FrameName=self.newestframe.FrameName
        if not alldownloaded:
            print('What to do from here?')
        wf.writeoutFrameYaml()
        return alldownloaded

    def updatecontainerbylastframecheck(self):

        newestrevnumsinsection = self.sagaapicall.getLatestRevNumCall(self.userdata['current_sectionid'])
        for containerid, newestdict in newestrevnumsinsection.items():
            newestframeyaml = join(self.desktopdir, 'ContainerMapWorkDir', containerid,
                                   'Main','Rev' + str(newestdict['newestrevnum']) + '.yaml')
            if not os.path.exists(newestframeyaml):
                workdir, self.networkcontainers[containerid] = self.downloadContainer(join(self.desktopdir,'ContainerMapWorkDir',containerid), containerid)




    def getStatus(self):
        # maincontainer = self.maincontainer
        allowcommit = False
        canrefresh = False
        if self.maincontainer is None:
            return '', False, False, {}
        if self.isNewContainer():
            if len(self.maincontainer.FileHeaders.keys())>0:
                allowcommit = True
            return 'New Container', allowcommit, False, {}
        self.updatecontainerbylastframecheck()
        # print('after calls updatecontainerbylastframecheck' + datetime.now().isoformat())
        self.newestframe, self.newestrevnum = self.sagaapicall.getNewestFrame(self.maincontainer, self.userdata['current_sectionid'])
        ## newestframe for only the maincontainer. And its not saved anywhere. Just exists as a comparison entity.
        # print('aftercall newestFrame' + datetime.now().isoformat())
        filesupdated, wffilesupdated = self.maincontainer.updateworkframe()
        notlatestrev = False
        # print('afterworkframeupdate' + datetime.now().isoformat())
        if self.maincontainer.revnum < self.newestrevnum:
            self.sagasync.setNewestFrame(self.newestframe)
        else:
            self.sagasync.setNewestFrame(None)
        # print('checkcontainer status' + datetime.now().isoformat())
        upstreamupdated, statustext, notlatestrev, containerchanged, changes =self.sagasync.checkContainerStatus(self.maincontainer, self.newestrevnum)
        # print('checkcontainer status end' + datetime.now().isoformat())
        if containerchanged and not self.sagasync.inconflict:
            allowcommit=True  ## could be one line but I think this is easier to read

        if upstreamupdated or notlatestrev:
            canrefresh=True ## could be one line but I think this is easier to read

        return statustext, allowcommit, canrefresh ,  changes

    def getNewVersionInstaller(self, app):
        # response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
        #                         headers={"Authorization": 'Bearer ' + self.authtoken})
        installPath = os.path.join(self.desktopdir, 'Saga.exe')
        # open(installPath, 'wb').write(response.content)
        self.sagaapicall.getNewVersionCall(installPath)
        Popen(installPath, shell=True)
        sys.exit(app.exec_())


    def CheckContainerCanDeleteOutput(self,  fileheader):
        # containerinfodict = self.sagaapicall.getContainerInfoDict()
        # response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + authtoken})
        # containerinfodict = json.loads(response.content)
        for containerid in self.containerinfodict.keys():
            if containerid==self.maincontainer.containerId:
                continue
            # if not os.path.exists(
            #         os.path.join(self.desktopdir, 'ContainerMapWorkDir', containerid, 'containerstate.yaml')):
            containerworkingfolder = os.path.join(self.desktopdir, 'ContainerMapWorkDir', containerid)
            containerworkingfolder, downstreamcont = self.downloadContainer(containerworkingfolder,  containerid)
            if fileheader in downstreamcont.FileHeaders.keys():
                if downstreamcont.FileHeaders[fileheader]['Container']==self.maincontainer.containerId:
                    return False, 'Downstream Container ' + downstreamcont.containerName + '  is still linked'
        return True, 'No downstream Container is linked '


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