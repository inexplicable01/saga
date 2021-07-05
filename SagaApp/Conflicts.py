from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication
import requests
import os
from Config import BASE
from SagaApp.FrameStruct import Frame

class Conflicts:
    def __init__(self, maincontainer, authtoken, filelist = None,  refframe = None, newestframe = None):
        self.mainContainer = maincontainer
        self.newestframe = newestframe
        self.refframe = refframe
        self.filelist = filelist

    def checkLatestRevision(self):
        payload = {'containerID': self.mainContainer.containerId}

        headers = {
            'Authorization': 'Bearer ' + authtoken
        }

        response = requests.get(BASE + 'CONTAINERS/newestrevnum', headers=headers, data=payload)
        resp = json.loads(response.content)
        self.newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        self.revNum = resp['newestrevnum']
        self.newestFiles = {}
        if self.mainContainer.revnum < self.revNum:
            if self.refreshedrevision < self.revNum:
                self.refreshContainerBttn.setEnabled(True)
                if self.refreshedcheck:
                    self.containerstatuslabel.setText(
                        'Newer Revision Exists!' + ' Current Rev: ' + self.refreshrevnum
                        + ', Latest Rev: ' + str(self.revNum))
                else:
                    self.containerstatuslabel.setText('Newer Revision Exists!' + ' Current Rev: ' + str(self.mainContainer.revnum)
                                                      + ', Latest Rev: ' + str(self.revNum))
                #if the newest rev num is different from local rev num:
                #loop through filesttrack of both newest frame, check if file exists in current frame and compare MD5s,
                # if exists, add update message to changes, if notadd new file message
                for fileheader in self.newestframe.filestrack.keys():
                    if fileheader in self.mainContainer.workingFrame.filestrack.keys():
                        if self.newestframe.filestrack[fileheader].md5 != self.mainContainer.workingFrame.filestrack[fileheader].md5:
                            if fileheader in self.changes.keys():
                                self.changes[fileheader]['reason'].append('File updated in newer Revision')
                            else:
                                self.changes[fileheader] = {'reason': ['File updated in newer Revision']}
                            #if 'File updated....' is within changes reason dictionary, display delta in GUI
                    else:
                        self.changes[fileheader] = {'reason': 'New File committed in newer Revision'}

                # Loop through working frame to check if any files have been deleted in new revision
                for fileheader in self.mainContainer.workingFrame.filestrack.keys():
                    if fileheader not in self.newestframe.filestrack.keys():
                        if fileheader in self.changes.keys():
                            self.changes[fileheader]['reason'].append('File deleted in newer Revision')
                        else:
                            self.changes[fileheader] = {'reason': ['File deleted in newer Revision']}

    def downloadchanges(self, fileheader, filestodownload):
        wf = self.mainContainer.workingFrame
        payload = {'md5': self.newestframe.filestrack[fileheader].md5,
                   'file_name': self.newestframe.filestrack[fileheader].file_name}
        headers = {}
        response = requests.get(BASE + 'FILES', headers=headers, data=payload)
        self.progress = downloadProgressBar(response.headers['file_name'])
        dataDownloaded = 0
        self.progress.updateProgress(dataDownloaded)
        if filestodownload[fileheader] == 'Overwrite':
            fileEditPath = os.path.join(
                wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                wf.filestrack[fileheader].file_name)
            with open(fileEditPath, 'wb') as f:
                for data in response.iter_content(1024):
                    dataDownloaded += len(data)
                    f.write(data)
                    percentDone = 100 * dataDownloaded / len(response.content)
                    self.progress.updateProgress(percentDone)
                    QGuiApplication.processEvents()
            return {fileheader: [self.newestframe.filestrack[fileheader].md5, os.path.getmtime(fileEditPath)]}

        elif filestodownload[fileheader] == 'Download Copy':
            filePath = os.path.join(
                wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                wf.filestrack[fileheader].file_name)
            filecopy_name = os.path.splitext(filePath)[0] + '_' + self.newestframe.FrameName + 'Copy' + \
                            os.path.splitext(filePath)[1]
            fileEditPath = os.path.join(
                wf.containerworkingfolder, wf.filestrack[fileheader].ctnrootpath,
                filecopy_name)
            filecopy = open(fileEditPath, 'wb')
            filecopy.write(response.content)
            return 'No working frame changes'



