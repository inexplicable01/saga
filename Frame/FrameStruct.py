import hashlib
import os
import yaml
from Frame.FileObjects import FileTrackObj
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *




class Frame:
    def __init__(self, FrameYaml, localfilepath):

        self.parentContainerId = FrameYaml['parentContainerId']
        self.FrameName = FrameYaml['FrameName']
        self.FrameInstanceId = FrameYaml['FrameInstanceId']
        self.commitMessage = FrameYaml['commitMessage']

        self.inlinks = FrameYaml['inlinks']
        self.outlinks = FrameYaml['outlinks']
        self.AttachedFiles = FrameYaml['AttachedFiles']
        try:
            self.commitUTCdatetime = FrameYaml['commitUTCdatetime']
        except:
            self.commitUTCdatetime = 1587625655.939034
        # self.inoutcheck()
        self.localfilepath=localfilepath
        filestrack = {}
        for ftrack in FrameYaml['filestrack']:

            ContainerObjName = ftrack['ContainerObjName']
            print('ftrack',ftrack)
            filestrack[ContainerObjName] = FileTrackObj(ContainerObjName=ftrack['ContainerObjName'],
                                                       file_name=ftrack['file_name'],
                                                       localfilepath=self.localfilepath,
                                                       md5=ftrack['md5'],
                                                       style=ftrack['style'],
                                                       db_id=ftrack['db_id'],
                                                       commitUTCdatetime=ftrack['commitUTCdatetime'],
                                                       lastEdited=ftrack['lastEdited']
                                                       )
            # print(ftrack)
        self.filestrack = filestrack
        print('self.localfilepath',self.localfilepath)

    #        self.misc= misc

    def add_fileTrack(self, filepath,ContainerObjName):

        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        # print('md5',md5)
        fileobj = FileTrackObj(ContainerObjName=ContainerObjName,
                     file_name=os.path.basename(filepath),
                     )
        # print('fileobj', fileobj)
        self.filestrack[ContainerObjName]=fileobj

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


    def addFileTotrack(self, fullpath, ContainerObjName, style):
        [path, file_name] = os.path.split(fullpath)
        if os.path.exists(fullpath):
            newfiletrackobj = FileTrackObj(file_name=file_name,
                                           ContainerObjName=ContainerObjName,
                                           localfilepath=self.localfilepath,
                                           style=style,
                                           lastEdited=os.path.getmtime(fullpath) )

            self.filestrack[ContainerObjName] = newfiletrackobj
        else:
            raise(fullpath + ' does not exist')


    def writeoutFrameYaml(self, yamlfn):
        outyaml = open(yamlfn, 'w')
        dictout = {}
        for key, value in vars(self).items():
            if 'filestrack' == key:
                filestrack = []
                for ContainerObjName, filetrackobj in value.items():
                    filestrack.append(filetrackobj.yamlify())
                dictout[key] = filestrack
            else:
                dictout[key] = value

        yaml.dump(dictout, outyaml)
        outyaml.close()

    def compareToAnotherFrame(self, frame2,filestomonitor):
        changes = []
        # print(self.filestrack.keys())
        # print(frame2.filestrack.keys())
        for ContainerObjName in filestomonitor:
            if ContainerObjName not in self.filestrack.keys():
                changes.append({'ContainerObjName' :ContainerObjName, 'reason':'missing'})
                continue
            if self.filestrack[ContainerObjName].md5 != frame2.filestrack[ContainerObjName].md5:
                changes.append({'ContainerObjName' :ContainerObjName, 'reason':'MD5 Changed'})
                print('MD5 Changed')
                continue
            if self.filestrack[ContainerObjName].lastEdited != frame2.filestrack[ContainerObjName].lastEdited:
                changes.append({'ContainerObjName':ContainerObjName, 'reason':'DateChangeOnly'})
                print('Date changed without Md5 changin')
                continue
        return changes

    def updateFrame(self, filestomonitor):
        for ContainerObjName in filestomonitor:
            ##  Is ContainerObjName in Frame, , if yes
            ##
            if ContainerObjName not in self.filestrack.keys():
                # if no, go find file
                print(self.filestrack.keys(),ContainerObjName)
                path = QFileDialog.getOpenFileName(self, "Open")[0]
                if path:
                    self.cframe.add_fileTrack(path, ContainerObjName, 'Style')
                    continue
            ## Does the file exist?
            # print('self.localfilepath', self.localfilepath)
            path = self.localfilepath + '/' + self.filestrack[ContainerObjName].file_name
            if not os.path.exists(path):
                # if not, go find a new file to track
                path = QFileDialog.getOpenFileName(self, "Open")[0]
                if path:
                    self.cframe.add_fileTrack(path, ContainerObjName, 'Style')
                    # reassign key contrainobj with new fileobj
                    continue
            fileb = open(path, 'rb')
            md5hash = hashlib.md5(fileb.read())
            md5 = md5hash.hexdigest()
            # calculate md5 of file, if md5 has changed, update md5
            if md5 != self.filestrack[ContainerObjName].md5:
                self.filestrack[ContainerObjName].md5 = md5
                self.filestrack[ContainerObjName].lastEdited = os.path.getmtime(path)
            # if file has been updated, update last edited
            if os.path.getmtime(path) != self.filestrack[ContainerObjName].lastEdited:
                self.filestrack[ContainerObjName].lastEdited = os.path.getmtime(path)
