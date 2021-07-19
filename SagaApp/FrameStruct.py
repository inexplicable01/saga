import hashlib
import os
import requests
from Config import BASE
import yaml
from SagaApp.FileObjects import FileTrack
from SagaApp.Connection import FileConnection, ConnectionTypes
import time
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import *
import requests
from Graphics.Dialogs import downloadProgressBar
from SagaApp.SagaUtil import FrameNumInBranch,ensureFolderExist
# from Config import typeInput,typeOutput,typeRequired, sagaGuiDir
from Config import BASE,changenewfile, changemd5,changedate , changeremoved, CONTAINERFN, TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN

blankFrame = {'parentcontainerid':"",'FrameName': NEWFRAMEFN, 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}
import shutil

class Frame:

    @classmethod
    def loadFramefromYaml(cls, containerworkingfolder,containfn):
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
            framefullpath, revnum = FrameNumInBranch(os.path.join(containerworkingfolder, 'Main'), None)
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
        self.getfile(reffiletrack, self.containerworkingfolder)
        ## Update FileTrack
        self.filestrack[alterinputfileinfo['nfileheader']]=FileTrack(
            FileHeader=alterinputfileinfo['nfileheader'],
            containerworkingfolder=self.containerworkingfolder,
            file_name=alterinputfileinfo['nfilename'],
            style='ref',
            persist= alterinputfileinfo['persist'],
        )
        # print('lots of work to be done.')

    def downloadfullframefiles(self):
        for fileheader, filetrack in self.filestrack.items():
            # print(filetrack.file_name,self.containerworkingfolder)
            self.getfile(filetrack, self.containerworkingfolder)

    def getfile(self, filetrack: FileTrack, filepath):
        response = requests.get(BASE + 'FILES',
                                data={'md5': filetrack.md5, 'file_name': filetrack.file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join(filepath, filetrack.ctnrootpath, filetrack.file_name)
        if not filetrack.ctnrootpath == '.':
            ensureFolderExist(fn)
        if response.headers['status']=='Success':
            open(fn, 'wb').write(response.content)
        else:
            open(fn,'w').write('Terrible quick bug fix')
            # There should be a like a nuclear warning here is this imples something went wrong with the server and the frame bookkeeping system
            # This might be okay meanwhile as this is okay to break during dev but not during production.
            print('could not find file ' + filetrack.md5 + ' on server')
        os.utime(fn, (filetrack.lastEdited, filetrack.lastEdited))



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


    def addfromOutputtoInputFileTotrack(self, fullpath, fileheader, reffiletrack:FileTrack,style,refContainerId,branch,rev):
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
                                        containerworkingfolder=path,
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
            with open(os.path.join(self.containerworkingfolder,'Main',fn), 'w') as outyaml:
                yaml.dump(self.dictify(), outyaml)
        else:
            with open(os.path.join(self.containerworkingfolder,'Main',self.workingyamlfn), 'w') as outyaml:
                yaml.dump(self.dictify(), outyaml)

    def __repr__(self):
        return json.dumps(self.dictify())

    def revertTo(self, reverttorev):
        framefn = os.path.join(self.containerworkingfolder, 'Main', reverttorev+'.yaml')
        revertframe = Frame.loadRefFramefromYaml(refframefullpath=framefn, containerworkingfolder = self.containerworkingfolder)
        for fileheader, filetrack in revertframe.filestrack.items():
            revertframe.getfile(filetrack, self.containerworkingfolder)

    def compareToRefFrame(self, refframefullpath, filestomonitor, changes):
        alterfiletracks=[]
        if NEWFRAMEFN == os.path.basename(refframefullpath):
            return {'NewContainer':{'reason': 'NewContainer'}},[]  ### this might not be final as alternating input files can bring in new difficulties
        refframe = Frame.loadRefFramefromYaml(refframefullpath,self.containerworkingfolder)
        refframefileheaders = list(refframe.filestrack.keys())
        for fileheader in filestomonitor.keys():
            if fileheader not in refframe.filestrack.keys() and fileheader not in self.filestrack.keys():
                # check if fileheader is in neither refframe or current frame,
                raise('somehow Container needs to track ' + fileheader + 'but its not in ref frame or current frame')

            if fileheader not in refframe.filestrack.keys() and fileheader in self.filestrack.keys():
                # check if fileheader is in the refframe, If not in frame, that means user just added a new fileheader
                changes[fileheader]= {'reason': [changenewfile]}
                continue
            refframefileheaders.remove(fileheader)
            filename = os.path.join(self.containerworkingfolder, self.filestrack[fileheader].ctnrootpath, self.filestrack[fileheader].file_name)
            fileb = open(filename, 'rb')
            self.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            # calculate md5 of file, if md5 has changed, update md5

            if refframe.filestrack[fileheader].md5 != self.filestrack[fileheader].md5:
                self.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                changes[fileheader] = {'reason': [changemd5]}
                if self.filestrack[fileheader].connection:
                    if self.filestrack[fileheader].connection.connectionType==ConnectionTypes.Input:
                        alterfiletracks.append(self.filestrack[fileheader])
                    # if file has been updated, update last edited
                    self.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                    continue
            elif self.filestrack[fileheader].lastEdited != refframe.filestrack[fileheader].lastEdited:
                changes[fileheader] = {'reason': [changedate]}
                self.filestrack[fileheader].lastEdited = os.path.getmtime(filename)
                print('Date changed without Md5 changing')
                continue

        for removedheaders in refframefileheaders:
            changes[removedheaders] = {'reason': [changeremoved]}
        return changes, alterfiletracks

    def downloadInputFile(self, fileheader, workingdir):
        response = requests.get(BASE + 'FILES',
                                data={'md5': self.filestrack[fileheader].md5,
                                      'file_name': self.filestrack[fileheader].file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join(workingdir,self.filestrack[fileheader].ctnrootpath, response.headers['file_name'])
        self.progress = downloadProgressBar(response.headers['file_name'])
        dataDownloaded = 0
        self.progress.updateProgress(dataDownloaded)
        with open(fn, 'wb') as f:
            for data in response.iter_content(1024):
                dataDownloaded += len(data)
                f.write(data)
                percentDone = 100 * dataDownloaded/len(response.content)
                self.progress.updateProgress(percentDone)
                QGuiApplication.processEvents()


        # saves the content into file.
        os.utime(fn, (self.filestrack[fileheader].lastEdited, self.filestrack[fileheader].lastEdited))
        return fn,self.filestrack[fileheader]
