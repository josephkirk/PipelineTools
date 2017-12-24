import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
import logging
from functools import partial
from string import ascii_uppercase as alphabet
from itertools import product
from ..core import general_utils as ul
from ..core import rigging_utils as rul
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
# UIClass
class Renamer(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
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
        self._initUIValue()
        self._getUIValue()
        self._initMainUI()
        # self._initMainUI()
        self._updateUIValue()
        self._connectFunction()

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
        self.numPos = 'After Name'
        self.letterPos = 'After Name'
        self.dirPos = 'After Name'
        # Optional Name Variable Value
        self.startNum = 1
        self.numPadding = 2
        self.startLetter = 0
        self.direction = 0

    def _getUIValue(self):
        # Main Name Value
        self.nameValue = self.getUIValue('renameUI_nameValue', self.nameValue)
        self.separator = self.getUIValue('renameUI_separatorValue', self.separator)
        self.prefixValue = self.getUIValue('renameUI_prefixValue', self.prefixValue)
        self.prefix_list = self.getUIValue('renameUI_prefixList', self.prefix_list)
        self.suffixValue = self.getUIValue('renameUI_suffixValue', self.suffixValue)
        self.suffix_list = self.getUIValue('renameUI_suffixList', self.suffix_list)
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
        self.direction = self.getUIValue('renameUI_dirValue', self.direction)

    def _updateUIValue(self):
        # Save Name Value
        updateNameText = partial(self.setUIValue,'renameUI_nameValue')
        self.name_text.textChanged.connect(updateNameText)
        # Save Prefix Value 
        def updatePrefixText(value):
            self.prefix_list = ','.join([
                self.prefix_combobox.itemText(i)
                for i in range(self.prefix_combobox.count())
                if i not in self.prefix_list.split(',')])
            self.setUIValue('renameUI_prefixList', self.prefix_list)
            self.setUIValue('renameUI_prefixValue', value)
        self.prefix_combobox.activated.connect(updatePrefixText)

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
        self.mainLayout.addWidget(self.buttonBox())

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

    def menuBar(self):
        pass
        # self.menuBar = QtWidgets.QMenu

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
        self.incGroup = QtWidgets.QGroupBox()
        # create Layout
        self.incLayout = QtWidgets.QHBoxLayout()
        self.incLayout.addWidget(self.directionBox())
        self.incLayout.addWidget(self.letteringBox())
        self.incLayout.addWidget(self.numberingBox())
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
            'Position: ',
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
        self.letterList = list(alphabet)
        self.letterList.extend(
            [''.join(list(i)) for i in list(
                product(alphabet, repeat=2))])
        for id, ch in enumerate(self.letterList):
            self.startletter_comboBox.insertItem(id,ch)
        for id, i in enumerate(['After Name', 'After Suffix']):
            self.letterPosition_comboBox.insertItem(id,i)
        for id, i in enumerate(['False', 'True']):
            self.letterIterate_comboBox.insertItem(id,i)
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
            'Position: ',
            QtWidgets.QComboBox,
            self.directionLayout)
        # Set Widget
        directionList = ("Left,Right,Up,Down,Center,Bottom,Middle,L,R,T,B,C,M,Mid").split(',')
        for id, ch in enumerate(directionList):
            self.direction_comboBox.insertItem(id,ch)
        self.direction_comboBox.setEditable(True)
        for id, i in enumerate(['Before Prefix','Before Name','After Name','After Suffix']):
            self.directionPosition_comboBox.insertItem(id,i)
        self.directionPosition_comboBox.setCurrentIndex(2)
        # Add Layout
        self.directionGroup.setLayout(self.directionLayout)
        return self.directionGroup

    def replaceNameBox(self):
        self.replaceNameGroup = QtWidgets.QGroupBox()
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
        groupbox = QtWidgets.QGroupBox()
        layout = QtWidgets.QHBoxLayout()
        # for i in range(3):
            # layout.setColumnMinimumWidth(i,100)
        self.selectedOnly_radiobutton = QtWidgets.QRadioButton('Selected')
        self.renameChild_radialbutton = QtWidgets.QRadioButton('Hierachy')
        self.renameAll_radiobutton = QtWidgets.QRadioButton('All')
        self.apply_button = QtWidgets.QPushButton('Apply')
        self.matchShapeName_button = QtWidgets.QPushButton('Rename All Shape')
        self.selectedOnly_radiobutton.setChecked(True)
        # Add Widget
        layout.addWidget(self.selectedOnly_radiobutton)
        layout.addWidget(self.renameChild_radialbutton)
        layout.addWidget(self.renameAll_radiobutton)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.matchShapeName_button)
        layout.setStretch(3,1)
        layout.setStretch(4,1)
        layout.addStretch(1)
        groupbox.setLayout(layout)
        return groupbox

    # Function CallBack

    def resetUI(self):
        self._initUIValue()
        self._initMainUI()

    def getOblist(self):
        ob_list = pm.selected() if not self.renameAll_radiobutton.isChecked() else pm.ls(type='transform')
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
        renameAllBool = self.renameAll_radiobutton.isChecked()
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
        ob_list = self.getOblist()
        if not name:
            pm.informBox('Error', 'Name is empty, input Name String')
            raise RuntimeError('Name is empty, input Name String')
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
                    print childCount, ob.getChildren(type='transform')
                    childs = ul.iter_hierachy(ob)
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

def show():
    win = Renamer()
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