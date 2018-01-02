import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
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
class Utilities(QtWidgets.QMainWindow):
    def __init__(self):
        super(Utilities, self).__init__()
        try:
            pm.deleteUI('PipelineToolWindow')
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Pipeline Tools')
        self.setObjectName('PipelineToolWindow')
        self.setMinimumSize(250,100)
        self._initMainUI()

    def _initMainUI(self, parent=None):
        self.mainCtner = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QGridLayout(self.mainCtner)
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
    
def rigUtilLayout(self):
    self.rigUtilUI = []

    self.button

class PipelineTool(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(PipelineTool, self).__init__()
        try:
            pm.deleteUI('PipelineToolWindow')
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Pipeline Tools')
        self.setObjectName('PipelineToolWindow')
        self.setMinimumSize(250,100)
        self._initMainUI()

    def _initMainUI(self):
        self.mainCtner = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)