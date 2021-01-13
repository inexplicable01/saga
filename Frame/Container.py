from Frame.FrameStruct import Frame
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import copy
import hashlib
import os
import yaml
import glob
import time
import requests
import json
import warnings
from Config import typeInput,typeOutput,typeRequired
from hackpatch import workingdir
from Frame.SagaUtil import FrameNumInBranch
from datetime import datetime

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[] }

class Container:
    def __init__(self, containerfn = 'Default',currentbranch='Main',revnum='1'):
        if containerfn == 'Default':
            containeryaml = blankcontainer

            self.containerworkingfolder = workingdir##something we need to figure out in the future

        else:
            self.containerworkingfolder = os.path.dirname(containerfn)
            with open(containerfn) as file:
                containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        self.containerfn = containerfn
        self.containerName = containeryaml['containerName']
        self.containerId = containeryaml['containerId']
        self.FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] ==typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            self.FileHeaders[fileheader] = fileinfo
        self.allowedUser = containeryaml['allowedUser']
        # self.yamlTracking = containeryaml['yamlTracking']
        self.currentbranch = currentbranch
        self.filestomonitor = {}
        for FileHeader, file in self.FileHeaders.items():
            self.filestomonitor[FileHeader]= file['type']
        if containerfn == 'Default':
            self.revnum = 1
            self.refframe ='dont have one yet'
        else:
            self.refframe, self.revnum = FrameNumInBranch( \
                os.path.join(self.containerworkingfolder,  currentbranch), \
                revnum)
        try:
            self.workingFrame = Frame(self.refframe, self.filestomonitor, self.containerworkingfolder)
        except Exception as e:
            self.workingFrame = Frame()



    def commit(self, commitmsg, authtoken, BASE):

        frameRef = Frame(self.refframe, self.filestomonitor, self.containerworkingfolder)

        filesToUpload = {}
        updateinfo = {}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            filepath = os.path.join(self.containerworkingfolder, filetrack.file_name)
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrack, filepath, frameRef)
            if fileheader not in self.FileHeaders.keys():
                warnings.warn('We need to make sure all the tracked files are adequatedly traced', Warning)
                return
            if commit_file:
                # new file needs to be committed as the new local file is not the same as previous md5
                filesToUpload[fileheader] = open(filepath,'rb')
                updateinfo[fileheader] = {
                    'file_name': filetrack.file_name,
                    'lastEdited': filetrack.lastEdited,
                    'md5': filetrack.md5,
                    'style': filetrack.style,
                }

        updateinfojson = json.dumps(updateinfo)
        containerdictjson = self.__repr__()
        framedictjson = frameRef.__repr__()


        response = requests.post(BASE + 'COMMIT',
                                 headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
                                 data={'containerID': self.containerId,
                                       'containerdictjson': containerdictjson,
                                       'framedictjson': framedictjson,
                                       'branch': self.currentbranch,
                                       'updateinfo': updateinfojson,
                                       'commitmsg':commitmsg},  files=filesToUpload)

        if 'commitsuccess' in response.headers.keys():
            # Updating new frame information
            frameyamlfn = os.path.join(self.containerId, self.currentbranch, response.headers['file_name'])
            open(frameyamlfn, 'wb').write(response.content)
            newframe = Frame(frameyamlfn, self.filestomonitor, self.containerworkingfolder)
            # Write out new frame information
            # The frame file is saved to the frame FS
            self.refframe = frameyamlfn
            return newframe, response.headers['commitsuccess']
        else:
            return self.workingFrame, response.headers['commitsuccess']

    def CommitNewContainer(self, containerName,commitmessage,authtoken,BASE):
        self.containerName = containerName
        self.containerId = containerName

        # self.tempFrame.description = self.descriptionText.toPlainText()
        self.workingFrame.commitMessage = commitmessage

        commitContainer = self.dictify()
        commitFrame = self.workingFrame.dictify()
        url = BASE + 'CONTAINERS/newContainer'
        payload = {'containerdictjson': json.dumps(commitContainer), 'framedictjson': json.dumps(commitFrame)}

        filesToUpload={}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            if filetrack.style in [typeOutput,typeRequired]:
                filepath = os.path.join(self.containerworkingfolder, filetrack.file_name)
                filesToUpload[fileheader] = open(filepath, 'rb')
                fileb = open(filepath, 'rb')
                filetrack.md5 = hashlib.md5(fileb.read()).hexdigest()


        headers = {
            'Authorization': 'Bearer ' + authtoken['auth_token']
        }
        response = requests.request("POST", url, headers=headers, data=payload, files=filesToUpload)
        if 'Container Made' == response.headers['response']:
            resp = response.json()
            returncontdict = resp['containerdictjson']
            returnframedict = resp['framedictjson']
            self.allowedUser= returncontdict['allowedUser']
            self.workingFrame.FrameInstanceId = returnframedict['FrameInstanceId']
            self.workingFrame.commitMessage = returnframedict['commitMessage']
            self.workingFrame.commitUTCdatetime = returnframedict['commitUTCdatetime']
            for filetrack in returnframedict['filestrack']:
                fileheader = filetrack['FileHeader']
                self.workingFrame.filestrack[fileheader].commitUTCdatetime = filetrack['commitUTCdatetime']
                if not self.workingFrame.filestrack[fileheader].md5 == filetrack['md5']:
                    warnings('MD5 changed')
                self.workingFrame.filestrack[fileheader].committedby = filetrack['committedby']
                self.workingFrame.filestrack[fileheader].file_id = filetrack['file_id']

            frameyamlfn = os.path.join(self.containerworkingfolder, self.currentbranch,self.workingFrame.FrameName + '.yaml')
            self.workingFrame.writeoutFrameYaml(frameyamlfn)
            self.save()
            return True
        else:
            return False

    @classmethod
    def downloadContainerInfo(cls, refpath, authToken, BASE, containerId):
        headers = {'Authorization': 'Bearer ' + authToken['auth_token']  }
        response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
        # response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # requests is a python object/class, that sends a http request
        # This returns a container Yaml File
        if not os.path.exists(refpath):
            os.mkdir(refpath)
        if not os.path.exists(os.path.join(refpath, containerId)):
            os.mkdir(os.path.join(refpath, containerId))
        open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
        cls.downloadFrame(refpath, authToken,containerId,BASE)

    @classmethod
    def downloadFrame(cls,refpath,authToken, containerId, BASE, branch='Main'):
        payload = {'containerID': containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + authToken['auth_token']
        }
        response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # request to FRAMES to get the latest frame from the branch as specified in currentbranch
        branch = response.headers['branch']
        # response also returned the name of the branch
        if not os.path.exists(os.path.join(refpath, containerId, branch)):
            os.mkdir(os.path.join(refpath, containerId,branch))
        frameyamlDL = os.path.join(refpath,containerId, branch, response.headers['file_name'])
        open(frameyamlDL, 'wb').write(response.content)
        return frameyamlDL

    def CheckCommit(self, filetrackobj, filepath, frameRef):
        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        if filetrackobj.FileHeader not in frameRef.filestrack.keys():
            return True, md5
        if (md5 != frameRef.filestrack[filetrackobj.FileHeader].md5):
            return True, md5
        if frameRef.filestrack[filetrackobj.FileHeader].lastEdited != os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name)):
            frameRef.filestrack[filetrackobj.FileHeader].lastEdited = os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name))
            return True, md5
        return False, md5
        # Make new Yaml file  some meta data sohould exit in Yaml file

    def commithistory(self):
        historydict = {}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, self.currentbranch , '*.yaml'))
        for yamlfn in yamllist:
            pastframe = Frame(yamlfn, self.filestomonitor, self.containerworkingfolder)
            historydict[pastframe.FrameName] = {'commitmessage':pastframe.commitMessage,
                                               'timestamp':pastframe.commitUTCdatetime }
        return historydict

    def save(self):
        # if self.containerfn == 'Default':
        #     self.containerfn = containerName
        outyaml = open(os.path.join(self.containerworkingfolder, 'containerstate.yaml'), 'w')
        yaml.dump(self.dictify(), outyaml)
        outyaml.close()

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    def __repr__(self):
        return json.dumps(self.dictify())

    def addFileObject(self, fileheader, fileInfo, fileType:str):
        print(fileType)
        if fileType ==typeInput:
            self.FileHeaders[fileheader] = fileInfo
            print(self.FileHeaders)
            # self.workingFrame.addfromOutputtoInputFileTotrack(fileheader, fileInfo, fileType,refContainerId,branch,rev)
        elif fileType == typeRequired:
            self.FileHeaders[fileheader] = fileInfo
            print(self.FileHeaders)
        elif fileType == typeOutput:
            self.FileHeaders[fileheader] = fileInfo
            print(self.FileHeaders)

    def addInputFileObject(self, fileheader,reffiletrack, fullpath,refContainerId,branch,rev):

        self.FileHeaders[fileheader] = {'Container': refContainerId, 'type': typeInput}
        self.workingFrame.addfromOutputtoInputFileTotrack(fileheader=fileheader,
        style=typeInput, fullpath=fullpath, reffiletrack=reffiletrack,
        refContainerId=refContainerId, branch=branch, rev=rev)

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

