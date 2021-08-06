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
from datetime import datetime
from PyQt5.QtWidgets import *



class SagaAPICall():
    def __init__(self, authtoken = None):
        self.authtoken = authtoken
        self.errormessageboxhandle = None


    def callhandling(self, URL, data):


        try:
            response = requests.post(URL, data=data)
            response.raise_for_status()
            # Code here will only run if the request is successful
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)
        if response.status_code == 200:
            print("The request was a success!")
            # Code here will only run if the request is successful
        elif response.status_code == 404:
            print("Result not found!")


    def signInCall(self, email, password):
        # print(self.email.text())
        expectedreturnkeysindict = ['status', 'message', 'auth_token', 'useremail', 'first_name', 'current_sectionname',
                                    'current_sectionid', 'sectionname_list', 'sectionid_list', 'last_name',
                                    'exptimestamp', 'version_num']
        payload = {'email': email,
                   'password': password}
        response = requests.post(BASE + 'auth/login',data=payload)
        signinresp = json.loads(response.content)

        if signinresp['status']=='success':
            status = 'success'
            self.authtoken = signinresp['auth_token']
        else:
            status = 'failed'
        return {'status': status, 'usertokeninfo':signinresp}

    def newUserSignUpCall(self,formentry):
        response = requests.post(BASE + 'auth/register',
                                 data=formentry)
        signupresponse = response.json()
        # if signupresponse['status'] == 'success':
        #     self.authtoken = signupresponse['auth_token']
        return signupresponse

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

    def getAvailableSectionsCall(self):
        # headers = {'Authorization': 'Bearer ' + self.authtoken}
        response = requests.get(BASE + 'SECTION/List')

        sectiondict = json.loads(response.content)
        # sectioninfo = resp['sectioninfo']
        # currentsection = resp['currentsection']
        return sectiondict

    def getListofSectionsforUser(self):
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        response = requests.get(BASE + 'USER/getusersections', headers=headers)

        resp = json.loads(response.content)
        sectioninfo = resp['sectioninfo']
        currentsection = resp['currentsection']
        return sectioninfo, currentsection

    def downloadContainerCall(self, containerworkingfolder, containerId, ismaincontainer=False):
        # print()
        print('start of downloadcall'+ datetime.now().isoformat())
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        response = requests.get(BASE + 'CONTAINERS/containerID', headers=headers, data={'containerID': containerId})
        ensureFolderExist(join(containerworkingfolder, 'Main', 'Rev1.yaml'))## Hack 'File name is needed but not used.'ATTENTION
        dlcontent = json.loads(response.content.decode('utf-8'))
        requestfailed = False
        if requestfailed:
            return
        for yamlfn, framedict in dlcontent['fullframelist'].items():
            frame = Frame.LoadFrameFromDict(framedict, containerworkingfolder, yamlfn)
            frame.writeoutFrameYaml(authorized=True)
        cont = Container.LoadContainerFromDict(dlcontent['containerdict'],containerworkingfolder, CONTAINERFN, ismaincontainer=ismaincontainer)
        cont.save()
        if ismaincontainer:
            cont.save(TEMPCONTAINERFN)
            cont.yamlfn = TEMPCONTAINERFN
        # # if exists(join(containerworkingfolder, 'containerstate.yaml')):
        # #     unhidefile(join(containerworkingfolder, 'containerstate.yaml'))
        # # open(join(newcontparentdirpath, containerId, 'containerstate.yaml'), 'wb').write(response.content)
        # makefilehidden(join(newcontparentdirpath, containerId, 'containerstate.yaml'))
        # self.downloadFrame(newcontparentdirpath, authtoken, containerId, BASE)
        print('end of downloadcall' + datetime.now().isoformat())
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

    def downloadFileCall(self, filetrack:FileTrack, containerworkingfolder, newfilename=None ):
        response = requests.get(BASE + 'FILES',
                                data={'md5': filetrack.md5,
                                      'file_name': filetrack.file_name})
        # Loops through the filestrack in curframe and request files listed in the frame
        # ATTENTION, MOST OF THE STUFF BELOW DOES NOT BELOW IN THIS CLASS
        if response.headers['status']=='Success':
            if newfilename is None:
                fn = os.path.join(containerworkingfolder, filetrack.ctnrootpath, filetrack.file_name)
            else:
                fn = os.path.join(containerworkingfolder, filetrack.ctnrootpath, newfilename)
            if not filetrack.ctnrootpath == '.':
                ensureFolderExist(fn)
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
            ####ATTENTION
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

    def sectionSwitchCall(self, newsectionid):
        payload = {'newsectionid': newsectionid}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        switchresponse = requests.post(BASE + 'USER/switchusersection', headers=headers, data=payload)
        resp = json.loads(switchresponse.content)
        report = resp['report']##ATTENTION...Imean comone
        usersection = resp['usersection']

        self.errormessageboxhandle.setText(report['status'])
        if report['status'] == 'User Current Section successfully changed':
            self.errormessageboxhandle.setIcon(QMessageBox.Information)
        else:
            self.errormessageboxhandle.setIcon(QMessageBox.Critical)
            ## if we arrived here, then that means either
        self.errormessageboxhandle.exec_()
        return report, usersection

    def addUserToContainerCall(self,userdata,emailtoadd,current_sectionid,containerId):

        expectedresponse=[]
        response = requests.post(BASE + 'PERMISSIONS/AddUserToContainer',
                                 headers={"Authorization": 'Bearer ' + self.authtoken},
                                 json={"email": userdata['email'],
                                       "new_email": emailtoadd,
                                       "sectionid": current_sectionid,
                                       "containerId": containerId,
                                       }
                                 )
        permissionsresponse = json.loads(response.content)

        print(permissionsresponse['ServerMessage'])
        if permissionsresponse['result']:
            self.maincontainer.setAllowedUser(permissionsresponse['allowedUser'])
        return permissionsresponse, self.maincontainer.allowedUser

        return permissionsresponse

    def shouldModelSwitchCall(self,containerId):
        payload = {'containerid': containerId}
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        permissionsresponse = requests.get(BASE + 'USER/checkcontainerpermissions', headers=headers, data=payload)
        print(permissionsresponse.headers['message'])
        # permissionsresponsecontent = json.loads(permissionsresponse.content)
        permissionsresponsecontent = json.loads(permissionsresponse.content)
        goswitch = permissionsresponsecontent['goswitch']
        newsectionid=permissionsresponsecontent['sectionid']
        message =permissionsresponse.headers['message']

        if newsectionid is None:
            # print('shouldModelSwitch call produced some sort of error')
            self.errormessageboxhandle.setText(message)
            self.errormessageboxhandle.exec_()
        return goswitch, newsectionid

    def getNewestFrame(self, maincontainer:Container, sectionid):
        ## This is the only place that knows of a later revision.
        notlatestrev = False
        payload = {'containerID': maincontainer.containerId, 'sectionid':sectionid}

        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }
        # print('1' + datetime.now().isoformat())
        response = requests.get(BASE + 'CONTAINERS/newestframeofcontainer', headers=headers, data=payload)
        # print('2' + datetime.now().isoformat())
        resp = json.loads(response.content)
        newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        newestrevnum = resp['newestrevnum']
        return newestframe,newestrevnum

    def getLatestRevNumCall(self, sectionid):
        ## This is the only place that knows of a later revision.
        notlatestrev = False
        payload = { 'sectionid':sectionid}

        headers = {
            'Authorization': 'Bearer ' + self.authtoken
        }
        response = requests.get(BASE + 'CONTAINERS/newestrevnum', headers=headers, data=payload)
        resp = json.loads(response.content)

        newestrevnumsinsection = resp
        return newestrevnumsinsection

    def getNewVersionCall(self, installPath):
        response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
                                headers={"Authorization": 'Bearer ' + self.authtoken})
        open(installPath, 'wb').write(response.content)


