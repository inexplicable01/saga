from Frame.FrameStruct import Frame as fr
import os
import filecmp

class StageFrame:
    def __init__(self, frame: fr):
        self.Frame = frame

    def ExamineStatus(self):
        for filestocheck in self.Frame.filestrack:
            if os.path.isfile(filestocheck['file_name']):
                print(filestocheck['file_name'] + 'exists')
                # print(filecmp.cmp(filestocheck['file_name'], filestocheck['db_id'], shallow=False))
                print(os.stat(filestocheck['file_name'])[8])
                print(os.stat(filestocheck['db_id'])[8])
           # filestocheck['file_name']





