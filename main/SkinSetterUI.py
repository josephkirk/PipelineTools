#!/usr/bin/env python
# -*- coding: utf-8 -*-
import maya.mel as mm
import pymel.core as pm
import logging
from functools import partial
from string import ascii_uppercase as alphabet
from itertools import product
from ..core import general_utils as ul
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
# UIClass
class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
        try:
            pm.deleteUI('SkinWeightToolWindow')
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
        self.setObjectName('SkinWeightToolWindow')
    # init UI
    def _initUIValue(self):
        self.objectName = 'None'
        self.skinType_list = ['Classic', 'Dual Quartenion', 'Blended'] 
        self.currentSkinType = 0
        self.objectInfluences = []
        self.lastSelected = []
        self.weightValue = 1.0
        self.normalizeToggle = True
        self.hierachyToggle = False
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
        self._setStyleSheet()
        # self._connectFunction()
        # self.autoUpdateUI()

    def _setStyleSheet(self):
        styleSheet = """
            QFrame {
                font: italic 12px; 
                border: 2px solid rgb(20,20,20);
                border-radius: 4px;
                border-width: 0px;
                padding: 2px;
                background-color: rgb(70,70,70);
                }

            QMenu {
                margin: 2px; /* some spacing around the menu */
            }

            QMenuBar {
                font: bold 12px;
                border-color: lightgray;
                border-width: 2px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(30,30,30), stop:1 rgb(40,40,40));
            }

            QPushButton {
                background-color: rgb(100,100,100);
                }

            QGroupBox {
                font: bold 12px;
                color: rgb(200,200,200);
                padding-top: 10px;
                background-color: rgb(80,80,80);
                border: 1px solid gray;
                border-radius: 4px;
                margin-top: 5px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center; /* position at the top center */
                padding: 0px 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 3px;
            }
            """
        self.setStyleSheet(styleSheet)
    # create Layout
    # Action Connector
    def _connectFunction(self):
        pass

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
        subLayout1 = QtWidgets.QHBoxLayout()
        # subLayout1 = QtWidgets.QGridLayout()
        # create Widget
        objectName_label = QtWidgets.QLabel('Skin Mesh')
        objectName_label.setAlignment(QtCore.Qt.AlignCenter)
        self.objectName_text = QtWidgets.QLineEdit(self.objectName)
        bonesName_label = QtWidgets.QLabel('Skin Bones')
        bonesName_label.setAlignment(QtCore.Qt.AlignCenter)
        self.bonesName_listBox = QtWidgets.QListWidget()
        self.lockBonesList_checkBox = QtWidgets.QCheckBox('Lock List')
        self.getInfluencesBone_button = QtWidgets.QPushButton('Get Influences')
        # set Widget Value
        self.objectName_text.setEnabled(False)
        # connect UI Function
        self.getInfluencesBone_button.clicked.connect(self.getSkinMeshInfluences)
        # add Widget
        layout.addWidget(objectName_label)
        layout.addWidget(self.objectName_text)
        layout.addWidget(self.skinTypeBox())
        layout.addWidget(bonesName_label)
        layout.addWidget(self.bonesName_listBox)
        subLayout1.addWidget(self.lockBonesList_checkBox)
        subLayout1.addWidget(self.getInfluencesBone_button)
        layout.addLayout(subLayout1)
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
        self.normalize_checkbox = QtWidgets.QCheckBox('normalize')
        self.hierachy_checkbox = QtWidgets.QCheckBox('hierachy')
        skinweight_label = QtWidgets.QLabel('Weight: ')
        self.weightValue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.weightValue_floatSpinBox = QtWidgets.QDoubleSpinBox()
        self.setWeight_button = QtWidgets.QPushButton('Set')
        self.setWeightInteractive_checkbox = QtWidgets.QCheckBox('live')
        # set Widget Value
        self.normalize_checkbox.setChecked(self.normalizeToggle)
        self.hierachy_checkbox.setChecked(self.hierachyToggle)
        self.weightValue_slider.setMaximum(100)
        self.weightValue_slider.setMinimum(0)
        self.weightValue_slider.setSingleStep(10)
        self.weightValue_slider.setPageStep(25)
        # self.weightValue_slider.setTickInterval(25)
        self.weightValue_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.weightValue_slider.setValue(self.weightValue*100)
        # self.weightValue_slider.setTickPosition(self.weightValue)
        self.weightValue_floatSpinBox.setMaximum(1.0)
        self.weightValue_floatSpinBox.setMinimum(0.0)
        self.weightValue_floatSpinBox.setDecimals(2)
        self.weightValue_floatSpinBox.setSingleStep(0.01)
        self.weightValue_floatSpinBox.setValue(self.weightValue)
        self.setWeightInteractive_checkbox.setChecked(self.weightInteractiveState)
        # connect Widget
        self.weightValue_slider.valueChanged.connect(self.updateWeightValue)
        self.weightValue_floatSpinBox.valueChanged.connect(self.updateWeightValue)
        self.setWeightInteractive_checkbox.stateChanged.connect(self.updateLiveWeightToggle)
        # add Widget
        subLayout1.addWidget(option_label)
        subLayout1.addWidget(self.normalize_checkbox)
        subLayout1.addWidget(self.hierachy_checkbox)
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
        # connect Widget
        self.blendWeightValue_slider.valueChanged.connect(self.updateBlendWeightValue)
        self.blendWeightValue_floatSpinBox.valueChanged.connect(self.updateBlendWeightValue)
        self.setBlendWeightInteractive_checkbox.stateChanged.connect(self.updateLiveBlendWeightToggle)
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
        def button(name):
            wid = QtWidgets.QPushButton(name)
            layout.addWidget(wid)
            return wid 
        self.addInfluence_button = button('add Influence')
        self.removeInfluence_button = button('remove Influence')
        self.freezeskinBone_button = button('Freeze Skin Bone')
        self.freezeskinBoneChain_button = button('Freeze Skin BoneChain')
        self.transferWeight_button = button('Transfer Weight Bone')
        self.transferChainWeight_button = button('Transfer Weight Bone Chain')
        self.resetBindPose = button('Reset BindPose')
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
        pass
    # UI Changed Action
    def resetUI(self):
        pass

    def updateUI(self):
        self.updateSkinMeshList()
        self.updateBonesNameList()
    
    def updateSkinMeshList(self):
        try:
            skinClster = ul.get_skin_cluster(pm.selected()[-1])
            if skinClster:
                self.objectName = pm.selected()[-1].name()
                self.objectInfluences = skinClster.getInfluence()
                self.objectName_text.setText(self.objectName)
                skinType = skinClster.getSkinMethod()
                self.skinType_combobox.setCurrentIndex(skinType)
                self.currentSkinType_text.setText(self.skinType_combobox.currentText())
            else:
                self.objectName_text.setText('None')
        except:
            pass

    def updateBonesNameList(self):
        if not self.lockBonesList_checkBox.checkState():
            self.bonesName_listBox.clear()
            self.skinBones = [
                b for b in pm.selected() if isinstance(b, pm.nt.Joint)]
            self.bonesName_listBox.insertItems(0, [b.name() for b in self.skinBones])

    def showEvent(self, event):
        self._initMainUI()
        self.createMenuBar()
        self.createStatusBar()
        self.updateUIJob = pm.scriptJob( e= ["SelectionChanged",self.updateUI], parent = 'SkinWeightToolWindow')
        self.show()

    def closeEvent(self, event):
        if hasattr(self, 'updateUIJob'):
            if pm.scriptJob(exists=self.updateUIJob):
                pm.scriptJob(k=self.updateUIJob)
        self.close()

    def updateLiveWeightToggle(self, value):
        self.weightInteractiveState = value

    def updateLiveBlendWeightToggle(self, value):
        self.blendInteractiveState = value

    def updateWeightValue(self, value):
        if isinstance(value, int):
            value = value/100.0
            self.weightValue_floatSpinBox.setValue(value)
        else:
            self.weightValue_slider.setValue(int(value*100))
        if self.weightInteractiveState:
            print value

    def updateBlendWeightValue(self, value):
        if isinstance(value, int):
            value = value/100.0
            self.blendWeightValue_floatSpinBox.setValue(value)
        else:
            self.blendWeightValue_slider.setValue(int(value*100))
        if self.blendInteractiveState:
            print value
    # Button Action
    def getSkinMeshInfluences(self):
        if self.objectInfluences:
            pm.select(self.objectInfluences,r=True)
    # Util Function
    @staticmethod
    def labelGroup(name, widget, parent, *args, **kws):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        # label.setAlignment(QtCore.Qt.AlignRight)
        createWidget = widget()
        layout.addWidget(label)
        layout.addWidget(createWidget)
        # layout.setColumnStretch(1,2)
        # layout.setColumnMinimumWidth(0,50)
        parent.addLayout(layout, *args, **kws)
        # layout.setContentsMargins(0,0,0,0)
        return createWidget

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