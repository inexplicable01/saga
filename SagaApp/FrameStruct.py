import hashlib
import os
import requests
from Config import BASE
import yaml
from SagaApp.FileObjects import FileTrack
from SagaApp.Connection import FileConnection, ConnectionTypes
import time
import json

from SagaApp.SagaUtil import getFramePathbyRevnum,ensureFolderExist, makefilehidden,unhidefile
# from Config import typeInput,typeOutput,typeRequired, sagaGuiDir
from Config import  CONTAINERFN, TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN

blankFrame = {'parentcontainerid':"",'FrameName': NEWFRAMEFN, 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}
import shutil

class Frame:

    @classmethod
    def LoadCurrentFrame(cls, containerworkingfolder,containfn):
        CONTAINERLIST = [TEMPCONTAINERFN, CONTAINERFN]
        if containfn in CONTAINERLIST:
            workingyamlfn = TEMPFRAMEFN
        else:
            workingyamlfn = NEWFRAMEFN
        # workingyamlfn = TEMPFRAMEFN if containfn==TEMPCONTAINERFN else NEWFRAMEFN
        # if containfn==TEMPCONTAINERFN:
        #     workingyamlfn = TEMPFRAMEFN
        # elif containfn==NEWCONTAINERFN:
        #     workingyamlfn = NEWFRAMEFN
        # elif containfn=='containerstate.yaml':
        #     workingyamlfn = TEMPFRAMEFN

        framefullpath = os.path.join(containerworkingfolder, 'Main', workingyamlfn)
        if not os.path.exists(framefullpath):
            framefullpath, revnum = getFramePathbyRevnum(os.path.join(containerworkingfolder, 'Main'), None)
            shutil.copy(framefullpath,os.path.join(containerworkingfolder, 'Main',TEMPFRAMEFN))

        with open(framefullpath,'r') as file:
            framedict = yaml.load(file, Loader=yaml.FullLoader)

        cframe = cls(parentcontainerid=framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=framedict['commitUTCdatetime'],
                     containerworkingfolder=containerworkingfolder,
                     filestracklist=framedict['filestrack'],
                     workingyamlfn=workingyamlfn)
        return cframe

    @classmethod
    def LoadFrameFromYaml(cls, frameyamlfullpath, containerworkingfolder):
        frameyaml = os.path.basename(frameyamlfullpath)
        with open(frameyamlfullpath,'r') as file:
            framedict = yaml.load(file, Loader=yaml.FullLoader)

        cframe = cls(parentcontainerid=framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=framedict['commitUTCdatetime'],
                     containerworkingfolder=containerworkingfolder,
                     filestracklist=framedict['filestrack'],
                     workingyamlfn=frameyaml)
        return cframe

    @classmethod
    def loadRefFramefromYaml(cls, refframefullpath,containerworkingfolder):
        path , workingyamlfn = os.path.split(refframefullpath)
        with open(refframefullpath,'r') as file:
            framedict = yaml.load(file, Loader=yaml.FullLoader)

        cframe = cls(parentcontainerid=framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=framedict['commitUTCdatetime'],
                     containerworkingfolder=containerworkingfolder,
                     filestracklist=framedict['filestrack'],
                     workingyamlfn=workingyamlfn)
        return cframe

    @classmethod
    def InitiateFrame(cls, parentcontainerid, parentcontainername, localdir):
        newframe = cls(filestracklist=[],
                       FrameName='Rev0',
                       parentcontainerid=parentcontainerid,
                       parentcontainername=parentcontainername,
                       containerworkingfolder=localdir,
                       workingyamlfn=NEWFRAMEFN)
        newframe.writeoutFrameYaml()
        return newframe

    @classmethod
    def LoadFrameFromDict(cls, framedict, containerworkingfolder='LoadedFromDict', workingyamlfn=TEMPFRAMEFN):
        cframe = cls(parentcontainerid= framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=framedict['commitUTCdatetime'],
                     containerworkingfolder=containerworkingfolder,
                     filestracklist=framedict['filestrack'],
                     workingyamlfn=workingyamlfn)
        return cframe

    def __init__(self,parentcontainerid=None,parentcontainername=None, FrameName=None, FrameInstanceId=None,commitMessage=None,
                 inlinks=None,outlinks=None,AttachedFiles=None,commitUTCdatetime=None,containerworkingfolder=None,filestracklist={},
                 workingyamlfn = TEMPFRAMEFN, branch='Main'
                 ):
        self.parentcontainerid = parentcontainerid
        self.parentcontainername=parentcontainername
        self.FrameName = FrameName
        self.FrameInstanceId = FrameInstanceId
        self.commitMessage = commitMessage
        self.workingyamlfn = workingyamlfn
        self.inlinks = inlinks
        self.outlinks = outlinks
        self.AttachedFiles = AttachedFiles
        self.commitUTCdatetime = commitUTCdatetime
        self.containerworkingfolder = containerworkingfolder
        self.framefullpath = os.path.join(containerworkingfolder, branch, workingyamlfn)
        self.filestrack = {}
        self.refreshedcheck = False
        self.refreshrevnum = ''
        for ftrack in filestracklist:
            FileHeader = ftrack['FileHeader']
            ctnrootpathlist=[]
            if 'ctnrootpathlist' in ftrack.keys():
                ctnrootpathlist=ftrack['ctnrootpathlist']
            conn=None
            if 'connection' in ftrack.keys() and ftrack['connection']:
                conn = FileConnection(ftrack['connection']['refContainerId'],
                    connectionType=ftrack['connection']['connectionType'],
                                         branch=ftrack['connection']['branch'],
                                         Rev=ftrack['connection']['Rev'])
            self.filestrack[FileHeader] = FileTrack(FileHeader=ftrack['FileHeader'],
                                                     file_name=ftrack['file_name'],
                                                     containerworkingfolder=containerworkingfolder,
                                                     md5=ftrack['md5'],
                                                     style=ftrack['style'],
                                                     # file_id=ftrack['file_id'],
                                                     commitUTCdatetime=ftrack['commitUTCdatetime'],
                                                     lastEdited=ftrack['lastEdited'],
                                                     connection=conn,
                                                     ctnrootpathlist=ctnrootpathlist,
                                                     persist=True)

    def dealwithalteredInput(self, alterinputfileinfo, refframefullpath):
        # self.filestrack[]
        # add new file track, determine whether its just this next rev or keep check in the future persist
        # rename altered input file names
        # re get the file from server
        filetrack = alterinputfileinfo['alterfiletrack']
        fileheader = filetrack.FileHeader

        refframe = Frame.loadRefFramefromYaml(refframefullpath, self.containerworkingfolder )
        reffiletrack = refframe.filestrack[fileheader]
        ## File Management
        os.rename(os.path.join(self.containerworkingfolder,filetrack.file_name), os.path.join(self.containerworkingfolder,alterinputfileinfo['nfilename']))
        self.downloadfile(reffiletrack, self.containerworkingfolder)
        ## Update FileTrack
        self.filestrack[alterinputfileinfo['nfileheader']]=FileTrack(
            FileHeader=alterinputfileinfo['nfileheader'],
            containerworkingfolder=self.containerworkingfolder,
            file_name=alterinputfileinfo['nfilename'],
            style='ref',
            persist= alterinputfileinfo['persist'],
        )
        # print('lots of work to be done.')


    def addFileTotrack(self, fileheader,filefullpath, fileType,ctnrootpathlist):
        branch = 'Main'
        # fullpath=fileinfo['FilePath']
        [path, file_name] = os.path.split(filefullpath)
        # FileHeader=fileinfo['fileheader']
        if fileType =='Required':
            conn=None
        elif fileType=='Output':
            conn = FileConnection([],
                                  connectionType=ConnectionTypes.Output,
                                  branch=branch)
        if os.path.exists(filefullpath):
            newfiletrackobj = FileTrack(file_name=file_name,
                                        FileHeader=fileheader,
                                        connection=conn,
                                        containerworkingfolder=path,
                                        style=fileType,
                                        lastEdited=os.path.getmtime(filefullpath),
                                        ctnrootpathlist=ctnrootpathlist)
            self.filestrack[fileheader] = newfiletrackobj
            self.writeoutFrameYaml()
        else:
            raise(filefullpath + ' does not exist')


    def addfromOutputtoInputFileTotrack(self, fullpath, fileheader, reffiletrack:FileTrack,style,refContainerId,rev,containerworkingfolder,branch='Main'):

        [path, file_name] = os.path.split(fullpath)
        conn = FileConnection(refContainerId,
                              connectionType=ConnectionTypes.Input,
                              branch=branch,
                              Rev=rev)

        if os.path.exists(fullpath):
            newfiletrackobj = FileTrack(file_name=file_name,
                                        FileHeader=fileheader,
                                        style=style,
                                        committedby=reffiletrack.committedby,
                                        # file_id=reffiletrack.file_id,
                                        commitUTCdatetime=reffiletrack.commitUTCdatetime,
                                        connection=conn,
                                        containerworkingfolder=containerworkingfolder,
                                        lastEdited=os.path.getmtime(fullpath))
            self.filestrack[fileheader] = newfiletrackobj
            self.writeoutFrameYaml()
        else:
            raise(fullpath + ' does not exist')

    def dictify(self):
        dictout = {}
        for key, value in vars(self).items():
            if 'filestrack' == key:
                filestrack = []
                for FileHeader, filetrackobj in value.items():
                    filestrack.append(filetrackobj.dictify())
                dictout[key] = filestrack
            elif 'filestomonitor' ==key:
                # print('skip')
                continue
            else:
                dictout[key] = value
        return dictout

    def writeoutFrameYaml(self, fn=None):
        if fn:
            fullfilepath = os.path.join(self.containerworkingfolder,'Main',fn)
        else:
            fullfilepath = os.path.join(self.containerworkingfolder,'Main',self.workingyamlfn)
        unhidefile(fullfilepath)
        with open(fullfilepath, 'w') as outyaml:
            yaml.dump(self.dictify(), outyaml)
        makefilehidden(fullfilepath)


    def __repr__(self):
        return json.dumps(self.dictify())





