import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from Config import BASE, mapdetailstxt, CONTAINERFN, typeInput,typeOutput,typeRequired,NEWCONTAINERFN,NEWREVISION,FILEADDED, FILEDELETED,UPDATEDUPSTREAM
import yaml
import json
import requests
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
from SagaApp.FileObjects import FileTrack
from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication
import re


class SagaGuiModel():
    def __init__(self, desktopdir, sourcecodedir,
                 versionnumber, authtoken=None, userdata=None , containerwrkdir=None,):
        self.authtoken = authtoken
        self.userdata= userdata
        self.containerwrkdir=containerwrkdir
        self.desktopdir = desktopdir
        self.sourcecodedir = sourcecodedir
        self.versionnumber = versionnumber
        self.guiworkingdir = os.getcwd()
        self.containernetworkkeys=[]
        self.changes = {}

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
        except Exception as e:
            raise('unable to load settings.yaml.  Please ensure it is in program folder.')
        sagaguimodel = cls(sourcecodedir=sourcecodedir, desktopdir=desktopdir, versionnumber=versionnumber)
        return sagaguimodel

    def setAuthToken(self, authtoken):
        self.authtoken = authtoken

    def setUserData(self, userdata):
        self.userdata = userdata

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                token = json.load(json_file)
            response = requests.get(
                BASE + '/auth/userdetails',
                headers={"Authorization": 'Bearer ' + token['auth_token']}
            )
            usertoken = response.json()
            if usertoken['status'] == 'success':
                # self.userdata = usertoken['data']
                self.setUserData(usertoken['data'])
                self.setAuthToken(token['auth_token'])
                userstatusstatement = 'User ' + self.userdata['email'] +\
                                           ' Signed in to Section ' + self.userdata['current_sectionname']
                signinsuccess = True
            else:
                self.setAuthToken(None)
                self.setUserData(None)
                userstatusstatement = 'Please sign in'
                signinsuccess = False
            sectioniddir = join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])
            if not os.path.exists(sectioniddir):
                os.mkdir(sectioniddir)

        except Exception as e:
            # print('No User Signed in yet')
            userstatusstatement = 'Please sign in'
            signinsuccess = False
        return { 'userstatusstatement':userstatusstatement,
                 'signinsuccess':signinsuccess}

    def getContainerInfo(self):
        response = requests.get(BASE + 'CONTAINERS/List', headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfodict = json.loads(response.content)
        if not containerinfodict:
            containerinfodict = {
                'EMPTY': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        return containerinfodict

    def getWorldContainers(self):
        # response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfodict = self.getContainerInfo()
        if 'EMPTY' in containerinfodict.keys():
            self.containernetworkkeys=[]
            return containerinfodict

        for containerID in containerinfodict.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID}, headers={"Authorization": 'Bearer ' + self.authtoken})
            if CONTAINERFN != response.headers['file_name']:
                raise('container file name should be ' + CONTAINERFN + ', time to check response file_name and otherwise')
            if not os.path.exists(join(self.desktopdir,'ContainerMapWorkDir',containerID)):
                os.mkdir(join(self.desktopdir,'ContainerMapWorkDir',containerID))
            containeryamlfn = join(self.desktopdir,'ContainerMapWorkDir', containerID, CONTAINERFN)
            if os.path.exists(containeryamlfn):
                open(containeryamlfn, 'rb+').write(response.content)
            else:
                open(containeryamlfn, 'wb').write(response.content)
            cont = Container.LoadContainerFromYaml(containeryamlfn, fullload=False)
            cont.downloadbranch('Main', BASE, self.authtoken,join(self.desktopdir,'ContainerMapWorkDir',containerID))

        self.containernetworkkeys = containerinfodict.keys()

        if not os.path.exists(join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(join(self.desktopdir, 'SagaGuiData',self.userdata['current_sectionid']))
        return containerinfodict

    def downloadfullframefiles(self, container:Container =None, framerev = 'latest'):
        if container is None:
            raise('Developers need to add a self.maincontainer for this model')
        wf = container.workingFrame
        for fileheader, filetrack in wf.filestrack.items():
            # print(filetrack.file_name,self.containerworkingfolder)
            self.downloadFile(filetrack, container.containerworkingfolder)

    def revertTo(self, reverttorev, fileheadertorevertto , containerworkingfolder):
        framefn = os.path.join(containerworkingfolder, 'Main', reverttorev+'.yaml')
        ## Assumes Frame Exists
        revertframe = Frame.loadRefFramefromYaml(refframefullpath=framefn, containerworkingfolder = containerworkingfolder)
        if fileheadertorevertto is None:
            for fileheader, filetrack in revertframe.filestrack.items():
                self.downloadfile(filetrack, containerworkingfolder)
        else:
            if fileheadertorevertto in revertframe.filestrack.keys():
                self.downloadfile(revertframe.filestrack[fileheadertorevertto], containerworkingfolder)
            else:
                warnings.warn('This frame does not have this fileheader ' + fileheadertorevertto)

    def downloadFile(self, filetrack:FileTrack, filepath, newfilename=None ):
        response = requests.get(BASE + 'FILES',
                                data={'md5': filetrack.md5,
                                      'file_name': filetrack.file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        if newfilename is None:
            fn = os.path.join(filepath,filetrack.ctnrootpath, response.headers['file_name'])
        else:
            fn = os.path.join(filepath, filetrack.ctnrootpath, newfilename)
        if not filetrack.ctnrootpath == '.':
            ensureFolderExist(fn)
        if response.headers['status']=='Success':
            progress = downloadProgressBar(response.headers['file_name'])
            dataDownloaded = 0
            progress.updateProgress(dataDownloaded)
            with open(fn, 'wb') as f:
                for data in response.iter_content(1024):
                    dataDownloaded += len(data)
                    f.write(data)
                    percentDone = 100 * dataDownloaded/len(response.content)
                    progress.updateProgress(percentDone)
                    QGuiApplication.processEvents()
        else:
            # open(fn,'w').write('Terrible quick bug fix')
            # # There should be a like a nuclear warning here is this imples something went wrong with the server and the frame bookkeeping system
            # # This might be okay meanwhile as this is okay to break during dev but not during production.
            raise('could not find file ' + filetrack.md5 + ' on server')
        # saves the content into file.
        os.utime(fn, (filetrack.lastEdited, filetrack.lastEdited))
        return fn#,self.filestrack[fileheader]

    def downloadbranch(self,containerworkingfolder, cont:Container, branch='Main'):
        payload = {'containerID': cont.containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }
        if not os.path.exists(join(containerworkingfolder,branch)):
            os.mkdir(join(containerworkingfolder,branch))
        makefilehidden(join(containerworkingfolder,branch))
        response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
        fullbranchlist = response.json()
        for rev in fullbranchlist:
            payload = {'containerID': cont.containerId,
                       'branch': branch,
                       'rev':rev}
            revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
            if os.path.exists(join(containerworkingfolder,branch, rev)):
                unhidefile(join(containerworkingfolder, branch, rev))
            open(join(containerworkingfolder, branch, rev), 'wb').write(revyaml.content)
            makefilehidden(join(containerworkingfolder,branch, rev))

    def checkUpstream(self, mainContainer):
        upstreamupdated = False
        workingFrame = mainContainer.workingFrame
        refFrame = Frame.loadRefFramefromYaml(mainContainer.refframefullpath,
                                              mainContainer.workingFrame.containerworkingfolder)
        for fileheader in mainContainer.filestomonitor().keys():
            if workingFrame.filestrack[fileheader].connection.connectionType.name == typeInput:
                if workingFrame.filestrack[
                    fileheader].connection.refContainerId is not workingFrame.parentcontainerid:
                    # Check to see if input file is internal to container, not referencing other containers
                    containerID = workingFrame.filestrack[fileheader].connection.refContainerId

                    # this is super slow and inefficient.
                    inputContainerPath = os.path.join(self.desktopdir, 'ContainerMapWorkDir')
                    inputContainerPathID = os.path.join(self.desktopdir, 'ContainerMapWorkDir', containerID)
                    dlcontainyaml = Container.downloadContainerInfo(inputContainerPath, self.authtoken,
                                                                    BASE,
                                                                    containerID)
                    dlcontainer = Container.LoadContainerFromYaml(containerfnfullpath=dlcontainyaml)
                    dlcontainer.downloadbranch('Main', BASE, self.authtoken, inputContainerPathID)
                    framePath = os.path.join(inputContainerPathID, 'Main',
                                             'Rev' + str(dlcontainer.revnum) + '.yaml')
                    inputFrame = Frame.loadRefFramefromYaml(framePath, dlcontainer.containerworkingfolder)
                    # ##Above Chuck of Code should be done in one line or two
                    # dlcontainer.workingFrame

                    # Is it necessary that we get the existing file's md5.   Why does checking upstream require knowledge the change in the current md5?
                    # This should really have two parts, one is to simply compare the last commit Rev of Downstream container to the last committed Rev of the Upstream container.
                    # if ref frame is upstreammd5  its fine, if workingframe is upstreammd5 its fine.
                    # if upstream md5 not equal to
                    # def revNumber(fn):
                    #     m = re.search('Rev(\d+).yaml', fn)
                    #     try:
                    #         return int(m.group(1))
                    #     except:
                    #         return 1
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
                                'fromcontainer':dlcontainer}
                        else:
                            self.changes[fileheader] = {'reason': [UPDATEDUPSTREAM],
                                                        'revision': inputFrame.FrameName,
                                                        'md5': inputFrame.filestrack[fileheader].md5,
                                                        'inputframe': inputFrame,
                                                        'fromcontainer':dlcontainer}
                        upstreamupdated=True
        return  upstreamupdated

    def getStatus(self, mainContainer:Container):
        allowcommit = False
        needtorefresh = False
        self.changes={}
        ###################ORDER IS IMPORTANT HERE..I think####
        self.changes, self.alterfiletracks = mainContainer.compareToRefFrame(self.changes)
        upstreamupdated = sagaguimodel.checkUpstream(mainContainer)
        statustext, notlatestrev = self.checkLatestRevision(mainContainer)
        changeisrelevant = self.checkChangeIsRelevant(mainContainer)
        containerchanged = self.checkContainerChanged(mainContainer)
        isnewcontainer = mainContainer.yamlfn == NEWCONTAINERFN
        if changeisrelevant or containerchanged:
            allowcommit=True  ## could be one line but I think this is easier to read

        if upstreamupdated or notlatestrev:
            needtorefresh=True ## could be one line but I think this is easier to read
        chgstr = ''
        for fileheader, change in self.changes.items():
            chgstr = chgstr + fileheader + '\t' + ', '.join(change['reason']) + '\n'

        return statustext,isnewcontainer, allowcommit, needtorefresh , chgstr, self.changes

    def isNewContainer(self,maincontainer:Container):
        return maincontainer.yamlfn == NEWCONTAINERFN

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

    def checkLatestRevision(self, mainContainer:Container):
        ## This is the only place that knows of a later revision.
        notlatestrev = False
        payload = {'containerID': mainContainer.containerId}

        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }

        response = requests.get(BASE + 'CONTAINERS/newestrevnum', headers=headers, data=payload)
        resp = json.loads(response.content)
        self.newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        self.newestrevnum = resp['newestrevnum']
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
                            self.changes[fileheader]['reason'].append(NEWREVISION)
                        else:
                            self.changes[fileheader] = {'reason': [NEWREVISION]}
                        # if 'File updated....' is within changes reason dictionary, display delta in GUI
                else:
                    self.changes[fileheader] = {'reason': [FILEADDED]}

            # Loop through working frame to check if any files have been deleted in new revision
            for fileheader in refframe.filestrack.keys():
                if fileheader not in self.newestframe.filestrack.keys():
                    if fileheader in self.changes.keys():
                        self.changes[fileheader]['reason'].append(FILEDELETED)
                    else:
                        self.changes[fileheader] = {'reason': [FILEDELETED]}
        else:
            statustext='This is the latest revision'
        return statustext, notlatestrev

    def latestRevFor(self,maincontainer:Container,fileheader):
        if fileheader not in maincontainer.FileHeaders.keys():
            return fileheader + " not in Container " + maincontainer.containerName
        curmd5 = maincontainer.workingFrame.filestrack[fileheader].md5
        # print(self.revnum, self.workingFrame.FrameName)
        lastsamerevnum=maincontainer.revnum
        while lastsamerevnum>1:
            lastsamerevnum-=1
            framefullpathyaml = join(maincontainer.containerworkingfolder, 'Main','Rev'+str(lastsamerevnum) +'.yaml')
            if not os.path.exists(framefullpathyaml):
                warnings.warn('this Should never happen')
                raise('Model is looking for a Rev that is not in local folder')
            #     self.downloadbranch(maincontainer.containerworkingfolder, maincontainer)
            pastframe = Frame.LoadFrameFromYaml(framefullpathyaml, maincontainer.containerworkingfolder)
            if fileheader in pastframe.filestrack.keys():
                if curmd5 != pastframe.filestrack[fileheader].md5:
                    return 'Rev'+str(lastsamerevnum+1), pastframe.commitMessage
                if lastsamerevnum == 1:
                    return 'Rev' + str(lastsamerevnum), pastframe.commitMessage
            else:
                return 'Rev'+str(lastsamerevnum+1), pastframe.commitMessage
        return 'Rev0', 'work in progress'

    # def addressAlteredInput(self):
    #     for alterfiletrack in self.alterfiletracks:
    #         dialogWindow = alteredinputFileDialog(alterfiletrack)
    #         alterinputfileinfo = dialogWindow.getInputs()
    #         if alterinputfileinfo:
    #             self.mainContainer.workingFrame.dealwithalteredInput(alterinputfileinfo,
    #                                                                  self.mainContainer.refframefullpath)
    #     self.readcontainer(os.path.join(self.mainContainer.containerworkingfolder, TEMPCONTAINERFN))
    #     self.checkdelta()

sagaguimodel = SagaGuiModel.loadModelFromConfig()