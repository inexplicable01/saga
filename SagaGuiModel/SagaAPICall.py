import os
from os.path import join, exists
import requests
from Config import BASE, CONTAINERFN, TEMPCONTAINERFN
from SagaApp.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaApp.FrameStruct import Frame
from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack
import json
from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication

class SagaAPICall():
    def __init__(self, authtoken = None):
        self.authtoken = authtoken

    def signInCall(self, email, password, tokenfile):
        # print(self.email.text())
        payload = {'email': email,
                   'password': password}
        response = requests.post(BASE + 'auth/login',
                                 data=payload,
                                 )
        signinresp = response.json()

        print('usertoken[status] ' + signinresp['status'])
        if signinresp['status']=='success':
            status = 'success'
            self.authtoken = signinresp['auth_token']
            with open(tokenfile, 'w') as tokenfile:
                json.dump(signinresp, tokenfile)
                #ATTENTION, MAY NOT NEED THIS ANYMORE POtentail security issue?

        else:
            status = 'failed'
        return {'status': status}

    def authUserDetails(self,tokenfile):
        if self.authtoken is None:
            return {'userstatusstatement': 'Need to sign in first before asking for details',
                'signinsuccess': False} , None
        try:
            # with open(tokenfile) as json_file:
            #     token = json.load(json_file)

            response = requests.get(
                BASE + '/auth/userdetails',
                headers={"Authorization": 'Bearer ' + self.authtoken}
            )
            usertoken = response.json()
            if usertoken['status'] == 'success':
                # self.userdata = usertoken['data']
                userdata = usertoken['data']
                # self.authtoken = token['auth_token']
                userstatusstatement = 'User ' + userdata['email'] + \
                                      ' Signed in to Section ' + userdata['current_sectionname']
                signinsuccess = True
            else:
                # self.authtoken= None
                userdata = None
                userstatusstatement = 'Please sign in'
                signinsuccess = False
        except Exception as e:
            # print('No User Signed in yet')
            userstatusstatement = 'Please sign in'
            signinsuccess = False
            userdata = None
        return {'userstatusstatement': userstatusstatement,
                'signinsuccess': signinsuccess} , userdata

    def getListofSectionsforUser(self):
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        response = requests.get(BASE + 'USER/getusersections', headers=headers)

        resp = json.loads(response.content)
        sectioninfo = resp['sectioninfo']
        currentsection = resp['currentsection']
        return sectioninfo, currentsection

    def downloadContainerCall(self, newcontparentdirpath, containerId, use):
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
        ensureFolderExist(join(newcontparentdirpath, containerId, 'Main', 'Rev1.yaml'))## Hack 'File name is needed but not used.'
        dlcontent = json.loads(response.content.decode('utf-8'))
        requestfailed = False
        if requestfailed:
            return
        containerworkingfolder = join(newcontparentdirpath, containerId)
        for yamlfn, framedict in dlcontent['fullframelist'].items():
            frame = Frame.LoadFrameFromDict(framedict, containerworkingfolder, yamlfn)
            frame.writeoutFrameYaml()
        cont = Container.LoadContainerFromDict(dlcontent['containerdict'],containerworkingfolder, CONTAINERFN)
        cont.save()
        if use=='WorkingContainer':
            cont.save(TEMPCONTAINERFN)
            cont.yamlfn = TEMPCONTAINERFN
        # # if exists(join(containerworkingfolder, 'containerstate.yaml')):
        # #     unhidefile(join(containerworkingfolder, 'containerstate.yaml'))
        # # open(join(newcontparentdirpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
        # makefilehidden(join(newcontparentdirpath, containerId, 'containerstate.yaml'))
        # self.downloadFrame(newcontparentdirpath, authtoken, containerId, BASE)
        return containerworkingfolder, cont

    @classmethod
    def downloadFrame(cls, refpath, authtoken, containerId, BASE, branch='Main'):
        payload = {'containerID': containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + authtoken
        }
        response = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
        # print(response.headers)
        # print(response.content)
        # request to FRAMES to get the latest frame from the branch as specified in currentbranch
        branch = 'Main'
        # response also returned the name of the branch
        if not os.path.exists(join(refpath, containerId, branch)):
            os.mkdir(join(refpath, containerId, branch))

        frameyamlDL = join(refpath, containerId, branch, response.headers['file_name'])
        if os.path.exists(frameyamlDL):
            unhidefile(frameyamlDL)
        open(frameyamlDL, 'wb').write(response.content)
        makefilehidden(join(refpath, containerId, branch))
        return frameyamlDL

    def downloadFile(self, filetrack:FileTrack, filepath, newfilename=None ):
        response = requests.get(BASE + 'FILES',
                                data={'md5': filetrack.md5,
                                      'file_name': filetrack.file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        if newfilename is None:
            fn = os.path.join(filepath,filetrack.ctnrootpath, response.headers['file_name'])
        else:
            fn = os.path.join(filepath, filetrack.ctnrootpath, newfilename)
        if not filetrack.ctnrootpath == '.':
            ensureFolderExist(fn)
        if response.headers['status']=='Success':
            progress = downloadProgressBar(response.headers['file_name'])
            dataDownloaded = 0
            progress.updateProgress(dataDownloaded)
            with open(fn, 'wb') as f:
                for data in response.iter_content(1024):
                    dataDownloaded += len(data)
                    f.write(data)
                    percentDone = 100 * dataDownloaded/len(response.content)
                    progress.updateProgress(percentDone)
                    QGuiApplication.processEvents()
        else:
            # open(fn,'w').write('Terrible quick bug fix')
            # # There should be a like a nuclear warning here is this imples something went wrong with the server and the frame bookkeeping system
            # # This might be okay meanwhile as this is okay to break during dev but not during production.
            raise('could not find file ' + filetrack.md5 + ' on server')
        # saves the content into file.
        os.utime(fn, (filetrack.lastEdited, filetrack.lastEdited))
        return fn#,self.filestrack[fileheader]




    def downloadbranch(self,containerworkingfolder, cont:Container, branch='Main'):

        payload = {'containerID': cont.containerId,
                   'branch': branch}
        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }
        if not os.path.exists(join(containerworkingfolder,branch)):
            os.mkdir(join(containerworkingfolder,branch))
        makefilehidden(join(containerworkingfolder,branch))
        response = requests.get(BASE + 'CONTAINERS/fullbranch', headers=headers, data=payload)
        fullbranchlist = response.json()
        for rev in fullbranchlist:
            payload = {'containerID': cont.containerId,
                       'branch': branch,
                       'rev':rev}
            revyaml = requests.get(BASE + 'FRAMES', headers=headers, data=payload)
            if os.path.exists(join(containerworkingfolder,branch, rev)):
                unhidefile(join(containerworkingfolder, branch, rev))
            open(join(containerworkingfolder, branch, rev), 'wb').write(revyaml.content)
            makefilehidden(join(containerworkingfolder,branch, rev))

    def getContainerInfoDict(self):
        response = requests.get(BASE + 'CONTAINERS/List', headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfodict = json.loads(response.content)
        if not containerinfodict:
            containerinfodict = {
                'EMPTY': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        return containerinfodict

    def commitToServer(self,containerdictjson, framedictjson, updateinfojson, filesToUpload,commitmessage, containerId, currentbranch):
        response = requests.post(BASE + 'SAGAOP/commit',
                                 headers={"Authorization": 'Bearer ' + self.authtoken},
                                 data={'containerID': containerId,
                                       'containerdictjson': containerdictjson,
                                       'framedictjson': framedictjson,
                                       'branch': currentbranch,
                                       'updateinfo': updateinfojson,
                                       'commitmsg':commitmessage},  files=filesToUpload)
        return response

    def commitNewContainerToServer(self,  payload,filesToUpload):
        url = BASE + 'SAGAOP/newContainer'
        headers = {  'Authorization': 'Bearer ' + self.authtoken}
        response = requests.request("POST", url, headers=headers, data=payload, files=filesToUpload)
        resp = response.json()
        returncontdict = resp['containerdictjson']
        returnframedict = resp['framedictjson']
        alloweduser = returncontdict['allowedUser']
        servermessage = response.headers['response']
        return returncontdict,returnframedict, servermessage

    def sectionSwitch(self, newsectionid):
        payload = {'newsectionid': newsectionid}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        switchresponse = requests.post(BASE + 'USER/switchusersection', headers=headers, data=payload)
        resp = json.loads(switchresponse.content)
        report = resp['report']
        status = report['status']
        return status

    def shouldModelSwitch(self,containerpath):

        loadingcontainer = Container.LoadContainerFromYaml(containerpath, revnum=None)
        payload = {'containerid': loadingcontainer.containerId}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        permissionsresponse = requests.get(BASE + 'USER/checkcontainerpermissions', headers=headers, data=payload)
        print(permissionsresponse.headers['message'])
        # permissionsresponsecontent = json.loads(permissionsresponse.content)
        permissionsresponsecontent = json.loads(permissionsresponse.content)
        goswitch = permissionsresponsecontent['goswitch']
        newsectionid=permissionsresponsecontent['sectionid']
        message =permissionsresponse.headers['message']
        return goswitch, newsectionid, message

    def callLatestRevision(self, maincontainer:Container):
        ## This is the only place that knows of a later revision.
        notlatestrev = False
        payload = {'containerID': maincontainer.containerId}

        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }

        response = requests.get(BASE + 'CONTAINERS/newestrevnum', headers=headers, data=payload)
        resp = json.loads(response.content)
        newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        newestrevnum = resp['newestrevnum']
        return newestframe,newestrevnum

