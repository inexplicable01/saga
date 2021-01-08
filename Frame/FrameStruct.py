import hashlib
import os
import requests
from Config import BASE
import yaml
from Frame.FileObjects import FileTrack
from Frame.Connection import FileConnection, ConnectionTypes
import time
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import requests
from Config import BASE

blankFrame = {'parentContainerId':"",'FrameName': "", 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}


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
        self.parentContainerId = FrameYaml['parentContainerId']
        self.FrameName = FrameYaml['FrameName']
        # self.description = FrameYaml['Description']
        self.FrameInstanceId = FrameYaml['FrameInstanceId']
        self.commitMessage = FrameYaml['commitMessage']
        self.filestomonitor = filestomonitor
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
            # cont= Container(os.path.join('Container/',self.parentContainerId, 'containerstate.yaml'))
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

        refframe = Frame(self.refframefn, self.filestomonitor ,self.localfilepath )
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
        revertframe = Frame(framefn, self.filestomonitor, self.localfilepath)
        for fileheader, filetrack in revertframe.filestrack.items():
            revertframe.getfile(filetrack.file_id, filetrack.file_name, self.localfilepath, filetrack.lastEdited)

    def compareToRefFrame(self):
        alterfiletracks=[]
        refframe = Frame(self.refframefn, self.filestomonitor, self.localfilepath)
        changes = []
        for fileheader in self.filestomonitor.keys():
            ##  Is fileheader in Frame, , if yes
            # if fileheader not in refframe.filestrack.keys():
            #     # if no, go find file
            #     print(self.filestrack.keys(),fileheader)
            #     path = QFileDialog.getOpenFileName(self, "Open")[0]
            #     if path:
            #         self.cframe.add_fileTrack(path, fileheader, 'Style')
            #         continue
            ## Does the file exist?
            # print('self.localfilepath', self.localfilepath)
            path = self.localfilepath + '/' + self.filestrack[fileheader].file_name
            # if not os.path.exists(path):
            #     # if not, go find a new file to track
            #     path = QFileDialog.getOpenFileName(self, "Open")[0]
            #     if path:
            #         self.cframe.add_fileTrack(path, fileheader, 'Style')
            #         # reassign key contrainobj with new fileobj
            #         continue
            fileb = open(path, 'rb')
            self.filestrack[fileheader].md5 = hashlib.md5(fileb.read()).hexdigest()
            # calculate md5 of file, if md5 has changed, update md5
            if refframe.filestrack[fileheader].md5 != self.filestrack[fileheader].md5:
                self.filestrack[fileheader].lastEdited = os.path.getmtime(path)
                changes.append({'fileheader': fileheader, 'reason': 'MD5 Changed'})
                if self.filestrack[fileheader].connection.connectionType==ConnectionTypes.Input:
                    alterfiletracks.append(self.filestrack[fileheader])
                continue
            # if file has been updated, update last edited
            self.filestrack[fileheader].lastEdited = os.path.getmtime(path)

            if self.filestrack[fileheader].lastEdited != refframe.filestrack[fileheader].lastEdited:
                changes.append({'fileheader': fileheader, 'reason': 'DateChangeOnly'})
                self.filestrack[fileheader].lastEdited = os.path.getmtime(path)
                print('Date changed without Md5 changin')
                continue
        return changes, alterfiletracks



    def downloadFrame(self,authToken, containerId, branch='Main' ):
        payload = {'containerID': containerId,
                   'branch': branch}
        files = [
        ]
        headers = {
            'Authorization': 'Bearer ' + authToken['auth_token']
        }
        response = requests.get(BASE + 'FRAMES', headers=headers, data=payload, files=files)
        # request to FRAMES to get the latest frame from the branch as specified in currentbranch
        branch = response.headers['branch']
        # response also returned the name of the branch
        if not os.path.exists(os.path.join(containerId, branch)):
            if not os.path.exists(containerId):
                os.mkdir(containerId)
            os.mkdir(os.path.join(containerId, branch))  ## make folder if folder doesn't exist
        frameyamlDL = os.path.join(containerId, branch, response.headers['file_name'])
        open(frameyamlDL, 'wb').write(response.content)
        # with open(frameyamlDL, 'r') as file:
        #     FrameYaml = yaml.load(file, Loader=yaml.FullLoader)
        return frameyamlDL
        ## write return binary file as the frame yaml file
