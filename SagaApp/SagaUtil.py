import os
import re
import warnings
from Config import BASE,TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN
import requests
import json
import ctypes
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_NORMAL = 0x80


def makefilehidden(entitypath):
    ret = ctypes.windll.kernel32.SetFileAttributesW(entitypath,
                                                    FILE_ATTRIBUTE_HIDDEN)
    if not ret:
        warnings.warn(entitypath+ 'attribute unable to set to Hidden')
        warnings.warn(ctypes.WinError())

def unhidefile(entitypath):
    ret = ctypes.windll.kernel32.SetFileAttributesW(entitypath,
                                                    FILE_ATTRIBUTE_NORMAL)
    if not ret:
        warnings.warn(entitypath+ 'attribute unable to set to Hidden')
        warnings.warn(ctypes.WinError())


def latestFrameInBranch(path):
    # add comment
    revnum = 0;
    latestrev= ''
    try:
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml', fn)
            if m:
                if int(m.group(1)) > revnum:
                    revnum = int(m.group(1))
                    latestrev = fn
        return latestrev, revnum
    except:
        return latestrev, revnum




def getFramePathbyRevnum(path, revnum):
    # function is to return frame yaml full path if it exists.  If it doesn't exist search for the latest rev
    # if the latest rev doesn't exist, shoot warning.'
    if os.path.exists(os.path.join(path, 'Rev' + str(revnum) + ".yaml")):
        # Container and Frames default revnum to None above should evaluate to RevNone.yaml most of the time.
        # if revnum is a numeric string and that yaml exists, return filepath
        return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    else:
        # Code should come here most of the time /
        latestrev, revnum = latestFrameInBranch(path)
        if revnum==0:
            warnings.warn("Cannot find reasonable Rev/Frame in " + path, Warning)
            return latestrev, revnum
        else:
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    # else:
    #     # if revnum is None, that means that they are looking for the latest greatest.
    #     # Before first Commit, this should return NEWFRAMEFN
    #     # After first Commit, this should either be latest Rev or TEMPFRAMEFN
    #
    #     # if os.path.exists(os.path.join(path, TEMPFRAMEFN)):
    #     #     return os.path.join(path, TEMPFRAMEFN), revnum
    #     if latestrev=='':
    #         if os.path.exists(os.path.join(path, NEWFRAMEFN)):
    #             return os.path.join(path, NEWFRAMEFN), 0
    #         warnings.warn("Can't find frame in Container", Warning)
    #     return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum



def ensureFolderExist(fn):
    if os.path.exists(fn):
        return
    else:
        dir, file = os.path.split(fn)
        ensureFolderExist(dir)
        if not os.path.exists(dir):
            os.mkdir(dir)



