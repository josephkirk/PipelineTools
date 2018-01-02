import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
from string import ascii_uppercase as alphabet
from itertools import product
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
        self.separator = '_'
        # self.setFixedSize(500,300)
        self._initMainUI()
        self.connectFunction()

    def connectFunction(self):
        def connect(button,func):
            button.clicked.connect(func)
        connect(self.getName_button, self.onGetNameClick)
        connect(self.deletePrefix_button, self.onDeletePrefixClick)
        connect(self.deleteSuffix_button, self.onDeleteSuffixClick)
        connect(self.deleteNameBefore_button, self.onDeleteNameBeforeClick)
        connect(self.deleteNameAfter_button, self.onDeleteNameAfterClick)
        connect(self.nameReplace_button, self.onRenameClick)
        connect(self.apply_button, self.onApplyClick)
    # Widget Definition
    def _initMainUI(self):
        self.mainCtner = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.addWidgets()
        self.setStyle()

    def addWidgets(self):
        self.mainLayout.addWidget(self.mainNameBox())
        self.mainLayout.addWidget(self.replaceNameBox())
        self.mainLayout.addWidget(self.optionBox())
        self.mainLayout.addLayout(self.buttonBox())


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
        self.deleteNameBefore_button = QtWidgets.QPushButton('Delete >>')
        self.deleteNameAfter_button = QtWidgets.QPushButton('<< Delete')
        self.suffix_label = QtWidgets.QLabel('Suffix: ')
        self.suffix_text = QtWidgets.QLineEdit()
        self.deleteSuffix_button = QtWidgets.QPushButton('Delete Suffix')
        # self.separator_label = QtWidgets.QLabel('Separator: ')
        # self.separator_text = QtWidgets.QLineEdit()
        self.getName_button = QtWidgets.QPushButton('Get Name')
        # Set Widget Value
        # self.separator_text.setText('_')
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
        # subLayout.addWidget(self.separator_label)
        # subLayout.addWidget(self.separator_text)
        subLayout.addWidget(self.getName_button)
        subLayout.addWidget(self.deleteNameAfter_button)
        self.mainNameLayout.addLayout(subLayout,2,1)
        addWidget(self.suffix_label,0,2)
        addWidget(self.suffix_text,1,2)
        addWidget(self.deleteSuffix_button,2,2)

        # Add Layout
        self.mainNameLayout.setColumnStretch(1,2)
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
        self.padding_spinBox = self.labelGroup(
            'Padding: ',
            QtWidgets.QSpinBox,
            self.numberLayout)
        self.numberPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.numberLayout)
        # Set Widget
        self.numberEnable_checkbox.setChecked(True)
        self.startNumber_spinBox.setValue(1)
        self.padding_spinBox.setValue(2)
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
        group = QtWidgets.QHBoxLayout()
        self.letterEnable_checkbox = QtWidgets.QCheckBox('Enable')
        group.addWidget(self.letterEnable_checkbox)
        self.letterAddSeparator_checkbox = QtWidgets.QCheckBox('Add Separator')
        group.addWidget(self.letterAddSeparator_checkbox)
        self.letterLayout.addLayout(group)
        self.startletter_comboBox = self.labelGroup(
            'Start At: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        self.letterPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.letterLayout)
        # Set Widget
        self.letterList = list(alphabet)
        self.letterList.extend(
            [''.join(list(i)) for i in list(
                product(alphabet, repeat=2))])
        for id, ch in enumerate(self.letterList):
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
        self.direction_comboBox = self.labelGroup(
            'Direction: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        self.directionPosition_comboBox = self.labelGroup(
            'Postion: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        # Set Widget
        self.directionList = ("Left,Right,Up,Down,Center,Bottom,Middle,L,R,T,B,C,M,Mid").split(',')
        for id, ch in enumerate(self.directionList):
            self.direction_comboBox.insertItem(id,ch)
        for id, i in enumerate(['Before Prefix','Before Name','After Name','After Suffix']):
            self.directionPosition_comboBox.insertItem(id,i)
        self.directionPosition_comboBox.setCurrentIndex(2)
        # Add Layout
        self.directionGroup.setLayout(self.directionLayout)
        return self.directionGroup

    def replaceNameBox(self):
        self.replaceNameGroup = QtWidgets.QGroupBox('Replace Name')
        self.replaceNameLayout = QtWidgets.QHBoxLayout()
        self.replaceNameLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create Widget
        self.nameSearch_text = self.labelGroup('Search:', QtWidgets.QLineEdit, self.replaceNameLayout)
        self.nameReplace_text = self.labelGroup('Replace:', QtWidgets.QLineEdit, self.replaceNameLayout)
        self.nameReplace_button = QtWidgets.QPushButton('Apply')
        self.replaceNameLayout.addWidget(self.nameReplace_button)
        # Set Widget
        # Add Layout
        self.replaceNameGroup.setLayout(self.replaceNameLayout)
        return self.replaceNameGroup
    def buttonBox(self):
        layout = QtWidgets.QGridLayout()
        for i in range(3):
            layout.setColumnMinimumWidth(i,100)
        self.apply_button = QtWidgets.QPushButton('Apply')
        layout.addWidget(self.apply_button,0,4)
        return layout
    # Function CallBack

    def onDeleteNameBeforeClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        for ob in pm.selected():
            if not hasattr(ob, 'rename'):
                continue
            newName = ob.name().split('|')[-1][1:]
            ob.rename(newName)

    def onDeleteNameAfterClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        for ob in pm.selected():
            if not hasattr(ob, 'rename'):
                continue
            newName = ob.name().split('|')[-1][:-1]
            ob.rename(newName)

    def onDeletePrefixClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        for ob in pm.selected():
            if not hasattr(ob, 'rename'):
                continue
            splitName = ob.name().split('|')[-1].split(self.separator)
            if len(splitName) > 1:
                newName = self.separator.join([c for c in splitName[1:] if c])
                ob.rename(newName)

    def onDeleteSuffixClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        for ob in pm.selected():
            if not hasattr(ob, 'rename'):
                continue
            splitName = ob.name().split('|')[-1].split(self.separator)
            if len(splitName) > 1:
                newName = self.separator.join([c for c in splitName[:-1] if c])
                ob.rename(newName)

    def onGetNameClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        if not hasattr(pm.selected()[0], 'name'):
            return
        name = pm.selected()[0].name().split('|')[-1]
        self.name_text.setText(name)

    def onRenameClick(self):
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        for ob in pm.selected():
            if not hasattr(ob, 'rename'):
                continue
            name = pm.selected()[0].name().split('|')[-1]
            newName = name.replace(self.nameSearch_text.text(),self.nameReplace_text.text())
            ob.rename(newName)

    def onApplyClick(self):
        # Base Name Variable
        separator = self.separator
        prefix = self.prefix_text.text()
        name = self.name_text.text()
        suffix = self.suffix_text.text()
        # Optional Name Variable Toggle State
        numBool = self.numberEnable_checkbox.checkState()
        numAddSepBool = self.numberAddSeparator_checkbox.checkState()
        letterBool = self.letterEnable_checkbox.checkState()
        letterAddSepBool = self.letterAddSeparator_checkbox.checkState()
        directionBool = self.directionEnable_checkbox.checkState()
        dirAddSepBool = self.directionAddSeparator_checkbox.checkState()
        # Optional Name Variable Position
        numPos = self.numberPosition_comboBox.currentText()
        letterPos = self.letterPosition_comboBox.currentText()
        dirPos = self.directionPosition_comboBox.currentText()
        # Optional Name Variable Value
        startNum = self.startNumber_spinBox.value()
        numPadding = self.padding_spinBox.value()
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
        if not pm.selected():
            pm.informBox('Error', 'No Object Selected')
            raise RuntimeError('No Object Selected')
        if not name:
            pm.informBox('Error', 'Name is empty, input Name String')
            raise RuntimeError('Name is empty, input Name String')
        result =[]
        for obid, ob in enumerate(pm.selected()):
            if hasattr(ob, 'rename'):
                baseName_list = [prefix, name, suffix]
                if numBool:
                    baseName_list.insert(getIndex(numPos), ("{:0"+str(numPadding)+"d}").format(startNum+obid))
                    if numAddSepBool:
                        baseName_list.insert(getIndex(numPos), separator)
                if letterBool:
                    baseName_list.insert(getIndex(letterPos), self.letterList[(startLetter+obid)])
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
                result.append(ob)
        return result

    @classmethod
    def showUI(cls):
        cls().show()
