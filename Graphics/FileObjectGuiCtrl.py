

class FileObjectGuiCtrl:

    def __init__(self, scene):
        for index, inputObj in enumerate(self.Container.inputObjs):
            # ellipse = scene.addEllipse(20, 20, 200, 70, QPen(Qt.red), QBrush(Qt.green))
            self.sceneObj[inputObj['ContainerObjName']] = scene.addRect(-100, -200 + 100 * index, boxwidth, boxheight,
                                                                        QPen(Qt.black), QBrush(Qt.yellow))
            # print(inputObj['FileObjName'])
            text = scene.addText(inputObj['ContainerObjName'])
            text.setPos(-100, -200 + 100 * index)
            print(inputObj['ContainerObjName'])
            if inputObj['ContainerObjName'] in self.cframe.filestrack.keys():
                text = scene.addText(self.cframe.filestrack[inputObj['ContainerObjName']].file_name)
                text.setPos(-100, -200 + 100 * index + 20)
            else:
                text = scene.addText('Missing')
                text.setPos(-100, -200 + 100 * index + 20)