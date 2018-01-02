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
class JetTool(QtWidgets.QMainWindow):
    def __init__(self):
        super(JetTool, self).__init__()
        try:
            pm.deleteUI('PipelineToolsWindow')
        except:
            pass
        # mayaMainWindow = {o.objectName(): o for o in QtWidgets.qApp.topLevelWidgets()}["MayaWindow"]
        self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Pipeline Tools')
        self.setObjectName('PipelineToolsWindow')
        self.setMinimumSize(250,100)
        self._makeUI()

    # def onclick(self):
    #     text_combo = [self.textbox.text(),self.textbox2.text()]
    #     self.convertClicked.emit(text_combo)
    #     print text_combo

    def _makeUI(self):
        #Generate Widget
        self.container = QtWidgets.QWidget(self)
        self.container2 = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QGridLayout(self.container2)
        #Interaction
        # self.button.clicked.connect(self.onclick)
        #Layout Widget
        self.layout = QtWidgets.QGridLayout(self.container)
        self.container.setLayout(self.layout)
        self.layout.setContentsMargins(5, 15, 5, 5)
        self.layout.setHorizontalSpacing(1)
        self.layout.setVerticalSpacing(2)

        for i in range(5):
            self.layout.setColumnMinimumWidth(i,15)
            if not i%2:
                self.layout.setColumnStretch(i,i)

                
                groupbox = QtWidgets.QGroupBox('testGp')
                label = QtWidgets.QLabel('Edit:',self.container)
                labeltextbox = QtWidgets.QLineEdit(self.container)
                labelbutton = QtWidgets.QPushButton('OK', self.container)
                subLayout = QtWidgets.QHBoxLayout(self.container)
                subLayout.addWidget(label)
                subLayout.addWidget(labeltextbox)
                subLayout.addWidget(labelbutton)
                groupbox.setLayout(subLayout)
                
                groupbox2 = QtWidgets.QGroupBox('testGp2')
                textbox = QtWidgets.QLineEdit(self.container)
                textbox2 = QtWidgets.QLineEdit(self.container)
                button = QtWidgets.QPushButton('OK', self.container)
                subLayout2 = QtWidgets.QVBoxLayout(self.container)
                subLayout2.addWidget(textbox)
                subLayout2.addWidget(textbox2)
                subLayout2.addWidget(button)
                groupbox2.setLayout(subLayout2)

                self.layout.addWidget(groupbox,0,i)
                self.layout.addWidget(groupbox2,1,i)
                
        self.tabWid = QtWidgets.QTabWidget(self)
        self.tabWid.addTab(self.container,'test')
        self.tabWid.addTab(self.container2,'test2')
        self.setCentralWidget(self.tabWid)
