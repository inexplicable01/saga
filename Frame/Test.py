from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys,os

class OpenDir(QMainWindow):
    def __init__(self):
        super(OpenDir, self).__init__()
        # self.openDirectory()
        self.button = QPushButton('Open', self)
        self.button.clicked.connect(self.openDirectory)
        self.setCentralWidget(self.button)

    def openDirectory(self):
        print("Hi i am openDirectory Function . I will open Directory selected ")
        self.openDirectoryDialog = QFileDialog.getExistingDirectory(self, "Get Dir Path")
        print(self.openDirectoryDialog)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F1:
            os.system('xdg-open "%s"' % self.openDirectoryDialog)

def main():
    app = QApplication(sys.argv)
    ui=OpenDir()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()