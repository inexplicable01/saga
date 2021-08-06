from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.FileObjects import FileTrack
from os.path import join
from Config import sourcecodedirfromconfig
# uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","newContainer.ui"), self)

class updateDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics","UI","updateDialog.ui"), self)
    def update(self):
        if self.exec_() == QDialog.Accepted:
            return True
        else:
            return False

class ganttChartProject(QDialog):
    def __init__(self):
        super().__init__()
        join(sourcecodedirfromconfig, "Graphics", "UI", "projectChart.ui")
        # uic.loadUi("Graphics/UI/projectChart.ui", self)
        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "projectChart.ui"), self)
        self.actualButton.clicked.connect(self.showActualChart)
        self.scheduledButton.clicked.connect(self.showScheduledChart)
    def showChart(self):
        self.exec()
    def showActualChart(self):
        self.titleLabel.setText("Actual Gantt Chart")
        self.chartPic.setPixmap(QPixmap(join(sourcecodedirfromconfig, "Graphics", "UI", "Demo_Project_Gantt_Completed.png")))
    def showScheduledChart(self):
        self.chartPic.setPixmap(QPixmap(join(sourcecodedirfromconfig, "Graphics", "UI", "Demo_Project_Gantt.png")))
        self.titleLabel.setText("Scheduled Gantt Chart")

# class errorPopUp(QDialog):
#     def __init__(self):
#         super().__init__()
#         uic.loadUi("Graphics/UI/errorMessage.ui",self)
#     def showMessage(self, text):
#         self.errorText.setText(text)
#         self.exec()

class downloadProgressBar(QWidget):
    def __init__(self, fileName):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "downloadProgressBar.ui"), self)
        self.fileNameLabel.setText(fileName)
    def updateProgress(self, value):
        self.progressBar.setValue(value)
        self.show()
        # self.progressBar.setProperty("value", percent)

class ErrorMessage(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ErrorMessage')
        self.setIcon(QMessageBox.Warning)
        self.setText('Please Fill In All Container Information First')
        self.setStandardButtons(QMessageBox.Ok)
    def showError(self):
        self.exec_()

# class inputFileDialog(QDialog):
#     def __init__(self, ContainerId, fileheader):
#         super().__init__()
#         # self.fileName = fileName
#         uic.loadUi("Graphics/UI/inputFileDialog.ui", self)
#         self.ContainerId, = ContainerId,
#         self.fileheader = fileheader
#         self.containerName_label.setText(self.ContainerId,)
#         self.fileNameLabel.setText(fileheader)
#
#     def getInputs(self):
#         if self.exec_() == QDialog.Accepted:
#             return {'Container': self.ContainerId, 'type': typeInput}
#         else:
#             return None

class removeFileDialog(QDialog):
    def __init__(self, fileheader,candelete, candeletemesssage):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "removeFileDialog.ui"), self)
        self.fileheader = fileheader
        self.fileNameLabel.setText(self.fileheader)

        if not candelete:
            self.deletewarninglbl.setText(candeletemesssage)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def removeFile(self):
        if self.exec_() == QDialog.Accepted:
            return True
        else:
            return None


from Graphics.QAbstract.ConflictListModel import CURRENTCOL, CURRENTREVCOL,NEWESTREVCOL,UPSTREAMCOL
class refreshContainerPopUp(QDialog):
    def __init__(self, conflictmodel, noticelistmodel):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "ConflictPopUp.ui"), self)
        # self.changes = changes
        self.conflictmodel = conflictmodel
        self.noticelistmodel = noticelistmodel
        # self.addedmodel = addedmodel
        # self.deletedmodel = deletedmodel
        # self.upstreamlistmodel = upstreamlistmodel
        # self.conflictsummary={}
        # for fileheader in changes.keys():
        #     self.conflictsummary[fileheader] = None

        self.conflicttableview.setModel(self.conflictmodel)
        self.conflicttableview.resizeRowsToContents()
        self.conflicttableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conflicttableview.clicked.connect(self.checkifallchecked)
        self.noticetableview.setModel(self.noticelistmodel)
        self.noticetableview.resizeRowsToContents()
        self.noticetableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.noticetableview.clicked.connect(self.checkifallchecked)
        # self.addedView.setModel(self.addedmodel)
        # self.addedView.resizeRowsToContents();
        # self.addedView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.addedView.clicked.connect(self.checkifallchecked)
        # self.deletedView.setModel(self.deletedmodel)
        # self.deletedView.resizeRowsToContents();
        # self.deletedView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.deletedView.clicked.connect(self.checkifallchecked)
        # self.upstreamtable.setModel(self.upstreamlistmodel)
        # self.upstreamtable.resizeRowsToContents();
        # self.upstreamtable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.upstreamtable.clicked.connect(self.checkifallchecked)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.filelist={}
        self.rowschecked={}
        for i,fileheader in enumerate(conflictmodel.rowheader):
            self.rowschecked[fileheader] = False
            self.filelist[fileheader] = {
                'change': conflictmodel.changearray[i],
                'wf':None,'lf':None,'nf':None,'uf':None,
            }
        for i,fileheader in enumerate(noticelistmodel.rowheader):
            self.filelist[fileheader] = {
                                'change': noticelistmodel.changearray[i],
                'wf':None,'lf':None,'nf':None,'uf':None,
            }


    def checkifallchecked(self, index):
        # listofmodels = [self.conflictmodel, self.addedmodel, self.deletedmodel, self.upstreamlistmodel]
        c = index.column()
        r = index.row()
        model = index.model()
        fileheader = model.rowheader[r]

        change=  self.filelist[fileheader]['change']

        # print(index.model().headers[c])
        # print(index.model().conflictdata[r])
        # for checkboxcol in model.checkcolumns:
        #     checkboxindex = model.index(r, checkboxcol)
        selectedvalue = model.checkState(QPersistentModelIndex(index))
        if change.inputscenariono in [1,3,4] or change.reqoutscenariono in [1,3,4]:
            for checkboxcol in model.checkcolumns:
                checkboxindex = model.index(r, checkboxcol)
                model.setData(checkboxindex, False, role=Qt.CheckStateRole)
            model.setData(index, selectedvalue, role=Qt.CheckStateRole)

        if model.checkState(QPersistentModelIndex(index)):
            if c == CURRENTCOL:
                self.filelist[fileheader]['wf']=change.wffiletrack
            elif c == CURRENTREVCOL:
                self.filelist[fileheader]['lf']=change.lffiletrack
            elif c == NEWESTREVCOL:
                self.filelist[fileheader]['nf'] = change.nffiletrack
            elif c == UPSTREAMCOL:
                self.filelist[fileheader]['uf'] = change.uffiletrack
        else:
            if c == CURRENTCOL:
                self.filelist[fileheader]['wf'] = None
            elif c == CURRENTREVCOL:
                self.filelist[fileheader]['lf'] = None
            elif c == NEWESTREVCOL:
                self.filelist[fileheader]['nf'] = None
            elif c == UPSTREAMCOL:
                self.filelist[fileheader]['uf'] = None
        rowchecked = False
        for checkboxcol in model.checkcolumns:
            checkboxindex = model.index(r, checkboxcol)
            if model.checkState(QPersistentModelIndex(checkboxindex)):
                rowchecked = True

        self.rowschecked[fileheader] = rowchecked
        # for colno in model.checkcolumns:
        #     if model.checkState(QPersistentModelIndex(index)):
        #     else:
        #         self.filelist[fileheader] = None

        eachrowhasonecheck = True

        for fileheader, value in self.rowschecked.items():
            if not value:
                eachrowhasonecheck = False
            # for checkboxcol in model.checkcolumns:
            #     checkboxindex = model.index(r, checkboxcol)
            #     self.filelist[fileheader][checkboxcol]
            #
        # for selection in self.filelist.values():
        #     if selection is None:
        #         allboxeschecked = False
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(eachrowhasonecheck)
        model.layoutChanged.emit()



    def selectFiles(self):
        if self.exec_() == QDialog.Accepted:
            combinedactionstate = {}
            combinedactionstate.update(self.conflictmodel.actionstate)
            combinedactionstate.update(self.noticelistmodel.actionstate)

            return combinedactionstate
        # self.fileList = {}
        # for fileheader in self.changes.keys():
        # listofmodels = [self.conflictmodel, self.addedmodel, self.deletedmodel, self.upstreamlistmodel]
        # # listofoption1str = ['Overwrite','Download', 'Delete']
        # # listofoption2str =['Download Copy', 'Do not download', 'Do not delete']
        # # col1 = [1,1,1]
        # # col2 = [2,2,2]
        #
        # for listi, model in enumerate(listofmodels):
        #     for index in model.checks:
        #         # how to get the row of the index from self.model.checks
        #         fileheader = model.conflictdata[index.row()]
        #         # if self.conflictmodel.conflictdata[index.row()] == fileheader:
        #         self.fileList[fileheader] = model.headers[index.column()]
        else:
            return None

class commitDialog(QDialog):
    def __init__(self, containerName, description, commitMessage):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "commitContainerDialog.ui"), self)
        self.containerName = containerName
        self.containerNameLabel.setText(self.containerName)
    def commit(self):
        if self.exec_() == QDialog.Accepted:
            return True
        else:
            return False

class commitConflictCheck(QDialog):
    def __init__(self, conflictfiles):
        super().__init__()

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "commitConflictList.ui"), self)
        for filename in conflictfiles:
            self.listWidget.addItem(filename)
    def showconflicts(self):
        if self.exec_() == QDialog.Accepted:
            print('Acknowledged')
        else:
            return None

class alteredinputFileDialog(QDialog):
    def __init__(self, alterfiletrack:FileTrack):
        super().__init__()
        # self.fileName = fileName

        uic.loadUi(join(sourcecodedirfromconfig, "Graphics", "UI", "alteredinputFileDialog.ui"), self)
        self.alterfiletrack = alterfiletrack
        self.old_filename_lbl.setText(alterfiletrack.file_name)
        self.old_fileheader_lbl.setText(alterfiletrack.FileHeader)

        linkstr= alterfiletrack.connection.refContainerId+'_'+alterfiletrack.connection.branch + '_'+ alterfiletrack.connection.Rev
        self.nfilename_edit.setText(linkstr + '_' + alterfiletrack.file_name)
        self.nfileheader_edit.setText(linkstr + '_' + alterfiletrack.FileHeader)
        # self.containerName_label.setText(self.containerName)
        # self.fileName_label.setText(fileheader)
    def getInputs(self):
        if self.exec_() == QDialog.Accepted:

            return { 'alterfiletrack':self.alterfiletrack,
                    'nfileheader': self.nfileheader_edit.text(),
                    'nfilename': self.nfilename_edit.text(),
                    'persist': self.persist_cb.checkState()}
        else:
            return None

