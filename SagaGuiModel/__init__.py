import sys
import warnings

from os.path import join
# sys.path.insert(1, 'C:/Users/waich/Documents/SagaCore')

# from SagaCore import *
from SagaCore.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaGuiModel.GuiModelConstants import CONTAINERFN, roleInput,roleOutput,roleRequired,NEWCONTAINERFN,SERVERNEWREVISION,SERVERFILEADDED, \
    SERVERFILEDELETED,UPDATEDUPSTREAM, TEMPFRAMEFN, TEMPCONTAINERFN, NEWFRAMEFN
from Config import sourcecodedirfromconfig, APPDATASAGAGUIDIR
import yaml
import json
import shutil

# from Graphics.Dialogs import downloadProgressBar
# from PyQt5.QtGui import QGuiApplication
from Graphics.QAbstract.HistoryListModel import HistoryListModel
from Graphics.QAbstract.SectionSyncFileModel import SectionSyncFileModel
from os import listdir
from os.path import isfile, join
from SagaGuiModel.SagaAPICall import SagaAPICall
from SagaGuiModel.SagaSync import SagaSync
from SagaGuiModel.SagaGuiUtility import *

from subprocess import Popen
import sys
from datetime import datetime
from Graphics.QAbstract.ContainerFileModel import ContainerFileModel
from SagaGuiModel.SagaGuiContainerOperations import *
from SagaCore.Container import Container, ContainerItem
from SagaCore.UserSessionUtils import UserSession
# from Graphics.QAbstract.ConflictListModel import ConflictListModel2, NoticeListModel
#     # AddedListModel, DeletedListModel, UpstreamListModel
import re


class SagaGuiModel():
    def __init__(self, appdata_saga, sourcecodedir,
                 versionnumber,tokenfile,profilelistfile, authtoken=None, usersess=None , containerwrkdir=None,):

        # self.userSession =
        self.usersess= usersess
        self.containerwrkdir=containerwrkdir
        self.appdata_saga = appdata_saga
        self.sourcecodedir = sourcecodedirfromconfig
        self.versionnumber = versionnumber
        self.guiworkingdir = os.getcwd()
        self.sagaapicall:SagaAPICall = SagaAPICall(authtoken)
        self.sagasync:SagaSync = SagaSync(self)
        self.mainguihandle = None
        self.networkcontainers={}
        self.containerinfodict = None
        self.debugmode = False
        self.errormessageboxhandle= None


        self.maincontainer:Container = None
        self.tokenfile = tokenfile
        self.profilelistfile = profilelistfile
        self.loadpassprofile()

        self.histModel = HistoryListModel({})  ### Attention, this should probalby be init at init
        self.sectionsyncmodel = SectionSyncFileModel(self)
        self.containerfilemodel = ContainerFileModel(None, self.sagasync, self)### Attention, ### Attention, this should probalby be init at init

        guidirs= [ 'SagaGuiData','ContainerMapWorkDir']
        if not os.path.exists(self.appdata_saga):
            os.mkdir(self.appdata_saga)
        for guidir in guidirs:
            guidatadir = os.path.join(self.appdata_saga,guidir)
            if not os.path.exists(guidatadir):
                os.mkdir(guidatadir)
            makefilehidden(guidatadir)

    def assignErrorMessageBoxHandle(self,errormessageboxhandle):
        self.errormessageboxhandle = errormessageboxhandle
        self.sagaapicall.errormessageboxhandle=errormessageboxhandle


    def checkUserStatus(self):
        success, usersessiondict = self.sagaapicall.authUserDetails()
        if success:
            self.usersess= UserSession.builduserSessionfromDict(usersessiondict)
            sectioniddir = join(self.appdata_saga, 'SagaGuiData', self.usersess.current_sectionid)
            if not os.path.exists(sectioniddir):
                os.mkdir(sectioniddir)
        return success,self.usersess


    @classmethod
    def loadModelFromConfig(cls):
        try:
            appdata_saga = join(os.getenv('appdata'), APPDATASAGAGUIDIR)
        except Exception as e:
            warnings.warn('cannot find environmental variable appdata')
            appdata_saga = os.getcwd()

        try:
            with open(join(sourcecodedirfromconfig, 'settings.yaml'), 'r') as file:
                settingsyaml = yaml.load(file, Loader=yaml.FullLoader)
            sourcecodedir = sourcecodedirfromconfig
            versionnumber= settingsyaml['versionnumber']
            tokenlocation = settingsyaml['tokenlocation']
            tokenfilename = settingsyaml['tokenfilename']
            profilelistfn = settingsyaml['profilelistfn']
            if tokenlocation=='appdata':
                tokenfile = join(appdata_saga,tokenfilename)
                profilelistfile = join(appdata_saga,profilelistfn)
            else:
                tokenfile = join(os.getcwd(), tokenfilename)
                profilelistfile = join(os.getcwd(), profilelistfn)

        except Exception as e:
            raise('unable to load settings.yaml.  Please ensure it is in program folder.')
        sagaguimodel = cls(sourcecodedir=sourcecodedir, appdata_saga=appdata_saga, versionnumber=versionnumber, tokenfile=tokenfile, profilelistfile=profilelistfile)
        return sagaguimodel



    def loadpassprofile(self):
        if os.path.exists(self.profilelistfile):
            try:
                with open(self.profilelistfile, 'r') as profilelistfilefh:
                    self.profiledict = json.load(profilelistfilefh)
            except Exception as E:
                self.profiledict={}
        else:
            self.profiledict = {}



    def signIn(self, email, password, saveprofile=False):
        success , respdict = self.sagaapicall.signInCall(email, password)
        if success:
            with open(self.tokenfile, 'w') as tokenfilefh:
                json.dump(respdict, tokenfilefh)    #ATTENTION, MAY NOT NEED THIS ANYMORE POtentail security issue?
            if saveprofile:
                with open(self.profilelistfile, 'w') as profilelistfilefh:
                    self.profiledict[email] = {
                        'authtoken':self.sagaapicall.authtoken,
                        'exptimestamp':self.sagaapicall.exptimestamp
                    }
                    json.dump(self.profiledict, profilelistfilefh)
            # self.checkUserStatus()
        return success , respdict

    def signOut(self):
        self.maincontainer: Container = None
        self.usersess = None
        self.sagaapicall.reset()
        self.container_reset()

    def addEmailsToSection(self,emailsToInvite):

        # print(emailsToInvite, self.usersess['current_sectionid'])
        success, servermessage = self.sagaapicall.\
            addEmailsToSectionCall(emailsToInvite, self.usersess.current_sectionid)

        return success, servermessage

    def newUserSignUp(self, email, password, firstname, lastname, sectionid):
        success, respdict = self.sagaapicall.newUserSignUpCall(email, password, firstname, lastname, sectionid )

        if success:
            with open(self.tokenfile, 'w') as tokenfile:
                json.dump(respdict, tokenfile)
            with open(self.profilelistfile, 'w') as profilelistfilefh:
                self.profiledict[email] = {
                    'authtoken':self.sagaapicall.authtoken,
                    'exptimestamp':self.sagaapicall.exptimestamp
                }
                json.dump(self.profiledict, profilelistfilefh)
        return success, respdict


    def getWorldContainers(self):
        success, self.containerinfodict = self.sagaapicall.getContainerInfoDict()### Get list of containers by authtoken.
        if 'EMPTY' in self.containerinfodict.keys():
            return {}
        self.networkcontainers={}
        self.containeridtoname={}
        for containerID in self.containerinfodict.keys():
            print(containerID, self.containerinfodict[containerID]['ContainerDescription'])
            self.containeridtoname[containerID] = self.containerinfodict[containerID]['ContainerDescription']
            self.provideContainer(containerID, update=True)
        updateEveryContainerInSection(self)
        if not os.path.exists(join(self.appdata_saga, 'SagaGuiData', self.usersess.current_sectionid)):
            os.mkdir(join(self.appdata_saga, 'SagaGuiData',self.usersess.current_sectionid))
        return self.containerinfodict , self.usersess.current_sectionname

    def provideContainer(self, containerid, update=False) -> Container:
        if containerid not in self.networkcontainers.keys():
            containyaml = os.path.join(self.appdata_saga, 'ContainerMapWorkDir',containerid, CONTAINERFN)
            if os.path.exists(containyaml) and not update:
                self.networkcontainers[containerid] = Container.LoadContainerFromYaml(containyaml, parentid=self.usersess.current_sectionid)
                return self.networkcontainers[containerid]
            else:
                containerworkingfolder = os.path.join(self.appdata_saga, 'ContainerMapWorkDir', containerid)
                containerworkingfolder, cont  = self.downloadContainer(containerworkingfolder,  containerid)
                if cont:
                    self.networkcontainers[containerid] = cont
                    return self.networkcontainers[containerid]
                else:
                    return None
                    warnings.warn('Error cannot find containerid ' + containerid)
        else:
            return self.networkcontainers[containerid]
    # def downloadfullframefiles(self, container:Container =None, framerev = 'latest'):
    #     if container is None:
    #         raise('Developers need to add a self.maincontainer for this model')
    #     wf = container.workingFrame
    #     for fileheader, filetrack in wf.filestrack.items():
    #         # print(filetrack.entity,self.containerworkingfolder)
    #         self.downloadFile(filetrack, container.containerworkingfolder)

    def revertTo(self, reverttorev, fileheadertorevertto ):
        containerworkingfolder = self.maincontainer.containerworkingfolder
        framefn = os.path.join(containerworkingfolder, 'Main', reverttorev+'.yaml')
        ## Assumes Frame Exists
        revertframe = Frame.loadRefFramefromYaml(refframefullpath=framefn, containerworkingfolder = containerworkingfolder)
        if fileheadertorevertto is None:
            for fileheader, filetrack in revertframe.filestrack.items():
                self.downloadTrack(filetrack, containerworkingfolder)
        else:
            if fileheadertorevertto in revertframe.filestrack.keys():
                self.downloadTrack(revertframe.filestrack[fileheadertorevertto], containerworkingfolder)
            else:
                warnings.warn('This frame does not have this fileheader ' + fileheadertorevertto)



    def checkAllowedtoCommit(self):
        if self.usersess.email not in self.maincontainer.allowedUser:
            return {'commitstatus':'UserDenied',
                    'message':'User Not Allowed to Commit',
                    'conflictfiles': None}
        # Check if there are any conflicting files from refresh action with 'RevXCopy' in file name
        filepath = self.maincontainer.workingFrame.containerworkingfolder
        files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        searchstring = 'Rev' + str(self.maincontainer.revnum) + 'Copy'### this might need to be refined.  Its any rev higher than current rev.
        conflictfiles = [f for f in files if searchstring in f]
        if len(conflictfiles) > 0:
            return {'commitstatus': 'ConflictedFiles',
                    'message': 'User Not Allowed to Commit',
                    'conflictfiles':conflictfiles}
        for citemid, citem in self.maincontainer.containeritems.items():
            if type(citem.track) ==FileTrack:
                if citem.track.entity=='MISSING':
                    return {'commitstatus': 'MISSINGITEMS',
                            'message': 'MISSINGITEMS!! Allocate file to container item ' + citem.containeritemname,
                            'conflictfiles': {}}
            elif type(citem.track)==FolderTrack:
                if citem.track.entity == 'MISSING':
                    return {'commitstatus': 'MISSINGITEMS',
                            'message': 'MISSING FOLDER!!Allocate folder to container item ' + citem.containeritemname,
                            'conflictfiles': {}}
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
            success, newsectionname = self.sectionSwitch(newsectionid)
        self.container_reset()
        print('start of loadcontainer' + datetime.now().isoformat())
        self.maincontainer = Container.LoadContainerFromYaml(containerpath, parentid=self.usersess.current_sectionid, revnum=None, ismaincontainer=ismaincontainer)
        self.histModel.load(commithistory(self.maincontainer))
        self.histModel.individualfilehistory(commithistorybyfile(self.maincontainer))
        self.containerfilemodel.update(self.maincontainer)### Attention,
        # print('hist and container model end' + datetime.now().isoformat())
        return self.maincontainer

    def initiateNewContainer(self, containerworkingfolder, containername, containerdesc):
        ensureFolderExist(os.path.join(containerworkingfolder, 'Main', 'anything'))#### ATTENTION Need to fix ensureFolderExists
        self.maincontainer = Container.InitiateContainer(containerworkingfolder, parentid=self.usersess.current_sectionid,containerName=containername, containerdesc=containerdesc)
        self.containerfilemodel.update(self.maincontainer)#
        self.histModel.load(commithistory(self.maincontainer))
        self.sagasync.reset()

        # return self.containerfilemodel, self.histModel


    def getAvailableSections(self):
        success, sectiondicts = self.sagaapicall.getAvailableSectionsCall()
        return success, sectiondicts

    def shouldModelSwitch(self,containerpath):
        loadingcontainer = Container.LoadContainerFromYaml(containerpath, parentid=self.usersess.current_sectionid, revnum=None, lightload=True)
        # print('damn loading' + datetime.now().isoformat())
        if loadingcontainer is None:
            raise('Could not load container with file ' + containerpath)###Attention feed to gui error box.
        if loadingcontainer.yamlfn == NEWCONTAINERFN:
            return False, self.usersess.current_sectionid
        success, goswitch, newsectionid = self.sagaapicall.shouldModelSwitchCall(loadingcontainer.containerId)
        return goswitch, newsectionid

    def sectionSwitch(self, newsectionid=None):
        # print('sectionstart' + datetime.now().isoformat())
        if newsectionid is None:
            if self.usersess.current_sectionid is None:
                return None, None
            else:
                newsectionid = self.usersess.current_sectionid
        success, newsectionname = self.sagaapicall.sectionSwitchCall(newsectionid)
        if success:
            self.container_reset()
            self.checkUserStatus()
            self.mainguihandle.loadSection()

            # self.usersess
        else:
            print('Error Occured.  Your current section has not change')
        return success, newsectionname

    def container_reset(self):
        self.maincontainer = None
        # self.containeridtoname= {}
        ## Sagatree, Network and Gantt models???
        self.histModel.reset()
        self.containerfilemodel.reset()
        self.sagasync.reset()
        # self.networkcontainers={}

    def downloadTrack(self, track:Track, containerworkingfolder, newfilename=None):

        filestoDownload=[]
        if type(track)==FileTrack:
            if newfilename:
                filename= newfilename
            else:
                filename = track.entity
            filestoDownload.append({'fullfilepath': os.path.join(containerworkingfolder, track.ctnrootpath, filename),
                                'md5': track.md5,
                                'filename': filename,
                                'lastEdited':track.lastEdited})

        if type(track)==FolderTrack:
            for filepath, md5 in track.folderdict.items():
                fn =os.path.join(containerworkingfolder, filepath)
                fullfolderpath, filename = os.path.split(fn)
                ensureFolderExist(fn)
                filestoDownload.append({'fullfilepath': fn,
                                'md5': md5,
                                'filename': filename,
                                'lastEdited':datetime.now().timestamp()})

        for fnitem in filestoDownload:
            self.sagaapicall.downloadTrackCall(fullfilepath = fnitem['fullfilepath'], md5 = fnitem['md5'], filename = fnitem['filename'], lastEdited=fnitem['lastEdited'] )

        # return fn


    def downloadContainer(self,containerworkingfolder,  dlcontainerid, ismaincontainer=False, virtual=False)-> (str, Container):
        ensureFolderExist(
            join(containerworkingfolder, 'Main', 'Rev1.yaml'))  ## Hack 'File name is needed but not used.'ATTENTION
        success,fullframelist, containerdict = self.sagaapicall.downloadContainerCall( dlcontainerid )
        if containerdict=={}:
            return None, None
        revnum = 0
        for yamlfn, framedict in fullframelist.items():
            frame = Frame.LoadFrameFromDict(framedict, containerworkingfolder, yamlfn)
            frame.writeoutFrameYaml(authorized=True)
            m = re.search('Rev(\d+).yaml', yamlfn)
            if m:
                if int(m.group(1)) > revnum:
                    revnum = int(m.group(1))
                    newestrev = m.group(0)
        if virtual==True:
            return 'VIRTUAL', Container.LoadVirtualContainer(fullframelist[newestrev], containerdict)
        cont = Container.LoadContainerFromDict(containerdict,containerworkingfolder, CONTAINERFN, ismaincontainer=ismaincontainer)
        cont.save()
        if ismaincontainer:
            cont.save(TEMPCONTAINERFN)
            cont.yamlfn = TEMPCONTAINERFN
            for citemid, track in cont.refframe.filestrack.items():
                self.downloadTrack(track, containerworkingfolder)
            self.maincontainer = cont
        return containerworkingfolder, cont

    def downloadbranch(self, branch='Main'):
        self.sagaapicall.downloadbranchcall(self.maincontainer.containerworkingfolder, self.maincontainer, branch )
        self.maincontainer.updatememorydict()
        self.maincontainer.updateRevNum()

    def addUserToContainer(self,emailtoadd):
        success, allowedUser, servermessage = self.sagaapicall.addUserToContainerCall(self.usersess,emailtoadd,self.usersess.current_sectionid,self.maincontainer.containerId)
        # print(permissionsresponse['ServerMessage'])
        if success:
            self.maincontainer.setAllowedUser(allowedUser)
            return success, '', self.maincontainer.allowedUser
        else:
            if USERALREADYALLOWED in servermessage:
                self.maincontainer.setAllowedUser(allowedUser)
                return False, '', self.maincontainer.allowedUser
            else:
                return False, servermessage, self.maincontainer.allowedUser

    def commitNewContainer(self, commitmessage):
        payload,filesToUpload = prepareNewCommitCall(self.maincontainer, commitmessage)
        success, returncontdict,returnframedict,servermessage = self.sagaapicall.commitNewContainerToServer(payload, filesToUpload)
        if success:
            self.maincontainer.allowedUser= returncontdict['allowedUser']
            frameRevName = returnframedict['FrameName'] + '.yaml'
            self.maincontainer.workingFrame = Frame.LoadFrameFromDict(returnframedict,self.maincontainer.containerworkingfolder, workingyamlfn=frameRevName)
            ### Maybe put a compare function here to compare the workingFrame before the commit and the Frame that was sent back.
            ## they should be identical.
            # self.maincontainer.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)# writes out TEMPFRAME
            yamlframefnfullpath = self.maincontainer.workingFrame.writeoutFrameYaml(fn =frameRevName, authorized=True)# writes out REVX.yaml
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
        containerdictjson, framedictjson, updateinfojson, filesToUpload = prepareCommitCall(self.maincontainer)
        success, response,  yamlframefn, yamlcontent = self.sagaapicall.commitNewRevisionCall(
            containerdictjson,framedictjson,updateinfojson,
            filesToUpload,commitmessage,self.maincontainer.containerId,self.maincontainer.currentbranch)

        if success:
            # Updating new frame information
            yamlframefnfullpath = join(self.maincontainer.containerworkingfolder, 'Main', yamlframefn)
            open(yamlframefnfullpath, 'w').write(yamlcontent)
            makefilehidden(yamlframefn)
            self.maincontainer.setContainerForNextframe(yamlframefnfullpath)
            # self.maincontainer.save(fn=CONTAINERFN, commitprocess=True)
            self.histModel.load(commithistory(self.maincontainer))
            self.containerfilemodel.update()
            message = 'Commit Success'
        else:
            self.mainguihandle.errout('Commit Fail')
            print('Commit Fail')
            message = 'Commit Failed!'
        return success,self.maincontainer.workingFrame.FrameName, message

    def addChildContainer(self, childcontainerdict):
        filerole = childcontainerdict['filerole']
        # citemid = childcontainerdict['citemid']
        childcontainername = childcontainerdict['containerName']
        downloadfile = None
        if filerole in [roleRequired,roleOutput]:
            # citemid = str(uuid.uuid4())[:8]
            success,parentcontainerdict, childcontainerdict, yamlframefn, yamlcontent = \
                self.sagaapicall.addChildContainerCall(childcontainername=childcontainername,
                                                   parentcontainerid=self.maincontainer.containerId,
                                                   childcontaineritemrole=filerole)
            if success:
                yamlframefnfullpath = join(self.maincontainer.containerworkingfolder, 'Main', yamlframefn)
                open(yamlframefnfullpath, 'wb').write(yamlcontent)
                makefilehidden(yamlframefn)
                self.maincontainer.setContainerForNextframe(yamlframefnfullpath)
                self.loadContainer()
                # sagaguimodel.loadContainer(containerpath, ismaincontainer=True)
            else:
                raise('Child Container creation failed, Need to have recovery code for this.')

        else:
            raise ('Doesnt recognize filerole.')
        self.workingFrame.writeoutFrameYaml()
        self.save()
        return downloadfile
############SyncStatusStuff

    def getRefreshPopUpModels(self):
        return self.sagasync.syncStatusModels2(self.maincontainer, self.containeridtoname)

    def dealWithUserSelection(self,combinedactionstate):
        # self.sagasync.updateContainerWithUserSelection(combinedactionstate, self.maincontainer)
        inputsupdated = False
        wf = self.maincontainer.workingFrame
        alldownloaded = True
            # wf.refreshedcheck = True

        def makesurenotoverwrite(ft:FileTrack, containerworkingfolder, append):

            filefullpath = join(containerworkingfolder, ft.ctnrootpath,ft.entity)
            filename, file_extension = os.path.splitext(ft.entity)
            # edited = '_wk'
            newfilename = filefullpath
            while os.path.exists(newfilename):
                newfilename = filename + append + file_extension
                newfilename = join(containerworkingfolder, ft.ctnrootpath,newfilename)
                append = append + '+'
            shutil.copyfile(filefullpath, newfilename)
            return newfilename

        for citemid, actionlist in combinedactionstate.items():
            for action in actionlist:       ### Main action sets to the working frame
                change = action['change']
                if action['main']:
                    if change.alterinput:
                        newfilename = makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder, 'altered_'+change.wffiletrack.connection.Rev)
                        self.maincontainer.duplicateFileTrack(action['filetrack'])
                        newfileheader = action['newfileheader']
                        self.maincontainer.containeritems[newfileheader] = {'Container': 'here', 'type': roleRequired}
                        # filepath =
                        self.maincontainer.workingFrame.addFileTotrack(newfileheader, newfilename, roleRequired,
                                                         action['filetrack'].rootpathlist())
                        # revyaml = change.wffiletrack.connection.Rev + '.yaml'
                        # pastframe = change.upcont.memoryframesdict[revyaml]
                        referencefiletrack = self.maincontainer.refframe.filestrack[change.fileheader]
                        self.maincontainer.workingFrame.filestrack[change.fileheader] = self.maincontainer.refframe.filestrack[change.fileheader]
                        self.sagaapicall.downloadTrackCall(filetrack=referencefiletrack,
                                                          containerworkingfolder=self.maincontainer.containerworkingfolder)

                    if change.filetype == roleInput:
                        ## what are the choices  There are 3
                        ## If user selected Local  It might mean
                        if action['filetracktype']=='wffiletrack':
                            if change.wffiletrack:
                                pass
                            else:
                                self.maincontainer.removeContainerItem(change.fileheader)
                        elif action['filetracktype']=='nffiletrack':
                            if change.nffiletrack:
                                try:
                                    # makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                                    fn = self.sagaapicall.downloadTrackCall(filetrack=action['filetrack'],
                                                                           containerworkingfolder=self.maincontainer.containerworkingfolder)
                                    inputsupdated = True
                                except:
                                    alldownloaded = False
                            else:
                                self.maincontainer.removeContainerItem(change.fileheader)
                            ## use newesttrack          ## download newest
                        elif action['filetracktype']=='uffiletrack':
                            ## download upstream
                            try:
                                # makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                                fn = self.sagaapicall.downloadTrackCall(filetrack=action['filetrack'],
                                                                       containerworkingfolder=self.maincontainer.containerworkingfolder)
                                inputsupdated = True
                            except:
                                alldownloaded = False
                    elif change.filetype in  [roleOutput, roleRequired]:
                        if action['filetracktype']=='wffiletrack':
                            if change.wffiletrack:
                                pass
                            else:
                                self.maincontainer.removeContainerItem(change.fileheader)
                        elif action['filetracktype']=='nffiletrack':
                            if change.nffiletrack:
                                try:
                                    if change.md5changed:
                                        makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder, action['filetrack'].lastupdated )
                                    fn = self.sagaapicall.downloadTrackCall(filetrack=action['filetrack'],
                                                                           containerworkingfolder=self.maincontainer.containerworkingfolder)
                                except:
                                    alldownloaded = False
                            else:
                                self.maincontainer.removeContainerItem(change.fileheader)

                    if citemid not in wf.filestrack.keys():
                        if action['filetracktype'] == 'uffiletrack':
                            self.maincontainer.addFileObject(
                                {'citemid': citemid,
                                 'filerole': roleInput,
                                 'containerfileinfo': {'Container': change.upcont.containerId,
                                                       'type': roleInput},
                                 'UpstreamContainer': change.upcont,
                                 'ctnrootpathlist': action['filetrack'].ctnrootpathlist}
                            )
                        else:
                            self.maincontainer.duplicateFileTrack(action['filetrack'])

                    if action['filetracktype']=='wffiletrack':
                        pass
                    else:
                        if action['filerole'] == roleInput:
                            wf.filestrack[citemid].md5 = action['filetrack'].md5
                            if action['filetracktype'] == 'uffiletrack':
                                wf.filestrack[citemid].connection.Rev = action['filetrack'].lastupdated
                            else:
                                wf.filestrack[citemid].connection.Rev = action['filetrack'].connection.Rev
                            wf.filestrack[citemid].lastEdited = action['filetrack'].lastEdited
                        else:
                            wf.filestrack[citemid].md5 = action['filetrack'].md5
                            wf.filestrack[citemid].lastupdated = action['filetrack'].lastupdated
                            wf.filestrack[citemid].lastEdited = action['filetrack'].lastEdited
                else:
                    if action['filetracktype']=='wffiletrack':
                        makesurenotoverwrite(action['filetrack'], self.maincontainer.containerworkingfolder)
                    else:
                        fn, file_extension = os.path.splitext(action['filetrack'].entity)
                        filename = fn + '_' + action['filetrack'].lastupdated + file_extension
                        fn = self.sagaapicall.downloadTrackCall(filetrack=action['filetrack'],
                                                               containerworkingfolder=self.maincontainer.containerworkingfolder,
                                                               newfilename=filename)
        wf.FrameName=self.newestframe.FrameName
        if not alldownloaded:
            print('What to do from here?')
        wf.writeoutFrameYaml()
        return alldownloaded, inputsupdated


    def getStatus(self):
        allowcommit = False
        canrefresh = False
        if self.maincontainer is None:
            return '', False, False, {}

        updateEveryContainerInSection(self)
        balh, vnewcont = self.downloadContainer(containerworkingfolder=self.maincontainer.containerworkingfolder,
                                                                     dlcontainerid=self.maincontainer.containerId,
                                                                     virtual=True)
        self.maincontainer.updateworkframe()

        if self.isNewContainer():
            if len(self.maincontainer.containeritems.keys())>0:
                allowcommit = True
            return 'New Container', allowcommit, False, {}

        ## newestframe for only the maincontainer. And its not saved anywhere. Just exists as a comparison entity.

        ## This is to deal with local container only.
        # if self.maincontainer.revnum < vnewcont.revnum:
        #     self.sagasync.setNewestFrame(vnewcont.refframe)
        # else:
        #     self.sagasync.setNewestFrame(None)

        oneormore_upstreamupdated, statustext, notlatestrev, oneormore_trackchanged, changes =self.sagasync.checkContainerStatus(self.maincontainer, vnewcont)

        if oneormore_trackchanged and not self.sagasync.inconflict:
            allowcommit=True  ## could be one line but I think this is easier to read

        if oneormore_upstreamupdated or notlatestrev:
            canrefresh=True ## could be one line but I think this is easier to read

        return statustext, allowcommit, canrefresh ,  changes

    def folderHasContainer(self, newcontparentdirpath):
        localcontaineryaml = join(newcontparentdirpath, CONTAINERFN)
        localtempcontaineryaml = join(newcontparentdirpath, TEMPCONTAINERFN)
        if os.path.exists(localcontaineryaml) or os.path.exists(localtempcontaineryaml):
            return True
        else:
            return False

    def getNewVersionInstaller(self, app):
        # response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
        #                         headers={"Authorization": 'Bearer ' + self.authtoken})
        installPath = os.path.join(self.appdata_saga, 'Saga.exe')
        # open(installPath, 'wb').write(response.content)
        self.sagaapicall.getNewVersionCall(installPath)
        Popen(installPath, shell=True)
        sys.exit(app.exec_())


    def CheckContainerCanDeleteOutput(self,  citem:ContainerItem):
        if citem.containeritemrole == roleOutput:
            for containerid in self.containerinfodict.keys():
                if containerid==self.maincontainer.containerId:
                    continue
                downstreamcont = self.provideContainer(containerid)
                if citem.containeritemid in downstreamcont.containeritems.keys():
                    if downstreamcont.containeritem[citem.containeritemid].containerid==self.maincontainer.containerId:
                        return False, 'Downstream Container ' + downstreamcont.containerName + '  is still linked'
        return True, 'No downstream Container is linked '

    def pingDownstream(self, downstreamcontainerid, citemid, upstreamcontainerid):
        self.sagaapicall.pingDownstreamCall(downstreamcontainerid, citemid, upstreamcontainerid)

    def getContainerPermissions(self):

        success, allowedUser, sectionUser=self.sagaapicall.getContainerPermissionsCall(
            email=self.usersess.email,
         current_sectionid=self.usersess.current_sectionid,
         containerId=self.maincontainer.containerId)
        ## Code here allows for the Model to deal if success is false.

        return allowedUser, sectionUser



# def revNumber(fn):
#     m = re.search('Rev(\d+).yaml', fn)
#     try:
#         return int(m.group(1))
#     except:
#         return 1

sagaguimodel = SagaGuiModel.loadModelFromConfig()