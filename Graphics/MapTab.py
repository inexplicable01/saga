from Graphics.ContainerMap import ContainerMap
from Graphics.DetailedMap import DetailedMap
import requests
from Config import BASE
import json
from Graphics.QAbstract.ContainerListModel import ContainerListModel
import os
from functools import partial
from Frame.FrameStruct import Frame
from Frame.Container import Container

class MapTab():
    def __init__(self, mainGuiHandle):
        self.index = 0

        self.detailsMapView = mainGuiHandle.detailsMapView
        self.containerMapView = mainGuiHandle.containerMapView
        self.returncontlist = mainGuiHandle.returncontlist
        self.containerlisttable = mainGuiHandle.containerlisttable
        self.generateContainerBttn = mainGuiHandle.generateContainerBttn

        self.generateContainerBttn.clicked.connect(self.generateContainerMap)

        self.selecteddetail = {'selectedobjname': None}
        self.returncontlist.clicked.connect(partial(mainGuiHandle.getContainerInfo, self.containerlisttable))
        ###########Gui Variables##############
        self.detailedmap = DetailedMap(self.detailsMapView, self.selecteddetail)
        self.containermap = ContainerMap({}, self.containerMapView, self.selecteddetail, self.detailedmap)

    def generateContainerMap(self):
        response = requests.get(BASE + 'CONTAINERS/List')
        containerinfolist = json.loads(response.headers['containerinfolist'])
        for containerID in containerinfolist.keys():
            response = requests.get(BASE + 'CONTAINERS/containerID', data={'containerID': containerID})
            open(os.path.join('ContainerMapWorkDir', containerID + '_' + response.headers['file_name']), 'wb').write(
                response.content)
            self.containermap.addActiveContainers(
                Container(os.path.join('ContainerMapWorkDir', containerID + '_' + response.headers['file_name'])))
        self.containermap.editcontainerConnections()
        self.containermap.plot()
        self.detailedmap.passobj(self.containermap)