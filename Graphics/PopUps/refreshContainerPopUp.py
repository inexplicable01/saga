from Graphics.QAbstract.ConflictListModel import CURRENTCOL, CURRENTREVCOL,NEWESTREVCOL,UPSTREAMCOL
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SagaCore.Track import FileTrack
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
        for i,citemname in enumerate(conflictmodel.rowheader):
            self.rowschecked[citemname] = False
            self.filelist[citemname] = {
                'change': conflictmodel.changearray[i],
                'wf':None,'rf':None,'nf':None,'uf':None,
            }
        for i,citemname in enumerate(noticelistmodel.rowheader):
            self.filelist[citemname] = {
                                'change': noticelistmodel.changearray[i],
                'wf':None,'rf':None,'nf':None,'uf':None,
            }


    def checkifallchecked(self, index):
        # listofmodels = [self.conflictmodel, self.addedmodel, self.deletedmodel, self.upstreamlistmodel]
        c = index.column()
        r = index.row()
        model = index.model()
        citemname = model.rowheader[r]

        change=  self.filelist[citemname]['change']

        selectedvalue = model.checkState(QPersistentModelIndex(index))
        if change.inputscenariono in [1,3,4] or change.reqoutscenariono in [1,3,4]:
            for checkboxcol in model.checkcolumns:
                checkboxindex = model.index(r, checkboxcol)
                model.setData(checkboxindex, False, role=Qt.CheckStateRole)
            model.setData(index, selectedvalue, role=Qt.CheckStateRole)

        if model.checkState(QPersistentModelIndex(index)):
            if c == CURRENTCOL:
                self.filelist[citemname]['wf']=change.wffiletrack
            elif c == CURRENTREVCOL:
                self.filelist[citemname]['rf']=change.lffiletrack
            elif c == NEWESTREVCOL:
                self.filelist[citemname]['nf'] = change.nffiletrack
            elif c == UPSTREAMCOL:
                self.filelist[citemname]['uf'] = change.uffiletrack
        else:
            if c == CURRENTCOL:
                self.filelist[citemname]['wf'] = None
            elif c == CURRENTREVCOL:
                self.filelist[citemname]['rf'] = None
            elif c == NEWESTREVCOL:
                self.filelist[citemname]['nf'] = None
            elif c == UPSTREAMCOL:
                self.filelist[citemname]['uf'] = None
        rowchecked = False
        for checkboxcol in model.checkcolumns:
            checkboxindex = model.index(r, checkboxcol)
            if model.checkState(QPersistentModelIndex(checkboxindex)):
                rowchecked = True
            if change.alterinput:
                if len(model.actionstate[change.citemname])>0:
                    if len(model.actionstate[change.citemname][0]['newfileheader'])>4:
                        rowchecked= True

        if citemname in self.rowschecked.keys():## this is to ensure the notice headers don't get counted also.
            self.rowschecked[citemname] = rowchecked
        # for colno in model.checkcolumns:
        #     if model.checkState(QPersistentModelIndex(index)):
        #     else:
        #         self.filelist[citemname] = None

        eachrowhasonecheck = True

        for citemname, value in self.rowschecked.items():
            if not value:
                eachrowhasonecheck = False
            # for checkboxcol in model.checkcolumns:
            #     checkboxindex = model.index(r, checkboxcol)
            #     self.filelist[citemname][checkboxcol]
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
        # for citemname in self.changes.keys():
        # listofmodels = [self.conflictmodel, self.addedmodel, self.deletedmodel, self.upstreamlistmodel]
        # # listofoption1str = ['Overwrite','Download', 'Delete']
        # # listofoption2str =['Download Copy', 'Do not download', 'Do not delete']
        # # col1 = [1,1,1]
        # # col2 = [2,2,2]
        #
        # for listi, model in enumerate(listofmodels):
        #     for index in model.checks:
        #         # how to get the row of the index from self.model.checks
        #         citemname = model.conflictdata[index.row()]
        #         # if self.conflictmodel.conflictdata[index.row()] == citemname:
        #         self.fileList[citemname] = model.headers[index.column()]
        else:
            return None
