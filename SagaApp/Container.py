from SagaApp.FrameStruct import Frame
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
from Config import typeInput,typeOutput,typeRequired, sagaGuiDir
from hackpatch import workingdir
from SagaApp.SagaUtil import FrameNumInBranch
from datetime import datetime

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[] }

class Container:
    def __init__(self, containerworkingfolder,containerName,containerId,
                 FileHeaders,allowedUser,currentbranch,revnum,refframe,
                 workingFrame: Frame):
        self.containerworkingfolder = containerworkingfolder
        self.containerName = containerName
        self.containerId = containerId
        self.FileHeaders = FileHeaders
        self.allowedUser = allowedUser
        self.currentbranch = currentbranch
        self.revnum =revnum
        self.refframe =refframe
        self.workingFrame= workingFrame
        self.updatedInputs = False


    @classmethod
    def InitiateContainer(cls, containerName = '', directory = sagaGuiDir):
        newcontainer = cls(containerworkingfolder=directory,
                           containerName=containerName,
                           containerId="",
                           FileHeaders={},
                           allowedUser=[],
                           currentbranch="Main",revnum='1',
                           refframe='dont have one yet', workingFrame = Frame())
        return newcontainer

    @classmethod
    def LoadContainerFromYaml(cls, containerfn, currentbranch='Main',revnum=None):
        containerworkingfolder = os.path.dirname(containerfn)
        with open(containerfn) as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] == typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            FileHeaders[fileheader] = fileinfo
        # filestomonitor = {}
        # for FileHeader, file in FileHeaders.items():
        #     filestomonitor[FileHeader]= file['type']
        refframe, revnum = FrameNumInBranch(os.path.join(containerworkingfolder, currentbranch), revnum)
        try:
            workingFrame = Frame(refframe, None, containerworkingfolder)
        except Exception as e:
            workingFrame = Frame()
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containeryaml['containerName'],
                           containerId=containeryaml['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containeryaml['allowedUser'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframe=refframe, workingFrame=workingFrame)
        return container

    def commit(self, commitmsg, authtoken, BASE):
        frameRef = Frame(self.refframe, None, self.containerworkingfolder)

        filesToUpload = {}
        updateinfo = {}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            if fileheader not in self.FileHeaders.keys():
                continue
            if self.FileHeaders[fileheader]['type']== typeInput:
                # only commit new input files if input files were downloaded
                if self.updatedInputs == False:
                    continue
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
                    'file_id': filetrack.file_id,
                    'file_name': filetrack.file_name,
                    'lastEdited': filetrack.lastEdited,
                    'md5': filetrack.md5,
                    'style': filetrack.style,
                }

        updateinfojson = json.dumps(updateinfo)
        containerdictjson = self.__repr__()
        framedictjson = self.workingFrame.__repr__()


        response = requests.post(BASE + 'SAGAOP/commit',
                                 headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
                                 data={'containerID': self.containerId,
                                       'containerdictjson': containerdictjson,
                                       'framedictjson': framedictjson,
                                       'branch': self.currentbranch,
                                       'updateinfo': updateinfojson,
                                       'commitmsg':commitmsg},  files=filesToUpload)

        if 'commitsuccess' in response.headers.keys():
            # Updating new frame information
            frameyamlfn = os.path.join(self.containerworkingfolder, self.currentbranch, response.headers['file_name'])
            open(frameyamlfn, 'wb').write(response.content)
            newframe = Frame(frameyamlfn, None, self.containerworkingfolder)
            # Write out new frame information
            # The frame file is saved to the frame FS
            self.refframe = frameyamlfn

            return newframe, response.headers['commitsuccess']
        else:
            print('Commit Fail')
            print(response.json())
            return self.workingFrame, False

    def CommitNewContainer(self, containerName,commitmessage,authtoken,BASE):
        self.containerName = containerName
        self.containerId = containerName

        # self.tempFrame.description = self.descriptionText.toPlainText()
        self.workingFrame.commitMessage = commitmessage

        commitContainer = self.dictify()
        commitFrame = self.workingFrame.dictify()
        url = BASE + 'SAGAOP/newContainer'
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
    def downloadContainerInfo(cls, refpath, authtoken, BASE, containerId):
        headers = {'Authorization': 'Bearer ' + authtoken['auth_token']  }
        response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
        # response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # requests is a python object/class, that sends a http request
        # This returns a container Yaml File
        if not os.path.exists(refpath):
            os.mkdir(refpath)
        if not os.path.exists(os.path.join(refpath, containerId)):
            os.mkdir(os.path.join(refpath, containerId))
        open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
        cls.downloadFrame(refpath, authtoken,containerId,BASE)
        return os.path.join(refpath, containerId, 'containerstate.yaml')

    @classmethod
    def downloadFrame(cls,refpath,authtoken, containerId, BASE, branch='Main'):
        payload = {'containerID': containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + authtoken['auth_token']
        }
        response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        print(response.headers)
        print(response.content)
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
            pastframe = Frame(yamlfn, None, self.containerworkingfolder)
            historydict[pastframe.FrameName] = {'commitmessage':pastframe.commitMessage,
                                               'timestamp':pastframe.commitUTCdatetime }
        return historydict

    def commithistorybyfile(self):
        changesbyfile = {}

        for fileheader in self.workingFrame.filestrack.keys():
            changesbyfile[fileheader] =[]
        containerframes={}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, self.currentbranch , '*.yaml'))
        for yamlfn in yamllist:
            pastframe = Frame(yamlfn, None, self.containerworkingfolder)
            containerframes[pastframe.commitUTCdatetime]= pastframe
        for revi, timestamp in enumerate(sorted(containerframes)):
            pastframe = containerframes[timestamp]
            for fileheader in changesbyfile.keys():
                if fileheader not in pastframe.filestrack.keys():
                    changesbyfile[fileheader].append({'rev':revi, 'md5':'missing'})
                    continue
                changesbyfile[fileheader].append({'rev':revi, 'md5':pastframe.filestrack[fileheader].md5})
                        # changesbyfile[fileheader].append(revi)

            # self.historydict[containerid].append({'commitmessage': pastframe.commitMessage,
            #                                     'timestamp': pastframe.commitUTCdatetime})
            #
            #
            # for fileheader, filetrack in self.workingFrame.filestrack.items():

        return changesbyfile

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
        # print(fileType)
        if fileType ==typeInput:
            self.FileHeaders[fileheader] = fileInfo
            # print(self.FileHeaders)
            # self.workingFrame.addfromOutputtoInputFileTotrack(fileheader, fileInfo, fileType,refContainerId,branch,rev)
        elif fileType == typeRequired:
            self.FileHeaders[fileheader] = fileInfo
            # print(self.FileHeaders)
        elif fileType == typeOutput:
            self.FileHeaders[fileheader] = fileInfo
            # print(self.FileHeaders)

    def addInputFileObject(self, fileheader,reffiletrack, fullpath,refContainerId,branch,rev):

        self.FileHeaders[fileheader] = {'Container': refContainerId, 'type': typeInput}
        self.workingFrame.addfromOutputtoInputFileTotrack(fileheader=fileheader,
        style=typeInput, fullpath=fullpath, reffiletrack=reffiletrack,
        refContainerId=refContainerId, branch=branch, rev=rev)
        # self.filestomonitor['fileheader'] =  typeInput

    def filestomonitor(self):
        ftm={}
        for FileHeader, file in self.FileHeaders.items():
            ftm[FileHeader] = file['type']
        return ftm

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    def downloadbranch(self,branch,BASE,authtoken,refpath):
        payload = {'containerID': self.containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + authtoken['auth_token']
        }
        if not os.path.exists(os.path.join(refpath,branch)):
            os.mkdir(os.path.join(refpath,branch))
        response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
        fullbranchlist = response.json()
        for rev in fullbranchlist:
            payload = {'containerID': self.containerId,
                       'branch': branch,
                       'rev':rev}
            revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)

            open(os.path.join(refpath,branch, rev), 'wb').write(revyaml.content)

    @staticmethod
    def compare(cont1,cont2):
        return recursivecompare(cont1.dictify(), cont2.dictify())

    # @staticmethod
    # def compareFileHeaders(curcont:'Container', newcont:'Container'):
    #     newcont2keys = list(newcont.keys())
    #     diff={}
    #     for fileheader, filevalue in curcont.FileHeaders.items():
    #         if fileheader not in newcont.FileHeaders.keys:
    #             diff[fileheader] = 'MissingInDict2'
    #             continue
    #         else:
    #             newcont2keys.remove(key)
    #         if dict2[key] != value:
    #             identical = False
    #             diff[key] = [value, dict2[key]]


def recursivecompare(dict1, dict2):
    diff = {}
    identical = True
    dict2keys = list(dict2.keys())
    for key, value in dict1.items():
        if key not in dict2.keys():
            # catches the keys missing in dict2 which is the new cont which means its something deleted
            diff[key]='MissingInDict2'
            identical=False
            continue
        else:
            dict2keys.remove(key)
        if type(value) is not dict:
            if dict2[key] != value:
                identical = False
                diff[key] = [value, dict2[key]]
        else:
            iden, difference = recursivecompare(value, dict2[key])
            identical = identical if iden else iden
            diff[key] = difference
    for remainingkey in dict2keys:
        diff[remainingkey]='MissingInDict1'
        # catches the keys missing in dict1 whic means the new cont has fileheaders curcont doesnt which means user added new fileheader
    return identical, diff





