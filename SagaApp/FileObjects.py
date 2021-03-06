import hashlib
import os
import json
from datetime import datetime
from SagaApp.Connection import FileConnection

class FileTrack:
    def __init__(self, FileHeader, localfilepath, \
                 file_name, connection:FileConnection=None, style=None, lastEdited=None, committedby='waichak', \
                 md5=None, file_id=None, commitUTCdatetime=None,persist: bool = True
                 ):
        self.FileHeader = FileHeader
        self.file_name = file_name
        if md5 is None:
            fileb = open(os.path.join(localfilepath, file_name) , 'rb')
            md5=hashlib.md5(fileb.read()).hexdigest()
        self.lastEdited= os.path.getmtime(os.path.join(localfilepath, file_name)) if lastEdited is None else lastEdited
        self.committedby = committedby
        self.md5 = md5
        self.style = style
        self.file_id = file_id
        self.commitUTCdatetime = commitUTCdatetime
        self.connection=connection
        self.persist=persist

    def dictify(self):
        ###Should__dict__be used instead?
        dictout = {}
        for key, value in vars(self).items():
            if key=='connection':
                if value:
                    dictout[key] = value.dictify()
                else:
                    dictout[key] = None
            else:
                dictout[key] = value
        return dictout

    def printdetails(self):
        print(self.md5)

    def __repr__(self):
        str=''
        # print('FileHeader:   '+ self.FileHeader)
        str +='\nFileHeader:   '+ self.FileHeader + '\n'
        str += 'file_name:   ' + self.file_name + '\n'
        str += 'md5:   ' + self.md5 + '\n'
        if self.lastEdited:
            str += 'lastEdited:   ' + datetime.fromtimestamp(self.lastEdited).isoformat()+ '\n'
        str += 'committedby:   ' + self.committedby+ '\n'
        if self.style:
            str += 'style:   ' + self.style+ '\n'
        str += 'file_id:   ' + self.file_id+ '\n'
        if self.commitUTCdatetime:
            str += 'commitUTCdatetime:   ' + datetime.fromtimestamp(self.commitUTCdatetime).isoformat()+ '\n'
        str += 'connection:     ' + self.connection.__repr__() + '\n'
        return str
