import json
from SagaCore.Container import Container,ContainerItem
from SagaCore import *
from SagaCore.Frame import Frame
from SagaCore.Track import FileTrack,FolderTrack, Track
# from SagaGuiModel.GuiModelConstants import

from os.path import join
import hashlib
import warnings


def prepareNewCommitCall(container:Container, commitmessage):
    container.workingFrame.commitMessage = commitmessage
    container.workingFrame.FrameName = 'Rev1'

    commitContainer = container.dictify()
    commitFrame = container.workingFrame.dictify()

    payload = {'containerdictjson': json.dumps(commitContainer), 'framedictjson': json.dumps(commitFrame)}
    updateinfo = {}
    filesToUpload = {}
    for citemid, citem in container.containeritems.items():
        if citem.containeritemrole in [roleOutput, roleRequired]:
            if type(citem.track)==FileTrack:
                filepath = join(container.containerworkingfolder, citem.track.ctnrootpath, citem.track.entity)
                filesToUpload[citem.track.md5] = open(filepath,'rb')
                updateinfo[citem.track.md5] = {
                    'track': ContainerItemType.Singlefile.name,
                    'filename': citem.track.entity,
                    'lastEdited': citem.track.lastEdited,
                    'md5': citem.track.md5,
                    'citemid':citem.containeritemid
                }
            elif type(citem.track)==FolderTrack:
                ## What is needed is a list of files that needs to be uploaded.
                newfilesinfolder = citem.prepareFolderTrackForCommit(containerworkingfolder=container.containerworkingfolder)
                for filepath in newfilesinfolder:
                    fileb = open(join(container.containerworkingfolder, filepath), 'rb')
                    md5 = hashlib.md5(fileb.read()).hexdigest()
                    filesToUpload[md5] = open(join(container.containerworkingfolder, filepath), 'rb')
                    updateinfo[md5] = {
                        'track': ContainerItemType.Folder.name,
                        'filepath': filepath,
                        'md5': md5,
                        'citemid': citem.containeritemid
                    }
    payload['updateinfo']  = json.dumps(updateinfo)
    return payload,  filesToUpload

def prepareCommitCall(container:Container):
         # = Frame.loadRefFramefromYaml(container.refframefullpath, container.containerworkingfolder)
    frameRef=container.refframe
    container.updateworkframe()
    filesToUpload = {}
    updateinfo = {}
    for containeritemid, citem in container.containeritems.items():
        if containeritemid not in container.containeritems.keys() or citem.containeritemrole not in [roleOutput,roleInput,roleRequired]:
            continue
        if container.containeritems[containeritemid].containeritemtype== roleInput:
            # the input updates are handles through the frame, no need to recommit it.  Or that the input update commit is handled in the framejson upload
            # the real trick is how to deal with altered inputs.
            # Dealing with input updates is gonna require a lot of thought.
            inputsupdated = True
        # filepath = join(container.containerworkingfolder,filetrack.ctnrootpath, filetrack.entity)
        # Should file be committed?
        # if containeritemid not in container.containeritems.keys():
        #     warnings.warn('We need to make sure all the tracked files are adequatedly traced', Warning)
        #     return
        if CheckCommit(container,citem, frameRef):
            # new file needs to be committed as the new local file is not the same as previous md5
            if type(citem.track)==FileTrack:
                filepath = join(container.containerworkingfolder, citem.track.ctnrootpath, citem.track.entity)
                filesToUpload[citem.track.md5] = open(filepath,'rb')
                updateinfo[citem.track.md5] = {
                    'track': ContainerItemType.Singlefile.name,
                    'filename': citem.track.entity,
                    'lastEdited': citem.track.lastEdited,
                    'md5': citem.track.md5,
                    'citemid':citem.containeritemid
                }
            elif type(citem.track)==FolderTrack:
                ## What is needed is a list of files that needs to be uploaded.
                newfilesinfolder = citem.prepareFolderTrackForCommit(containerworkingfolder=container.containerworkingfolder)
                for filepath in newfilesinfolder:
                    fileb = open(join(container.containerworkingfolder, filepath), 'rb')
                    md5 = hashlib.md5(fileb.read()).hexdigest()
                    filesToUpload[md5] = open(join(container.containerworkingfolder, filepath), 'rb')
                    updateinfo[md5] = {
                        'track': ContainerItemType.Folder.name,
                        'filepath': filepath,
                        'md5': md5,
                        'citemid': citem.containeritemid
                    }



    updateinfojson = json.dumps(updateinfo)
    containerdictjson = container.__repr__()
    framedictjson = container.workingFrame.__repr__()

    return containerdictjson,framedictjson, updateinfojson, filesToUpload



def CheckCommit(container:Container, citem:ContainerItem, frameRef):
    if citem.reftrack == None:
        return True  ## (this means that this was added precommit)
    if type(citem.track)==FileTrack:
        if citem.track.md5 != citem.reftrack.md5:
            return True  ## MD5 changed
    if type(citem.track)==FolderTrack:
        return citem.checkCItemFolderTrackAltered(containerworkingfolder=container.containerworkingfolder)
    return False
    # Make new Yaml file  some meta data sohould exit in Yaml file

def commithistorybyfile(container):
    changesbyfile = {}
    for citemid in container.refframe.filestrack.keys():
        changesbyfile[citemid] = []
    containerframes = {}
    # glob.glob() +'/'+ Rev + revnum + ".yaml"
    # yamllist = glob.glob(join(container.containerworkingfolder, container.currentbranch , 'Rev*.yaml'))
    for revyaml, pastframe in container.memoryframesdict.items():
        # pastframe = Frame.loadRefFramefromYaml(yamlframefn, container.containerworkingfolder)
        containerframes[pastframe.commitUTCdatetime] = pastframe
    for revi, timestamp in enumerate(sorted(containerframes)):
        pastframe = containerframes[timestamp]
        for fileheader in changesbyfile.keys():
            if fileheader not in pastframe.filestrack.keys():
                changesbyfile[fileheader].append({'rev': revi, 'md5': 'missing'})
                continue
            changesbyfile[fileheader].append({'rev': revi, 'md5': 'pastframe.filestrack[fileheader].md5'})

    return changesbyfile

    # @classmethod
    # def downloadFrame(cls,refpath,authtoken, containerId, BASE, branch='Main'):
    #     payload = {'containerID': containerId,
    #                'branch': branch}
    #     headers = {
    #         'Authorization': 'Bearer ' + authtoken
    #     }
    #     response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
    #     # print(response.headers)
    #     # print(response.content)
    #     # request to FRAMES to get the latest frame from the branch as specified in currentbranch
    #     branch = 'Main'
    #     # response also returned the name of the branch
    #     if not os.path.exists(join(refpath, containerId, branch)):
    #         os.mkdir(join(refpath, containerId,branch))
    #
    #     frameyamlDL = join(refpath,containerId, branch, response.headers['filename'])
    #     if os.path.exists(frameyamlDL):
    #         unhidefile(frameyamlDL)
    #     open(frameyamlDL, 'wb').write(response.content)
    #     makefilehidden(join(refpath, containerId, branch))
    #     return frameyamlDL
    # @classmethod
    # def downloadContainerInfo(cls, refpath, authtoken, BASE, containerId):
    #     headers = {'Authorization': 'Bearer ' + authtoken  }
    #     response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
    #     # response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
    #     # requests is a python object/class, that sends a http request
    #     # This returns a container Yaml File
    #     if not os.path.exists(refpath):
    #         os.mkdir(refpath)
    #     if not os.path.exists(join(refpath, containerId)):
    #         os.mkdir(join(refpath, containerId))
    #     if os.path.exists(join(refpath, containerId, 'containerstate.yaml')):
    #         unhidefile(join(refpath, containerId, 'containerstate.yaml'))
    #     open(join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
    #     makefilehidden(join(refpath, containerId, 'containerstate.yaml'))
    #     cls.downloadFrame(refpath, authtoken,containerId,BASE)
    #     return join(refpath, containerId, 'containerstate.yaml')

    # def downloadbranch(self,branch,BASE,authtoken,refpath):
    #     payload = {'containerID': self.containerId,
    #                'branch': branch}
    #     headers = {
    #         'Authorization': 'Bearer ' + authtoken
    #     }
    #     if not os.path.exists(join(refpath,branch)):
    #         os.mkdir(join(refpath,branch))
    #     makefilehidden(join(refpath,branch))
    #     response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
    #     fullbranchlist = response.json()
    #     for rev in fullbranchlist:
    #         payload = {'containerID': self.containerId,
    #                    'branch': branch,
    #                    'rev':rev}
    #         revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
    #         if os.path.exists(join(refpath,branch, rev)):
    #             unhidefile(join(refpath,branch, rev))
    #         open(join(refpath, branch, rev), 'wb').write(revyaml.content)
    #         makefilehidden(join(refpath,branch, rev))
   # def compareToRefFrame(self, changes):
    #     alterfiletracks=[]
    #     wf = self.workingFrame
    #     if NEWFRAMEFN == os.path.basename(self.refframefullpath):
    #         return {'NewContainer':{'reason': 'NewContainer'}},[]  ### this might not be final as alternating input files can bring in new difficulties
    #     refframe = Frame.loadRefFramefromYaml(self.refframefullpath,self.containerworkingfolder)
    #     refframefiletrackids = list(refframe.filestrack.keys())
    #     for containeritemid, containeritem in self.containeritem.items():
    #         if containeritemid not in refframe.filestrack.keys() and containeritemid not in wf.filestrack.keys():
    #             # check if fileheader is in neither refframe or current frame,
    #             raise('somehow Container needs to track ' + containeritemid + 'but its not in ref frame or current frame')
    #
    #         if containeritemid not in refframe.filestrack.keys() and containeritemid in wf.filestrack.keys():
    #             # check if fileheader is in the refframe, If not in frame, that means user just added a new fileheader
    #             changes[containeritemid]= {'reason': [LOCALCITEMNAMEADDED]}
    #             continue
    #         refframefiletrackids.remove(containeritemid)
    #         filename = os.path.join(self.containerworkingfolder, wf.filestrack[containeritemid].ctnrootpath, wf.filestrack[containeritemid].entity)
    #         fileb = open(filename, 'rb')
    #         wf.filestrack[containeritemid].md5 = hashlib.md5(fileb.read()).hexdigest()
    #         # calculate md5 of file, if md5 has changed, update md5
    #
    #         if refframe.filestrack[containeritemid].md5 != wf.filestrack[containeritemid].md5:
    #             wf.filestrack[containeritemid].lastEdited = os.path.getmtime(filename)
    #             changes[containeritemid] = {'reason': [MD5CHANGED]}
    #             if wf.filestrack[containeritemid].connection.containeritemrole==roleInput:
    #                 alterfiletracks.append(wf.filestrack[containeritemid])
    #             # if file has been updated, update last edited
    #             wf.filestrack[containeritemid].lastEdited = os.path.getmtime(filename)
    #             continue
    #         elif wf.filestrack[containeritemid].lastEdited != refframe.filestrack[containeritemid].lastEdited:
    #             changes[containeritemid] = {'reason': [DATECHANGED]}
    #             wf.filestrack[containeritemid].lastEdited = os.path.getmtime(filename)
    #             print('Date changed without Md5 changing')
    #             continue
    #
    #     for remainingiletrackid in refframefiletrackids:
    #         changes[remainingiletrackid] = {'reason': [LOCALCITEMNAMEREMOVED]}
    #     return changes, alterfiletracks
import re
def commithistory(container:Container):
    historydict = {}
    for revyaml, pastframe in container.memoryframesdict.items():
        m = re.search('(Rev\d+).yaml', revyaml)
        revx = m.group(1)
        # pastframe = Frame.loadRefFramefromYaml(yamlframefn, self.containerworkingfolder)
        historydict[revx] = {'commitmessage':pastframe.commitMessage,
                                           'timestamp':pastframe.commitUTCdatetime,
                                            'frame':pastframe}
    return historydict
