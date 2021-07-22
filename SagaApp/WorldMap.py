from Config import  BASE
import requests
import os
from SagaApp.Container import Container
import json
from SagaGuiModel import sagaguimodel

class WorldMap:
    def __init__(self , desktopdir):
        # self.desktopdir = desktopdir\
        pass


    @staticmethod
    def CheckContainerCanDeleteOutput(curcontainerid,  fileheader, desktopdir,authtoken):
        response = requests.get(BASE + 'CONTAINERS/List',headers={"Authorization": 'Bearer ' + authtoken})
        containerinfodict = json.loads(response.content)
        for containerid in containerinfodict.keys():
            if containerid==curcontainerid:
                continue
            if not os.path.exists(
                    os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerid, 'containerstate.yaml')):
                response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerid})
                os.mkdir(os.path.join(sagaguimodel.desktopdir, 'ContainerMapWorkDir', containerid))
                open(os.path.join(sagaguimodel.desktopdir,'ContainerMapWorkDir', containerid, response.headers['file_name']), 'wb').write(
                    response.content)
            downstreamcont = Container.LoadContainerFromYaml(
                os.path.join(sagaguimodel.desktopdir,'ContainerMapWorkDir', containerid, 'containerstate.yaml'))
            if fileheader in downstreamcont.FileHeaders.keys():
                if downstreamcont.FileHeaders[fileheader]['Container']==curcontainerid:
                    return False, 'Downstream Container ' + downstreamcont.containerName + '  is still linked'
        return True, 'No downstream Container is linked '



