import os
import requests
import yaml
from SagaApp.Container import Container
from SagaApp.FrameStruct import Frame
BASE = "http://fatpanda1985.pythonanywhere.com/"

# BASE = "http://127.0.0.1:5000/"
## BareBones script to download a container


containerID = 'ContainerC'

response = requests.get(BASE+'CONTAINERS/containerID', data={'containerID':containerID})
# requests is a python object/class, that sends a http request
# http request has address, header/body (places where you put small information, what's the request about)
# requests.get(url, data)
# This returns a container Yaml File

if not os.path.exists(containerID):
    os.mkdir(containerID)## Make a folder if it doesn't exist already

open(os.path.join(containerID,response.headers['file_name']), 'wb').write(response.content)
# takes the binary data from response.content and save as a file with file name also supplied from response
curcont = Container.LoadContainerFromYaml(os.path.join(containerID,response.headers['file_name']), response.headers['branch'], response.headers['revnum'])
# takes the contain.yaml file we just made and load it as a container object

response = requests.get(BASE+'FRAMES', data={'containerID':containerID, 'branch':'Main'})
# request to FRAMES to get the latest frame from the branch as specified in currentbranch
branch = response.headers['branch']
# response also returned the name of the branch
if not os.path.exists(os.path.join(containerID,branch)):
    os.mkdir(os.path.join(containerID,branch))## make folder if folder doesn't exist
frameyaml = os.path.join(containerID,branch,response.headers['file_name'])
open(frameyaml, 'wb').write(response.content)
## write return binary file as the frame yaml file

with open(frameyaml) as file:
    fnyaml = yaml.load(file, Loader=yaml.FullLoader)
## load the yaml file as a yaml object.
curframe = Frame(fnyaml,containerID )
## frame uses the yaml object to make a frame object.

for key,fileobj in curframe.filestrack.items():
    response = requests.get(BASE + 'FILES',
                            data={'file_id': fileobj.file_id, 'file_name':fileobj.file_name})
    #Loops through the filestrack in curframe and request files listed in the frame
    fn = os.path.join(containerID,  response.headers['file_name'])
    open(fn, 'wb').write(response.content)
    # saves the content into file.
    os.utime(fn,(fileobj.lastEdited,fileobj.lastEdited))

