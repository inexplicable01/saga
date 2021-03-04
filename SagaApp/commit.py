from SagaApp.FrameStruct import Frame
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import copy
import hashlib
import os
import yaml


from datetime import datetime

def commit(curframe : Frame,largestRev):
    committed = False

    client = MongoClient()
    db = client.SagaDataBase
    framedb = client.framedb
    fs = gridfs.GridFS(db)
    framefs = gridfs.GridFS(framedb)


    frameYamlfileb = framefs.get(file_id=ObjectId(curframe.FrameInstanceId))
    with open('temp.yaml', 'wb') as wfile:
        wfile.write(frameYamlfileb.read())
    with open('temp.yaml') as file:
        frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
    frameRef = Frame(frameRefYaml)

    for ContainerObjName, filetrackobj in curframe.filestrack.items():
        fileb = open(os.path.join(filetrackobj.localFilePath, filetrackobj.file_name), 'rb')
        # Should file be committed?
        commit_file, md5 =  CheckCommit(filetrackobj,fileb,frameRef)    # a function with filetrackobj and look for it in reference SagaApp Instance.
        if commit_file:
            # new file needs to be committed as the new local file is not the same as previous md5
            storageinfo = fs.put(fileb,
                                 ContainerObjName=filetrackobj.ContainerObjName ,
                                 file_name=filetrackobj.file_name,
                                 localFilePath=filetrackobj.localFilePath,
                                 lastEdited=filetrackobj.lastEdited
                                 )
            committed=True
            filetrackobj.md5= md5
            filetrackobj.db_id = storageinfo.__str__()
            filetrackobj.commitUTCdatetime= datetime.timestamp(datetime.utcnow())

   ###End For Loop

    if committed:
        print('Something was updated.')
        newframe = copy.deepcopy(curframe)
        newframeId = ObjectId()
        newframe.FrameInstanceId =newframeId.__str__()# save newframe, write new frame generate new id for new frame
        nextYamlfn = "ExampleMiddleFrameRev" + str(largestRev + 1) + ".yaml"
        nextYaml = open(nextYamlfn, 'w')
        newframe.writeoutFrameYaml(nextYaml)
        frameYamlfileb = open(nextYamlfn, 'rb')
        framefs.put(frameYamlfileb,_id=newframeId, yamlfile=nextYamlfn)
    ### save same yaml in a different database?
        return newframe, committed
    else:
        return curframe, committed
        # grab a bunch of files where md5 is changed



