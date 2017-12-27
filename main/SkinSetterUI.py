#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.mel as mm
import pymel.core as pm
import logging
import uiStyle
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
#
reload(uiStyle)
# Logging initialize #
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
# Get Maya Main Window
mayaMainWindow = pm.ui.Window('MayaWindow').asQtObject()
# Wrapper
SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT
# UIClass
class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
        self._name = 'SkinWeightToolWindow'
        try:
            pm.deleteUI(self._name)
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('SkinWeightTool')
        self.setObjectName(self._name)
        # print self.objectName()
    # init UI
    def _initUIValue(self):
        self.lastSelection = []
        self.objectName = 'None'
        self.objectList = []
        self.components_list = []
        self.skinType_list = ['Linear', 'Dual Quartenion', 'Blended'] 
        self.currentSkinType = 0
        self.bones_list = []
        self.selectedBones_list = []
        self.weightValue = 1.0
        self.normalizeToggle = True
        self.hierachyToggle = False
        self.useLastSelectToggle = True
        self.blendWeightValue = 0.0
        self.weightThreshold = [0.0, 0.1]
        self.weightInteractiveState = False
        self.blendInteractiveState = False
        self.weightTick = 5

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

    # create Layout


    # Create UI Widget
    def createMainWidgets(self):
        def addWidget(wid):
            self.mainLayout.addWidget(wid)
        addWidget(self.objectBox())
        # addWidget(self.skinTypeBox())
        addWidget(self.weightFilterBox())
        addWidget(self.setWeightBox())
        addWidget(self.setDualWeightBox())
        addWidget(self.weightUtilBox())

    def objectBox(self):
        # create Frame
        uiGrp = QtWidgets.QGroupBox('Object')
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignVCenter)
        bottomLayout = QtWidgets.QHBoxLayout()
        leftSideLayout = QtWidgets.QVBoxLayout()
        rightSideLayout = QtWidgets.QVBoxLayout()
        mainListLayout = QtWidgets.QGridLayout()
        # bottomLayout = QtWidgets.QGridLayout()
        # create Widget
        objectName_label = QtWidgets.QLabel('Skin Mesh')
        objectName_label.setAlignment(QtCore.Qt.AlignCenter)
        self.objectName_text = QtWidgets.QLineEdit(self.objectName)
        bonesName_label = QtWidgets.QLabel('Skin Bones')
        bonesName_label.setAlignment(QtCore.Qt.AlignCenter)
        self.bonesName_listBox = QtWidgets.QListWidget()
        self.lockBonesList_checkBox = QtWidgets.QCheckBox('Lock List')
        self.getInfluencesBone_button = QtWidgets.QPushButton('Get Influences')
        self.removeBone_button = QtWidgets.QPushButton('Remove Select')
        self.removeTopBoneList_button = QtWidgets.QPushButton('<X')
        self.removeAllBones_button = QtWidgets.QPushButton('X')
        self.removeBottomBoneList_button = QtWidgets.QPushButton('X>')
        self.moveBoneUpList_button = QtWidgets.QPushButton('M>')
        self.makeBoneMainList_button = QtWidgets.QPushButton('M')
        self.moveBoneDownList_button = QtWidgets.QPushButton('<M')
        # set Widget Value
        self.objectName_text.setEnabled(False)
        self.bonesName_listBox.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        # connect UI Function

        # add Widget
        bottomLayout.addWidget(self.lockBonesList_checkBox)
        bottomLayout.addWidget(self.getInfluencesBone_button)
        bottomLayout.addWidget(self.removeBone_button)

        rightSideLayout.addWidget(self.removeTopBoneList_button)
        rightSideLayout.addWidget(self.removeAllBones_button)
        rightSideLayout.addWidget(self.removeBottomBoneList_button)

        leftSideLayout.addWidget(self.moveBoneUpList_button)
        leftSideLayout.addWidget(self.makeBoneMainList_button)
        leftSideLayout.addWidget(self.moveBoneDownList_button)

        mainListLayout.addLayout(leftSideLayout,0,0)
        mainListLayout.addWidget(self.bonesName_listBox,0,1)
        mainListLayout.addLayout(rightSideLayout,0,2)
        mainListLayout.setColumnStretch(1,3)

        layout.addWidget(objectName_label)
        layout.addWidget(self.objectName_text)
        layout.addWidget(self.skinTypeBox())
        layout.addWidget(bonesName_label)
        layout.addLayout(mainListLayout)
        layout.addLayout(bottomLayout)
        # set Layout
        uiGrp.setLayout(layout)
        return uiGrp

    def skinTypeBox(self):
        # create Frame
        uiGrp = QtWidgets.QGroupBox('SkinCluster Type')
        layout = QtWidgets.QVBoxLayout()
        # create Widget
        self.currentSkinType_text = self.labelGroup('Current: ', QtWidgets.QLineEdit, layout)
        self.skinType_combobox = self.labelGroup('Set to: ', QtWidgets.QComboBox, layout)
        # set Widget Value
        self.currentSkinType_text.setText('None')
        self.currentSkinType_text.setEnabled(False)
        self.skinType_combobox.insertItems(0, self.skinType_list)
        self.skinType_combobox.setCurrentIndex(self.currentSkinType)
        # add Widget
        # set Layout
        uiGrp.setLayout(layout)
        return uiGrp

    def weightFilterBox(self):
        uiGrp = QtWidgets.QGroupBox('Weight Filter Select')
        layout = QtWidgets.QVBoxLayout()
        subLayout1 = QtWidgets.QHBoxLayout()
        # create Widget
        weightThreshold_label = QtWidgets.QLabel('Threshold:')
        weightMin_label = QtWidgets.QLabel("Min:")
        self.weightThresholdMin_spinBox = QtWidgets.QDoubleSpinBox()
        weightMax_label = QtWidgets.QLabel("Max:")
        self.weightThresholdMax_spinBox = QtWidgets.QDoubleSpinBox()
        self.selectFilterWeight_button = QtWidgets.QPushButton('Select')
        # set Widget Value
        self.weightThresholdMin_spinBox.setSingleStep(0.01)
        self.weightThresholdMin_spinBox.setDecimals(2)
        self.weightThresholdMax_spinBox.setSingleStep(0.01)
        self.weightThresholdMax_spinBox.setDecimals(2)
        self.weightThresholdMin_spinBox.setValue(self.weightThreshold[0])
        self.weightThresholdMax_spinBox.setValue(self.weightThreshold[1])
        # add Widget
        layout.addWidget(weightThreshold_label)
        subLayout1.addWidget(weightMin_label)
        subLayout1.addWidget(self.weightThresholdMin_spinBox)
        subLayout1.addWidget(weightMax_label)
        subLayout1.addWidget(self.weightThresholdMax_spinBox)
        subLayout1.addWidget(self.selectFilterWeight_button)
        layout.addLayout(subLayout1)
        # set Layout
        uiGrp.setLayout(layout)
        return uiGrp

    def setWeightBox(self):
        uiGrp = QtWidgets.QGroupBox('Set Skin Weight')
        layout = QtWidgets.QVBoxLayout()
        subLayout1 = QtWidgets.QHBoxLayout()
        subLayout2 = QtWidgets.QGridLayout()
        # set Layout Property
        subLayout2.setColumnStretch(1,2)
        # create Widget
        option_label = QtWidgets.QLabel('Option: ')
        self.normalize_checkbox = QtWidgets.QCheckBox('Normalize')
        self.hierachy_checkbox = QtWidgets.QCheckBox('Hierachy')
        self.useLastSelect_checkbox = QtWidgets.QCheckBox('Use last Selection')
        skinweight_label = QtWidgets.QLabel('Weight: ')
        self.weightValue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.weightValue_floatSpinBox = QtWidgets.QDoubleSpinBox()
        self.setWeight_button = QtWidgets.QPushButton('Set')
        self.setWeightInteractive_checkbox = QtWidgets.QCheckBox('live')
        # set Widget Value
        self.normalize_checkbox.setChecked(self.normalizeToggle)
        self.hierachy_checkbox.setChecked(self.hierachyToggle)
        self.useLastSelect_checkbox.setChecked(self.useLastSelectToggle)
        self.weightValue_slider.setMaximum(100)
        self.weightValue_slider.setMinimum(0)
        self.weightValue_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.weightValue_slider.setTickInterval(5)
        self.weightValue_slider.setSingleStep(10)
        self.weightValue_slider.setPageStep(25)
        self.weightValue_slider.setValue(self.weightValue*100)
        # self.weightValue_slider.setTickPosition(self.weightValue)
        self.weightValue_floatSpinBox.setMaximum(1.0)
        self.weightValue_floatSpinBox.setMinimum(0.0)
        self.weightValue_floatSpinBox.setDecimals(2)
        self.weightValue_floatSpinBox.setSingleStep(0.01)
        self.weightValue_floatSpinBox.setValue(self.weightValue)
        self.setWeightInteractive_checkbox.setChecked(self.weightInteractiveState)
        # add Widget
        subLayout1.addWidget(option_label)
        subLayout1.addWidget(self.normalize_checkbox)
        subLayout1.addWidget(self.hierachy_checkbox)
        subLayout1.addWidget(self.useLastSelect_checkbox)
        subLayout2.addWidget(skinweight_label,0,0)
        subLayout2.addWidget(self.weightValue_slider,0,1)
        subLayout2.addWidget(self.weightValue_floatSpinBox,0,2)
        subLayout2.addWidget(self.setWeightInteractive_checkbox,1,2)
        subLayout2.addWidget(self.setWeight_button,1,1)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        # set Layout
        uiGrp.setLayout(layout)
        return uiGrp

    def setDualWeightBox(self):
        uiGrp = QtWidgets.QGroupBox('Set Dual Quarternion Weight')
        layout = QtWidgets.QGridLayout()
        # set Layout Property
        layout.setColumnStretch(1,2)
        # create Widget
        blendWeight_label = QtWidgets.QLabel('Weight: ')
        self.blendWeightValue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.blendWeightValue_floatSpinBox = QtWidgets.QDoubleSpinBox()
        self.setBlendWeight_button = QtWidgets.QPushButton('Set')
        self.setBlendWeightInteractive_checkbox = QtWidgets.QCheckBox('live')
        # set Widget Value
        self.blendWeightValue_slider.setMaximum(100)
        self.blendWeightValue_slider.setMinimum(0)
        self.blendWeightValue_slider.setSingleStep(10)
        self.blendWeightValue_slider.setPageStep(25)
        # self.blendWeightValue_slider.setTickInterval(25)
        self.blendWeightValue_slider.setValue(self.blendWeightValue*100)
        # self.blendWeightValue_slider.setTickPosition(self.blendWeightValue)
        self.blendWeightValue_floatSpinBox.setMaximum(1.0)
        self.blendWeightValue_floatSpinBox.setMinimum(0.0)
        self.blendWeightValue_floatSpinBox.setDecimals(2)
        self.blendWeightValue_floatSpinBox.setSingleStep(0.01)
        self.blendWeightValue_floatSpinBox.setValue(self.blendWeightValue)
        self.setBlendWeightInteractive_checkbox.setChecked(self.blendInteractiveState)
        # add Widget
        layout.addWidget(blendWeight_label,0,0)
        layout.addWidget(self.blendWeightValue_slider,0,1)
        layout.addWidget(self.blendWeightValue_floatSpinBox,0,2)
        layout.addWidget(self.setBlendWeightInteractive_checkbox,1,2)
        layout.addWidget(self.setBlendWeight_button,1,1)
        # set Layout
        uiGrp.setLayout(layout)
        return uiGrp

    def weightUtilBox(self):
        uiGrp = QtWidgets.QGroupBox('Utilities')
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(1)
        layout.setAlignment(QtCore.Qt.AlignTop)
        def button(name, action=None):
            wid = QtWidgets.QPushButton(name)
            layout.addWidget(wid)
            if action:
                wid.clicked.connect(action)
            return wid
        buttonGroup = partial(self.buttonGroup, parent=layout)
        self.enableSkin_button, self.disableSkin_button = buttonGroup(
            ['Smooth Skin', 'Fix Bad Weight'],
            actions=[self.onSmoothSkinWeightClick, self.onHammerSkinWeightClick])
        self.addInfluence_button, self.removeInfluence_button = buttonGroup(
            ['add Influence', 'remove Influence'],
            actions=[self.onAddInfluenceClick, self.onRemoveInfluenceClick])
        self.freezeskinBone_button, self.freezeskinBoneChain_button = buttonGroup(
            ['Freeze Skin Bone', 'Freeze Skin BoneChain'],
            actions=[self.onFreezeSkinBoneClick, self.onFreezeSkinChainClick])
        self.transferWeight_button, self.transferChainWeight_button = buttonGroup(
            ['Transfer Weight Bone', 'Transfer Weight Bone Chain'],
            actions=[self.onTransferWeightClick, self.onTransferChainClick])
        self.resetBindPose = button('Reset BindPose', self.onResetBindPose)
        uiGrp.setLayout(layout)
        return uiGrp

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

    def createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Tool to convenient set skin weight')

    # Action Connector
    def _connectFunction(self):
        #Button CallBack
        ## objectBox
        self.removeTopBoneList_button.clicked.connect(self.boneList_removeTop)
        self.removeAllBones_button.clicked.connect(self.boneList_clear)
        self.removeBottomBoneList_button.clicked.connect(self.boneList_removeBottom)
        self.removeBone_button.clicked.connect(self.boneList_removeSelect)
        self.getInfluencesBone_button.clicked.connect(self.getSkinMeshInfluences)
        # weight Filter Box
        self.selectFilterWeight_button.clicked.connect(self.onWeightFilterClick)
        # weight Setter Box
        self.setWeight_button.clicked.connect(self.onSetWeightClick)
        # blend weight setter box
        self.setBlendWeight_button.clicked.connect(self.onSetBlendWeightClick)

        #UI Callback
        ## object Box
        self.skinType_combobox.currentTextChanged.connect(self.switchSkinType)
        self.bonesName_listBox.itemSelectionChanged.connect(self.updateSelectBone)
        self.bonesName_listBox.doubleClicked.connect(self.selectBoneFromList)
        # self.bonesName_listBox.entered.connect(self.editItemInList)
        ## weight Filter Box
        self.weightThresholdMin_spinBox.valueChanged.connect(self.updateMinimumWeightThreshold)
        self.weightThresholdMax_spinBox.valueChanged.connect(self.updateMaximumWeightThreshold)
        ## set Weight Box
        self.normalize_checkbox.stateChanged.connect(self.updateNormalizeState)
        self.hierachy_checkbox.stateChanged.connect(self.updateHierachyState)
        self.useLastSelect_checkbox.stateChanged.connect(self.updateUseLastSelectState)
        self.weightValue_slider.valueChanged.connect(self.updateWeightValue)
        self.weightValue_floatSpinBox.valueChanged.connect(self.updateWeightValue)
        self.setWeightInteractive_checkbox.stateChanged.connect(self.updateLiveWeightToggle)
        ## set DualWeight Box
        self.blendWeightValue_slider.valueChanged.connect(self.updateBlendWeightValue)
        self.blendWeightValue_floatSpinBox.valueChanged.connect(self.updateBlendWeightValue)
        self.setBlendWeightInteractive_checkbox.stateChanged.connect(self.updateLiveBlendWeightToggle)
        

    # UI Changed Action
    def showEvent(self, event):
        self._initMainUI()
        self.createMenuBar()
        self.createStatusBar()
        self._connectFunction()
        self.updateUIJob = pm.scriptJob(
            e= ["SelectionChanged",self.autoUpdateUI],
            parent = self._name,
            rp=True)
        self.show()

    def closeEvent(self, event):
        if hasattr(self, 'updateUIJob'):
            if pm.scriptJob(exists=self.updateUIJob):
                pm.scriptJob(k=self.updateUIJob)
        self.close()

    def autoUpdateUI(self):
        self.updateSkinMeshList()
        self.updateBonesList()

    def resetUI(self):
        pass

    def updateSkinMeshList(self):
        try:
            objectList = [
                o for o in pm.selected() 
                if ul.get_type(o) == 'mesh']
            self.components_list = [
                c for c in pm.selected()
                if any([ul.get_type(c) == t for t in ['vertex','edge','face']])]
            if objectList:
                self.objectList = objectList
                self.objectName = self.objectList[-1].name()
                self.objectName_text.setText(self.objectName)
                skinClster = ul.get_skin_cluster(self.objectList[-1])
                # self.bones_list = skinClster.getInfluence()
                skinType = skinClster.getSkinMethod()
                # self.skinType_combobox.setCurrentIndex(skinType)
                self.currentSkinType_text.setText(self.skinType_list[skinType])
            else:
                self.currentSkinType_text.setText('None')
        except:
            self.currentSkinType_text.setText('None')

    def updateNormalizeState(self, value):
        self.normalizeToggle = True if value else False
        self.statusbar.showMessage(
            "Normalise Toggle %s" % ('On' if self.normalizeToggle else 'Off'), 500)
        self.updateBoneItemNames()

    def updateHierachyState(self, value):
        self.hierachyToggle = True if value else False
        self.statusbar.showMessage(
            "Hierachy Toggle %s" % ('On' if self.hierachyToggle else 'Off'), 500)

    def updateUseLastSelectState(self, value):
        self.useLastSelectToggle = True if value else False
        self.statusbar.showMessage(
            "Use Last Select %s" % ('On' if self.useLastSelectToggle else 'Off'), 500)

    def updateSelectBone(self):
        self.selectedIndexes = [
            item.row() for item in self.bonesName_listBox.selectedIndexes()]
        # if self.selectedIndexes:
        self.selectedBones_list = []
        for id in self.selectedIndexes:
            try:
                self.selectedBones_list.append(self.bones_list[id])
                assert pm.objExists(self.bones_list[id])
            except IndexError:
                continue
            except AssertionError:
                log.warning('bone {} is no longer exists. Remove from list'.format(self.bones_list[id]))
                self.bonesName_listBox.takeItem(id)
                self.selectedBones_list.pop()
        log.debug('Current Select From List:\n{}'.format(str(self.selectedBones_list)))

    def updateBonesList(self):
        try:
            if not self.lockBonesList_checkBox.checkState():
                bones_list = [
                    b for b in pm.selected() if isinstance(b, pm.nt.Joint)]
                if bones_list:
                    self.bones_list = bones_list
                    self.updateBoneItemNames()
            else:
                if not pm.selected():
                    return
                if pm.selected()[0] in self.bones_list:
                    self.bonesName_listBox.setCurrentRow(
                        self.bones_list.index(pm.selected()[0]))
        except (OSError, IOError, RuntimeError) as why:
            print why
            raise

    def updateBoneItemNames(self):
        if self.bones_list:
            self.bonesName_listBox.clear()
            boneItemNames = [
                'Main: {:^25.21} Weight set to: {:.2f}'.format(
                    b.name().split('|')[-1], self.weightValue) if id == 0 else
                'Filler: {:^25.21} Weight set to: {:.2f}'.format(
                    b.name().split('|')[-1],
                    (1.0-self.weightValue)/(len(self.bones_list)-1) if self.normalizeToggle else (1.0-self.weightValue))
                for id, b in enumerate(self.bones_list)]
            self.bonesName_listBox.addItems(boneItemNames)
        else:
            self.bonesName_listBox.clear()

    def updateMinimumWeightThreshold(self, value):
        if value > self.weightThresholdMax_spinBox.value():
            value = self.weightThresholdMax_spinBox.value()
            self.weightThresholdMin_spinBox.setValue(value)
        self.weightThreshold[0] = value

    def updateMaximumWeightThreshold(self, value):
        if value < self.weightThresholdMin_spinBox.value():
            value = self.weightThresholdMin_spinBox.value()
            self.weightThresholdMax_spinBox.setValue(value)
        self.weightThreshold[1] = value

    def updateLiveWeightToggle(self, value):
        self.weightInteractiveState = True if value else False
        self.statusbar.showMessage(
            "Weight Interactive %s" % ('On' if self.weightInteractiveState else 'Off'), 500)

    def updateLiveBlendWeightToggle(self, value):
        self.blendInteractiveState = True if value else False
        self.statusbar.showMessage(
            "Blend Weight Interactive %s" % ('On' if self.blendInteractiveState else 'Off'), 500)

    def updateWeightValue(self, value):
        if isinstance(value, int):
            value = value/100.0
            self.weightValue_floatSpinBox.setValue(value)
        else:
            self.weightValue_slider.setValue(int(value*100))
        self.weightValue = value
        if self.weightInteractiveState:
            self.onSetWeightClick()
        self.updateBoneItemNames()

    def updateBlendWeightValue(self, value):
        if isinstance(value, int):
            value = value/100.0
            self.blendWeightValue_floatSpinBox.setValue(value)
        else:
            self.blendWeightValue_slider.setValue(int(value*100))
        self.blendWeightValue = value
        if self.blendInteractiveState:
            self.onSetBlendWeightClick()

    # Button Action
    def switchSkinType(self, value):
        if self.objectList:
            skinType = value
            rul.switch_skin_type(self.objectList[-1], type=skinType)
            self.currentSkinType_text.setText(value)
            self.statusbar.showMessage("Skin type set to %s" % value, 500)

    def selectBoneFromList(self, value):
        itemIndex = value.row()
        pm.select(self.bones_list[itemIndex], r=True)

    def getSkinMeshInfluences(self):
        if self.objectList:
            skinCluster = ul.get_skin_cluster(self.objectList[-1])
            self.bones_list = skinCluster.getInfluence()
        self.updateBoneItemNames()

    def boneList_removeTop(self):
        self.bones_list= self.bones_list[1:]
        self.updateBoneItemNames()

    def boneList_clear(self):
        self.bones_list = []
        self.updateBoneItemNames()

    def boneList_removeBottom(self):
        self.bones_list.pop()
        self.updateBoneItemNames()

    def boneList_removeSelect(self):
        selectItems = self.bonesName_listBox.selectedItems()
        for item in selectItems:
            id = self.bonesName_listBox.row(item)
            self.bones_list.pop(id)
        self.updateBoneItemNames()

    def onWeightFilterClick(self):
        if self.selectedBones_list:
            filterBones = self.selectedBones_list
        elif self.bones_list:
            filterBones = self.bones_list
        else:
            filterBones = [j for j in pm.selected() if ul.get_type(j)=='joint']
        if self.objectList and filterBones:
            rul.skin_weight_filter(
                self.objectList[-1],
                filterBones[0],
                min=self.weightThreshold[0],
                max=self.weightThreshold[1],
                select=True)

    def onSetWeightClick(self):
        currentSelection = [
            c for c in pm.selected()
            if any([ul.get_type(c) == t for t in ['mesh', 'vertex','edge','face']])]
        msg = '''
        Last Selection:
        {}
        Current Selection Bone:
        {}
        BonesList:
        {}
        Current Selection Bones:
        {}
        '''.format(
            self.lastSelection,
            currentSelection,
            self.bones_list,
            self.selectedBones_list
        )
        log.debug(msg)
        if self.useLastSelectToggle:
            if not currentSelection:
                currentSelection = self.lastSelection
        self.assertTrue(currentSelection, 'Select component to set skin Weight\n'+\
            'Component can be Vertex, Edge, Face or whole Mesh')
        self.assertTrue(self.bones_list, 'Bone List is empty\nSelect bone to add to list')
        bones_list = self.selectedBones_list if self.selectedBones_list else self.bones_list
        rul.skin_weight_setter(
            currentSelection,
            bones_list,
            skin_value=self.weightValue,
            normalized=self.normalizeToggle,
            hierachy=self.hierachyToggle)
        self.lastSelection = currentSelection
        # show Skin Paint Tools
        if pm.currentCtx() != 'artAttrSkinContext':
            mm.eval('artAttrSkinToolScript 3;')
        lastJoint = pm.artAttrSkinPaintCtx(pm.currentCtx(), query=True, influence=True)
        # artAttrSkinPaintCtx(currentCtx(), edit=True, influence=get_joint[0])
        mm.eval('''
        artAttrSkinToolScript 3;
        artSkinInflListChanging "%s" 0;
        artSkinInflListChanging "%s" 1;
        artSkinInflListChanged artAttrSkinPaintCtx;
        artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;'''
        % (lastJoint, unicode(bones_list[0])))

    def onSetBlendWeightClick(self):
        rul.dual_weight_setter(
            weight_value=self.blendWeightValue,
            sl=True)
        # self.last_selection()
        self.statusbar.showMessage("Dual Quarternion Weight Set!", 500)

    def onSmoothSkinWeightClick(self):
        if self.objectList or self.components_list or self.lastSelection:
            mm.eval('doSmoothSkinWeightsArgList 3 { "0", "5", "0", "1"   };')
            self.statusbar.showMessage("Skin Smooth", 500)

    def onHammerSkinWeightClick(self):
        if self.objectList:
            rul.fix_bad_weight(self.objectList[-1])
            self.statusbar.showMessage("Skin Hammer", 500)

    def onAddInfluenceClick(self):
        addBones = [j for j in pm.selected() if ul.get_type(j)=='joint']
        if self.objectList:
            for bone in addBones:
                rul.add_joint_influence(bone,self.objectList[-1])

    def onRemoveInfluenceClick(self):
        if self.selectedBones_list:
            removeBones = self.selectedBones_list
        elif self.bones_list:
            removeBones = self.bones_list
        else:
            removeBones = [j for j in pm.selected() if ul.get_type(j)=='joint']
        if self.objectList and removeBones:
            if pm.confirmBox('Remove Bone',
                '{} will be remove from {}'.format(
                    [j.name() for j in removeBones], self.objectList[-1])):
                for bone in removeBones:
                    rul.add_joint_influence(bone,self.objectList[-1], remove=True)

    def onFreezeSkinBoneClick(self):
        rul.freeze_skin_joint(sl=True)
    
    def onFreezeSkinChainClick(self):
        rul.freeze_skin_joint(hi=True, sl=True)

    def onTransferWeightClick(self):
        rul.move_skin_weight(sl=True)

    def onTransferChainClick(self):
        rul.move_skin_weight(hi=True, sl=True)
    
    def onResetBindPose(self):
        if self.selectedBones_list:
            selectBones = self.selectedBones_list
        elif self.bones_list:
            selectBones = self.bones_list
        else:
            selectBones = [j for j in pm.selected() if ul.get_type(j)=='joint']
        if selectBones:
            pm.select(selectBones[0],r=True)
            rul.reset_bindPose_all()

    # Util Function
    @staticmethod
    def labelGroup(name, widget, parent, *args, **kws):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        createWidget = widget()
        layout.addWidget(label)
        layout.addWidget(createWidget)
        parent.addLayout(layout, *args, **kws)
        return createWidget

    @staticmethod
    def buttonGroup(names, parent=None, actions=[]):
        layout = QtWidgets.QHBoxLayout()
        createWidgets = []
        for name in names:
            # print name
            createWidget = QtWidgets.QPushButton(name)
            layout.addWidget(createWidget)
            createWidgets.append(createWidget)
        if actions:
            for id, cc in enumerate(actions):
                try:
                    createWidgets[id].clicked.connect(cc)
                except IndexError:
                    pass
        if parent:
            parent.addLayout(layout)
            print tuple(createWidgets)
            return tuple(createWidgets)
        else:
            return (tuple(createWidgets), layout)

    @staticmethod
    def assertTrue(value,msg):
        try:
            assert value
        except AssertionError as why:
            pm.informBox('Error:',msg)
            log.error(msg)
            raise RuntimeError(msg)
    def selection(self):
        if pm.selected():
            self.last_selected = pm.selected()
        return self.last_selected
    
    def previewSkinWeight(self):
        get_joint = [j for j in self.selection() if isinstance(j, pm.nt.Joint)]
        if not get_joint:
            return
        if currentCtx() != 'artAttrSkinContext':
            mm.eval('artAttrSkinToolScript 3;')
        lastJoint = pm.artAttrSkinPaintCtx(pm.currentCtx(), query=True, influence=True)
        # artAttrSkinPaintCtx(currentCtx(), edit=True, influence=get_joint[0])
        mm.eval('''
        artAttrSkinToolScript 3;
        artSkinInflListChanging "%s" 0;
        artSkinInflListChanging "%s" 1;
        artSkinInflListChanged artAttrSkinPaintCtx;
        artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;'''
        % (lastJoint, unicode(get_joint[0])))

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