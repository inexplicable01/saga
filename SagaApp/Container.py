from SagaApp.FrameStruct import Frame
import copy
import hashlib
import os
import yaml
import glob
import time
import requests
import json
import warnings
import re
import uuid
from Config import BASE,LOCALFILEHEADERADDED, MD5CHANGED,DATECHANGED , LOCALFILEHEADERREMOVED,\
    typeInput,typeOutput,typeRequired,  TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN,CONTAINERFN,NEEDSDOCTOR
# from hackpatch import workingdir
from SagaApp.SagaUtil import getFramePathbyRevnum,makefilehidden, unhidefile
from datetime import datetime
from SagaApp.FileObjects import FileTrack
import ctypes
import shutil
from os.path import join
# from SagaGuiModel import sagaguimodel

FILE_ATTRIBUTE_HIDDEN = 0x02

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[] }

class Container:
    def __init__(self, containerworkingfolder,containerName,containerid,
                 FileHeaders,allowedUser,readingUsers,currentbranch,revnum,refframefullpath,description,
                 workingFrame: Frame,lightload,  yamlfn=TEMPCONTAINERFN, ):
        self.containerworkingfolder = containerworkingfolder
        self.containerName = containerName
        self.containerId = containerid
        self.FileHeaders = FileHeaders
        self.allowedUser = allowedUser
        self.readingUsers = readingUsers
        self.currentbranch = currentbranch
        self.revnum =revnum
        self.refframefullpath =refframefullpath
        try: ### ATTENTION
            self.refframe = Frame.loadRefFramefromYaml(refframefullpath, self.containerworkingfolder)
        except:
            self.refframe = None
        self.workingFrame= workingFrame
        self.updatedInputs = False
        self.yamlfn = yamlfn
        self.memoryframesdict={}
        self.description = description
        if not lightload:
            self.updatememorydict()


    def updatememorydict(self):
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, 'Main', 'Rev*.yaml'))
        for yamlfn in yamllist:
            revyaml = os.path.basename(yamlfn)
            if revyaml not in self.memoryframesdict.keys():
                pastframe = Frame.loadRefFramefromYaml(yamlfn, self.containerworkingfolder)
                self.memoryframesdict[revyaml] = pastframe

    def commithistory(self):
        historydict = {}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        # yamllist = glob.glob(join(self.containerworkingfolder, self.currentbranch , 'Rev*.yaml'))
        # m = re.search('Rev(\d+).yaml', fn)
        # if m:
        #     if int(m.group(1)) > revnum:
        #         revnum = int(m.group(1))
        #         latestrev = fn
        for revyaml, pastframe in self.memoryframesdict.items():
            m = re.search('(Rev\d+).yaml', revyaml)
            revx = m.group(1)
            # pastframe = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
            historydict[revx] = {'commitmessage':pastframe.commitMessage,
                                               'timestamp':pastframe.commitUTCdatetime,
                                                'frame':pastframe}
        return historydict

    @classmethod
    def InitiateContainer(cls, containerworkingfolder,containerName = '', currentbranch='Main'):
        newcontainer = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containerName,
                           containerid=uuid.uuid4().__str__(),
                           FileHeaders={},
                           allowedUser=[],
                           readingUsers=[],
                           currentbranch="Main",revnum=0,
                           refframefullpath=join(containerworkingfolder,currentbranch, NEWFRAMEFN),
                           workingFrame = Frame.InitiateFrame(parentcontainerid=containerName,
                                                              parentcontainername=containerName,
                                                              containerworkingfolder=containerworkingfolder),
                           yamlfn = NEWCONTAINERFN,
                           description='',
                           lightload = False
                           )
        newcontainer.save()
        return newcontainer

    ##This is problematic as this only works for Client side.    working folder is meant for client side only and can only serve as confusion for the server side
    ## How to make sure Container class can be identical on client side and server side.
    ## Need to think of a way to further remove seperation of concern.
    ## Loading containers on Client side is fundamentally different than loading them on the server side.
    @classmethod
    def LoadContainerFromDict(cls, containerdict,containerworkingfolder, containeryamlfn, currentbranch='Main',revnum=0,
                              environ='FrontEnd', sectionid='',ismaincontainer= False ):
        FileHeaders = containerdict['FileHeaders']
        refframefullpath, revnum = getFramePathbyRevnum(os.path.join(containerworkingfolder, currentbranch), revnum)
        if ismaincontainer:
            framefullpath = os.path.join(containerworkingfolder, 'Main', TEMPFRAMEFN)# since container is downloaded as containers won't be in dict unless its that.
            if not os.path.exists(framefullpath):
                shutil.copy(refframefullpath, os.path.join(containerworkingfolder, 'Main', TEMPFRAMEFN))## is temp doesn't exist, use the latest rev found in main folder
                framefullpath = os.path.join(containerworkingfolder, 'Main', TEMPFRAMEFN)
            try:
                workingFrame = Frame.loadRefFramefromYaml(framefullpath,containerworkingfolder)
            except Exception as e:
                workingFrame = Frame.InitiateFrame(parentcontainerid=containerdict['containerId'],
                                                   parentcontainername=containerdict['containerName'],
                                                   containerworkingfolder= containerworkingfolder)
        else:
            workingFrame =None
        if 'description' not in containerdict.keys():
            containerdict['description'] = 'Need Description'
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containerdict['containerName'],
                            yamlfn=containeryamlfn,
                            readingUsers=containerdict['allowedUser'],## ATTENTION, need to create different levels of permissions user
                           containerid=containerdict['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containerdict['allowedUser'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframefullpath=refframefullpath,
                        workingFrame=workingFrame,
                    lightload = False,
                        description=containerdict['description'])
        container.FixConnections()
        return container



    @classmethod
    def LoadContainerFromYaml(cls, containerfnfullpath, currentbranch='Main',revnum=None,  ismaincontainer=False , lightload=False):
        containerworkingfolder = os.path.dirname(containerfnfullpath)
        containeryamlfn = os.path.basename(containerfnfullpath)
        if os.path.exists(join(containerworkingfolder,TEMPCONTAINERFN)):
            containerfnfullpath = join(containerworkingfolder,TEMPCONTAINERFN)
        try:
            with open(containerfnfullpath, 'r') as file:
                containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        except BaseException as e:
            warnings.warn('Container Load Fail.' +containerfnfullpath + ' seems to be corrupted')
            return None

        FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] == typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            FileHeaders[fileheader] = fileinfo
        if 'readingUsers' not in containeryaml.keys():
            containeryaml['readingUsers']=[]

        if ismaincontainer:
            CONTAINERLIST = [TEMPCONTAINERFN, CONTAINERFN]
            if containeryamlfn in CONTAINERLIST:
                workingyamlfn = TEMPFRAMEFN
            else:
                workingyamlfn = NEWFRAMEFN
            framefullpath = os.path.join(containerworkingfolder, 'Main', workingyamlfn)
            if not os.path.exists(framefullpath):
                framefullpath, revnum = getFramePathbyRevnum(os.path.join(containerworkingfolder, 'Main'), None)
                shutil.copy(framefullpath, os.path.join(containerworkingfolder, 'Main', TEMPFRAMEFN))
            workingFrame = Frame.loadRefFramefromYaml(refframefullpath=framefullpath,
                                                      containerworkingfolder=containerworkingfolder)
        else:
            workingFrame = None

        if containeryamlfn==NEWCONTAINERFN:
            refframefullpath, revnum = join(containerworkingfolder,currentbranch, NEWFRAMEFN), 0
        else:
            refframefullpath, revnum = getFramePathbyRevnum(join(containerworkingfolder, currentbranch), revnum)
        if 'description' not in containeryaml.keys():
            containeryaml['description'] = 'Need Description'
        # print('Beginnign of frame iters ' + containeryaml['containerName']+ '__' + datetime.now().isoformat())
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containeryaml['containerName'],
                           containerid=containeryaml['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containeryaml['allowedUser'],
                           readingUsers=containeryaml['readingUsers'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframefullpath=refframefullpath, workingFrame=workingFrame,
                            yamlfn=containeryamlfn,
                        description=containeryaml['description'],
                        lightload=lightload,
                        )
        # print('End of Frame iters' + datetime.now().isoformat())
        if not lightload:
            container.FixConnections()
        if container.yamlfn == CONTAINERFN:
            container.yamlfn == TEMPFRAMEFN
            container.save()
        return container

    def updateworkframe(self):
        wf = self.workingFrame
        wffilesupdated = []
        filesupdated = False
        for fileheader in wf.filestrack.keys():
            if wf.filestrack[fileheader].connection.connectionType.name in [typeOutput, typeRequired]:
                filefullpath = os.path.join(self.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                                        wf.filestrack[fileheader].file_name)
                fileb = open(filefullpath, 'rb')
                readmd5 = hashlib.md5(fileb.read()).hexdigest()
                if wf.filestrack[fileheader].md5!=readmd5:
                    wf.filestrack[fileheader].md5 = readmd5
                    filesupdated = True
                    wffilesupdated.append((fileheader, filefullpath))
                    wf.filestrack[fileheader].lastEdited = os.path.getmtime(filefullpath)
        if filesupdated:
            wf.writeoutFrameYaml()
        return filesupdated, wffilesupdated

    def FixConnections(self):
        revnum = 1
        filemd5={}
        filemd5history={}
        while revnum<100:
            REVSTR= 'Rev' + str(revnum)
            revyaml = 'Rev' + str(revnum) + '.yaml'
            yamlfn = os.path.join(self.containerworkingfolder, 'Main', 'Rev'+str(revnum)+'.yaml')
            if os.path.exists(yamlfn):
                try:
                    if revyaml in self.memoryframesdict.keys():
                        pastframe = self.memoryframesdict[revyaml]
                    else:
                        Frame.loadRefFramefromYaml(yamlfn, self.containerworkingfolder)
                except:
                    print('Rev'+str(revnum)+'.yaml doesnt exist')
                    revnum+=1
                    continue
                for fileheader, filetrack in pastframe.filestrack.items():
                    # if filetrack.lastupdated == NEEDSDOCTOR:
                    if fileheader in filemd5.keys():
                        if filemd5[fileheader]['md5'] == filetrack.md5:
                            filetrack.lastupdated = filemd5[fileheader]['latestrev']
                        else:
                            filetrack.lastupdated = REVSTR
                            filemd5[fileheader] = {'latestrev': REVSTR, 'md5': filetrack.md5}
                        if filetrack.md5 not in filemd5history[fileheader].keys():
                            filemd5history[fileheader][filetrack.md5]= REVSTR
                    else:
                        filemd5history[fileheader] = {filetrack.md5:REVSTR}
                        filemd5[fileheader] = {'latestrev': REVSTR, 'md5': filetrack.md5}
                        filetrack.lastupdated = REVSTR
                    # if filetrack.connection.connectionType.name==typeOutput:
                    #         print(self.containerId + ' ID with name ' + self.containerName + ' and ' + revnum + ' has ' + fileheader +' has broken Input rev ')

                #     if filetrack.connection.connectionType.name==typeInput:
                #
                #         pastrevnum=1
                #         found = False
                #         while pastrevnum<100:
                #             sectionfolder = os.path.dirname(self.containerworkingfolder)
                #             frameyaml = os.path.join(sectionfolder,filetrack.connection.refContainerId, 'Main','Rev' + str(pastrevnum)+'.yaml')
                #             if os.path.exists(frameyaml):
                #                 upstreampastframe = Frame.loadFramefromYaml(frameyaml, None)
                #                 if fileheader in upstreampastframe.filestrack.keys():
                #                     if upstreampastframe.filestrack[fileheader].md5 == filetrack.md5:
                #                         print(self.containerId + ' ID with name ' + self.containerName + ' and ' + str(
                #                             revnum) + ' has ' + fileheader + ' has broken Input but found it at ' + filetrack.connection.refContainerId+ ' at rev ' +upstreampastframe.FrameName )
                #                         if filetrack.connection.Rev is None:
                #                             filetrack.connection.Rev = upstreampastframe.FrameName
                #                         else:
                #                             if filetrack.connection.Rev !=upstreampastframe.FrameName:
                #                                 print(filetrack.connection.Rev, upstreampastframe.FrameName)
                #                                 filetrack.connection.Rev = upstreampastframe.FrameName
                #                         found = True
                #                         break
                #             else:
                #                 pass
                #             pastrevnum+=1
                #         if not found:
                #             print(self.containerId + ' ID with name ' + self.containerName + ' and ' + str(
                #                 revnum) + ' has ' + fileheader + ' has broken Input and cannot match to upstream md5')
                #
                #     # pastframe.writeoutFrameYaml(yamlfn = yamlfn)
                # pastframe.writeoutFrameYaml(fn = 'Rev'+str(revnum)+'.yaml', authorized=True)
            revnum+=1
        self.filemd5history = filemd5history



    def compareToRefFrame(self, changes):
        alterfiletracks=[]
        wf = self.workingFrame
        if NEWFRAMEFN == os.path.basename(self.refframefullpath):
            return {'NewContainer':{'reason': 'NewContainer'}},[]  ### this might not be final as alternating input files can bring in new difficulties
        refframe = Frame.loadRefFramefromYaml(self.refframefullpath,self.containerworkingfolder)
        refframefileheaders = list(refframe.filestrack.keys())
        for fileheader in self.FileHeaders.keys():
            if fileheader not in refframe.filestrack.keys() and fileheader not in wf.filestrack.keys():
                # check if fileheader is in neither refframe or current frame,
                raise('somehow Container needs to track ' + fileheader + 'but its not in ref frame or current frame')

            if fileheader not in refframe.filestrack.keys() and fileheader in wf.filestrack.keys():
                # check if fileheader is in the refframe, If not in frame, that means user just added a new fileheader
                changes[fileheader]= {'reason': [LOCALFILEHEADERADDED]}
                continue
            refframefileheaders.remove(fileheader)
            filename = os.path.join(self.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath, wf.filestrack[fileheader].file_name)
            fileb = open(filename, 'rb')
            wf.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            # calculate md5 of file, if md5 has changed, update md5

            if refframe.filestrack[fileheader].md5 != wf.filestrack[fileheader].md5:
                wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                changes[fileheader] = {'reason': [MD5CHANGED]}
                if wf.filestrack[fileheader].connection.connectionType==typeInput:
                    alterfiletracks.append(wf.filestrack[fileheader])
                # if file has been updated, update last edited
                wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                continue
            elif wf.filestrack[fileheader].lastEdited != refframe.filestrack[fileheader].lastEdited:
                changes[fileheader] = {'reason': [DATECHANGED]}
                wf.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                print('Date changed without Md5 changing')
                continue

        for removedheaders in refframefileheaders:
            changes[removedheaders] = {'reason': [LOCALFILEHEADERREMOVED]}
        return changes, alterfiletracks




    def getRefFrame(self):
        # frameRef= Frame.loadRefFramefromYaml(self.refframefullpath, self.containerworkingfolder)
        return self.refframe

    def prepareCommitCall(self):
         # = Frame.loadRefFramefromYaml(self.refframefullpath, self.containerworkingfolder)
        frameRef=self.getRefFrame()

        filesToUpload = {}
        updateinfo = {}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            if fileheader not in self.FileHeaders.keys():
                continue
            if self.FileHeaders[fileheader]['type']== typeInput:
                # the input updates are handles through the frame, no need to recommit it.  Or that the input update commit is handled in the framejson upload
                # the real trick is how to deal with altered inputs.
                # Dealing with input updates is gonna require a lot of thought.
                inputsupdated = True
            filepath = join(self.containerworkingfolder,filetrack.ctnrootpath, filetrack.file_name)
            # Should file be committed?
            # commit_file =
            if fileheader not in self.FileHeaders.keys():
                warnings.warn('We need to make sure all the tracked files are adequatedly traced', Warning)
                return
            if self.CheckCommit(filetrack, frameRef):
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
        framedictjson = self.workingFrame.__repr__()

        return containerdictjson,framedictjson, updateinfojson, filesToUpload

    def CheckCommit(self, filetrack:FileTrack, frameRef):
        if filetrack.FileHeader not in frameRef.filestrack.keys():
            return True
        if filetrack.md5 != frameRef.filestrack[filetrack.FileHeader].md5:
            return True
        # if filetrack.lastEdited != os.path.getmtime(filepath):
        #
        #     return True, md5
        return False
        # Make new Yaml file  some meta data sohould exit in Yaml file

    def setContainerForNextframe(self,yamlframefnfullpath):
        yamlframefn = os.path.basename(yamlframefnfullpath)
        self.workingFrame = Frame.loadRefFramefromYaml(yamlframefnfullpath, self.containerworkingfolder)
        self.refframefullpath = yamlframefnfullpath
        self.save(fn=CONTAINERFN, commitprocess=True)
        # self.workingFrame.writeoutFrameYaml()
        self.workingFrame.writeoutFrameYaml(fn=TEMPFRAMEFN)
        self.workingFrame.workingyamlfn=TEMPFRAMEFN
        m = re.search('Rev(\d+).yaml', yamlframefn)
        if m:
            self.revnum = int(m.group(1))
        self.memoryframesdict[yamlframefn] = Frame.loadRefFramefromYaml(yamlframefnfullpath, self.containerworkingfolder)

    def prepareNewCommitCall(self, commitmessage):

        self.workingFrame.commitMessage = commitmessage
        self.workingFrame.FrameName= 'Rev1'

        commitContainer = self.dictify()
        commitFrame = self.workingFrame.dictify()

        payload = {'containerdictjson': json.dumps(commitContainer), 'framedictjson': json.dumps(commitFrame)}
        # refframe = self.getRefFrame()

        filesToUpload={}
        for fileheader, filetrack in self.workingFrame.filestrack.items():
            if filetrack.style in [typeOutput,typeRequired]:
                filepath = join(self.containerworkingfolder, filetrack.file_name)
                filesToUpload[fileheader] = open(filepath, 'rb')
                fileb = open(filepath, 'rb')
                filetrack.md5 = hashlib.md5(fileb.read()).hexdigest()
        return  payload, filesToUpload


    # @classmethod
    # def downloadContainerInfo(cls, refpath, authtoken, BASE, containerId):
    #     headers = {'Authorization': 'Bearer ' + authtoken  }
    #     response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
    #     # response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
    #     # requests is a python object/class, that sends a http request
    #     # This returns a container Yaml File
    #     if not os.path.exists(refpath):
    #         os.mkdir(refpath)
    #     if not os.path.exists(join(refpath, containerId)):
    #         os.mkdir(join(refpath, containerId))
    #     if os.path.exists(join(refpath, containerId, 'containerstate.yaml')):
    #         unhidefile(join(refpath, containerId, 'containerstate.yaml'))
    #     open(join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
    #     makefilehidden(join(refpath, containerId, 'containerstate.yaml'))
    #     cls.downloadFrame(refpath, authtoken,containerId,BASE)
    #     return join(refpath, containerId, 'containerstate.yaml')

    # @classmethod
    # def downloadFrame(cls,refpath,authtoken, containerId, BASE, branch='Main'):
    #     payload = {'containerID': containerId,
    #                'branch': branch}
    #     headers = {
    #         'Authorization': 'Bearer ' + authtoken
    #     }
    #     response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
    #     # print(response.headers)
    #     # print(response.content)
    #     # request to FRAMES to get the latest frame from the branch as specified in currentbranch
    #     branch = 'Main'
    #     # response also returned the name of the branch
    #     if not os.path.exists(join(refpath, containerId, branch)):
    #         os.mkdir(join(refpath, containerId,branch))
    #
    #     frameyamlDL = join(refpath,containerId, branch, response.headers['file_name'])
    #     if os.path.exists(frameyamlDL):
    #         unhidefile(frameyamlDL)
    #     open(frameyamlDL, 'wb').write(response.content)
    #     makefilehidden(join(refpath, containerId, branch))
    #     return frameyamlDL








    def commithistorybyfile(self):
        changesbyfile = {}

        for fileheader in self.getRefFrame().filestrack.keys():
            changesbyfile[fileheader] =[]
        containerframes={}
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        # yamllist = glob.glob(join(self.containerworkingfolder, self.currentbranch , 'Rev*.yaml'))
        for revyaml, pastframe in self.memoryframesdict.items():
            # pastframe = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
            containerframes[pastframe.commitUTCdatetime]= pastframe
        for revi, timestamp in enumerate(sorted(containerframes)):
            pastframe = containerframes[timestamp]
            for fileheader in changesbyfile.keys():
                if fileheader not in pastframe.filestrack.keys():
                    changesbyfile[fileheader].append({'rev':revi, 'md5':'missing'})
                    continue
                changesbyfile[fileheader].append({'rev':revi, 'md5':pastframe.filestrack[fileheader].md5})

        return changesbyfile

    def save(self,fn=None, commitprocess=False):
#https://stackoverflow.com/questions/13215716/ioerror-errno-13-permission-denied-when-trying-to-open-hidden-file-in-w-mod
        if fn==None:
            fn = self.yamlfn
        else:
            if commitprocess:
                fn = CONTAINERFN
                print('Only allow CONTAINERFN to be overwritten during commitprocess')
            else:
                fn = TEMPCONTAINERFN
        if os.path.exists(join(self.containerworkingfolder, fn)):
            unhidefile(join(self.containerworkingfolder, fn))
        outyaml = open(join(self.containerworkingfolder, fn), 'w')
        yaml.dump(self.dictify(), outyaml)
        outyaml.close()
        makefilehidden(join(self.containerworkingfolder, fn))
        if commitprocess==True:
            fn = TEMPCONTAINERFN  ## Set this back to temp after CONTAINFN has been written
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
        self.save()


    def addFileTrack(self, filetrack:FileTrack):
        filetype = filetrack.connection.connectionType.name
        # filetype = fileinfo['filetype']
        fileheader = filetrack.FileHeader
        downloadfile = None
        filepath = os.path.join( self.containerworkingfolder, filetrack.ctnrootpath, filetrack.file_name)
        if filetype ==typeInput:
            # self.FileHeaders[fileheader] =
            # upstreamcontainer = fileinfo['UpstreamContainer']
            # upstreamfiletrack = upstreamcontainer.getRefFrame().filestrack[fileheader]
            #
            # # destintationfilepath  = join( self.containerworkingfolder, upstreamfiletrack.ctnrootpath, upstreamfiletrack.file_name)
            self.FileHeaders[fileheader] = {'Container': filetrack.connection.refContainerId, 'type': filetype}
            self.workingFrame.addfromOutputtoInputFileTotrack(fileheader=fileheader,
                                                              style=typeInput,
                                                              reffiletrack=filetrack,
                                                              containerworkingfolder=self.containerworkingfolder,
                                                              refContainerId=filetrack.connection.refContainerId,
                                                              rev=filetrack.connection.Rev)
        elif filetype == typeRequired:
            self.FileHeaders[fileheader] = {'Container': 'here', 'type': filetype}
            self.workingFrame.addFileTotrack(fileheader, filepath,filetype,filetrack.rootpathlist())
        elif filetype == typeOutput:
            self.FileHeaders[fileheader] = {'Container': '[]', 'type': filetype}
            self.workingFrame.addFileTotrack(fileheader, filepath,filetype,filetrack.rootpathlist())
        else:
            raise ('Doesnt recognize filetype.')
        self.workingFrame.writeoutFrameYaml()
        self.save()
    #     if filetype ==typeInput:
    # def addInputFileObject(self, fileheader,reffiletrack, fullpath,refContainerId,branch,rev):
    def addFileObject(self, fileinfo):
        # fileheader, containerfileinfo, filepath, filetype: str, ctnrootpathlist, rev=None):
        filetype = fileinfo['filetype']
        fileheader = fileinfo['fileheader']
        downloadfile = None
        if filetype ==typeInput:
            upstreamcontainer = fileinfo['UpstreamContainer']
            upstreamfiletrack = upstreamcontainer.getRefFrame().filestrack[fileheader]

            # destintationfilepath  = join( self.containerworkingfolder, upstreamfiletrack.ctnrootpath, upstreamfiletrack.file_name)
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addfromOutputtoInputFileTotrack(fileheader=fileheader,
                                                              style=typeInput,
                                                              reffiletrack=upstreamfiletrack,
                                                              containerworkingfolder=self.containerworkingfolder,
                                                              refContainerId=upstreamcontainer.containerId,
                                                              rev='Rev' + str(upstreamcontainer.revnum))
            downloadfile = {'filetrack':self.workingFrame.filestrack[fileheader] }
        elif filetype == typeRequired:
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addFileTotrack(fileheader, fileinfo['FilePath'],filetype,fileinfo['ctnrootpathlist'])
        elif filetype == typeOutput:
            self.FileHeaders[fileheader] = fileinfo['containerfileinfo']
            self.workingFrame.addFileTotrack(fileheader, fileinfo['FilePath'],filetype,fileinfo['ctnrootpathlist'])
        else:
            raise ('Doesnt recognize filetype.')
        self.workingFrame.writeoutFrameYaml()
        self.save()
        return downloadfile
        # self.filestomonitor['fileheader'] =  typeInput

    def filestomonitor(self):
        ftm={}
        for FileHeader, file in self.FileHeaders.items():
            ftm[FileHeader] = file['type']
        return ftm

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders','allowedUser', 'description']
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
        if not os.path.exists(join(refpath,branch)):
            os.mkdir(join(refpath,branch))
        makefilehidden(join(refpath,branch))
        response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
        fullbranchlist = response.json()
        for rev in fullbranchlist:
            payload = {'containerID': self.containerId,
                       'branch': branch,
                       'rev':rev}
            revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
            if os.path.exists(join(refpath,branch, rev)):
                unhidefile(join(refpath,branch, rev))
            open(join(refpath, branch, rev), 'wb').write(revyaml.content)
            makefilehidden(join(refpath,branch, rev))


    def yamlpath(self):
        return join(self.containerworkingfolder,self.yamlfn)

    def editusers(self, userlist):
        for user in userlist:
            if user not in self.allowedUser:
                self.allowedUser.append(user)
        self.save()




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







