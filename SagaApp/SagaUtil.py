import os
import re
import warnings
from Config import BASE,TEMPCONTAINERFN, TEMPFRAMEFN, NEWCONTAINERFN, NEWFRAMEFN


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


def FrameNumInBranch(path, revnum):
    # add comment
    if revnum:
        if os.path.exists(os.path.join(path, "Rev"+ str(revnum) + ".yaml")):
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            warnings.warn("Rev " + str(revnum) + " doesn't exist in " + path , Warning)
            latestrev, revnum = latestFrameInBranch(path)
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    else:
        # if revnum is None, that means that they are looking for the latest greatest.
        # Before first Commit, this should return NEWFRAMEFN
        # After first Commit, this should either be latest Rev or TEMPFRAMEFN
        ##
        latestrev, revnum = latestFrameInBranch(path)

        # if os.path.exists(os.path.join(path, TEMPFRAMEFN)):
        #     return os.path.join(path, TEMPFRAMEFN), revnum
        if latestrev=='':
            if os.path.exists(os.path.join(path, NEWFRAMEFN)):
                return os.path.join(path, NEWFRAMEFN), 0
            warnings.warn("Can't find frame in Container", Warning)
        return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum

