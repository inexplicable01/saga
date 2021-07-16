import sys
from PyQt5 import QtCore, QtWidgets
from Graphics.QAbstract.SagaTreeDelegate import SagaTreeDelegate
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Food(object):
    def __init__(self, name, shortDescription, note, parent = None):
        self.data = (name, shortDescription, note);
        self.parentIndex = parent

class FavoritesTableModel(QAbstractItemModel):
    def __init__(self):
        super(FavoritesTableModel, self).__init__()
        self.foods = []
        self.parent =None
        self.loadData()

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.foods[index.row()].data[index.column()]
        return None

    def rowCount(self, index=QModelIndex()):
        return len(self.foods)

    def columnCount(self, index=QModelIndex()):
        return 3

    def index(self, row, column, parent = QModelIndex()):
        return self.createIndex(row, column, parent)

    # def parent(self, index):
    #     if self.parent is None:
    #         return self.foods[0].parentIndex

    def loadData(self):
        allFoods=("Apples", "Pears", "Grapes", "Cookies", "Stinkberries")
        allDescs = ("Red", "Green", "Purple", "Yummy", "Huh?")
        allNotes = ("Bought recently", "Kind of delicious", "Weird wine grapes",
                    "So good...eat with milk", "Don't put in your nose")
        for name, shortDescription, note in zip(allFoods, allDescs, allNotes):
            food = Food(name, shortDescription, note, self)
            self.foods.append(food)

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


class CustomNode(QtCore.QAbstractItemModel):
    def __init__(self, data):
        QtCore.QAbstractItemModel.__init__(self)
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]


    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)####is this listing the position index of the child relative to parent?
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)## ideally there should be a recusive
        ## this is a nightmare.


class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = CustomNode(None)
        for node in nodes:
            self._root.addChild(node)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                print('index',index.row(), index.column())
                print('parent',p.row())
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()### this ensures that only 2nd level child nodes set columnCount

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:

            return node.data(index.column())
        return None


class MyTree():
    """
    """
    def __init__(self):
        self.items = []

        # Set some random data:
        for i in 'abc':
            self.items.append(CustomNode(i))
            self.items[-1].addChild(CustomNode(['d', 'e', 'f']))
            self.items[-1].addChild(CustomNode(['g', 'h', 'i']))
        self.items[1]._children[0].addChild(CustomNode(['there', 'is', 'hope','huh']))
        self.items[2]._children[1].addChild(CustomNode(['d', 'e', 'f']))

        self.tw = QtWidgets.QTreeView()
        self.tw.setModel(CustomModel(self.items))
        self.tw.setItemDelegate(SagaTreeDelegate())
        self.tw.header().moveSection(1,0)

    def add_data(self, data):
        """
        TODO: how to insert data, and update tree.
        """
        # self.items[-1].addChild(CustomNode(['1', '2', '3']))
        # self.tw.setModel(CustomModel(self.items))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mytree = MyTree()
    mytree.tw.show()
    sys.exit(app.exec_())