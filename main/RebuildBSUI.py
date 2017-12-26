#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymel.core as pm
import logging
from functools import partial
from string import ascii_uppercase as alphabet
from itertools import product
import uiStyle
# from ..core import general_utils as ul
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
class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
        try:
            pm.deleteUI('RebuildBlendShapeWindow')
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Rebuild BlendShape')
        self.setObjectName('RebuildBlendShapeWindow')

    def _initUIValue(self):
        self.currentBS = 0
        self.blendShape_list = self.getBlendShapes()
        self.exclude_list = []
        self.rebuildBlendShapeName = 'RebuildBS'
        self.rebuildBlendShapeGrpName = 'facialTarget'
        # self.set
        self.offsetValue = 20

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

    def createMainWidgets(self):
        # create Layout
        grpBox = QtWidgets.QGroupBox()
        layout = QtWidgets.QVBoxLayout()
        subLayout1 = QtWidgets.QGridLayout()
        subLayout2 = QtWidgets.QHBoxLayout()
        # create widget
        blendShapes_label = QtWidgets.QLabel('BlendShapes: ')
        self.blendShapes_comboxBox = QtWidgets.QComboBox()
        # self.blendShapesRefresh_button = QtWidgets.QPushButton('Refresh')
        layout.addLayout(subLayout1)
        self.exclude_lineedit = self.labelGroup('Exclude: ', QtWidgets.QLineEdit, layout)
        self.rebuildBSName_lineedit = self.labelGroup('Rebuild BS Name: ', QtWidgets.QLineEdit, layout)
        self.rebuildName_lineedit = self.labelGroup('Rebuild Group Name: ', QtWidgets.QLineEdit, layout)
        self.offset_spinbox = self.labelGroup('Offset: ', QtWidgets.QSpinBox, subLayout2)
        self.rebuild_button = QtWidgets.QPushButton('Rebuild')
        # add Widget
        subLayout1.addWidget(blendShapes_label,0,0)
        subLayout1.addWidget(self.blendShapes_comboxBox,0,1)
        # subLayout1.addWidget(self.blendShapesRefresh_button,0,2)
        subLayout2.addWidget(self.rebuild_button)
        subLayout1.setColumnStretch(1,2)
        layout.addLayout(subLayout2)
        grpBox.setLayout(layout)
        self.mainLayout.addWidget(grpBox)
        # set Widget Value
        self.blendShapes_comboxBox.addItems(self.blendShape_list)
        self.offset_spinbox.setValue(self.offsetValue)
        self.rebuildBSName_lineedit.setText(self.rebuildBlendShapeName)
        self.rebuildName_lineedit.setText(self.rebuildBlendShapeGrpName)

    def connectEvent(self):
        # self.blendShapesRefresh_button.clicked.connect(self.onRefreshBlendShapeListClick)
        self.rebuild_button.clicked.connect(self.onRebuildBlendShapeClick)

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
        self.statusbar.showMessage('Tool to Rebuild BlendShape')

    # Main UI Event
    def showEvent(self, event):
        self._initUIValue()
        self._initMainUI()
        self.createMenuBar()
        self.createStatusBar()
        self.connectEvent()
        self.updateUIJob = pm.scriptJob(
            e=['idle', self.autoUpdateUI],
            parent='RebuildBlendShapeWindow',
            rp=True
        )
        self.show()

    def closeEvent(self, event):
        if hasattr(self, 'updateUIJob'):
            if pm.scriptJob(exists=self.updateUIJob):
                pm.scriptJob(k=self.updateUIJob)
        self.close()

    def autoUpdateUI(self):
        if self.blendShape_list != self.getBlendShapes():
            self.refreshBlendShapeList()
            # self.refreshBlendShapeList()

    def resetUI(self):
        pass
    # UI Item Event

    def refreshBlendShapeList(self):
        for i in range(self.blendShapes_comboxBox.count()):
            self.blendShapes_comboxBox.removeItem(0)
        self.blendShape_list = self.getBlendShapes()
        self.blendShapes_comboxBox.addItems(self.blendShape_list)
    
    def onRebuildBlendShapeClick(self):
        rul.rebuild_blendshape_target(
            self.blendShapes_comboxBox.currentText(),
            self.rebuildBSName_lineedit.text(),
            rebuild=True,
            parent=self.rebuildName_lineedit.text(),
            offset=self.offset_spinbox.value(),
            exclude=self.exclude_lineedit.text().split(',')
        )
        # self.onRefreshBlendShapeListClick()

    # Util Function
    @staticmethod
    def getBlendShapes():
        bsList = [bs.name() for bs in pm.ls(type='blendShape')]
        return bsList
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