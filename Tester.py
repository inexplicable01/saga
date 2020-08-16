###load frame

from Delta.CompareFrames import StageFrame
from Frame.FrameStruct import Frame, FileTrackObj
from Frame.commit import commit

import hashlib

# blah = Frame
import yaml
import re
import os
import glob


dr = glob.glob('*.yaml')
largestRev=2
for filename in dr:
    revnum = re.findall('Rev(\d+)', filename)
    if revnum:
        if int(revnum[0])>largestRev:
            largestRev=int(revnum[0])
fullpath="C:/Users/waich/PycharmProjects/Saga/ExampleDIR/GroupC/LongVideo.mp4"
file_frame_name= 'VideoOutput'
style='OutputFile'

with open("ExampleMiddleFrameRev"+ str(largestRev)+ ".yaml") as file:
    examFrameYaml = yaml.load(file, Loader=yaml.FullLoader)
examFrame = Frame(examFrameYaml)

# examFrame.addFileTotrack(fullpath,file_frame_name, style)

# staging = StageFrame(examFrame)
# staging.ExamineStatus()

newFrame, committed = commit(examFrame,largestRev)

if committed:
    print('soemthing was committed')
# print(newFrame.filestrack)

# path=b"C:\Users\waich\LocalGitProjects\jetbrains-webcast-build-with-mongodb\src\yougotthis.mp4"
# bpath = hashlib.md5()
# binaryfile = open('C:/Users/waich/LocalGitProjects/jetbrains-webcast-build-with-mongodb/src/yougotthis.mp4','rb')
# result = hashlib.md5(path)
#
# print(result.hexdigest())
#
# result2 = hashlib.md5(binaryfile.read())
#
# print(result2.hexdigest())

