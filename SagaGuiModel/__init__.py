import os
import warnings

from os.path import join
from SagaApp.SagaUtil import makefilehidden
from Config import BASE, mapdetailstxt, CONTAINERFN
import yaml
import json
import requests
from SagaApp.Container import Container


# with open(containerfn, 'r') as file:



class SagaGuiModel():
    def __init__(self, desktopdir, sourcecodedir,
                 versionnumber, authtoken=None, userdata=None , containerwrkdir=None,):
        self.authtoken = authtoken
        self.userdata= userdata
        self.containerwrkdir=containerwrkdir
        self.desktopdir = desktopdir
        self.sourcecodedir = sourcecodedir
        self.versionnumber = versionnumber
        self.guiworkingdir = os.getcwd()
        self.containernetworkkeys=[]

        guidirs= [ 'SagaGuiData','ContainerMapWorkDir']
        if not os.path.exists(self.desktopdir):
            os.mkdir(self.desktopdir)
        for guidir in guidirs:
            guidatadir = os.path.join(self.desktopdir,guidir)
            if not os.path.exists(guidatadir):
                os.mkdir(guidatadir)
            makefilehidden(guidatadir)

    @classmethod
    def loadModelFromConfig(cls):
        try:
            appdatadir = os.getenv('appdata')
            desktopdir = join(appdatadir, 'SagaDesktop')
        except Exception as e:
            warnings.warn('cannot find environmental variable appdata')
            desktopdir = ''

        try:
            with open('settings.yaml', 'r') as file:
                settingsyaml = yaml.load(file, Loader=yaml.FullLoader)
            sourcecodedir = settingsyaml['sourcecodedir']
            versionnumber= settingsyaml['versionnumber']
        except Exception as e:
            raise('unable to load settings.yaml.  Please ensure it is in program folder.')
        sagaguimodel = cls(sourcecodedir=sourcecodedir, desktopdir=desktopdir, versionnumber=versionnumber)
        return sagaguimodel

    def setAuthToken(self, authtoken):
        self.authtoken = authtoken

    def setUserData(self, userdata):
        self.userdata = userdata

    def checkUserStatus(self):
        try:
            with open('token.txt') as json_file:
                token = json.load(json_file)
            response = requests.get(
                BASE + '/auth/userdetails',
                headers={"Authorization": 'Bearer ' + token['auth_token']}
            )
            usertoken = response.json()
            if usertoken['status'] == 'success':
                # self.userdata = usertoken['data']
                self.setUserData(usertoken['data'])
                self.setAuthToken(token['auth_token'])
                userstatusstatement = 'User ' + self.userdata['email'] +\
                                           ' Signed in to Section ' + self.userdata['current_sectionname']
                signinsuccess = True
            else:
                self.setAuthToken(None)
                self.setUserData(None)
                userstatusstatement = 'Please sign in'
                signinsuccess = False
            sectioniddir = join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])
            if not os.path.exists(sectioniddir):
                os.mkdir(sectioniddir)

        except Exception as e:
            # print('No User Signed in yet')
            userstatusstatement = 'Please sign in'
            signinsuccess = False
        return { 'userstatusstatement':userstatusstatement,
                 'signinsuccess':signinsuccess}

    def getContainerInfo(self):
        response = requests.get(BASE + 'CONTAINERS/List', headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfodict = json.loads(response.headers['containerinfolist'])
        if not containerinfodict:
            containerinfodict = {
                'EMPTY': {'ContainerDescription': 'empty', 'branches': [{'name': 'Empty', 'revcount': 0}]}}
        return containerinfodict

    def getWorldContainers(self):
        # response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + self.authtoken})
        containerinfodict = self.getContainerInfo()
        if 'EMPTY' in containerinfodict.keys():
            self.containernetworkkeys=[]
            return containerinfodict

        for containerID in containerinfodict.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID}, headers={"Authorization": 'Bearer ' + self.authtoken})
            if CONTAINERFN != response.headers['file_name']:
                raise('container file name should be ' + CONTAINERFN + ', time to check response file_name and otherwise')
            if not os.path.exists(join(self.desktopdir,'ContainerMapWorkDir',containerID)):
                os.mkdir(join(self.desktopdir,'ContainerMapWorkDir',containerID))
            containeryamlfn = join(self.desktopdir,'ContainerMapWorkDir', containerID, CONTAINERFN)
            if os.path.exists(containeryamlfn):
                open(containeryamlfn, 'rb+').write(response.content)
            else:
                open(containeryamlfn, 'wb').write(response.content)
            cont = Container.LoadContainerFromYaml(containeryamlfn, fullload=False)
            cont.downloadbranch('Main', BASE, self.authtoken,join(self.desktopdir,'ContainerMapWorkDir',containerID))

        self.containernetworkkeys = containerinfodict.keys()

        if not os.path.exists(join(self.desktopdir, 'SagaGuiData', self.userdata['current_sectionid'])):
            os.mkdir(join(self.desktopdir, 'SagaGuiData',self.userdata['current_sectionid']))
        return containerinfodict

sagaguimodel = SagaGuiModel.loadModelFromConfig()