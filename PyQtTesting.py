from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
from Frame.FrameStruct import Frame, FileTrackObj,Container
from Frame.commit import commit

# Form, Window=uic.loadUiType()
def init_container(containeryaml):
    container = Container(containerName=containeryaml['containerName'],
                       containerId=containeryaml['containerId'],
                       inputObjs=containeryaml['inputObjs'],
                       outputObjs=containeryaml['outputObjs'],
                       requiredObjs=containeryaml['requiredObjs'],
                       references=containeryaml['references'],
                       mainBranch=containeryaml['mainBranch'],
                       yamlTracking=containeryaml['yamlTracking'])
    return container



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("Graphics/SagaGui.ui", self)


        self.openContainerBttn.setText('Open Container')

        self.openContainerBttn.clicked.connect(self.readcontainer)
        self.show()

    def readcontainer(self):
        # alert=QMessageBox()
        # alert.setText("You clicked the button!")
        # alert.exec_()
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            print(path)
        with open(path) as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        self.Container = init_container(containeryaml)

        # print(self.Container.containerName)
        self.label.setText('Current Container :' + self.Container.containerName)

        print(self.Container.inputObjs)
        scene = QGraphicsScene()
        for index, inputObj in enumerate(self.Container.inputObjs):
            # ellipse = scene.addEllipse(20, 20, 200, 70, QPen(Qt.red), QBrush(Qt.green))
            scene.addRect(-100, -200 + 100*index, 30, 30, QPen(Qt.black), QBrush(Qt.yellow))
        self.frameView.setScene(scene)
        for index, outputObj in enumerate(self.Container.outputObjs):
            # ellipse = scene.addEllipse(20, 20, 200, 70, QPen(Qt.red), QBrush(Qt.green))
            scene.addRect(100, -200 + 100*index, 30, 30, QPen(Qt.black), QBrush(Qt.green))


        # dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        # filenames = QStringList()
        # if dlg.exec_():
        #     filenames = dlg.selectedFiles()
        #     f = open(filenames[0], 'r')
        #
        #     with f:
        #         data = f.read()
        #         # self.contents.setText(data)


app=QApplication([])
window = UI()
app.exec_()


#




# app = QApplication([])
#
# window=QWidget()
# layout= QVBoxLayout()
# layout.addWidget(QPushButton('Top'))
# somebutton=QPushButton('Something')
# def clicked():
#     alert=QMessageBox()
#     alert.setText("b")
#     alert.exec_()
# layout.addWidget(somebutton)
# somebutton.clicked.connect(clicked)
#
# window.setLayout(layout)
# window.show()
#
# app.setStyle('Fusion')
#
# app.exec()