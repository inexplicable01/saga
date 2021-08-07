from Graphics.QAbstract.ConflictListModel import CURRENTCOL, CURRENTREVCOL,NEWESTREVCOL,UPSTREAMCOL
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaApp.FileObjects import FileTrack
from os.path import join
from Config import sourcecodedirfromconfig

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
        dialog = QDialog(self)
        dialog.setWindowFlags(dialog.windowFlags() |
                              Qt.WindowSystemMenuHint |
                              Qt.WindowMinMaxButtonsHint)

        self.conflicttableview.setModel(self.conflictmodel)
        self.conflicttableview.resizeRowsToContents()
        self.conflicttableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conflicttableview.clicked.connect(self.checkifallchecked)
        self.noticetableview.setModel(self.noticelistmodel)
        self.noticetableview.resizeRowsToContents()
        self.noticetableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.noticetableview.clicked.connect(self.checkifallchecked)

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
