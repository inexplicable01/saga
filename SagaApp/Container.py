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
from Config import typeInput,typeOutput,typeRequired,  TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN,CONTAINERFN
from hackpatch import workingdir
from SagaApp.SagaUtil import getFramePathbyRevnum,makefilehidden
from datetime import datetime
import ctypes

FILE_ATTRIBUTE_HIDDEN = 0x02

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[] }

class Container:
    def __init__(self, containerworkingfolder,containerName,containerId,
                 FileHeaders,allowedUser,readingUsers,currentbranch,revnum,refframefullpath,
                 workingFrame: Frame, yamlfn=TEMPCONTAINERFN):
        self.containerworkingfolder = containerworkingfolder
        self.containerName = containerName
        self.containerId = containerId
        self.FileHeaders = FileHeaders
        self.allowedUser = allowedUser
        self.readingUsers = readingUsers
        self.currentbranch = currentbranch
        self.revnum =revnum
        self.refframefullpath =refframefullpath
        self.workingFrame= workingFrame
        self.updatedInputs = False
        self.yamlfn = yamlfn



    @classmethod
    def InitiateContainer(cls, directory,containerName = ''):
        newcontainer = cls(containerworkingfolder=directory,
                           containerName=containerName,
                           containerId="",
                           FileHeaders={},
                           allowedUser=[],
                           readingUsers=[],
                           currentbranch="Main",revnum='0',
                           refframefullpath=NEWFRAMEFN,
                           workingFrame = Frame.InitiateFrame(parentcontainerid=containerName,parentcontainername=containerName, localdir=directory),
                           yamlfn = NEWCONTAINERFN)
        return newcontainer

    @classmethod
    def LoadContainerFromYaml(cls, containerfn, currentbranch='Main',revnum=None, fullload=True):
        containerworkingfolder = os.path.dirname(containerfn)
        containeryamlfn = os.path.basename(containerfn)
        with open(containerfn, 'r') as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)

        FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] == typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            FileHeaders[fileheader] = fileinfo
        if 'readingUsers' not in containeryaml.keys():
            containeryaml['readingUsers']=[]
        if fullload:
            workingFrame = Frame.loadFramefromYaml(containerworkingfolder=containerworkingfolder, containfn=containeryamlfn)
        else:
            workingFrame=None

        if containerfn==NEWCONTAINERFN:
            refframefullpath, revnum = os.path.join(containerworkingfolder, NEWFRAMEFN), 0
        else:
            refframefullpath, revnum = getFramePathbyRevnum(os.path.join(containerworkingfolder, currentbranch), revnum)

        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containeryaml['containerName'],
                           containerId=containeryaml['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containeryaml['allowedUser'],
                           readingUsers=containeryaml['readingUsers'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframefullpath=refframefullpath, workingFrame=workingFrame, yamlfn=containeryamlfn)
        if container.yamlfn == CONTAINERFN:
            container.yamlfn == TEMPFRAMEFN
            container.save()
        return container

    def commit(self, commitmsg, authtoken, BASE):
        frameRef = Frame.loadRefFramefromYaml(self.refframefullpath, self.containerworkingfolder)

        filesToUpload = {}
        updateinfo = {}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            if fileheader not in self.FileHeaders.keys():
                continue
            if self.FileHeaders[fileheader]['type']== typeInput:
                # only commit new input files if input files were downloaded
                # Dealing with input updates is gonna require a lot of thought.
                inputsupdated = True
                # if not frameRef.filestrack[fileheader].connection.Rev == filetrack.connection.Rev:
                #     inputsupdated = True
                # else:
                #     continue

                # if self.updatedInputs == False:
                #     continue
            filepath = os.path.join(self.containerworkingfolder,filetrack.ctnrootpath, filetrack.file_name)
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrack, filepath, frameRef)
            if fileheader not in self.FileHeaders.keys():
                warnings.warn('We need to make sure all the tracked files are adequatedly traced', Warning)
                return
            if commit_file:
                # new file needs to be committed as the new local file is not the same as previous md5
                filesToUpload[fileheader] = open(filepath,'rb')
                updateinfo[fileheader] = {

                    # 'file_id': filetrack.file_id,

                    'file_name': filetrack.file_name,
                    'lastEdited': filetrack.lastEdited,
                    'md5': filetrack.md5,
                    'style': filetrack.style,
                }

        updateinfojson = json.dumps(updateinfo)
        containerdictjson = self.__repr__()
        framedictjson = self.workingFrame.__repr__()


        response = requests.post(BASE + 'SAGAOP/commit',
                                 headers={"Authorization": 'Bearer ' + authtoken},
                                 data={'containerID': self.containerId,
                                       'containerdictjson': containerdictjson,
                                       'framedictjson': framedictjson,
                                       'branch': self.currentbranch,
                                       'updateinfo': updateinfojson,
                                       'commitmsg':commitmsg},  files=filesToUpload)

        if 'commitsuccess' in response.headers.keys():
            # Updating new frame information
            yamlframefn = os.path.join(self.containerworkingfolder, self.currentbranch, response.headers['file_name'])
            open(yamlframefn, 'wb').write(response.content)
            makefilehidden(yamlframefn)
            self.workingFrame = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
            self.save(fn=CONTAINERFN)
            self.save(fn=TEMPCONTAINERFN)
            # self.workingFrame.writeoutFrameYaml()
            self.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)

            self.refframefullpath = yamlframefn

            return response.headers['commitsuccess']
        else:
            print('Commit Fail')
            resp = json.loads(response.content)
            print(resp)
            return self.workingFrame, False

    def CommitNewContainer(self, containerName,commitmessage,authtoken,BASE):
        self.containerName = containerName
        self.containerId = containerName

        # self.tempFrame.description = self.descriptionText.toPlainText()
        self.workingFrame.commitMessage = commitmessage
        self.workingFrame.FrameName= 'Rev1'

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
        headers = {  'Authorization': 'Bearer ' + authtoken}
        response = requests.request("POST", url, headers=headers, data=payload, files=filesToUpload)
        if 'Container Made' == response.headers['response']:
            resp = response.json()
            returncontdict = resp['containerdictjson']
            returnframedict = resp['framedictjson']
            self.allowedUser= returncontdict['allowedUser']
            self.workingFrame = Frame.LoadFrameFromDict(returnframedict,self.containerworkingfolder)
            ### Maybe put a compare function here to compare the workingFrame before the commit and the Frame that was sent back.
            ## they should be identical.
            self.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)# writes out TEMPFRAME
            self.workingFrame.writeoutFrameYaml(returnframedict['FrameName'] + '.yaml')# writes out REVX.yaml
            self.save(fn=CONTAINERFN)
            self.yamlfn = TEMPCONTAINERFN
            self.save()

            try:
                os.remove(self.containerworkingfolder, NEWCONTAINERFN)
                os.remove(self.containerworkingfolder, 'Main',NEWFRAMEFN)
            except:
                print('Can''t remove pre First Commit files.')
            return True
        else:
            self.workingFrame.FrameName = 'Rev0'
            return False

    @classmethod
    def downloadContainerInfo(cls, refpath, authtoken, BASE, containerId):
        headers = {'Authorization': 'Bearer ' + authtoken  }
        response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
        # response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # requests is a python object/class, that sends a http request
        # This returns a container Yaml File
        if not os.path.exists(refpath):
            os.mkdir(refpath)
        if not os.path.exists(os.path.join(refpath, containerId)):
            os.mkdir(os.path.join(refpath, containerId))
        if os.path.exists(os.path.join(refpath, containerId, 'containerstate.yaml')):
            open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'rb+').write(response.content)
        else:
            open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
        makefilehidden(os.path.join(refpath, containerId, 'containerstate.yaml'))
        cls.downloadFrame(refpath, authtoken,containerId,BASE)
        return os.path.join(refpath, containerId, 'containerstate.yaml')

    @classmethod
    def downloadFrame(cls,refpath,authtoken, containerId, BASE, branch='Main'):
        payload = {'containerID': containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + authtoken
        }
        response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # print(response.headers)
        # print(response.content)
        # request to FRAMES to get the latest frame from the branch as specified in currentbranch
        branch = 'Main'
        # response also returned the name of the branch
        if not os.path.exists(os.path.join(refpath, containerId, branch)):
            os.mkdir(os.path.join(refpath, containerId,branch))
        makefilehidden(os.path.join(refpath, containerId,branch))
        frameyamlDL = os.path.join(refpath,containerId, branch, response.headers['file_name'])
        if os.path.exists(frameyamlDL):
            open(frameyamlDL, 'rb+').write(response.content)
        else:
            open(frameyamlDL, 'wb').write(response.content)
        return frameyamlDL

    def CheckCommit(self, filetrack, filepath, frameRef):
        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        if filetrack.FileHeader not in frameRef.filestrack.keys():
            return True, md5
        if (md5 != frameRef.filestrack[filetrack.FileHeader].md5):
            return True, md5
        if frameRef.filestrack[filetrack.FileHeader].lastEdited != os.path.getmtime(filepath):
            frameRef.filestrack[filetrack.FileHeader].lastEdited = os.path.getmtime(filepath)
            return True, md5
        return False, md5
        # Make new Yaml file  some meta data sohould exit in Yaml file

    def commithistory(self):
        historydict = {}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, self.currentbranch , 'Rev*.yaml'))
        for yamlframefn in yamllist:
            pastframe = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
            historydict[pastframe.FrameName] = {'commitmessage':pastframe.commitMessage,
                                               'timestamp':pastframe.commitUTCdatetime,
                                                'frame':pastframe}
        return historydict

    def commithistorybyfile(self):
        changesbyfile = {}

        for fileheader in self.workingFrame.filestrack.keys():
            changesbyfile[fileheader] =[]
        containerframes={}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, self.currentbranch , 'Rev*.yaml'))
        for yamlframefn in yamllist:
            pastframe = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
            containerframes[pastframe.commitUTCdatetime]= pastframe
        for revi, timestamp in enumerate(sorted(containerframes)):
            pastframe = containerframes[timestamp]
            for fileheader in changesbyfile.keys():
                if fileheader not in pastframe.filestrack.keys():
                    changesbyfile[fileheader].append({'rev':revi, 'md5':'missing'})
                    continue
                changesbyfile[fileheader].append({'rev':revi, 'md5':pastframe.filestrack[fileheader].md5})

        return changesbyfile

    def save(self, fn = TEMPCONTAINERFN):
#https://stackoverflow.com/questions/13215716/ioerror-errno-13-permission-denied-when-trying-to-open-hidden-file-in-w-mod
        if os.path.exists(os.path.join(self.containerworkingfolder, fn)):
            outyaml = open(os.path.join(self.containerworkingfolder, fn), 'r+')
        else:
            outyaml = open(os.path.join(self.containerworkingfolder, fn), 'w')
        yaml.dump(self.dictify(), outyaml)
        outyaml.close()
        makefilehidden(os.path.join(self.containerworkingfolder, fn))
        self.yamlfn=fn

    def setAllowedUser(self, allowedUserList):
        self.allowedUser= allowedUserList
        self.save()

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    def __repr__(self):
        return json.dumps(self.dictify())

    def removeFileHeader(self, fileheader):
        if fileheader in self.FileHeaders.keys():
            del self.FileHeaders[fileheader]
        else:
            print('Fileheader ' + fileheader +' doesn''t exist in the container.  The removal of Fileheader was not performed because its not in the container')
        if fileheader in self.workingFrame.filestrack.keys():
            del self.workingFrame.filestrack[fileheader]
        else:
            print('Fileheader ' + fileheader + ' doesn''t exist in the frame.  The removal of Fileheader was not performed because its not in the container')
        self.workingFrame.writeoutFrameYaml()
        self.save(fn=self.yamlfn)

    # def addInputFileObject(self, fileheader,reffiletrack, fullpath,refContainerId,branch,rev):
    def addFileObject(self, fileinfo):
        # fileheader, containerfileinfo, filepath, filetype: str, ctnrootpathlist, rev=None):
        filetype = fileinfo['filetype']
        fileheader = fileinfo['fileheader']
        if filetype ==typeInput:
            upstreamcontainer = fileinfo['UpstreamContainer']
            fullpath, filetrack = upstreamcontainer.workingFrame.downloadInputFile(fileinfo['fileheader'],
                                                                                   self.workingdir)
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addfromOutputtoInputFileTotrack(fileheader=fileheader,
                                                              style=typeInput, fullpath=fullpath,
                                                              reffiletrack=filetrack,
                                                              containerworkingfolder=self.containerworkingfolder,
                                                              refContainerId=fileinfo['containerfileinfo']['containerid'],
                                                              rev='Rev' + str(upstreamcontainer.revnum))
        elif filetype == typeRequired:
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addFileTotrack(fileheader, fileinfo['FilePath'],filetype,fileinfo['ctnrootpathlist'])
        elif filetype == typeOutput:
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addFileTotrack(fileheader, fileinfo['FilePath'],filetype,fileinfo['ctnrootpathlist'])
        else:
            raise ('Doesnt recognize filetype.')
        self.workingFrame.writeoutFrameYaml()
        self.save(fn=self.yamlfn)
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
            'Authorization': 'Bearer ' + authtoken
        }
        if not os.path.exists(os.path.join(refpath,branch)):
            os.mkdir(os.path.join(refpath,branch))
        makefilehidden(os.path.join(refpath,branch))
        response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
        fullbranchlist = response.json()
        for rev in fullbranchlist:
            payload = {'containerID': self.containerId,
                       'branch': branch,
                       'rev':rev}
            revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
            if os.path.exists(os.path.join(refpath,branch, rev)):
                open(os.path.join(refpath, branch, rev), 'rb+').write(revyaml.content)
            else:
                open(os.path.join(refpath, branch, rev), 'wb').write(revyaml.content)
            makefilehidden(os.path.join(refpath,branch, rev))


    def yamlpath(self):
        return os.path.join(self.containerworkingfolder,self.yamlfn)

    def editusers(self, userlist):
        for user in userlist:
            if user not in self.allowedUser:
                self.allowedUser.append(user)
        self.save(fn=self.yamlfn)

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







