#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymel.core as pm
import logging
from functools import partial
from string import ascii_uppercase as alphabet
from itertools import product
import uiStyle
# from ..core import general_utils as ul
# from ..core import rigging_utils as rul
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

# Logging initialize #
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
# Get Maya Main Window
mayaMainWindow = pm.ui.Window('MayaWindow').asQtObject()
# Wrapper
SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT
#
def iter_hierachy(root, filter = ['transform']):
    '''yield hierachy generator object with stack method'''
    stack = [root]
    level = 0
    while stack:
        level +=1
        node = stack.pop()
        yield node
        if hasattr(node, 'getChildren'):
            childs = node.getChildren( type=filter )
            if len(childs) > 1:
                log.debug('\nsplit to %s, %s'%(len(childs),str(childs)))
                for child in childs:
                    subStack = iter_hierachy(child)
                    for subChild in subStack:
                        yield subChild
            else:
                stack.extend( childs )
# UIClass
class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
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
        # init UI
        self._initMainUI()
        self.createMenuBar()
        self.statusBar()

    # Util Function
    @staticmethod
    def getUIValue(valueName, defaultValue=""):
        if valueName in pm.optionVar:
            return pm.optionVar[valueName]
        else:
            pm.optionVar[valueName] = defaultValue
            return defaultValue

    @staticmethod
    def setUIValue(valueName, value):
        pm.optionVar[valueName] = value

    @staticmethod
    def labelGroup(name, widget, parent, *args, **kws):
        layout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel(name)
        # label.setAlignment(QtCore.Qt.AlignRight)
        createWidget = widget()
        layout.addWidget(label,0,0)
        layout.addWidget(createWidget,0,1)
        parent.addLayout(layout, *args, **kws)
        layout.setColumnStretch(1,2)
        layout.setColumnMinimumWidth(0,50)
        # layout.setContentsMargins(0,0,0,0)
        return createWidget

    @staticmethod
    def createSeparator():
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("QFrame { background-color: gray;}")
        return line

    # Initial Value Definition
    def _initUIValue(self):
        # Main Name Value
        self.nameValue = ""
        self.separator = '_'
        self.prefixValue = 0
        self.prefix_list = ',mdl,model'
        self.suffixValue = 0
        baseSuffix_list = 'bon,bone,ctl,cnt,loc,root'.split(',')
        suffix_list = ',mdl,skinDeform,secSkinDeform,gp,grp'.split(',') + baseSuffix_list[:]
        suffix_list.extend([i+'Gp' for i in baseSuffix_list])
        suffix_list.extend([i+'Grp' for i in baseSuffix_list])
        self.suffix_list = ','.join(suffix_list)
        # Replace Name Value
        self.searchName = 'Left'
        self.replaceName = 'Right'
        # Optional Name Variable Toggle State
        self.numBool = True
        self.numAddSepBool = False
        self.letterBool = False
        self.letterIterBool = False
        self.letterAddSepBool = False
        self.directionBool = False
        self.dirAddSepBool = False
        self.renameChildBool = False
        self.renameAllBool = False
        # Optional Name Variable Position
        self.numPos = 0
        self.letterPos = 0
        self.dirPos = 1
        # Optional Name Variable Value
        self.startNum = 1
        self.numPadding = 2
        self.letterList = list(alphabet)
        self.letterList.extend(
            [''.join(list(i)) for i in list(
                product(alphabet, repeat=2))])
        self.startLetter = 0
        self.directionList = ("Left,Right,Up,Down,Center,Bottom,Middle,L,R,T,B,C,M,Mid")
        self.direction = 0

    def _getUIValue(self):
        # Main Name Value
        self.nameValue = self.getUIValue('renameUI_nameValue', self.nameValue)
        self.separator = self.getUIValue('renameUI_separatorValue', self.separator)
        self.prefixValue = self.getUIValue('renameUI_prefixValue', self.prefixValue)
        self.prefix_list = self.getUIValue('renameUI_prefixList', self.prefix_list)
        self.suffixValue = self.getUIValue('renameUI_suffixValue', self.suffixValue)
        self.suffix_list = self.getUIValue('renameUI_suffixList', self.suffix_list)
        # Name Replace Value
        self.searchName = self.getUIValue('renameUI_searchValue', self.searchName)
        self.replaceName = self.getUIValue('renameUI_replaceValue', self.replaceName)
        # Optional Name Variable Toggle State
        self.numBool = self.getUIValue('renameUI_numberToggle', self.numBool)
        self.numAddSepBool = self.getUIValue('renameUI_numberAddSepToggle', self.numAddSepBool)
        self.letterBool = self.getUIValue('renameUI_letterToggle', self.letterBool)
        self.letterIterBool = self.getUIValue('renameUI_letterIterToggle', self.letterIterBool)
        self.letterAddSepBool = self.getUIValue('renameUI_letterAddSepToggle', self.letterAddSepBool)
        self.directionBool = self.getUIValue('renameUI_dirToggle', self.directionBool)
        self.dirAddSepBool = self.getUIValue('renameUI_dirAddSepToggle', self.dirAddSepBool)
        self.renameChildBool = self.getUIValue('renameUI_renameChildToggle', self.renameChildBool)
        self.renameAllBool = self.getUIValue('renameUI_renameAllToggle', self.renameAllBool)
        # Optional Name Variable Position
        self.numPos = self.getUIValue('renameUI_numberPosValue', self.numPos)
        self.letterPos = self.getUIValue('renameUI_letterPosValue', self.letterPos)
        self.dirPos = self.getUIValue('renameUI_dirPosValue', self.dirPos)
        # Optional Name Variable Value
        self.startNum = self.getUIValue('renameUI_startNumberValue', self.startNum)
        self.numPadding = self.getUIValue('renameUI_paddingValue', self.numPadding)
        self.startLetter = self.getUIValue('renameUI_startLetterValue', self.startLetter)
        self.directionList = self.getUIValue('renameUI_directionList', self.directionList)
        self.direction = self.getUIValue('renameUI_dirValue', self.direction)

    def _initMainUI(self):
        self._initUIValue()
        self._getUIValue()
        # create Widget
        self.topFiller = QtWidgets.QWidget(self)
        self.topFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.bottomFiller = QtWidgets.QWidget(self)
        self.bottomFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainCtner = QtWidgets.QWidget(self)
        # Create Layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        # Add widget
        self.addWidgets()
        # Set Layout
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.setStyleSheet(uiStyle.styleSheet)
        self._connectFunction()

    def addWidgets(self):
        # self.mainLayout.addWidget(self.createSeparator())
        # self.mainLayout.addWidget(self.topFiller)
        self.mainLayout.addWidget(self.mainNameBox())
        self.mainLayout.addWidget(self.replaceNameBox())
        self.mainLayout.addWidget(self.optionBox())
        self.mainLayout.addWidget(self.buttonBox())
        self.mainLayout.addWidget(self.bottomFiller)

    def _connectFunction(self):
        def connect(button,func):
            button.clicked.connect(func)
        connect(self.getName_button, self.onGetNameClick)
        connect(self.addPrefix_button, self.onAddPrefixClick)
        connect(self.deletePrefix_button, self.onDeletePrefixClick)
        connect(self.addSuffix_button, self.onAddSuffixClick)
        connect(self.deleteSuffix_button, self.onDeleteSuffixClick)
        connect(self.deleteNameBefore_button, self.onDeleteNameBeforeClick)
        connect(self.deleteNameAfter_button, self.onDeleteNameAfterClick)
        connect(self.nameReplace_button, self.onReplaceNameClick)
        connect(self.apply_button, self.onApplyClick)
        connect(self.matchShapeName_button, self.onRenameShapeClick)
        connect(self.labelJoint_button, self.onLabelJointClick)
        # Connect Change Signal
        self.name_text.textChanged.connect(self.updateNameText)
        self.prefix_combobox.activated.connect(self.updatePrefixText)
        self.suffix_combobox.activated.connect(self.updateSuffixText)
        self.nameSearch_text.textChanged.connect(self.updateSearchNameText)
        self.nameReplace_text.textChanged.connect(self.updateReplaceNameText)
        self.directionEnable_checkbox.stateChanged.connect(self.updateDirEnableState)
        self.directionAddSeparator_checkbox.stateChanged.connect(self.updateDirAddSepState)
        self.direction_comboBox.activated.connect(self.updateDirectionValue)
        self.directionPosition_comboBox.activated.connect(self.updateDirectionPos)
        self.letterEnable_checkbox.stateChanged.connect(self.updateLetterEnableState)
        self.letterAddSeparator_checkbox.stateChanged.connect(self.updateLetterEnableState)
        self.startletter_comboBox.activated.connect(self.updateLetterValue)
        self.letterIterate_comboBox.activated.connect(self.updateLetterIterState)
        self.letterPosition_comboBox.activated.connect(self.updateLetterPos)
        self.numberEnable_checkbox.stateChanged.connect(self.updateNumEnableState)
        self.numberAddSeparator_checkbox.stateChanged.connect(self.updateNumAddSepState)
        self.startNumber_spinBox.valueChanged.connect(self.updateNumValue)
        self.numPadding_spinBox.valueChanged.connect(self.updateNumPaddingValue)
        self.renameChild_radialbutton.toggled.connect(self.updateRenameChildState)
        self.renameAll_radialbutton.toggled.connect(self.updateRenameAllState)

    def createMenuBar(self):
        # create Action
        self.reset_action = QtWidgets.QAction('Reset', self)
        self.reset_action.setToolTip('Reset UI To Default Value')
        self.reset_action.setStatusTip('Reset UI To Default Value')
        self.reset_action.triggered.connect(self.resetUI)
        # create Menu
        self.menubar = self.menuBar()
        self.optionmenu = self.menubar.addMenu('Option')
        self.optionmenu.addAction(self.reset_action)
        # self.me

    def mainNameBox(self):
        self.mainNameGroup = QtWidgets.QGroupBox()
        # self.mainNameGroup.setFixedHeight(100)
        # create Layout
        self.mainNameLayout = QtWidgets.QGridLayout()
        # Create Widgets
        self.addPrefix_button = QtWidgets.QPushButton('Add')
        self.deletePrefix_button = QtWidgets.QPushButton('Delete')
        self.prefix_label = QtWidgets.QLabel('Prefix: ')
        self.prefix_combobox = QtWidgets.QComboBox()
        self.name_label = QtWidgets.QLabel('Name: ')
        self.name_text = QtWidgets.QLineEdit()
        self.deleteNameBefore_button = QtWidgets.QPushButton('Delete >>')
        self.deleteNameAfter_button = QtWidgets.QPushButton('<< Delete')
        self.suffix_label = QtWidgets.QLabel('Suffix: ')
        self.suffix_combobox = QtWidgets.QComboBox()
        self.addSuffix_button = QtWidgets.QPushButton('Add')
        self.deleteSuffix_button = QtWidgets.QPushButton('Delete')
        self.getName_button = QtWidgets.QPushButton('Get Name')
        # Set Widget Value
        self.prefix_combobox.setEditable(True)
        self.prefix_combobox.insertItems(0, self.prefix_list.split(','))
        self.suffix_combobox.setEditable(True)
        self.suffix_combobox.insertItems(0, self.suffix_list.split(','))
        self.name_text.setText(self.nameValue)
        self.prefix_combobox.setCurrentIndex(self.prefixValue)
        # add Widgets
        def addWidget(widget,*args):
            self.mainNameLayout.addWidget(widget,*args)
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.addWidget(self.addPrefix_button)
        subLayout.addWidget(self.deletePrefix_button)
        self.mainNameLayout.addLayout(subLayout,2,0)
        addWidget(self.prefix_label,0,0)
        addWidget(self.prefix_combobox,1,0)
        addWidget(self.name_label,0,1)
        addWidget(self.name_text,1,1)
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.addWidget(self.deleteNameBefore_button)
        subLayout.addWidget(self.getName_button)
        subLayout.addWidget(self.deleteNameAfter_button)
        self.mainNameLayout.addLayout(subLayout,2,1)
        addWidget(self.suffix_label,0,2)
        addWidget(self.suffix_combobox,1,2)
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.addWidget(self.addSuffix_button)
        subLayout.addWidget(self.deleteSuffix_button)
        self.mainNameLayout.addLayout(subLayout,2,2)

        # Add Layout
        self.mainNameLayout.setColumnStretch(1,2)
        self.mainNameGroup.setLayout(self.mainNameLayout)
        return self.mainNameGroup
    
    def optionBox(self):
        self.incGroup = QtWidgets.QGroupBox('Extra Option')
        # create Layout
        self.incLayout = QtWidgets.QHBoxLayout()
        self.incLayout.addWidget(self.directionBox())
        self.incLayout.addWidget(self.letteringBox())
        self.incLayout.addWidget(self.numberingBox())
        self.incGroup.setLayout(self.incLayout)
        return self.incGroup

    def numberingBox(self):
        self.numberGroup = QtWidgets.QGroupBox("Add Number")
        # Create Layout
        self.numberLayout = QtWidgets.QVBoxLayout()
        self.numberLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        # self.numberLayout.addWidget(QtWidgets.QLabel('Numbering:'))
        group = QtWidgets.QHBoxLayout()
        self.numberEnable_checkbox = QtWidgets.QCheckBox('Enable')
        group.addWidget(self.numberEnable_checkbox)
        self.numberAddSeparator_checkbox = QtWidgets.QCheckBox('Add Separator')
        group.addWidget(self.numberAddSeparator_checkbox)
        self.numberLayout.addLayout(group)
        self.startNumber_spinBox = self.labelGroup(
            'Start At: ',
            QtWidgets.QSpinBox,
            self.numberLayout)
        self.numPadding_spinBox = self.labelGroup(
            'Padding: ',
            QtWidgets.QSpinBox,
            self.numberLayout)
        self.numberPosition_comboBox = self.labelGroup(
            'Position: ',
            QtWidgets.QComboBox,
            self.numberLayout)
        # Set Widget
        self.numberEnable_checkbox.setChecked(self.numBool)
        self.startNumber_spinBox.setValue(self.startNum)
        self.numPadding_spinBox.setValue(self.numPadding)
        for id, i in enumerate(['After Name', 'After Suffix']):
            self.numberPosition_comboBox.insertItem(id,i)
        self.numberPosition_comboBox.setCurrentIndex(self.numPos)
        # Add Layout
        self.numberGroup.setLayout(self.numberLayout)
        return self.numberGroup

    def letteringBox(self):
        self.letterGroup = QtWidgets.QGroupBox('Add Letter')
        self.letterLayout = QtWidgets.QVBoxLayout()
        self.letterLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        # self.letterLayout.addWidget(QtWidgets.QLabel('Lettering:'))
        group = QtWidgets.QHBoxLayout()
        self.letterEnable_checkbox = QtWidgets.QCheckBox('Enable')
        group.addWidget(self.letterEnable_checkbox)
        self.letterAddSeparator_checkbox = QtWidgets.QCheckBox('Add Separator')
        group.addWidget(self.letterAddSeparator_checkbox)
        self.letterLayout.addLayout(group)
        self.startletter_comboBox = self.labelGroup(
            'Character: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        self.letterIterate_comboBox = self.labelGroup(
            'Interate: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        self.letterPosition_comboBox = self.labelGroup(
            'Position: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        # Set Widget
        for id, ch in enumerate(self.letterList):
            self.startletter_comboBox.insertItem(id,ch)
        for id, i in enumerate(['After Name', 'After Suffix']):
            self.letterPosition_comboBox.insertItem(id,i)
        for id, i in enumerate(['False', 'True']):
            self.letterIterate_comboBox.insertItem(id,i)
        self.letterEnable_checkbox.setChecked(self.letterBool)
        self.letterAddSeparator_checkbox.setChecked(self.letterAddSepBool)
        self.letterPosition_comboBox.setCurrentIndex(self.letterPos)
        self.startletter_comboBox.setCurrentIndex(self.startLetter)
        self.letterIterate_comboBox.setCurrentIndex(self.letterIterBool)
        # Add Layout
        self.letterGroup.setLayout(self.letterLayout)
        return self.letterGroup

    def directionBox(self):
        self.directionGroup = QtWidgets.QGroupBox("Add Direction")
        self.directionLayout = QtWidgets.QVBoxLayout()
        # self.directionLayout.addWidget(QtWidgets.QLabel('Direction:'))
        self.directionLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        group = QtWidgets.QHBoxLayout()
        self.directionEnable_checkbox = QtWidgets.QCheckBox('Enable')
        group.addWidget(self.directionEnable_checkbox)
        self.directionAddSeparator_checkbox = QtWidgets.QCheckBox('Add Separator')
        group.addWidget(self.directionAddSeparator_checkbox)
        self.directionLayout.addLayout(group)
        self.direction_comboBox = self.labelGroup(
            'Direction: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        self.directionPosition_comboBox = self.labelGroup(
            'Position: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        # Set Widget
        for id, ch in enumerate(self.directionList.split(',')):
            self.direction_comboBox.insertItem(id,ch)
        self.direction_comboBox.setEditable(True)
        for id, i in enumerate(['Before Name','After Name','After Suffix']):
            self.directionPosition_comboBox.insertItem(id,i)
        self.directionEnable_checkbox.setChecked(self.directionBool)
        self.directionAddSeparator_checkbox.setChecked(self.dirAddSepBool)
        self.direction_comboBox.setCurrentIndex(self.direction)
        self.directionPosition_comboBox.setCurrentIndex(self.dirPos)
        # Add Layout
        self.directionGroup.setLayout(self.directionLayout)
        return self.directionGroup

    def replaceNameBox(self):
        self.replaceNameGroup = QtWidgets.QGroupBox("Search && Replace Name")
        self.replaceNameLayout = QtWidgets.QHBoxLayout()
        self.replaceNameLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        self.nameSearch_text = self.labelGroup('Search:', QtWidgets.QLineEdit, self.replaceNameLayout)
        self.nameReplace_text = self.labelGroup('Replace:', QtWidgets.QLineEdit, self.replaceNameLayout)
        self.nameReplace_button = QtWidgets.QPushButton('Apply')
        self.replaceNameLayout.addWidget(self.nameReplace_button)
        # Set Widget
        self.nameSearch_text.setText(self.searchName)
        self.nameReplace_text.setText(self.replaceName)
        # Add Layout
        self.replaceNameGroup.setLayout(self.replaceNameLayout)
        return self.replaceNameGroup

    def buttonBox(self):
        groupbox = QtWidgets.QGroupBox()
        layout = QtWidgets.QHBoxLayout()
        # for i in range(3):
            # layout.setColumnMinimumWidth(i,100)
        self.selectedOnly_radiobutton = QtWidgets.QRadioButton('Selected')
        self.renameChild_radialbutton = QtWidgets.QRadioButton('Hierachy')
        self.renameAll_radialbutton = QtWidgets.QRadioButton('All')
        self.apply_button = QtWidgets.QPushButton('Apply')
        self.matchShapeName_button = QtWidgets.QPushButton('Rename Shape')
        self.labelJoint_button = QtWidgets.QPushButton('Label Joint')
        # set Wiget Value
        # self.apply_button.toolTip().setText('asdasd')
        self.apply_button.setToolTip('Rename Object')
        self.apply_button.setStatusTip('Rename Object')
        if not self.renameChildBool and not self.renameAllBool:
            self.selectedOnly_radiobutton.setChecked(True)
        else:
            self.selectedOnly_radiobutton.setChecked(False)
        self.renameChild_radialbutton.setChecked(self.renameChildBool)
        self.renameAll_radialbutton.setChecked(self.renameAllBool)
        # Add Widget
        layout.addWidget(self.selectedOnly_radiobutton)
        layout.addWidget(self.renameChild_radialbutton)
        layout.addWidget(self.renameAll_radialbutton)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.matchShapeName_button)
        layout.addWidget(self.labelJoint_button)
        layout.setStretch(3,1)
        layout.setStretch(4,1)
        # layout.addStretch(1)
        groupbox.setLayout(layout)
        return groupbox

    # Function CallBack

    def updateNameText(self, value): 
        self.nameValue = value
        self.setUIValue('renameUI_nameValue', value)

    def updatePrefixText(self, value):
        self.prefix_list = ','.join([
            self.prefix_combobox.itemText(i)
            for i in range(self.prefix_combobox.count())
            if i not in self.prefix_list.split(',')])
        self.prefixValue = value
        self.setUIValue('renameUI_prefixList', self.prefix_list)
        self.setUIValue('renameUI_prefixValue', value)

    def updateSuffixText(self, value):
        self.suffix_list = ','.join([
            self.suffix_combobox.itemText(i)
            for i in range(self.suffix_combobox.count())
            if i not in self.suffix_list.split(',')])
        self.suffixValue = value
        self.setUIValue('renameUI_suffixList', self.suffix_list)
        self.setUIValue('renameUI_suffixValue', value)

    def updateSearchNameText(self, value):
        self.searchName = value
        self.setUIValue('renameUI_searchValue', value)

    def updateReplaceNameText(self, value):
        self.replaceName = value
        self.setUIValue('renameUI_replaceValue', value)

    def updateDirEnableState(self, value):
        self.directionBool = value
        self.setUIValue('renameUI_dirToggle', value)

    def updateDirAddSepState(self, value):
        self.dirAddSepBool = value
        self.setUIValue('renameUI_dirAddSepToggle', value)

    def updateDirectionValue(self, value):
        self.directionList = ','.join([
            self.direction_comboBox.itemText(i)
            for i in range(self.direction_comboBox.count())
            if i not in self.directionList.split(',')])
        self.direction = value
        self.setUIValue('renameUI_directionList', self.directionList)
        self.setUIValue('renameUI_dirValue', value)

    def updateDirectionPos(self, value):
        self.dirPos = value
        self.setUIValue('renameUI_dirPosValue', value)

    def updateLetterEnableState(self, value):
        self.letterBool = value
        self.setUIValue('renameUI_letterToggle', value)

    def updateLetterValue(self, value):
        self.startLetter = value
        self.setUIValue('renameUI_letterAddSepToggle', value)

    def updateLetterIterState(self, value):
        self.letterIterBool = value
        self.setUIValue('renameUI_letterIterToggle', value)

    def updateLetterPos(self, value):
        self.letterPos = value
        self.setUIValue('renameUI_letterPosValue', value)

    def updateNumEnableState(self, value):
        self.numBool = value
        self.setUIValue('renameUI_numberToggle', value)

    def updateNumAddSepState(self, value):
        self.setUIValue('renameUI_numberAddSepToggle', value)

    def updateNumValue(self, value):
        self.startNum = value
        self.setUIValue('renameUI_startNumberValue', value)

    def updateNumPaddingValue(self, value):
        self.numPadding = value
        self.setUIValue('renameUI_paddingValue', value)

    def updateRenameChildState(self, value):
        # print value
        self.renameChildBool = value
        self.setUIValue('renameUI_renameChildToggle', value)

    def updateRenameAllState(self, value):
        # print value
        self.renameAllBool = value
        self.setUIValue('renameUI_renameAllToggle', value)

    def resetUI(self):
        resetOptionVar()
        self._initMainUI()
        self.show()

    def getOblist(self):
        ob_list = pm.selected() if not self.renameAll_radialbutton.isChecked() else pm.ls(type='transform')
        if not ob_list:
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        return ob_list

    def rename(self, ob, newName):
        def doRename(o):
            oldname = o.name().split('|')[-1]
            o.rename(newName)
            if newName != oldname:
                log.info("name {} rename to {}".format(oldname, newName))
        try:
            doRename(ob)
            if self.renameChild_radialbutton.isChecked():
                for obchild in ob.getChildren(type='transform', ad=True):
                    doRename(obchild)
        except (AttributeError, RuntimeError) as why:
            log.warning('%s %s'%(ob.__repr__(), str(why)))

    def onDeleteNameBeforeClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            newName = ob.name().split('|')[-1][1:]
            self.rename(ob, newName)

    def onDeleteNameAfterClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            newName = ob.name().split('|')[-1][:-1]
            self.rename(ob, newName)

    def onAddPrefixClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            obName = ob.name().split('|')[-1]
            newName = self.separator.join([self.prefix_combobox.currentText(), obName])
            self.rename(ob, newName)

    def onDeletePrefixClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            splitName = ob.name().split('|')[-1].split(self.separator)
            if len(splitName) > 1:
                newName = self.separator.join([c for c in splitName[1:] if c])
                self.rename(ob, newName)

    def onAddSuffixClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            obName = ob.name().split('|')[-1]
            newName = self.separator.join([obName, self.suffix_combobox.currentText()])
            self.rename(ob, newName)

    def onDeleteSuffixClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            splitName = ob.name().split('|')[-1].split(self.separator)
            if len(splitName) > 1:
                newName = self.separator.join([c for c in splitName[:-1] if c])
                self.rename(ob, newName)

    def resetTextField(self):
        self.prefix_combobox.setCurrentText('')
        self.name_text.setText('')
        self.suffix_combobox.setCurrentText('')

    def onGetNameClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        if not hasattr(pm.selected()[0], 'name'):
            return
        self.resetTextField()
        name = pm.selected()[0].name().split('|')[-1]
        splitName = name.split(self.separator)
        prefix = ''
        suffix = ''
        if len(splitName) > 2:
            prefix = splitName[0]
            name = self.separator.join(splitName[1:-1])
            suffix = splitName[-1]
        elif len(splitName) == 2:
            if len(splitName[1]) > len(splitName[0]):
                name = splitName[1]
                prefix = splitName[0]
            else:
                name = splitName[0]
                suffix = splitName[1]
        self.prefix_combobox.setCurrentText(prefix)
        self.name_text.setText(name)
        self.suffix_combobox.setCurrentText(suffix)

    def onReplaceNameClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            name = ob.name().split('|')[-1]
            newName = name.replace(self.nameSearch_text.text(),self.nameReplace_text.text())
            self.rename(ob, newName)

    def onRenameShapeClick(self):
        ob_list = self.getOblist()
        for ob in ob_list:
            if not hasattr(ob, 'name'):
                continue
            name = ob.name().split('|')[-1]
            newName = name+'Shape'
            if hasattr(ob, 'getShapes'):
                for obShape in ob.getShapes():
                    obShape.rename(newName)
            if self.renameChild_radialbutton.isChecked():
                for obChild in ob.getChildren(type='transform', ad=True):
                    if hasattr(obChild, 'getShapes'):
                        name = obChild.name().split('|')[-1]
                        newName = name+'Shape'
                        for obCShape in obChild.getShapes():
                            obCShape.rename(newName)

    def onLabelJointClick(self):
        remove_prefixes=['CH_'],
        direction_label={
            'Left': (1, ['left', 'Left', '_L_', 'L_', '_L']),
            'Right': (2, ['right', 'Right', '_R_', 'R_', '_R'])}
        ob_list = self.getOblist()
        def labelJoint(ob):
            if not isinstance(ob, pm.nt.Joint):
                return
            try:
                ob.attr('type').set(18)
                wildcard = ''
                sideid = 0
                for dir, (side_id, name_wc) in direction_label.items():
                    for wc in name_wc:
                        # print wc, ob.name()
                        if wc in ob.name():
                            wildcard = wc
                            sideid = side_id
                            break
                    if wildcard:
                        break
                #print wildcard
                label_name = ob.name().replace(wildcard, '')
                if '|' in label_name:
                    label_name = label_name.split('|')[-1]
                    for prefix in remove_prefixes:
                        print label_name, prefix
                        label_name = label_name.replace(prefix, '')
                ob.otherType.set(label_name)
                ob.side.set(sideid)
                log.info('set {} joint label to {}'.format(ob, label_name))
            except (AttributeError,RuntimeError) as why:
                log.error(why)
        for ob in ob_list:
            labelJoint(ob)
            if self.renameChildBool:
                for obc in ob.getChildren(type='joint', ad=True):
                    labelJoint(obc)

    def onApplyClick(self):
        # Base Name Variable
        separator = self.separator
        prefix = self.prefix_combobox.currentText()
        name = self.name_text.text()
        suffix = self.suffix_combobox.currentText()
        # Optional Name Variable Toggle State
        numBool = self.numberEnable_checkbox.checkState()
        numAddSepBool = self.numberAddSeparator_checkbox.checkState()
        letterBool = self.letterEnable_checkbox.checkState()
        letterIterBool = self.letterIterate_comboBox.currentIndex()
        letterAddSepBool = self.letterAddSeparator_checkbox.checkState()
        directionBool = self.directionEnable_checkbox.checkState()
        dirAddSepBool = self.directionAddSeparator_checkbox.checkState()
        renameChildBool = self.renameChild_radialbutton.isChecked()
        renameAllBool = self.renameAll_radialbutton.isChecked()
        # Optional Name Variable Position
        numPos = self.numberPosition_comboBox.currentText()
        letterPos = self.letterPosition_comboBox.currentText()
        dirPos = self.directionPosition_comboBox.currentText()
        # Optional Name Variable Value
        startNum = self.startNumber_spinBox.value()
        numPadding = self.numPadding_spinBox.value()
        startLetter = self.startletter_comboBox.currentIndex()
        direction = self.direction_comboBox.currentText()
        # Name List generate
        def getIndex(postext):
            if 'prefix' in postext.lower():
                if prefix:
                    if postext.lower().startswith('before'):
                        return baseName_list.index(prefix)
                    else:
                        return baseName_list.index(prefix)+1
                else:
                    return 0
            if 'name' in postext.lower():
                if postext.lower().startswith('before'):
                    return baseName_list.index(name)
                else:
                    return baseName_list.index(name)+1
            if 'suffix' in postext.lower():
                if suffix:
                    if postext.lower().startswith('before'):
                        return baseName_list.index(suffix)
                    else:
                        return baseName_list.index(suffix)+1
                else:
                    return (len(baseName_list)-1)
        ob_list = self.getOblist()
        if not name:
            msg = 'Name is empty, input Name String'
            pm.informBox('Error', msg)
            log.error(msg)
            return
        for obid, ob in enumerate(ob_list):
            if hasattr(ob, 'rename'):
                baseName_list = [prefix, name, suffix]
                letterIndex = (startLetter+obid) if letterIterBool else startLetter
                if numBool:
                    baseName_list.insert(getIndex(numPos), ("{:0"+str(numPadding)+"d}").format(startNum+obid))
                    if numAddSepBool:
                        baseName_list.insert(getIndex(numPos), separator)
                if letterBool:
                    baseName_list.insert(getIndex(letterPos), self.letterList[letterIndex])
                    if letterAddSepBool:
                        baseName_list.insert(getIndex(letterPos), separator)
                if directionBool:
                    baseName_list.insert(getIndex(dirPos), direction)
                    if dirAddSepBool:
                        if prefix and suffix:
                            baseName_list.insert(getIndex(dirPos), separator)
                        elif dirPos != 'After Suffix':
                            baseName_list.insert(getIndex(dirPos), separator)
                if prefix:
                    baseName_list.insert(1,separator)
                if suffix:
                    baseName_list.insert(getIndex('before suffix'),separator)
                newName = ''.join(baseName_list)
                ob.rename(newName)
                if renameChildBool:
                    if suffix:
                        obname = ob.name().replace(self.separator+suffix,'')
                    else:
                        obname = ob.name()
                    # if len(ob.getChildren()) > 1:
                    childCount = len(ob.getChildren(type='transform'))
                    # print childCount, ob.getChildren(type='transform')
                    childs = iter_hierachy(ob)
                    i = 1
                    l = -1
                    for child in iter(childs):
                        if child == ob:
                            continue
                        if hasattr(child,'getParent'):
                            if child.getParent() == ob:
                                i = 1
                                l += 1
                        if hasattr(child,'rename'):
                            if childCount > 1:
                                childName = '{}_{}{:02d}{}'.format(
                                    obname,
                                    self.letterList[l],
                                    i,
                                    '_%s'%suffix if suffix else '')
                            else:
                                childName = '{}_{:02d}{}'.format(
                                    obname,
                                    i,
                                    '_%s'%suffix if suffix else '')
                            child.rename(childName)
                            i += 1

    @classmethod
    def showUI(cls):
        cls().show()

def resetOptionVar():
    for var in [
        'renameUI_nameValue',
        'renameUI_separatorValue',
        'renameUI_prefixValue',
        'renameUI_prefixList',
        'renameUI_suffixValue',
        'renameUI_suffixList',
        'renameUI_numberToggle',
        'renameUI_numberAddSepToggle',
        'renameUI_letterToggle',
        'renameUI_letterIterToggle',
        'renameUI_letterAddSepToggle',
        'renameUI_dirToggle',
        'renameUI_dirAddSepToggle',
        'renameUI_renameChildToggle',
        'renameUI_renameAllToggle',
        'renameUI_numberPosValue',
        'renameUI_letterPosValue',
        'renameUI_dirPosValue',
        'renameUI_startNumberValue',
        'renameUI_paddingValue',
        'renameUI_startLetterValue',
        'renameUI_directionList',
        'renameUI_dirValue']:
        try:
            del pm.optionVar[var]
        except KeyError:
            pass

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