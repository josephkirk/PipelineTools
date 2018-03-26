import os
from maya import OpenMayaUI, cmds, mel
import pymel.core as pm
import uiStyle
import logging
from ..core.objectClass import controlShape as cs
from functools import partial
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

reload(cs)
reload(uiStyle)
# ------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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
def connect_transform(ob, target, **kws):
    attrdict = {
        'translate': ['tx', 'ty', 'tz'],
        'rotate': ['rx', 'ry', 'rz'],
        'scale': ['sx', 'sy', 'sz']
    }
    for atr in attrdict:
        if atr not in kws:
            kws[atr] = False
            if 'all' in kws:
                if kws['all']:
                    kws[atr] = True
    for atr, value in attrdict.items():
        if atr in kws:
            if kws[atr] is False:
                continue
            if 'disconnect' in kws:
                if kws['disconnect']:
                    ob.attr(atr) // target.attr(atr)
                    for attr in value:
                        ob.attr(attr) // target.attr(attr)
                        log.info('{} disconnect to {}'.format(
                            ob.attr(attr), target.attr(attr)))
                    continue
            ob.attr(atr) >> target.attr(atr)
            for attr in value:
                ob.attr(attr) >> target.attr(attr)
                log.info('{} connect to {}'.format(
                    ob.attr(attr), target.attr(attr)))

def xformTo(ob, target):
    const = pm.parentConstraint(target, ob)
    pm.delete(const)
    log.info('{} match to {}'.format(ob,target))

def create_group(ob):
    obname = ob.name().split('|')[-1]
    if ob.nodeType() == 'joint':
        parent = pm.nt.Joint(name=obname + '_offset')
    else:
        parent = pm.nt.Transform(name=obname + 'Gp')
    oldParent = ob.getParent()
    # parent.setTranslation(ob.getTranslation('world'), 'world')
    # parent.setRotation(ob.getRotation('world'), 'world')
    xformTo(parent, ob)
    parent.setParent(oldParent)
    ob.setParent(parent)
    log.info('create Parent Transform %s'%parent)
    return parent

def create_loc(ob):
    obname = ob.name().split('|')[-1]
    loc = pm.spaceLocator(name=obname + '_loc')
    loc.setTranslation(ob.getTranslation('world'), 'world')
    loc.setRotation(ob.getRotation('world'), 'world')
    loc_Gp = create_group(loc)
    return loc

def getUIValue(valueName, defaultValue=0):
    if valueName in pm.optionVar:
        log.debug('{}:{}'.format(valueName, pm.optionVar[valueName]))
        return pm.optionVar[valueName]
    else:
        pm.optionVar[valueName] = defaultValue
        log.debug('{}:{}'.format(valueName, pm.optionVar[valueName]))
        return defaultValue

def setUIValue(valueName, value):
    pm.optionVar[valueName] = value
    log.debug('{}:{}'.format(valueName, pm.optionVar[valueName]))

def null():
    pass
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
        self.createMenuBar()
        self.createStatusBar()

    def _initUIValue(self):
        self.nameSuffix = 'ctl'
        self.name = "controlObject"
        self.controlObject = cs.main(self.name, color=(255,255,0,255))
        self.controlColor = tuple(self.controlObject.color)
        self.connectType_dict = {
            'translate': partial(connect_transform, translate=True),
            'rotate': partial(connect_transform, rotate=True),
            'scale': partial(connect_transform, scale=True),
            'all': partial(connect_transform, all=True),
            'parent': partial(pm.parentConstraint, mo=True),
            'point': partial(pm.pointConstraint, mo=True),
            'orient': partial(pm.orientConstraint, mo=True),
        }
        getUIValue('controlmaker_connectUseLoc', 0)
        getUIValue('controlmaker_connectType',0)
        getUIValue('controlmaker_createSelOffset', 1)
        getUIValue('controlmaker_createCtlOffset', 1)
        getUIValue('controlmaker_createChain', 0)
        getUIValue('controlmaker_useObjectName', 0)

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
        self.disableSetAxis = False
        self._connectFunction()

    def createMainWidgets(self):
        self.mainLayout.addWidget(self.controlShapeBox())

    def controlShapeBox(self):
        uiGrp = QtWidgets.QGroupBox('Control Shape Maker')
        layout = QtWidgets.QVBoxLayout()
        # - Create Sub Layout --------------------------
        controlAttributeGroupLayout = QtWidgets.QGridLayout()
        controlNameAttributeLayout = QtWidgets.QVBoxLayout()
        controlAttributeGroupLayout.setAlignment(QtCore.Qt.AlignTop)
        controlNameAttributeLayout.setAlignment(QtCore.Qt.AlignTop)
        controlNameAttributeLayout.setSpacing(2)
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
        self.controlHeight_label, self.controlHeight_floatspinbox = uiStyle.labelGroup(
            "Height: ", QtWidgets.QDoubleSpinBox, controlAttributeLayout, returnLabel=True)
        self.controlLength_label, self.controlLength_floatspinbox = uiStyle.labelGroup(
            "Length: ", QtWidgets.QDoubleSpinBox, controlAttributeLayout, returnLabel=True)
        self.controlRadius_label, self.controlRadius_floatspinbox = uiStyle.labelGroup(
            "Radius: ", QtWidgets.QDoubleSpinBox, controlAttributeLayout, returnLabel=True)
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
        # self.groupControl_checkbox, = uiStyle.multiOptionsLayout(
        #     ['group',],
        #     parent=controlOptionGroupLayout
        # )
        self.offsetX_floatspinbox,\
        self.offsetY_floatspinbox,\
        self.offsetZ_floatspinbox = uiStyle.multiLabelLayout(
            ['x', 'y', 'z'],
            QtWidgets.QDoubleSpinBox,
            groupLabel='Offset: ',
            parent=controlOptionGroupLayout
        )
        self.addControlShape_button = QtWidgets.QPushButton('Add Shape')
        self.deleteControlShape_button = QtWidgets.QPushButton('Delete Shape')
        self.changeControlShape_button = QtWidgets.QPushButton('Change Shape')
        self.createControl_button = QtWidgets.QPushButton('Create Control')
        self.setColor_button = QtWidgets.QPushButton('Set Color')
        createButtonLayout.addWidget(self.addControlShape_button)
        createButtonLayout.addWidget(self.deleteControlShape_button)
        createButtonLayout.addWidget(self.changeControlShape_button)
        createButtonLayout.addWidget(self.setColor_button)
        createButtonLayout.addWidget(self.createControl_button)
        layout.addWidget(controlOptionGroup)
        layout.addLayout(createButtonLayout)
        # ----------------------------------------------
        self.controlName_text.setPlaceholderText(self.name)
        self.controlNameSuffix_comboBox.addItems(['ctl','cnt','control'])
        self.controlLength_floatspinbox.setValue(self.controlObject.length)
        self.controlRadius_floatspinbox.setValue(self.controlObject.radius)
        self.controlHeight_floatspinbox.setValue(self.controlObject.height)
        self.controlHeight_label.hide()
        self.controlHeight_floatspinbox.hide()
        self.controlType_combobox.addItems(self.controlObject._controlType.keys())
        self.controlType_combobox.setCurrentText('Pin')
        self.controlSmoothness_combobox.addItems(self.controlObject._resolutions.keys())
        self.controlAxis_combobox.addItems(self.controlObject._axisList)
        self.controlColor_button.setStyleSheet(".QPushButton { background-color: rgba(%d,%d,%d,%d) } "%tuple(self.controlObject.color))
        # ----------------------------------------------
        uiGrp.setLayout(layout)
        return uiGrp


    def createMenuBar(self):
        # create Action
        def menuItem(name, func , parent, **kws):
            newAction = QtWidgets.QAction(name, self)
            if 'checkable' in kws:
                newAction.setCheckable(kws['checkable'])
                if 'checked' in kws:
                    # if kws['checked'].isdigit():
                    #     newAction.setChecked(bool(int(kws['checked'])))
                    if 'value' in kws and kws['value'] != 'isCheck':
                        newAction.setChecked(kws['checked'] == kws['value'])
                    else:
                        newAction.setChecked(kws['checked'])
            if 'value' in kws:
                def emitValue():
                    if kws['value'] == 'isCheck':
                        # print newAction.isChecked() 
                        func(newAction.isChecked())
                        return
                    func(kws['value'])
                newAction.triggered.connect(emitValue)
            else:
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
        self.optionmenu.addSeparator().setText('Connect Action')
        # self.toggleConnectThroughLocAction = menuItem(
        #     'Create Control for Childrens', partial(setUIValue, 'controlmaker_createForHie'), self.optionmenu, value ='isCheck',
        #     checkable=True, checked=getUIValue('controlmaker_createForHie'))
        self.toggleConnectThroughLocAction = menuItem(
            'Connect Through Loc', partial(setUIValue, 'controlmaker_connectUseLoc'), self.optionmenu, value ='isCheck',
            checkable=True, checked=getUIValue('controlmaker_connectUseLoc'))
        self.connectTypeGroup = QtWidgets.QActionGroup(self)
        self.toggleConnectTranslateAction = menuItem(
            'Connect Translate', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='translate', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.toggleConnectRotateAction = menuItem(
            'Connect Rotate', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='rotate', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.toggleConnectAllAction = menuItem(
            'Connect All', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='all', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.togglePoConstraintAction = menuItem(
            'Point Constraint', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='point', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.toggleOConstraintAction = menuItem(
            'Orient Constraint', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='orient', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.togglePConstraintAction = menuItem(
            'Parent Constraint', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value='parent', 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        self.toggleConnectAction = menuItem(
            'None', partial(setUIValue, 'controlmaker_connectType'), self.connectTypeGroup, value=0, 
            checkable=True, checked=getUIValue('controlmaker_connectType'))
        # self.toggleConnectAction.setChecked(True)
        self.optionmenu.addAction(self.toggleConnectTranslateAction)
        self.optionmenu.addAction(self.toggleConnectRotateAction)
        self.optionmenu.addAction(self.toggleConnectAllAction)
        self.optionmenu.addAction(self.togglePoConstraintAction)
        self.optionmenu.addAction(self.toggleOConstraintAction)
        self.optionmenu.addAction(self.togglePConstraintAction)
        self.optionmenu.addAction(self.toggleConnectAction)
        self.toggleCreateSelectOffset = menuItem(
            'Create Select Offset', partial(setUIValue, 'controlmaker_createSelOffset') , self.optionmenu, value ='isCheck',
            checkable=True, checked=getUIValue('controlmaker_createSelOffset'))
        self.toggleTakeObjectName = menuItem(
            'Use Object Name', partial(setUIValue, 'controlmaker_useObjectName') , self.optionmenu, value ='isCheck',
            checkable=True, checked=getUIValue('controlmaker_useObjectName'))
        self.optionmenu.addSeparator().setText('Other Action')
        self.toggleCreateOffset = menuItem(
            'Create Control Offset', partial(setUIValue, 'controlmaker_createCtlOffset') , self.optionmenu, value ='isCheck',
            checkable=True, checked=getUIValue('controlmaker_createCtlOffset'))
        self.toggleParent = menuItem(
            'Create Parent Chain', partial(setUIValue, 'controlmaker_createChain') , self.optionmenu, value ='isCheck',
            checkable=True, checked=getUIValue('controlmaker_createChain'))

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
        self.resetOptionVar()
        self._initMainUI()
        self.show()

    def _connectFunction(self):
        self.controlName_text.textEdited.connect(self.onChangeName)
        self.controlNameSuffix_comboBox.currentTextChanged.connect(self.onChangeNameSuffix)
        self.controlRadius_floatspinbox.valueChanged.connect(self.onChangeRadius)
        self.controlLength_floatspinbox.valueChanged.connect(self.onChangeLength)
        self.controlHeight_floatspinbox.valueChanged.connect(self.onChangeHeight)
        self.controlColor_button.clicked.connect(self.onChangeColor)
        self.controlType_combobox.currentTextChanged.connect(self.onChangeType)
        self.controlSmoothness_combobox.currentTextChanged.connect(self.onChangeResolution)
        self.controlAxis_combobox.currentTextChanged.connect(self.onChangeAxis)
        # self.groupControl_checkbox.stateChanged.connect(self.setGroupOptionState)
        # self.setAxis_checkbox.stateChanged.connect(self.setAxisOptionState)
        # self.mirror_checkbox.stateChanged.connect(self.setMirrorOptionState)        
        self.offsetX_floatspinbox.valueChanged.connect(self.onChangeOffsetX)
        self.offsetY_floatspinbox.valueChanged.connect(self.onChangeOffsetY)
        self.offsetZ_floatspinbox.valueChanged.connect(self.onChangeOffsetZ)
        self.addControlShape_button.clicked.connect(self.onAddShape)
        self.deleteControlShape_button.clicked.connect(self.onDeleteShape)
        self.changeControlShape_button.clicked.connect(self.onChangeShape)
        self.createControl_button.clicked.connect(self.onCreateShape)
        self.setColor_button.clicked.connect(self.onSetColor)

    # def onToggleConnectType(self):
    #     if self.toggleConnectAction.isChecked():
    #         self.toggleConstraintAction.setChecked(False)
    #         return
    #     if self.toggleConstraintAction.isChecked():
    #         self.toggleConnectAction.setChecked(False)
    #         return
    def onChangeName(self, value):
        self.controlObject.name = value
        log.debug("name: %s"%self.controlObject.name)

    def onChangeNameSuffix(self, value):
        self.controlObject._suffix = value
        log.debug("Name: %s"%self.controlObject.name)

    def onChangeRadius(self, value):
        self.controlObject.radius = value
        log.debug("Radius: %s"%self.controlObject.radius)

    def onChangeLength(self, value):
        self.controlObject.length = value
        log.debug("Length: %s"%self.controlObject.length)

    def onChangeHeight(self, value):
        self.controlObject.height = value
        log.debug("Height: %s"%self.controlObject.height)

    def onChangeColor(self):
        colorDialog = QtWidgets.QColorDialog.getColor(QtCore.Qt.yellow)
        color = colorDialog.getRgb()
        self.controlColor_button.setStyleSheet(
            ".QPushButton { background-color: rgba(%d,%d,%d,%d) } "%tuple(color))
        self.controlObject.color = [color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0]
        log.debug("Color: %s"%self.controlObject.color)

    def onChangeType(self, value):
        self.controlObject.currentType = value
        currentIndex = self.controlAxis_combobox.currentIndex()
        self.controlAxis_combobox.setEnabled(True)
        self.controlSmoothness_combobox.setEnabled(True)
        self.disableSetAxis = True
        self.controlObject.forceSetAxis = False
        self.controlLength_label.show()
        self.controlLength_floatspinbox.show()
        self.controlHeight_label.hide()
        self.controlHeight_floatspinbox.hide()
        self.controlRadius_label.show()
        self.controlRadius_floatspinbox.show()
        self.controlRadius_label.setText('Radius')
        if value.endswith('Pin'):
            self.controlAxis_combobox.clear()
            if value.startswith('Double'):
                self.controlAxis_combobox.addItems(
                    self.controlObject._axisList[:6])
            if value.startswith('Sphere'):
                axisList = self.controlObject._axisList[:2]
                axisList.append(self.controlObject._axisList[3])
                axisList.extend(['-'+a for a in axisList])
                self.controlAxis_combobox.addItems(axisList)
            else:
                self.controlAxis_combobox.addItems(
                    self.controlObject._axisList)
        elif any([value == typ for typ in ['Arrow','Cylinder', 'CircleArrow','HalfCylinder','Circle','Hemisphere']]):
            self.controlObject.forceSetAxis = True
            self.controlAxis_combobox.clear()
            self.controlAxis_combobox.addItems(
                self.controlObject._axisList[:6])
        elif any([value == typ for typ in ['DoubleArrow','Rectangle', 'Cross', 'Triangle', 'ThinCross', 'RoundSquare']]):
            self.controlSmoothness_combobox.setEnabled(False)
            self.controlObject.forceSetAxis = True
            self.controlAxis_combobox.clear()
            self.controlAxis_combobox.addItems(
                self.controlObject._axisList[:3])
            self.controlRadius_label.hide()
            self.controlRadius_floatspinbox.hide()
        else:
            self.controlAxis_combobox.setEnabled(False)
        self.controlAxis_combobox.setCurrentIndex(currentIndex)
        self.disableSetAxis = False
        if currentIndex > (self.controlAxis_combobox.count()-1):
            self.controlAxis_combobox.setCurrentIndex(
                self.controlAxis_combobox.count()-1)
        if any([value == typ for typ in ['Octa','NSphere','Hemisphere','Sphere','Circle']]):
            self.controlLength_label.hide()
            self.controlLength_floatspinbox.hide()
            self.controlHeight_label.hide()
            self.controlHeight_floatspinbox.hide()
            self.controlSmoothness_combobox.setEnabled(False)
        if any([value == typ for typ in ['Cube','Arrow','DoubleArrow']]):
            self.controlRadius_label.show()
            self.controlRadius_floatspinbox.show()
            self.controlRadius_label.setText('Width')
            self.controlHeight_label.show()
            self.controlHeight_floatspinbox.show()
        self.controlLength_floatspinbox.setEnabled(True)
        log.debug("CurrentType: %s"%self.controlObject.currentType.__name__)

    def onChangeResolution(self, value):
        self.controlObject.step = value
        log.debug("Resolution: %s"%self.controlObject.step)

    def onChangeAxis(self, value):
        if not self.disableSetAxis:
            self.controlObject.axis = value
        log.debug("Axis: %s"%self.controlObject.axis)

    def onChangeOffsetX(self, value):
        offset = self.controlObject.offset
        offset[0] = value
        self.controlObject.offset = offset
        log.debug("Offset: %s"%self.controlObject.offset)

    def onChangeOffsetY(self, value):
        offset = self.controlObject.offset
        offset[1] = value
        self.controlObject.offset = offset
        log.debug("Offset: %s"%self.controlObject.offset)

    def onChangeOffsetZ(self, value):
        offset = self.controlObject.offset
        offset[2] = value
        self.controlObject.offset = offset
        log.debug("Offset: %s"%self.controlObject.offset)

    def onCreateShape(self):
        if pm.selected():
            controls = []
            # with pm.UndoChunk():
            pm.undoInfo( state=False )
            sel = pm.selected()
            for ob in sel:
                control = self.controlObject.currentType()
                control.setMatrix(ob.getMatrix(ws=True), ws=True)
                if getUIValue('controlmaker_useObjectName'):
                    control.rename(ob+'_ctl')
                if getUIValue('controlmaker_createCtlOffset'):
                    create_group(control)
                if getUIValue('controlmaker_createSelOffset'):
                    if ob.nodeType() == "joint":
                        create_group(ob)
                if getUIValue('controlmaker_connectType'):
                    if getUIValue('controlmaker_connectUseLoc'):
                        loc = create_loc(ob)
                        pm.parentConstraint(control, loc)
                        loc.getParent().setParent(control.getParent())
                        self.connectType_dict[getUIValue('controlmaker_connectType')](loc, ob)
                    else:
                        self.connectType_dict[getUIValue('controlmaker_connectType')](control, ob)
                if controls and getUIValue('controlmaker_createChain'):
                    if control.getParent():
                        control.getParent().setParent(controls[-1])
                    else:
                        control.setParent(controls[-1])
                controls.append(control)
            pm.undoInfo( state=True )
            return controls
        else:
            control = self.controlObject.currentType
            return control()

    def onSetColor(self):
        for control in pm.selected():
            try:
                controlShape = control.getShape()
                if controlShape:
                    controlShape.overrideEnabled.set(True)
                    controlShape.overrideRGBColors.set(True)
                    controlShape.overrideColorRGB.set(self.controlObject.color)
                sg = control.shadingGroups()[0] if control.shadingGroups() else None
                if sg:
                    shdr = sg.inputs()[0]
                    shdr.outColor.set(self.controlObject.color.rgb)
                    shdr.outTransparency.set([self.controlObject.color.a for i in range(3)])
            except AttributeError as why:
                log.error(why)

    def onChangeShape(self):
        for control in pm.selected():
            temp = self.controlObject.currentType()
            pm.delete(control.getShape(), shape=True)
            pm.parent(temp.getShape(), control, r=True, s=True)
            pm.delete(temp)
            # return control

    def onAddShape(self):
        for control in pm.selected():
            temp = self.controlObject.currentType()
            pm.parent(temp.getShape(), control, r=True, s=True)
            pm.delete(temp)

    def onDeleteShape(self):
        for control in pm.selected():
            try:
                pm.delete(control.getShapes()[-1])
            except AttributeError, IndexError:
                pass

    @staticmethod
    def resetOptionVar():
        for var in pm.optionVar:
            try:
                if var.startswith('controlmaker'):
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