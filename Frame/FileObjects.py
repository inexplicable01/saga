import hashlib
import os

class FileTrackObj:
    def __init__(self, ContainerObjName, localfilepath, file_name,style=None,lastEdited=None, md5=None,file_id=None,commitUTCdatetime=None):
        self.ContainerObjName = ContainerObjName
        self.file_name = file_name
        if  md5 is None:
            fullpath = os.path.join(localfilepath, file_name)
            fileb = open(fullpath , 'rb')
            md5hash = hashlib.md5(fileb.read())
            md5=md5hash.hexdigest()
        self.lastEdited= lastEdited#
        self.md5 = md5
        self.style = style
        self.file_id = file_id
        self.commitUTCdatetime = commitUTCdatetime

    def yamlify(self):
        dictout = {}
        for key, value in vars(self).items():
            dictout[key] = value
        return dictout

    def printdetails(self):
        print(self.md5)

class InputFileObj(FileTrackObj):
    def __init__(self, ContainerObjName, file_name,localFilePath,style,fromContainerId,md5=None,file_id=None,commitUTCdatetime=None):
        super().__init__(self, ContainerObjName, file_name,localFilePath,style,md5,file_id,commitUTCdatetime)
        self.fromContainerId=fromContainerId

class OutFileObj(FileTrackObj):
    def __init__(self, ContainerObjName, file_name,localFilePath,style,toContainerID,md5=None,file_id=None,commitUTCdatetime=None):
        super().__init__(self, ContainerObjName, file_name,localFilePath,style,md5,file_id,commitUTCdatetime)
        self.toContainerID=toContainerID