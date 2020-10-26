import os
import requests
import yaml
from Frame.Container import Container
from Frame.FrameStruct import Frame
#BASE = "http://fatpanda1985.pythonanywhere.com/"

BASE = "http://127.0.0.1:5000/"



containerID = 'ContainerC'

response = requests.get(BASE+'CONTAINERS', data={'containerID':containerID})
os.mkdir(containerID)
open(os.path.join(containerID,response.headers['file_name']), 'wb').write(response.content)
curcont = Container(os.path.join(containerID,response.headers['file_name']))

response = requests.get(BASE+'FRAMES', data={'containerID':containerID, 'branch':curcont.yamlTracking['currentbranch']})
branch = response.headers['branch']
os.mkdir(os.path.join(containerID,branch))
frameyaml = os.path.join(containerID,branch,response.headers['file_name'])
open(frameyaml, 'wb').write(response.content)

with open(frameyaml) as file:
    fnyaml = yaml.load(file, Loader=yaml.FullLoader)
curframe = Frame(fnyaml,containerID )

for key,fileobj in curframe.filestrack.items():
    response = requests.get(BASE + 'FILES',
                            data={'file_id': fileobj.file_id, 'file_name':fileobj.file_name})
    fn = os.path.join(containerID,  response.headers['file_name'])
    open(fn, 'wb').write(response.content)
    os.utime(fn,(fileobj.lastEdited,fileobj.lastEdited))


# print(response.content)




# # response = requests.get(BASE)
# # print (response.json())


#Upload File
# files = {'file' : open('LongVideo.mp4','rb')}
#
# r=requests.post(BASE+'UPLOADS', files=files)
# print(r.json())
#

#Get File
# r=requests.get(BASE+'UPLOADS')
# # print(r.content)
#
# file = open('try.mp4', "wb")
# file.write(r.content)
# file.close()


#Delete File
# r=requests.delete(BASE+'UPLOADS')
# print(r.json())


# print(r.text)