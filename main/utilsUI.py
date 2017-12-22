import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
from .core import general_utils as ul
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

# Get Maya Main Window
mayaMainWindow = pm.ui.Window('MayaWindow').asQtObject()
# Wrapper
SIGNAL = QtCore.Signal
# UIClass
class RenamerUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(RenamerUI, self).__init__()
        try:
            pm.deleteUI('RenamerWindow')
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Renamer')
        self.setObjectName('RenamerWindow')
        self.setMinimumSize(250,100)
        self._initMainUI()

    def _initMainUI(self):
        self.mainCtner = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)