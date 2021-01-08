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
        self.FileHeaders = containeryaml['FileHeaders']
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

    def commit(self, cframe: Frame, commitmsg, authtoken, BASE):

        frameRef = Frame(self.refframe, self.filestomonitor, self.containerworkingfolder)

        filesToUpload = {}
        updateinfo = {}
        for fileheader, filetrack in cframe.filestrack.items():
            filepath = os.path.join(self.containerworkingfolder, filetrack.file_name)
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrack, filepath, frameRef)
            if fileheader not in self.FileHeaders.keys():
                warnings.warn('We need to make sure all the tracked files are adequatedly traced', Warning)
                return
            # if self.FileHeaders[fileheader]['type']=='input':
            #     warnings.warn( 'Saga app requires changes to input files to be to saved seperately' , Warning)
            #     cframe.add_fileTrack(filepath,fileheader)
            #     return

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
            return cframe, response.headers['commitsuccess']

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

    def addFileObject(self, fileObjHeader, fileInfo, fileType:str):
        print(fileType)
        if fileType in ['Input', 'refOutput']:
            self.FileHeaders[fileObjHeader] = fileInfo
            print(self.FileHeaders)
        elif fileType == 'Required':
            self.FileHeaders[fileObjHeader] = fileInfo
            print(self.FileHeaders)
        elif fileType == 'Output':
            self.FileHeaders[fileObjHeader] = fileInfo
            print(self.FileHeaders)

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

