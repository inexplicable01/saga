import os
from os.path import join

## THe point of this module is to off load smaller self contained methods that exercise SagaGuiModel.
def updateEveryContainerInSection(sagaguimodel):
    ### Get the Latest Container Rev number of EVERY container in the section.  Download the new container
    success, latestrevdict = sagaguimodel.sagaapicall.getLatestRevNumCall(sagaguimodel.usersess.current_sectionid)
    for containerid, newestdict in latestrevdict.items():
        newestframeyaml = join(sagaguimodel.appdata_saga, 'ContainerMapWorkDir', containerid,
                               'Main', 'Rev' + str(newestdict['newestrevnum']) + '.yaml')
        if not os.path.exists(newestframeyaml):  ## Download the entire container if its been updated.
            workdir, sagaguimodel.networkcontainers[containerid] = sagaguimodel.downloadContainer(
                join(sagaguimodel.appdata_saga, 'ContainerMapWorkDir', containerid), containerid)
