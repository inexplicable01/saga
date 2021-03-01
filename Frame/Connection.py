from enum import Enum,auto
import json

class ConnectionTypes(Enum):
    Input=auto()
    Output=auto()



class FileConnection:
    def __init__(self, ContainerId,connectionType,branch='Main',Rev = None):
        self.refContainerId=ContainerId
        if connectionType=='Input' or connectionType == ConnectionTypes.Input:
            self.connectionType = ConnectionTypes.Input
        elif connectionType=='Output' or connectionType == ConnectionTypes.Output:
            self.connectionType = ConnectionTypes.Output
        else:
            raise('connection type screwed up')
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
            if key=='connectionType':
                if value:
                    dictout[key] = value.name
                else:
                    dictout[key] = None
            else:
                dictout[key] = value
        # print(json.dumps(dictout))
        return dictout

    def __repr__(self):
        str=''
        # print('FileHeader:   '+ self.FileHeader)
        str +='\n\t\tFileConnection:  ' + self.refContainerId + '\n'
        str += '\t\tconnectionType:   ' + self.connectionType.name + '\n'
        str += '\t\tbranch:   ' + self.branch + '\n'
        if self.Rev:
            str += '\t\tRev:   ' + self.Rev + '\n'
        else:
            str += '\t\tRev:   Missing \n'
        return str
