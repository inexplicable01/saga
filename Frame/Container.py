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


from datetime import datetime

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

blankcontainer = {'containerName':"" ,'containerId':"",'inputObjs':[] , 'outputObjs':[] , 'requiredObjs':[] ,'references':[] ,'allowedUser':[] }

class Container:
    def __init__(self, containerfn = 'Default',currentbranch='Main',revnum='1'):
        if containerfn == 'Default':
            containeryaml = blankcontainer
            self.containerworkingfolder = 'C:/Users/happy/Documents/GitHub/saga/newContainers'
        else:
            self.containerworkingfolder = os.path.dirname(containerfn)
            with open(containerfn) as file:
                containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        self.containerfn = containerfn
        self.containerName = containeryaml['containerName']
        self.containerId = containeryaml['containerId']
        self.inputObjs = containeryaml['inputObjs']
        self.outputObjs = containeryaml['outputObjs']
        self.requiredObjs = containeryaml['requiredObjs']
        self.references = containeryaml['references']
        self.allowUsers = containeryaml['allowedUser']
        # self.yamlTracking = containeryaml['yamlTracking']
        self.currentbranch = currentbranch
        self.revnum = revnum
        self.filestomonitor = []
        for typeindex, fileobjtype in enumerate(fileobjtypes):
            # print(typeindex, fileobjtype)
            if getattr(self, fileobjtype):
                for fileindex, fileObj in enumerate(getattr(self, fileobjtype)):
                    self.filestomonitor.append(fileObj['ContainerObjName'])
        # print(self.yamlTracking['currentbranch'] + Rev  + str(self.yamlTracking['rev']) +".yaml")
        self.refframe = os.path.join(self.containerworkingfolder,
                                     currentbranch +'/'+ Rev + revnum + ".yaml")

    def commit(self, cframe: Frame, commitmsg, authtoken, BASE):
        committed = False

        # # frameYamlfileb = framefs.get(file_id=ObjectId(curframe.FrameInstanceId))
        with open(self.refframe) as file:
            frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
        frameRef = Frame(frameRefYaml, self.containerworkingfolder)

        # allowCommit, changes = self.Container.checkFrame(cframe)
        print(frameRef.FrameName)

        filesToUpload = {}
        updateinfo = {}
        for ContainerObjName, filetrackobj in cframe.filestrack.items():
            filepath = os.path.join(self.containerworkingfolder, filetrackobj.file_name)
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrackobj, filepath, frameRef)
            committime = datetime.timestamp(datetime.utcnow())
            if commit_file:
                # new file needs to be committed as the new local file is not the same as previous md5
                filesToUpload[ContainerObjName] = open(filepath,'rb')
                updateinfo[ContainerObjName] = {
                    'file_name': filetrackobj.file_name,
                    'lastEdited': filetrackobj.lastEdited,
                    'md5': filetrackobj.md5,
                    'style': filetrackobj.style,
                }

        updateinfojson = json.dumps(updateinfo)
        print (updateinfo)


        response = requests.post(BASE + 'FRAMES',
                                 headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
                                 data={'containerID': self.containerId, 'branch': self.currentbranch,
                                       'updateinfo': updateinfojson, 'commitmsg':commitmsg},  files=filesToUpload)


        print(response)
        if response.headers['commitsuccess']:
            # Updating new frame information
            frameyamlfn = os.path.join(self.containerId, self.currentbranch, response.headers['file_name'])
            open(frameyamlfn, 'wb').write(response.content)
            # Frame(frameyaml,None)
            with open(frameyamlfn) as file:
                frameyaml = yaml.load(file, Loader=yaml.FullLoader)
            newframe = Frame(frameyaml, self.containerworkingfolder)
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
        if filetrackobj.ContainerObjName not in frameRef.filestrack.keys():
            return True, md5
        if (md5 != frameRef.filestrack[filetrackobj.ContainerObjName].md5):
            return True, md5
        if frameRef.filestrack[filetrackobj.ContainerObjName].lastEdited != os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name)):
            frameRef.filestrack[filetrackobj.ContainerObjName].lastEdited = os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name))
            return True, md5
        return False, md5
        # Make new Yaml file  some meta data sohould exit in Yaml file

    def checkFrame(self, cframe):
        allowCommit = False
        cframe.updateFrame(self.filestomonitor)

        with open(self.refframe) as file:
            fyaml = yaml.load(file, Loader=yaml.FullLoader)
        ref = Frame(fyaml, self.containerworkingfolder)
        print('ref', ref.FrameName)
        changes = cframe.compareToAnotherFrame(ref, self.filestomonitor)
        # print(len(changes))
        if len(changes) > 0:
            allowCommit = True
        return allowCommit, changes

    def commithistory(self):
        historyStr = ''
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(self.containerworkingfolder + '/' + self.currentbranch + '*.yaml')
        for yamlfn in yamllist:
            # print(yamlfn)
            with open(yamlfn) as file:
                pastYaml = yaml.load(file, Loader=yaml.FullLoader)
            # print(pastYaml)
            pastframe = Frame(pastYaml, self.containerworkingfolder)
            # print(pastframe.commitMessage)
            historyStr = historyStr + pastframe.FrameName + '\t' + pastframe.commitMessage + '\t\t\t\t' + \
                         time.ctime(pastframe.commitUTCdatetime) + '\t\n'
        return historyStr

    def printDelta(self, changes):
        framestr = ''
        for change in changes:
            framestr = framestr + change['ContainerObjName'] + '     ' + change['reason'] + '\n'
        return framestr

    def save(self,containerName):
        if self.containerfn == 'Default':
            self.containerfn = containerName
        dictout = {}
        outyaml = open(os.path.join(self.containerworkingfolder, self.containerfn + '.yaml'), 'w')
        keytosave = ['containerName', 'containerId', 'outputObjs', 'inputObjs', 'requiredObjs', 'references']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        yaml.dump(dictout, outyaml)
        outyaml.close()

    def addFileObject(self, fileInfo, fileType:str):
        print(fileType)
        if fileType in ['Input', 'refOutput']:
            self.inputObjs.append(fileInfo)
            print(self.inputObjs)
        elif fileType == 'Required':
            self.requiredObjs.append(fileInfo)
            print(self.requiredObjs)
        elif fileType == 'Output':
            self.outputObjs.append(fileInfo)
