import os
from maya import OpenMayaUI, cmds, mel
import pymel.core as pm
import uiStyle
import logging
from ..core import rig_class as rcl
from functools import partial
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

reload(rcl)
reload(uiStyle)
# ------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

# ------------------------------------------------------------------------------

SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT

# ------------------------------------------------------------------------------   

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    # window = OpenMayaUI.MQtUtil.mainWindow()
    # window = shiboken.wrapInstance(long(window), QMainWindow)
    window = pm.ui.Window('MayaWindow').asQtObject()
    return window

# ------------------------------------------------------------------------------

class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
        self._name = 'ControlCreatorWindow'
        try:
            pm.deleteUI(self._name)
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaWindow())
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Control Maker')
        self.setObjectName(self._name)
        self.setStyleSheet(uiStyle.styleSheet)

    def _initUIValue(self):
        self.nameSuffix = 'ctl'
        self.name = "controlObject%s"%self.nameSuffix
        self.controlObject = rcl.ControlObject(color=(255,255,0,255))
        self.controlColor = tuple(self.controlObject.color)

    def _initMainUI(self):
        self._initUIValue()
        # create Widget
        self.topFiller = QtWidgets.QWidget(self)
        self.topFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.bottomFiller = QtWidgets.QWidget(self)
        self.bottomFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainCtner = QtWidgets.QWidget(self)
        # Create Layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        # Add widget
        self.mainLayout.addWidget(self.topFiller)
        self.createMainWidgets()
        self.mainLayout.addWidget(self.bottomFiller)
        # Set Layout
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.setStyleSheet(uiStyle.styleSheet)
        self.createMenuBar()
        self.createStatusBar()
        self._connectFunction()

    def createMainWidgets(self):
        self.mainLayout.addWidget(self.controlShapeBox())

    def controlShapeBox(self):
        uiGrp = QtWidgets.QGroupBox('Control Shape Maker')
        layout = QtWidgets.QVBoxLayout()
        # - Create Sub Layout --------------------------
        controlAttributeGroupLayout = QtWidgets.QGridLayout()
        controlNameAttributeLayout = QtWidgets.QVBoxLayout()
        controlNameLayout = QtWidgets.QHBoxLayout()
        controlAttributeLayout = QtWidgets.QHBoxLayout()
        controlShapeLayout = QtWidgets.QVBoxLayout()
        controlOptionGroup = QtWidgets.QGroupBox('Option')
        controlOptionGroupLayout = QtWidgets.QHBoxLayout()
        controlOptionGroup.setLayout(controlOptionGroupLayout)
        createButtonLayout = QtWidgets.QHBoxLayout()
        # - Create Widget ------------------------------
        self.controlName_text = uiStyle.labelGroup(
            "Name: ", QtWidgets.QLineEdit, controlNameLayout)
        self.controlNameSuffix_comboBox = uiStyle.labelGroup(
            "Suffix: ", QtWidgets.QComboBox, controlNameLayout)
        controlNameAttributeLayout.addLayout(controlNameLayout)
        self.controlLength_floatspinbox = uiStyle.labelGroup(
            "Length: ", QtWidgets.QDoubleSpinBox, controlAttributeLayout)
        self.controlRadius_floatspinbox = uiStyle.labelGroup(
            "Radius: ", QtWidgets.QDoubleSpinBox, controlAttributeLayout)
        self.controlColor_button = uiStyle.labelGroup(
            "Color: ", QtWidgets.QPushButton, controlAttributeLayout)
        controlNameAttributeLayout.addLayout(controlAttributeLayout)
        self.controlType_combobox = uiStyle.labelGroup(
            "Type: ", QtWidgets.QComboBox, controlShapeLayout)
        self.controlSmoothness_combobox = uiStyle.labelGroup(
            "Step: ", QtWidgets.QComboBox, controlShapeLayout)
        self.controlAxis_combobox = uiStyle.labelGroup(
            "Axis: ", QtWidgets.QComboBox, controlShapeLayout)
        controlAttributeGroupLayout.addLayout(controlNameAttributeLayout,0,0)
        controlAttributeGroupLayout.addLayout(controlShapeLayout,0,1)
        controlAttributeGroupLayout.setColumnStretch(0,2)
        layout.addLayout(controlAttributeGroupLayout)
        self.groupControl_checkbox,\
        self.setAxis_checkbox,\
        self.mirror_checkbox = uiStyle.multiOptionsLayout(
            ['group', 'force set axis', 'mirror'],
            parent=controlOptionGroupLayout
        )
        self.offsetX_floatspinbox,\
        self.offsetY_floatspinbox,\
        self.offsetZ_floatspinbox = uiStyle.multiLabelLayout(
            ['x', 'y', 'z'],
            QtWidgets.QDoubleSpinBox,
            groupLabel='Offset: ',
            parent=controlOptionGroupLayout
        )
        self.changeControlShape_button = QtWidgets.QPushButton('Change Shape')
        self.createControl_button = QtWidgets.QPushButton('Create Control')
        self.setColor_button = QtWidgets.QPushButton('Set Color')
        createButtonLayout.addWidget(self.changeControlShape_button)
        createButtonLayout.addWidget(self.createControl_button)
        createButtonLayout.addWidget(self.setColor_button)
        layout.addWidget(controlOptionGroup)
        layout.addLayout(createButtonLayout)
        # ----------------------------------------------
        self.controlNameSuffix_comboBox.addItems(['ctl','cnt','control'])
        self.controlLength_floatspinbox.setValue(self.controlObject.length)
        self.controlRadius_floatspinbox.setValue(self.controlObject.radius)
        self.controlType_combobox.addItems(self.controlObject._controlType.keys())
        self.controlSmoothness_combobox.addItems(self.controlObject._resolutions.keys())
        self.controlAxis_combobox.addItems(self.controlObject._axisList)
        self.controlColor_button.setStyleSheet(".QPushButton { background-color: rgba(%d,%d,%d,%d) } "%tuple(self.controlObject.color))
        # ----------------------------------------------
        uiGrp.setLayout(layout)
        return uiGrp


    def createMenuBar(self):
        # create Action
        def menuItem(name, func , parent=None):
            newAction = QtWidgets.QAction(name, self)
            newAction.triggered.connect(func)
            if parent:
                parent.addAction(newAction)
            return newAction
        self.reset_action = QtWidgets.QAction('Reset', self)
        self.reset_action.setToolTip('Reset UI To Default Value')
        self.reset_action.setStatusTip('Reset UI To Default Value')
        self.reset_action.triggered.connect(self.resetUI)
        # create Menu
        self.menubar = self.menuBar()
        self.optionmenu = self.menubar.addMenu('Option')
        self.optionmenu.addAction(self.reset_action)

    def createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Tool to create rig Controls')
    # UI Changed Action
    def showEvent(self, event):
        self._initMainUI()
        # self.updateUIJob = pm.scriptJob(
        #     e= ["SelectionChanged",self.autoUpdateUI],
        #     parent = self._name,
        #     rp=True)
        self.show()

    def closeEvent(self, event):
        # if hasattr(self, 'updateUIJob'):
        #     if pm.scriptJob(exists=self.updateUIJob):
        #         pm.scriptJob(k=self.updateUIJob)
        self.close()

    def autoUpdateUI(self):
        pass

    def resetUI(self):
        self._initMainUI()
        self.show()

    def _connectFunction(self):
        self.controlName_text.textEdited.connect(self.onChangeName)
        self.controlNameSuffix_comboBox.currentTextChanged.connect(self.onChangeNameSuffix)
        self.controlRadius_floatspinbox.valueChanged.connect(self.onChangeRadius)
        self.controlLength_floatspinbox.valueChanged.connect(self.onChangeLength)
        self.controlColor_button.clicked.connect(self.onChangeColor)

    def onChangeName(self, value):
        self.controlObject.name = value
        print self.controlObject.name

    def onChangeNameSuffix(self, value):
        self.controlObject._suffix = value
        print self.controlObject.name

    def onChangeRadius(self, value):
        self.controlObject.radius = value
        print self.controlObject.radius

    def onChangeLength(self, value):
        self.controlObject.length = value
        print self.controlObject.length

    def onChangeColor(self):
        colorDialog = QtWidgets.QColorDialog.getColor(QtCore.Qt.yellow)
        self.controlObject.color = colorDialog.getRgb()
        self.controlColor_button.setStyleSheet(".QPushButton { background-color: rgba(%d,%d,%d,%d) } "%tuple(self.controlObject.color))

def show():
    win = main()
    win.show()
    return win

if __name__ =='__main__':
    try:
        app = QtWidgets.QApplication([])
    except:
        raise
    show()
    if app in globals():
        app.exec_()