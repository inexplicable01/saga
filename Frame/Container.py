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

from datetime import datetime

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']
Rev = 'Rev'

class Container:
    def __init__(self, containerfn):
        self.containerworkingfolder= os.path.dirname(containerfn)
        with open(containerfn) as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        self.containerfn = containerfn
        self.containerName = containeryaml['containerName']
        self.containerId = containeryaml['containerId']
        self.inputObjs = containeryaml['inputObjs']
        self.outputObjs = containeryaml['outputObjs']
        self.requiredObjs = containeryaml['requiredObjs']
        self.references = containeryaml['references']
        self.yamlTracking = containeryaml['yamlTracking']

        self.filestomonitor =[]
        for typeindex, fileobjtype in enumerate(fileobjtypes):
            # print(typeindex, fileobjtype)
            for fileindex, fileObj in enumerate(getattr(self, fileobjtype)):
                self.filestomonitor.append(fileObj['ContainerObjName'])
        # print(self.yamlTracking['currentbranch'] + Rev  + str(self.yamlTracking['rev']) +".yaml")
        self.refframe = os.path.join(self.containerworkingfolder,self.yamlTracking['currentbranch'] + Rev + str(self.yamlTracking['rev']) +".yaml")

    def commit(self,cframe : Frame, commitmsg):
        committed = False
        client = MongoClient()
        db = client.SagaDataBase
        framedb = client.framedb
        fs = gridfs.GridFS(db)
        framefs = gridfs.GridFS(framedb)
        # print('here')
        # # frameYamlfileb = framefs.get(file_id=ObjectId(curframe.FrameInstanceId))
        with open(self.refframe) as file:
            frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
        frameRef = Frame(frameRefYaml,self.containerworkingfolder)

        # allowCommit, changes = self.Container.checkFrame(cframe)
        print(frameRef.FrameName)
        for ContainerObjName, filetrackobj in cframe.filestrack.items():
            fileb = open(os.path.join(self.containerworkingfolder, filetrackobj.file_name), 'rb')
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrackobj, fileb,frameRef)
            committime = datetime.timestamp(datetime.utcnow())
            if commit_file:
                # new file needs to be committed as the new local file is not the same as previous md5
                storageinfo = fs.put(fileb,
                                     ContainerObjName=filetrackobj.ContainerObjName,
                                     file_name=filetrackobj.file_name,
                                     localFilePath=self.containerworkingfolder,
                                     lastEdited=filetrackobj.lastEdited
                                     )
                committed = True
                filetrackobj.md5 = md5
                filetrackobj.db_id = storageinfo.__str__()
                filetrackobj.lastEdited = os.path.getmtime(os.path.join(self.containerworkingfolder, filetrackobj.file_name))
                filetrackobj.commitUTCdatetime = committime

        if committed:
            print('Something washhh updated.')

            # Updating new frame information
            newframe = copy.deepcopy(cframe)
            newframeId = ObjectId()
            newframe.FrameInstanceId = newframeId.__str__()  # save newframe, write new frame generate new id for new frame
            self.yamlTracking['rev'] = self.yamlTracking['rev'] +1
            newrevname = self.yamlTracking['currentbranch'] + Rev + str(self.yamlTracking['rev'])
            newframe.FrameName = newrevname
            newframe.commitMessage =commitmsg
            newframe.commitUTCdatetime = committime

            # Write out new frame information
            newframefullpath = os.path.join(self.containerworkingfolder,newrevname +".yaml")
            newframe.writeoutFrameYaml(newframefullpath)
            # The frame file is saved to the frame FS
            frameYamlfileb = open(newframefullpath, 'rb')
            framefs.put(frameYamlfileb, _id=newframeId, yamlfile=newrevname +".yaml")
            self.refframe = newframefullpath
            return newframe, committed
        else:
            return cframe, committed

    def CheckCommit(self,filetrackobj, fileb, frameRef):
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
        ref = Frame(fyaml,self.containerworkingfolder)
        print('ref',ref.FrameName)
        changes = cframe.compareToAnotherFrame(ref, self.filestomonitor)
        # print(len(changes))
        if len(changes)>0:
            allowCommit = True
        return allowCommit, changes

    def commithistory(self):
        historyStr=''
        # glob.glob()
        yamllist = glob.glob(self.containerworkingfolder + '/' + self.yamlTracking['currentbranch'] + '*.yaml')
        for yamlfn in yamllist:
            # print(yamlfn)
            with open(yamlfn) as file:
                pastYaml = yaml.load(file, Loader=yaml.FullLoader)
            # print(pastYaml)
            pastframe = Frame(pastYaml, self.containerworkingfolder)
            # print(pastframe.commitMessage)
            historyStr= historyStr +  pastframe.FrameName  + '\t' + pastframe.commitMessage+'\t\t\t\t' + \
                        time.ctime(pastframe.commitUTCdatetime)+'\t\n'
        return historyStr

    def printDelta(self, changes):
        framestr=''
        for change in changes:
            framestr=framestr+change['ContainerObjName'] + '     ' + change['reason'] +'\n'
        return framestr

    def save(self):
        dictout = {}
        outyaml = open(os.path.join(self.containerworkingfolder, self.containerfn),'w')
        keytosave = ['containerName','containerId','outputObjs','inputObjs','requiredObjs','references','yamlTracking']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        yaml.dump(dictout, outyaml)
        outyaml.close()