import os
from os.path import join, exists
import requests
from Config import BASE
from SagaGuiModel.GuiModelConstants import CONTAINERFN, TEMPCONTAINERFN
from SagaCore.SagaUtil import makefilehidden, ensureFolderExist, unhidefile
from SagaCore.Frame import Frame
from SagaCore.Container import Container
from SagaCore.Track import FileTrack
import json
from Graphics.Dialogs import downloadProgressBar
from PyQt5.QtGui import QGuiApplication
from datetime import datetime
from PyQt5.QtWidgets import *
import warnings


class SagaAPICall():
    def __init__(self, authtoken = None ):
        self.authtoken = authtoken
        self.errormessageboxhandle = None
        self.mainguihandle = None
        self.exptimestamp = None


    def callhandling(self, URL, METHOD, data = None , expectedkeys={}, headers=None, decodeformat=None, files=None):
        callreport={'missingkeys' :[],}
        predictedCallBehaviour = False
        errtext=''
        try:
            if METHOD=='GET':
                response = requests.get(URL, headers=headers, data=data)
            elif METHOD=='POST':
                response = requests.post(URL, headers=headers, data=data, files=files)
            else:
                raise('Wrong Method')

            if response.status_code == 200:
                # print("The request was a success!")
                predictedCallBehaviour=True
                # Code here will only run if the request is successful
            elif response.status_code == 201:
                # print("The request was a success!")
                predictedCallBehaviour=True
                self.mainguihandle.errout('Sign Up Successful')
                # Code here will only run if the request is successful
            elif response.status_code == 401:
                print("Auth Failed")
                predictedCallBehaviour = True
                # response.raise_for_status()
                # Code here will only run if the request is successful
            elif response.status_code == 404:
                # predictedCallBehaviour = True
                response.raise_for_status()
                errtext = errtext + 'Results not found for url : ' + URL + '\n'
            # Code here will only run if the request is successful
        except requests.exceptions.HTTPError as errh:
            errtext = errtext + errh.__str__() + '\n'
        except requests.exceptions.ConnectionError as errc:
            errtext = errtext + errc.__str__() + '\n'
        except requests.exceptions.Timeout as errt:
            errtext = errtext + errt.__str__() + '\n'
        except requests.exceptions.RequestException as err:
            errtext = errtext + err.__str__() + '\n'



        if not predictedCallBehaviour:
            self.mainguihandle.errout(errtext)
        try:
            if decodeformat:
                resp = json.loads(response.content.decode(decodeformat))
            else:
                resp = json.loads(response.content)
            for key in expectedkeys:
                if key not in resp.keys():
                    warnings.warn('In call :' +URL, '\n Expected return key :' + key+ 'Missing')
                    # callreport['missingkeys'].append(key)
                    resp[key]:None
            return predictedCallBehaviour, resp
        except Exception as e:
            returndict = {}
            for key in expectedkeys:
                returndict[key] = None
            return predictedCallBehaviour, returndict



    def signInCall(self, email, password):
        # print(self.email.text())
        expectedreturnkeysindict = ['success', 'message','failmessage','e', 'auth_token', 'exptimestamp']
        payload = {'email': email,
                   'password': password}
        success = False
        predictedCallBehaviour, respdict= self.callhandling(BASE + 'auth/login','POST', data=payload, expectedkeys=expectedreturnkeysindict)
        if respdict['success']:
            success = True
            self.authtoken = respdict['auth_token']
            self.exptimestamp = respdict['exptimestamp']
        return respdict['success'], respdict

    def newUserSignUpCall(self, email, password, firstname, lastname, sectionid ):
        payload = {'email': email,
                   'password': password,
                   'first_name':firstname,
                   'last_name':lastname,
                   'sectionid':sectionid
                   }
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e', 'auth_token', 'exptimestamp']
        predictedCallBehaviour, respdict = self.callhandling(BASE + 'auth/register','POST', data=payload, expectedkeys=expectedreturnkeysindict)
        # signupresponse = response.json()
        if respdict['success']:
            self.authtoken = respdict['auth_token']
            self.exptimestamp = respdict['exptimestamp']
        return respdict['success'], respdict

    def authUserDetails(self):
        if self.authtoken is None:
            return False , None
        expectedreturnkeysindict=['success', 'message', 'failmessage', 'e','usersessiondict']
        headers={"Authorization": 'Bearer ' + self.authtoken}
        predictedCallBehaviour,resp = self.callhandling(BASE + 'auth/userdetails', 'GET',  expectedkeys=expectedreturnkeysindict, headers=headers, )
        # userresponse = json.loads(response.content)
        if resp['success']:
            return resp['success'], resp['usersessiondict']
        else:
            return False, None

    def getAvailableSectionsCall(self):

        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','sectioninfo']
        # headers = {'Authorization': 'Bearer ' + self.authtoken}
        predictedCallBehaviour,resp, = self.callhandling(BASE + 'SECTION/List', 'GET',  expectedkeys=expectedreturnkeysindict)
        if resp['success']:
            sectiondicts = resp['sectioninfo']
        else:
            sectiondicts={}
        return resp['success'],sectiondicts

    def getListofSectionsforUser(self):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','sectioninfo','currentsection']
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        # response = requests.get(BASE + '', headers=headers)
        predictedCallBehaviour,resp= self.callhandling(BASE + 'USER/getusersections', 'GET', headers = headers, expectedkeys=expectedreturnkeysindict)
        # resp = json.loads(response.content)
        sectioninfo = resp['sectioninfo']
        currentsection = resp['currentsection']
        return resp['success'],sectioninfo, currentsection

    def downloadContainerCall(self,containerId):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','fullframelist','containerdict','revnum']
        print('start of downloadcall'+ datetime.now().isoformat())
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        predictedCallBehaviour, resp= self.callhandling(BASE + 'CONTAINERS/containerID', 'GET', headers=headers,data={'containerID': containerId},
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)

        if resp['success']:
            fullframelist = resp['fullframelist']
            containerdict = resp['containerdict']
        else:
            fullframelist = {}
            containerdict = {}
        # print('end of downloadcall' + datetime.now().isoformat())
        return resp['success'], fullframelist,containerdict

    # @classmethod
    # def downloadFrame(cls, refpath, authtoken, containerId, BASE, branch='Main'):
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
    #         os.mkdir(join(refpath, containerId, branch))
    #
    #     frameyamlDL = join(refpath, containerId, branch, response.headers['filename'])
    #     if os.path.exists(frameyamlDL):
    #         unhidefile(frameyamlDL)
    #     open(frameyamlDL, 'wb').write(response.content)
    #     makefilehidden(join(refpath, containerId, branch))
    #     return frameyamlDL

    def downloadTrackCall(self, fullfilepath , md5, filename, lastEdited):
        response = requests.get(BASE + 'FILES',
                                data={'md5': md5,
                                      'filename': filename})
        # Loops through the filestrack in curframe and request files listed in the frame
        # ATTENTION, MOST OF THE STUFF BELOW DOES NOT BELOW IN THIS CLASS
        if response.headers['status']=='Success':
            progress = downloadProgressBar(response.headers['filename'])
            dataDownloaded = 0
            progress.updateProgress(dataDownloaded)
            with open(fullfilepath, 'wb') as f:
                for data in response.iter_content(1024):
                    dataDownloaded += len(data)
                    f.write(data)
                    percentDone = 100 * dataDownloaded/len(response.content)
                    progress.updateProgress(percentDone)
                    QGuiApplication.processEvents()
            os.utime(fullfilepath, (lastEdited, lastEdited))
        else:
            warnings.warn('could not find file ' + md5 + ' on server')
        # saves the content into file.

        # return fn#,self.filestrack[fileheader]


    def downloadbranchcall(self,containerworkingfolder, cont:Container, branch='Main'):
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
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','containerinfodict']
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        predictedCallBehaviour, resp= self.callhandling( BASE + 'CONTAINERS/List', 'GET', headers=headers,data={},
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        if not resp['success']:
            containerinfodict = {
                'EMPTY': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        else:
            containerinfodict = resp['containerinfodict']
        return resp['success'], containerinfodict

    def getContainerInfoDict(self):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','containerinfodict']
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        predictedCallBehaviour, resp= self.callhandling( BASE + 'CONTAINERS/List', 'GET', headers=headers,data={},
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        if not resp['success']:
            containerinfodict = {
                'EMPTY': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        else:
            containerinfodict = resp['containerinfodict']
        return resp['success'], containerinfodict

    def commitNewRevisionCall(self,containerdictjson, framedictjson, updateinfojson, filesToUpload,commitmessage, containerId, currentbranch):
        data = {'containerID': containerId,
                'containerdictjson': containerdictjson,
                'framedictjson': framedictjson,
                'branch': currentbranch,
                'updateinfo': updateinfojson,
                'commitmsg': commitmessage}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','yamlframefn','framecontent']
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        predictedCallBehaviour,  resp= self.callhandling( BASE + 'SAGAOP/commit', 'POST', headers=headers,data=data,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict, files=filesToUpload)

        if resp['success']:
            # Updating new frame information
            yamlframefn = resp['yamlframefn']
            yamlcontent = resp['framecontent']
        else:
            yamlframefn = None
            yamlcontent = None
        return resp['success'], resp , yamlframefn , yamlcontent

    def addChildContainerCall(self,childcontaineritemrole,childcontainername, parentcontainerid):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','parentcontainerdict','childcontainerdict']
        print('start of downloadcall'+ datetime.now().isoformat())
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        predictedCallBehaviour,  resp= self.callhandling(BASE + 'CONTAINERS/containerID', 'GET', headers=headers,
                                             data={'parentcontainerid': parentcontainerid,
                                                   'childcontainername':childcontainername,
                                                   'childcontaineritemrole':childcontaineritemrole},
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        success = resp['success']
        parentcontainerdict = resp['parentcontainerdict']
        childcontainerdict= resp['childcontainerdict']
        yamlframefn = resp['yamlframefn']
        yamlcontent = resp['yamlcontent']
        return success,parentcontainerdict, childcontainerdict, yamlframefn , yamlcontent


    def commitNewContainerToServer(self,  payload,filesToUpload):
        headers = {  'Authorization': 'Bearer ' + self.authtoken}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','containerdictjson','framedictjson']
        predictedCallBehaviour, resp= self.callhandling(BASE + 'SAGAOP/newContainer', 'POST', headers=headers,
                                             data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict, files=filesToUpload)

        success = resp['success']
        returncontdict = resp['containerdictjson']
        returnframedict = resp['framedictjson']
        # alloweduser = returncontdict['allowedUser']
        message = resp['message']
        return success,returncontdict,returnframedict, message

    def sectionSwitchCall(self, newsectionid):
        payload = {'newsectionid': newsectionid}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e',
                                    'sectionname']
        predictedCallBehaviour, resp= self.callhandling(BASE + 'USER/switchusersection', 'POST', headers=headers,
                                             data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)

        # usersection = resp['usersection']

        self.errormessageboxhandle.setText(resp['message'])
        if resp['success']:
            self.errormessageboxhandle.setIcon(QMessageBox.Information)
        else:
            self.errormessageboxhandle.setIcon(QMessageBox.Critical)
            ## if we arrived here, then that means either
        self.errormessageboxhandle.exec_()
        return resp['success'], resp['sectionname']

    def addEmailsToSectionCall(self, emailsToInvite, sectionid):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e']
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        predictedCallBehaviour, resp= self.callhandling(BASE + 'SECTION/addemailstosection', 'POST', headers=headers,
                                             data={'emailsToInvite': emailsToInvite,
                                                   'sectionid':sectionid},
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        success = resp['success']
        if success:
            servermessage = resp['message']
        else:
            servermessage = resp['failmessage']
        # response = requests.post(BASE + 'USER/addemailstosection', headers=headers, data=payload)
        # addemailresponse = json.loads(response.content)
        # report = resp['addemailresponse']##ATTENTION...Imean comone
        # usersection = resp['usersection']
        return success, servermessage

    def addUserToContainerCall(self,usersess,emailtoadd,current_sectionid,containerId):

        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e', 'allowedUser']
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        data = {"email": usersess.email,
                                       "new_email": emailtoadd,
                                       "sectionid": current_sectionid,
                                       "containerId": containerId,
                                       }
        predictedCallBehaviour, resp= self.callhandling(BASE + 'PERMISSIONS/AddUserToContainer', 'POST', headers=headers,
                                             data=data,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)

        # if permissionsresponse['result']:
        #     self.maincontainer.setAllowedUser(permissionsresponse['allowedUser'])
        # return permissionsresponse, self.maincontainer.allowedUser

        return resp['success'], resp['allowedUser'], resp['message']

    def shouldModelSwitchCall(self,containerId):
        payload = {'containerid': containerId}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e', 'message','goswitch','sectionid']
        predictedCallBehaviour, resp= self.callhandling(BASE + 'USER/checkcontainerpermissions', 'GET', headers=headers,
                                             data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        # permissionsresponse = requests.get(BASE + 'USER/checkcontainerpermissions', headers=headers, data=payload)
        # print(resp.headers['message'])
        # Variable should be call managed or unmanaged.CallSuccess perhaps.
        goswitch = resp['goswitch']
        sectionid=resp['sectionid']
        if not resp['success']:
            self.errormessageboxhandle.setText(resp['failmessage'])
            self.errormessageboxhandle.exec_()
        return resp['success'],goswitch, sectionid



    def getNewestFrame(self, maincontainer:Container, sectionid):
        ## This is the only place that knows of a later revision.
        ### Get the Latest Frame Rev number of a container in the section
        payload = {'containerID': maincontainer.containerId, 'sectionid':sectionid}
        headers = {'Authorization': 'Bearer ' + self.authtoken        }
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e', 'message','framedict','newestrevnum']
        predictedCallBehaviour, resp= self.callhandling(BASE + 'CONTAINERS/newestframeofcontainer', 'GET', headers=headers,
                                             data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        newestframe = Frame.LoadFrameFromDict(resp['framedict'])
        newestrevnum = resp['newestrevnum']
        return resp['success'],newestframe,newestrevnum

    def getLatestRevNumCall(self, sectionid):
        ### Get the Latest Container Rev number of EVERY container in the section
        notlatestrev = False
        payload = {'sectionid':sectionid}
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e', 'latestrevdict']
        predictedCallBehaviour, resp= self.callhandling(BASE + 'CONTAINERS/newestrevnum', 'GET', headers=headers,
                                             data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        if resp['success']:
            latestrevdict = resp['latestrevdict']
        else:
            latestrevdict= None
        return resp['success'], latestrevdict

    def getNewVersionCall(self, installPath):
        response = requests.get(BASE + 'GENERAL/UpdatedInstallation',
                                headers={"Authorization": 'Bearer ' + self.authtoken})
        open(installPath, 'wb').write(response.content)

    def pingDownstreamCall(self,downstreamcontainerid, citemid, upstreamcontainerid):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e']
        payload = {'downstreamcontainerid': downstreamcontainerid,
                   'citemid':citemid,
                   'upstreamcontainerid':upstreamcontainerid}
        headers = {'Authorization': 'Bearer ' + self.authtoken}

        predictedCallBehaviour, resp= self.callhandling(BASE + 'PING/PingContainerToUpdateInputs', 'POST', headers=headers,data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
    def newSectionCall(self, newsectionname, newsectiondesp):
        headers = {'Authorization': 'Bearer ' + self.authtoken}
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e','newsection']
        # expectedreturnkeysindict = ['status', ]
        payload = {'newsectionname': newsectionname, 'newsectiondescription':newsectiondesp}
        predictedCallBehaviour, resp= self.callhandling(BASE + 'SECTION/newsection', 'POST', headers=headers, data=payload,
                                             decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        success = resp['success']
        newsection = resp['newsection']
        return success, newsection

    def getContainerPermissionsCall(self, email, current_sectionid, containerId):
        expectedreturnkeysindict = ['success', 'message', 'failmessage', 'e',
                                    'allowedUser', 'sectionUser']

        headers = {'Authorization': 'Bearer ' + self.authtoken}
        payload ={"email": email,
         "current_sectionid": current_sectionid,
         "containerId": containerId}
        predictedCallBehaviour, resp = self.callhandling(BASE + 'PERMISSIONS/getByContainer', 'GET', headers=headers,
                                                         data=payload,
                                                         decodeformat='utf-8', expectedkeys=expectedreturnkeysindict)
        if resp['success']:
            allowedUser = resp['allowedUser']
            sectionUser= resp['sectionUser']
        else:
            allowedUser= []
            sectionUser=[]

        return resp['success'], allowedUser, sectionUser

    def reset(self):
        self.authtoken = None

