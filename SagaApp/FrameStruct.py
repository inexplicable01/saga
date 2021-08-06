import hashlib
import os
import requests
from Config import BASE
import yaml
from SagaApp.FileObjects import FileTrack
from SagaApp.Connection import FileConnection, ConnectionTypes
import time
import json
import re

from SagaApp.SagaUtil import getFramePathbyRevnum,ensureFolderExist, makefilehidden,unhidefile
# from Config import typeInput,typeOutput,typeRequired, sagaGuiDir
from Config import  CONTAINERFN, TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN, NEEDSDOCTOR, TOBECOMMITTED

blankFrame = {'parentcontainerid':"",'FrameName': NEWFRAMEFN, 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}
import shutil

class Frame:

    # @classmethod
    # def LoadCurrentFrame(cls, containerworkingfolder,containfn):
    #
    #
    #
    #     with open(framefullpath,'r') as file:
    #         framedict = yaml.load(file, Loader=yaml.FullLoader)
    #
    #     cframe = cls(parentcontainerid=framedict['parentcontainerid'],
    #                  FrameName=framedict['FrameName'],
    #                  FrameInstanceId=framedict['FrameInstanceId'],
    #                  commitMessage=framedict['commitMessage'],
    #                  inlinks=framedict['inlinks'],
    #                  outlinks=framedict['outlinks'],
    #                  AttachedFiles=framedict['AttachedFiles'],
    #                  commitUTCdatetime=framedict['commitUTCdatetime'],
    #                  containerworkingfolder=containerworkingfolder,
    #                  filestracklist=framedict['filestrack'],
    #                  workingyamlfn=workingyamlfn)
    #     return cframe

    # @classmethod
    # def LoadFrameFromYaml(cls, frameyamlfullpath, containerworkingfolder):
    #     frameyaml = os.path.basename(frameyamlfullpath)
    #     with open(frameyamlfullpath,'r') as file:
    #         framedict = yaml.load(file, Loader=yaml.FullLoader)
    #
    #     cframe = cls(parentcontainerid=framedict['parentcontainerid'],
    #                  FrameName=framedict['FrameName'],
    #                  FrameInstanceId=framedict['FrameInstanceId'],
    #                  commitMessage=framedict['commitMessage'],
    #                  inlinks=framedict['inlinks'],
    #                  outlinks=framedict['outlinks'],
    #                  AttachedFiles=framedict['AttachedFiles'],
    #                  commitUTCdatetime=framedict['commitUTCdatetime'],
    #                  containerworkingfolder=containerworkingfolder,
    #                  filestracklist=framedict['filestrack'],
    #                  workingyamlfn=frameyaml)
    #     return cframe
    #
    # ### Makes zero sense thare are two ways to load frames from yaml
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
    def InitiateFrame(cls, parentcontainerid, parentcontainername, containerworkingfolder):
        newframe = cls(filestracklist=[],
                       FrameName='Rev0',
                       parentcontainerid=parentcontainerid,
                       parentcontainername=parentcontainername,
                       containerworkingfolder=containerworkingfolder,
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
                 lastupdated = 'Needs Doctor', workingyamlfn = TEMPFRAMEFN, branch='Main'
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
            if 'lastupdated' not in ftrack.keys():
                ftrack['lastupdated'] = NEEDSDOCTOR
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
                                                     persist=True,
                                                    lastupdated = ftrack['lastupdated']
            )

    # def dealwithalteredInput(self, alterinputfileinfo, refframefullpath):
    #     # self.filestrack[]
    #     # add new file track, determine whether its just this next rev or keep check in the future persist
    #     # rename altered input file names
    #     # re get the file from server
    #     filetrack = alterinputfileinfo['alterfiletrack']
    #     fileheader = filetrack.FileHeader
    #
    #     refframe = Frame.loadRefFramefromYaml(refframefullpath, self.containerworkingfolder )
    #     reffiletrack = refframe.filestrack[fileheader]
    #     ## File Management
    #     os.rename(os.path.join(self.containerworkingfolder,filetrack.file_name), os.path.join(self.containerworkingfolder,alterinputfileinfo['nfilename']))
    #     self.downloadfile(reffiletrack, self.containerworkingfolder)
    #     ## Update FileTrack
    #     self.filestrack[alterinputfileinfo['nfileheader']]=FileTrack(
    #         FileHeader=alterinputfileinfo['nfileheader'],
    #         containerworkingfolder=self.containerworkingfolder,
    #         file_name=alterinputfileinfo['nfilename'],
    #         style='ref',
    #         persist= alterinputfileinfo['persist'],
    #     )
        # print('lots of work to be done.')


    def addFileTotrack(self, fileheader,filefullpath, fileType,ctnrootpathlist):
        branch = 'Main'
        # fullpath=fileinfo['FilePath']
        [path, file_name] = os.path.split(filefullpath)
        # FileHeader=fileinfo['fileheader']
        if fileType =='Required':
            conn=FileConnection([],
                                  connectionType=ConnectionTypes.Required,
                                  branch=branch)
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
                                        ctnrootpathlist=ctnrootpathlist,
                                        lastupdated=TOBECOMMITTED)
            self.filestrack[fileheader] = newfiletrackobj
            self.writeoutFrameYaml()
        else:
            raise(filefullpath + ' does not exist')


    def addfromOutputtoInputFileTotrack(self, fileheader, reffiletrack:FileTrack,style,refContainerId,rev,containerworkingfolder,branch='Main'):

        # [path, file_name] = os.path.split(fullpath)
        conn = FileConnection(refContainerId,
                              connectionType=ConnectionTypes.Input,
                              branch=branch,
                              Rev=rev)#######ATTENTION NEEDS UPDATING.  ITs Updating to latest REv, but not the earilest Rev that this was committed


        newfiletrackobj = FileTrack(file_name=reffiletrack.file_name,
                                    FileHeader=fileheader,
                                    style=style,
                                    committedby=reffiletrack.committedby,
                                    md5 = reffiletrack.md5,
                                    commitUTCdatetime=reffiletrack.commitUTCdatetime,
                                    connection=conn,
                                    containerworkingfolder=containerworkingfolder,
                                    lastEdited=reffiletrack.lastEdited,
                                    lastupdated=TOBECOMMITTED)
        self.filestrack[fileheader] = newfiletrackobj
        self.writeoutFrameYaml()


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

    def writeoutFrameYaml(self, fn=None, authorized = False):
        if fn:
            fullfilepath = os.path.join(self.containerworkingfolder,'Main',fn)
        else:
            fullfilepath = os.path.join(self.containerworkingfolder,'Main',self.workingyamlfn)
        yamlfn = os.path.basename(fullfilepath)
        if numofRev(yamlfn)!=0 and not authorized:
            raise('Authorized Writing of RevX.yaml file')
        unhidefile(fullfilepath)
        with open(fullfilepath, 'w') as outyaml:
            yaml.dump(self.dictify(), outyaml)
        makefilehidden(fullfilepath)
        return fullfilepath


    def __repr__(self):
        return json.dumps(self.dictify())

def numofRev(rev):
    m = re.search('Rev(\d+)', rev)
    if m:
        return int(m.group(1))
    else:
        return 0





