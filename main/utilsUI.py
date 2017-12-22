import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
import string
from ..core import general_utils as ul
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
class Renamer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Renamer, self).__init__()
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
        # self.setFixedSize(500,300)
        self._initMainUI()

    def connectFunction(self):
        pass

    def _initMainUI(self):
        self.mainCtner = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.addWidgets()
        self.setStyle()

    def addWidgets(self):
        self.mainLayout.addWidget(self.mainNameBox())
        self.mainLayout.addWidget(self.optionBox())
        layout = QtWidgets.QGridLayout()
        for i in range(3):
            layout.setColumnMinimumWidth(i,100)
        self.rename_button = QtWidgets.QPushButton('Apply')
        layout.addWidget(self.rename_button,0,4)
        self.mainLayout.addLayout(layout)

    def setStyle(self):
        styleSheet = """
            QPushButton {
                background-color: rgb(60,60,60);
                }
            QGroupBox {
                background-color: rgb(80,80,80);
                border-radius: 4px;
            }
            """
        self.mainCtner.setStyleSheet(styleSheet)

    @staticmethod
    def labelGroup(name, widget, parent, *args, **kws):
        layout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel(name)
        createWidget = widget()
        layout.addWidget(label,0,1)
        layout.addWidget(createWidget,0,2)
        parent.addLayout(layout, *args, **kws)
        return createWidget

    def mainNameBox(self):
        self.mainNameGroup = QtWidgets.QGroupBox()
        # self.mainNameGroup.setFixedHeight(100)
        # create Layout
        self.mainNameLayout = QtWidgets.QGridLayout()
        # Create Widgets
        self.deletePrefix_button = QtWidgets.QPushButton('Delete Prefix')
        self.prefix_label = QtWidgets.QLabel('Prefix: ')
        self.prefix_text = QtWidgets.QLineEdit()
        self.name_label = QtWidgets.QLabel('Name: ')
        self.name_text = QtWidgets.QLineEdit()
        self.deleteNameBefore_button = QtWidgets.QPushButton('X>')
        self.deleteNameAfter_button = QtWidgets.QPushButton('<X')
        self.suffix_label = QtWidgets.QLabel('Suffix: ')
        self.suffix_text = QtWidgets.QLineEdit()
        self.deleteSuffix_button = QtWidgets.QPushButton('Delete Suffix')
        self.separator_label = QtWidgets.QLabel('Separator: ')
        self.separator_text = QtWidgets.QLineEdit()
        self.getName_button = QtWidgets.QPushButton('Get Name')
        # Set Widget Value
        self.separator_text.setText('_')
        # add Widgets
        def addWidget(widget,*args):
            self.mainNameLayout.addWidget(widget,*args)    
        addWidget(self.deletePrefix_button,2,0)
        addWidget(self.prefix_label,0,0)
        addWidget(self.prefix_text,1,0)
        addWidget(self.name_label,0,1)
        addWidget(self.name_text,1,1)
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.addWidget(self.deleteNameBefore_button)
        subLayout.addWidget(self.separator_label)
        subLayout.addWidget(self.separator_text)
        subLayout.addWidget(self.getName_button)
        subLayout.addWidget(self.deleteNameAfter_button)
        self.mainNameLayout.addLayout(subLayout,2,1)
        addWidget(self.suffix_label,0,2)
        addWidget(self.suffix_text,1,2)
        addWidget(self.deleteSuffix_button,2,2)

        # Add Layout
        self.mainNameGroup.setLayout(self.mainNameLayout)
        return self.mainNameGroup
    
    def optionBox(self):
        self.incGroup = QtWidgets.QGroupBox()
        # create Layout
        self.incLayout = QtWidgets.QHBoxLayout()
        self.incLayout.addWidget(self.numberingBox())
        self.incLayout.addWidget(self.letteringBox())
        self.incLayout.addWidget(self.directionBox())
        self.incGroup.setLayout(self.incLayout)
        return self.incGroup

    def numberingBox(self):
        self.numberGroup = QtWidgets.QGroupBox()
        # Create Layout
        self.numberLayout = QtWidgets.QVBoxLayout()
        self.numberLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        self.numberLayout.addWidget(QtWidgets.QLabel('Numbering:'))
        self.numberEnable_checkbox = QtWidgets.QCheckBox('Enable')
        self.numberLayout.addWidget(self.numberEnable_checkbox)
        self.startNumber_spinBox = self.labelGroup(
            'Start At: ',
            QtWidgets.QSpinBox,
            self.numberLayout)
        self.padding_spinBox = self.labelGroup(
            'Padding: ',
            QtWidgets.QSpinBox,
            self.numberLayout)
        self.numberPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.numberLayout)
        # Set Widget
        for id, i in enumerate(['After Name', 'After Suffix']):
            self.numberPosition_comboBox.insertItem(id,i)
        # Add Layout
        self.numberGroup.setLayout(self.numberLayout)
        return self.numberGroup

    def letteringBox(self):
        self.letterGroup = QtWidgets.QGroupBox()
        self.letterLayout = QtWidgets.QVBoxLayout()
        self.letterLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        self.letterLayout.addWidget(QtWidgets.QLabel('Lettering:'))
        self.letterEnable_checkbox = QtWidgets.QCheckBox('Enable')
        self.letterLayout.addWidget(self.letterEnable_checkbox)
        self.startletter_comboBox = self.labelGroup(
            'Start At: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        self.letterPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        # Set Widget
        for id, ch in enumerate(string.ascii_uppercase):
            self.startletter_comboBox.insertItem(id,ch)
        for id, i in enumerate(['After Name', 'After Suffix']):
            self.letterPosition_comboBox.insertItem(id,i)
        # Add Layout
        self.letterGroup.setLayout(self.letterLayout)
        return self.letterGroup

    def directionBox(self):
        self.directionGroup = QtWidgets.QGroupBox()
        self.directionLayout = QtWidgets.QVBoxLayout()
        self.directionLayout.addWidget(QtWidgets.QLabel('Direction:'))
        self.directionLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        group = QtWidgets.QHBoxLayout()
        self.directionEnable_checkbox = QtWidgets.QCheckBox('Enable')
        group.addWidget(self.directionEnable_checkbox)
        self.directionAddSeparator_checkbox = QtWidgets.QCheckBox('Add Separator')
        group.addWidget(self.directionAddSeparator_checkbox)
        self.directionLayout.addLayout(group)
        self.startdirection_comboBox = self.labelGroup(
            'Direction: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        self.directionPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        # Set Widget
        for id, ch in enumerate(
                ("Left,Right,Up,Down,Center,Bottom,Middle"+\
                "L,R,T,B,C,M,Mid").split(',')):
            self.startdirection_comboBox.insertItem(id,ch)
        for id, i in enumerate(['Before Name','After Name','Before Suffix','After Suffix']):
            self.directionPosition_comboBox.insertItem(id,i)
        # Add Layout
        self.directionGroup.setLayout(self.directionLayout)
        return self.directionGroup
    
    def rename(self):
        separator = self.separator_text.text()
        newName = separator.join([])
        if pm.selected():
            for o in pm.selected():
                if hasattr(o, 'rename'):
                    o.rename(newName)


    @classmethod
    def showUI(cls):
        cls().show()