import os
import yaml
import hashlib

class Container:
    def __init__(self, containerName,containerId,inputObjs,outputObjs,requiredObjs,references,mainBranch,yamlTracking):
        self.containerName=containerName
        self.containerId=containerId
        self.inputObjs=inputObjs
        self.outputObjs=outputObjs
        self.requiredObjs=requiredObjs
        self.references=references
        self.mainBranch=mainBranch
        self.yamlTracking=yamlTracking

    # def readYaml(containeryaml):
    #          __init__(containerName=containeryaml['containerName'],
    #                        containerId=containeryaml['containerId'],
    #                        inputLinks=containeryaml['inputLinks'],
    #                        outputLinks=containeryaml['outputLinks'],
    #                        requiredFiles=containeryaml['requiredFiles'],
    #                        references=containeryaml['references'],
    #                        mainBranch=containeryaml['mainBranch'],
    #                        yamlTracking=containeryaml['yamlTracking'])
    #     return self


class Frame:
    def __init__(self, FrameYaml):

        self.parentContainerId = 'alsjfasdf'
        self.FrameName = FrameYaml['FrameName']
        self.FrameInstanceId = FrameYaml['FrameInstanceId']
        self.commitMessage = FrameYaml['commitMessage']

        self.inlinks = FrameYaml['inlinks']
        self.outlinks = FrameYaml['outlinks']
        self.AttachedFiles = FrameYaml['AttachedFiles']
        # self.inoutcheck()

        filestrack = {}
        for ftrack in FrameYaml['filestrack']:
            # print(ftrack)
            file_frame_name = ftrack['file_frame_name']

            filestrack[file_frame_name] = FileTrackObj(file_frame_name=ftrack['file_frame_name'],
                                                       file_name=ftrack['file_name'],
                                                       localFilePath=ftrack['localFilePath'],
                                                       md5=ftrack['md5'],
                                                       style=ftrack['style'],
                                                       db_id=ftrack['db_id'],
                                                       commitUTCdatetime=ftrack['commitUTCdatetime'],
                                                       lastEdited=ftrack['lastEdited']
                                                       )
        self.filestrack = filestrack

    #        self.misc= misc

    def add_fileTrack(self, FileTrackObj):
        self.filestrack.append(FileTrackObj)

    def add_inlinks(self, inlinks):
        self.inlinks.append(inlinks)

    def add_outlinks(self, outlinks):
        self.outlinks.append(outlinks)

    def add_AttachedFiles(self, AttachedFiles):
        self.AttachedFiles.append(AttachedFiles)

    def add_misc(self, misc):
        self.misc.append(misc)

    def filestoCheck(self):
        filestocheck = []
        for filetrackobj in self.filestrack:
            filestocheck.append(filetrackobj['file_name'])
        return filestocheck

    # def inoutcheck(self):
    #     for inlink in self.inlinks:
    #         # print(inlink)
    #     for outlink in self.outlinks:
    #         # print(outlink)

    def addFileTotrack(self, fullpath, file_frame_name, style):
        [path, file_name] = os.path.split(fullpath)
        if os.path.exists(fullpath):
            newfiletrackobj = FileTrackObj(localFilePath=path,
                                           file_name=file_name,
                                           file_frame_name=file_frame_name,
                                           style=style,
                                           lastEdited=os.path.getmtime(path) )

            self.filestrack[file_frame_name] = newfiletrackobj
        else:
            raise(fullpath + ' does not exist')


    def writeoutFrameYaml(self, outyaml):
        dictout = {}
        for key, value in vars(self).items():
            if 'filestrack' == key:
                filestrack = []
                for file_frame_name, filetrackobj in value.items():
                    filestrack.append(filetrackobj.yamlify())
                dictout[key] = filestrack
            else:
                dictout[key] = value

        yaml.dump(dictout, outyaml)
        outyaml.close()


class FileTrackObj:
    def __init__(self, file_frame_name, file_name,localFilePath,style,lastEdited=None, md5=None,db_id=None,commitUTCdatetime=None):
        self.file_frame_name = file_frame_name
        self.file_name = file_name
        self.localFilePath = localFilePath
        if  md5 is None:
            fullpath = os.path.join(localFilePath, file_name)
            fileb = open(fullpath , 'rb')
            md5hash = hashlib.md5(fileb.read())
            md5=md5hash.hexdigest()
        self.lastEdited= lastEdited#
        self.md5 = md5
        self.style = style
        self.db_id = db_id
        self.commitUTCdatetime = commitUTCdatetime

    def yamlify(self):
        dictout = {}
        for key, value in vars(self).items():
            dictout[key] = value
        return dictout

class InputFileObj(FileTrackObj):
    def __init__(self, file_frame_name, file_name,localFilePath,style,fromContainerId,md5=None,db_id=None,commitUTCdatetime=None):
        super().__init__(self, file_frame_name, file_name,localFilePath,style,md5,db_id,commitUTCdatetime)
        self.fromContainerId=fromContainerId

class OutFileObj(FileTrackObj):
    def __init__(self, file_frame_name, file_name,localFilePath,style,toContainerID,md5=None,db_id=None,commitUTCdatetime=None):
        super().__init__(self, file_frame_name, file_name,localFilePath,style,md5,db_id,commitUTCdatetime)
        self.toContainerID=toContainerID