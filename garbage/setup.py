from Delta.CompareFrames import StageFrame
from Frame.FrameStruct import Frame, FileTrackObj, Container

from Frame.commit import commit

import hashlib
# blah = Frame
import yaml
import re
import os
import glob

def init_container(containeryaml):
    container = Container(containerName=containeryaml['containerName'],
                       containerId=containeryaml['containerId'],
                       inputObjs=containeryaml['inputObjs'],
                       outputObjs=containeryaml['outputObjs'],
                       requiredObjs=containeryaml['requiredObjs'],
                       references=containeryaml['references'],
                       mainBranch=containeryaml['mainBranch'],
                       yamlTracking=containeryaml['yamlTracking'])
    return container

with open("GroupA\GroupAContainer.yaml") as file:
    containeryaml = yaml.load(file, Loader=yaml.FullLoader)

groupAcontainer=init_container(containeryaml)

with open("GroupB\GroupBContainer.yaml") as file:
    containeryaml = yaml.load(file, Loader=yaml.FullLoader)

groupBcontainer=init_container(containeryaml)

with open("GroupC\GroupCContainer.yaml") as file:
    containeryaml = yaml.load(file, Loader=yaml.FullLoader)

groupCcontainer=init_container(containeryaml)

with open("GroupD\GroupDContainer.yaml") as file:
    containeryaml = yaml.load(file, Loader=yaml.FullLoader)

groupDcontainer=init_container(containeryaml)







