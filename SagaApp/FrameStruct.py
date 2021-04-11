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
from Config import BASE,changenewfile, changemd5,changedate , changeremoved

blankFrame = {'parentcontainerid':"",'FrameName': "", 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}


class Frame:
    def __init__(self, framefn = None, filestomonitor = None,localfilepath = 'Default'):
        if framefn == None:
            FrameYaml = blankFrame
            localfilepath = 'newFrames/' #generalize this file path
        else:
            with open(framefn,'r') as file:
                FrameYaml = yaml.load(file, Loader=yaml.FullLoader)
        # self.containerworkingfolder = os.path.dirname(containerfn)
        self.refframefn = framefn
        self.parentcontainerid = FrameYaml['parentcontainerid']
        self.FrameName = FrameYaml['FrameName']
        # self.description = FrameYaml['Description']
        self.FrameInstanceId = FrameYaml['FrameInstanceId']
        self.commitMessage = FrameYaml['commitMessage']
        # self.filestomonitor = filestomonitor
        self.inlinks = FrameYaml['inlinks']
        self.outlinks = FrameYaml['outlinks']
        self.AttachedFiles = FrameYaml['AttachedFiles']
        try:
            self.commitUTCdatetime = FrameYaml['commitUTCdatetime']
        except:
            self.commitUTCdatetime = 1587625655.939034
        # self.inoutcheck()
        self.localfilepath=localfilepath
        self.filestrack = {}
        for ftrack in FrameYaml['filestrack']:
            FileHeader = ftrack['FileHeader']
            # cont= Container(os.path.join('Container/',self.parentcontainerid, 'containerstate.yaml'))
            conn=None
            if 'connection' in ftrack.keys() and ftrack['connection']:
                conn = FileConnection(ftrack['connection']['refContainerId'],
                    connectionType=ftrack['connection']['connectionType'],
                                         branch=ftrack['connection']['branch'],
                                         Rev=ftrack['connection']['Rev'])

            self.filestrack[FileHeader] = FileTrack(FileHeader=ftrack['FileHeader'],
                                                     file_name=ftrack['file_name'],
                                                     localfilepath=self.localfilepath,
                                                     md5=ftrack['md5'],
                                                     style=ftrack['style'],
                                                     file_id=ftrack['file_id'],
                                                     commitUTCdatetime=ftrack['commitUTCdatetime'],
                                                     lastEdited=ftrack['lastEdited'],
                                                     connection=conn)

    def add_fileTrack(self, filepath,FileHeader):

        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        # print('md5',md5)
        fileobj = FileTrack(FileHeader=FileHeader,
                            localfilepath=os.path.dirname(filepath),
                            file_name=os.path.basename(filepath),
                            md5=md5,


                            )

        self.filestrack[FileHeader]=fileobj

    def add_inlinks(self, inlinks):
        self.inlinks.append(inlinks)

    def add_outlinks(self, outlinks):
        self.outlinks.append(outlinks)

    def add_AttachedFiles(self, AttachedFiles):
        self.AttachedFiles.append(AttachedFiles)

    def add_misc(self, misc):
        self.misc.append(misc)

    def filestoCheck(self):
        filestocheck = []
        for filetrackobj in self.filestrack:
            filestocheck.append(filetrackobj['file_name'])
        return filestocheck

    def dealwithalteredInput(self, alterinputfileinfo):
        # self.filestrack[]
        # add new file track, determine whether its just this next rev or keep check in the future persist
        # rename altered input file names
        # re get the file from server
        filetrack = alterinputfileinfo['alterfiletrack']
        fileheader = filetrack.FileHeader

        refframe = Frame(self.refframefn, None,self.localfilepath )
        reffiletrack = refframe.filestrack[fileheader]
        ## File Management
        os.rename(os.path.join(self.localfilepath,filetrack.file_name), os.path.join(self.localfilepath,alterinputfileinfo['nfilename']))
        self.getfile(reffiletrack.file_id, reffiletrack.file_name, self.localfilepath, reffiletrack.lastEdited)
        ## Update FileTrack
        self.filestrack[alterinputfileinfo['nfileheader']]=FileTrack(
            FileHeader=alterinputfileinfo['nfileheader'],
            localfilepath=self.localfilepath,
            file_name=alterinputfileinfo['nfilename'],
            style='ref',
            persist= alterinputfileinfo['persist'],
        )
        # print('lots of work to be done.')

    def downloadfullframefiles(self):
        for fileheader, filetrack in self.filestrack.items():
            # print(filetrack.file_name,self.localfilepath)
            self.getfile(filetrack.file_id,filetrack.file_name,self.localfilepath,filetrack.lastEdited )

    def getfile(self, file_id, file_name, filepath, lastEdited):
        response = requests.get(BASE + 'FILES',
                                data={'file_id': file_id, 'file_name': file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join(filepath, response.headers['file_name'])
        open(fn, 'wb').write(response.content)
        # saves the content into file.
        os.utime(fn, (lastEdited, lastEdited))


    def addFileTotrack(self, fullpath, FileHeader, style):
        [path, file_name] = os.path.split(fullpath)
        if os.path.exists(fullpath):
            newfiletrackobj = FileTrack(file_name=file_name,
                                        FileHeader=FileHeader,
                                        # localfilepath=self.localfilepath,
                                        localfilepath=path,
                                        style=style,
                                        lastEdited=os.path.getmtime(fullpath))
            self.filestrack[FileHeader] = newfiletrackobj
        else:
            raise(fullpath + ' does not exist')

    def addOutputFileTotrack(self, fileinfo, style):
        branch = 'Main'
        fullpath = fileinfo['FilePath']
        [path, file_name] = os.path.split(fullpath)
        conn = FileConnection([],
                              connectionType=ConnectionTypes.Output,
                              branch=branch)
        if os.path.exists(fileinfo['FilePath']):
            newfiletrackobj = FileTrack(file_name=file_name,
                                        FileHeader=fileinfo['fileheader'],
                                        # localfilepath=self.localfilepath,
                                        localfilepath=path,
                                        style=style,
                                        connection=conn,
                                        lastEdited=os.path.getmtime(fullpath))
            self.filestrack[fileinfo['fileheader']] = newfiletrackobj
        else:
            raise(fullpath + ' does not exist')



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
                                        file_id=reffiletrack.file_id,
                                        commitUTCdatetime=reffiletrack.commitUTCdatetime,
                                        connection=conn,
                                        localfilepath=path,
                                        lastEdited=os.path.getmtime(fullpath))


            self.filestrack[fileheader] = newfiletrackobj
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

    def writeoutFrameYaml(self, yamlfn):
        with open(yamlfn, 'w') as outyaml:
            yaml.dump(self.dictify(), outyaml)

    def __repr__(self):
        return json.dumps(self.dictify())

    def revertTo(self, reverttirev):
        framefn = os.path.join(self.localfilepath, 'Main', reverttirev+'.yaml')
        revertframe = Frame(framefn, None, self.localfilepath)
        for fileheader, filetrack in revertframe.filestrack.items():
            revertframe.getfile(filetrack.file_id, filetrack.file_name, self.localfilepath, filetrack.lastEdited)

    def compareToRefFrame(self, filestomonitor):
        alterfiletracks=[]
        refframe = Frame(self.refframefn, None, self.localfilepath)
        changes = {}
        refframefileheaders = list(refframe.filestrack.keys())
        for fileheader in filestomonitor.keys():
            if fileheader not in refframe.filestrack.keys() and fileheader not in self.filestrack.keys():
                # check if fileheader is in neither refframe or current frame,
                raise('somehow Container needs to track ' + fileheader + 'but its not in ref frame or current frame')

            if fileheader not in refframe.filestrack.keys() and fileheader in self.filestrack.keys():
                # check if fileheader is in the refframe, If not in frame, that means user just added a new fileheader
                changes[fileheader]= {'reason': changenewfile}
                continue
            refframefileheaders.remove(fileheader)
            path = self.localfilepath + '/' + self.filestrack[fileheader].file_name
            fileb = open(path, 'rb')
            self.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            # calculate md5 of file, if md5 has changed, update md5

            if refframe.filestrack[fileheader].md5 != self.filestrack[fileheader].md5:
                self.filestrack[fileheader].lastEdited = os.path.getmtime(path)
                changes[fileheader]= {'reason': changemd5}
                if self.filestrack[fileheader].connection:
                    if self.filestrack[fileheader].connection.connectionType==ConnectionTypes.Input:
                        alterfiletracks.append(self.filestrack[fileheader])
                    continue
            # if file has been updated, update last edited
            self.filestrack[fileheader].lastEdited = os.path.getmtime(path)

            if self.filestrack[fileheader].lastEdited != refframe.filestrack[fileheader].lastEdited:
                changes[fileheader] = {'reason': changedate}
                self.filestrack[fileheader].lastEdited = os.path.getmtime(path)
                print('Date changed without Md5 changin')
                continue
        for removedheaders in refframefileheaders:
            changes[removedheaders] = {'reason': changeremoved}
        return changes, alterfiletracks




    def downloadInputFile(self, fileheader, workingdir):
        response = requests.get(BASE + 'FILES',
                                data={'file_id': self.filestrack[fileheader].file_id,
                                      'file_name': self.filestrack[fileheader].file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        fn = os.path.join(workingdir, response.headers['file_name'])
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
