try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

class Ui_InsertBlock(object):
    def setupUi(self, InsertBlock):
        InsertBlock.setObjectName("InsertBlock")
        InsertBlock.resize(400, 107)
        self.gridLayout = QtGui.QGridLayout(InsertBlock)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(InsertBlock)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 2)
        self.lineEdit = QtGui.QLineEdit(InsertBlock)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 2)
 
        self.retranslateUi(InsertBlock)
        QtCore.QMetaObject.connectSlotsByName(InsertBlock)
        InsertBlock.setTabOrder(self.lineEdit, self.listWidget)
        return InsertBlock
 
    def retranslateUi(self, InsertBlock):
        InsertBlock.setWindowTitle(QtGui.QApplication.translate("InsertBlock", "Insert Block", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == 'main':
    app = QtWidgets.QApplication([])
    win = Ui_InsertBlock().setupUi(QtWidgets.QMainWindow())
    win.show()
    app.exec_()