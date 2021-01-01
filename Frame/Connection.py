from enum import Enum,auto
import json

class ConnectionTypes(Enum):
    Input=auto()
    Output=auto()

class FileConnection:
    def __init__(self, ContainerId,connectionType,branch='Main',Rev = None):
        self.refContainerId=ContainerId
        self.connectionType=connectionType
        self.branch=branch
        self.Rev=Rev

    @classmethod
    def create_valid_connection(cls, ContainerId,connectionType:ConnectionTypes,branch='Main',Rev = None):
        if connectionType is None:
            return None
        else:
            return cls(ContainerId,connectionType,branch,Rev)

    def dictify(self):
        dictout = {}
        for key, value in vars(self).items():
            dictout[key] = value
        # print(json.dumps(dictout))
        return dictout

    def __repr__(self):
        str=''
        # print('FileHeader:   '+ self.FileHeader)
        str +='\n\t\tFileConnection:  ' + self.refContainerId + '\n'
        str += '\t\tconnectionType:   ' + self.connectionType + '\n'
        str += '\t\tbranch:   ' + self.branch + '\n'
        str += '\t\tRev:   ' + self.Rev + '\n'
        return str
