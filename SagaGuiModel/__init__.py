import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from Config import BASE, mapdetailstxt, CONTAINERFN
import yaml
import json
import requests
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
from SagaApp.FileObjects import FileTrack
from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication


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
                self.downloadbranch(maincontainer.containerworkingfolder, maincontainer)
            pastframe = Frame.LoadFrameFromYaml(framefullpathyaml, maincontainer.containerworkingfolder)
            if fileheader in pastframe.filestrack.keys():
                if curmd5 != pastframe.filestrack[fileheader].md5:
                    return 'Rev'+str(lastsamerevnum+1), pastframe.commitMessage
                if lastsamerevnum == 1:
                    return 'Rev' + str(lastsamerevnum), pastframe.commitMessage
            else:
                return 'Rev'+str(lastsamerevnum+1), pastframe.commitMessage
        return 'Rev0', 'work in progress'

sagaguimodel = SagaGuiModel.loadModelFromConfig()