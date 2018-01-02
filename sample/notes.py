'''
NOTES

Notes/Todo for Maya

Author: Peppe Russo
All rights reserved (c) 2017

pepperusso.uk
contact.pepperusso@gmail.com

---------------------------------------------------------------------------------------------

INSTALLATION:

Place the notes.py in your maya scripts folder and run this code (in python):

import notes
notes.install()


This will create an icon in the current shelf


---------------------------------------------------------------------------------------------

You are using this script on you own risk.
Things can always go wrong, and under no circumstances the author
would be responsible for any damages caused from the use of this software.

---------------------------------------------------------------------------------------------

The coded instructions, statements, computer programs, and/or related
material (collectively the "Data") in these files are subject to the terms
and conditions defined by
Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License:
   http://creativecommons.org/licenses/by-nc-nd/4.0/
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt

---------------------------------------------------------------------------------------------
'''

__version__ = "1.1.2"
__author__ = 'Peppe Russo'



from maya import cmds


try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

# Logger
import logging

logging.basicConfig()
logger = logging.getLogger('Notes')
logger.setLevel(logging.INFO)




def start():
    logger.debug('Starting')

    createNotes()

    w = MainWindow()
    w.show()

    try:
        checkUpdates()
    except:
        logger.debug("Can't check updates")


def createNotes(*args):
    if cmds.objExists('Notes'):
      logger.debug('Notes node already exist.')
    else:
        # Create notes node
        node = cmds.group(em=True, name='Notes')
        #cmds.setAttr('Notes.hiddenInOutliner', True) # Hide in the outliner

        # Create custom attr
        if not cmds.attributeQuery("notes", n = node, ex = True):
            cmds.addAttr(node, ln = "notes", sn="nts", dt="string")
            #cmds.setAttr("%s.notes"%node, 'Insert notes here..', type="string")
        else:
            logger.debug("%s already has a notes attribute" % node)

def selectNotes(*args):
    if cmds.objExists('Notes'):
      cmds.select('Notes', r=True)
    else:
        logger.info('Notes node doesn\'t exist.')

def deleteNotes(*args):
    if cmds.objExists('Notes'):
        cmds.delete('Notes')
    else:
        logger.info('Notes node doesn\'t exist.')

def toggleOutlinerVis(*args):
    try:
        status = cmds.getAttr('Notes.hiddenInOutliner')
        if status == False:
            cmds.setAttr('Notes.hiddenInOutliner', True) # Hide in the outliner
        else:
            cmds.setAttr('Notes.hiddenInOutliner', False) # Show in the outliner

        # Refresh outliner
        import maya.mel as mel
        mel.eval('AEdagNodeCommonRefreshOutliners();')
    except:
        logger.info("The Notes node doesn't exist")

def settingsUI():
    getNotes = cmds.getAttr("Notes.notes")

    windowName= 'Notes Settings'

    # Make a new window
    if cmds.window(windowName, query=True, exists=True):
        cmds.deleteUI(windowName)

    window = cmds.window(windowName, title=windowName, resizeToFitChildren=True, toolbox=True)

    cmds.columnLayout(adjustableColumn=True)

    cmds.button(label='Create', command=createNotes)
    cmds.button(label='Select', command=selectNotes)
    cmds.button( label='Delete', command=deleteNotes)
    cmds.button( label='Toggle Outliner Vis', command=toggleOutlinerVis)
    cmds.separator()
    cmds.button(label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)'))


    cmds.setParent( '..' )
    cmds.showWindow(window)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Delete if exists
        try:
            cmds.deleteUI('notesWindow')
            logger.debug('Deleted previous UI')
        except:
            logger.debug('No previous UI exists')

        # Get Maya window and parent the controller to it
            
        self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)

        self.setWindowTitle('Notes')
        self.setObjectName('notesWindow')

        self.setMinimumSize(400,400)

        self.buildUI()
        self.populate()

    def buildUI(self):
        # Main widget
        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        # Layout
        self.layout = QtWidgets.QGridLayout()
        widget.setLayout(self.layout)

        # Add Widgets
        self.notesField = QtWidgets.QPlainTextEdit()
        try:
            self.notesField.setPlaceholderText('Insert notes here...')
        except:
            self.notesField.setPlainText('Insert notes here...')
        self.layout.addWidget(self.notesField, 0,0,1,0)

        updateBtn = QtWidgets.QPushButton()
        updateBtn.setText("Update")
        updateBtn.clicked.connect(self.updateNotes)
        self.layout.addWidget(updateBtn, 1,1)

        settingsBtn = QtWidgets.QPushButton()
        settingsBtn.setIcon(QtGui.QIcon(':\gear.png'))
        settingsBtn.setIconSize(QtCore.QSize(24,24))
        settingsBtn.setFixedSize(50,50)
        settingsBtn.clicked.connect(settingsUI)
        self.layout.addWidget(settingsBtn, 1,0,0)

    def populate(self):
        getNotes = cmds.getAttr("Notes.notes")
        self.notesField.setPlainText(getNotes)

    def updateNotes(self):
        logger.debug('Updating notes')

        newText = self.notesField.toPlainText()
        cmds.setAttr("Notes.notes", newText, type="string")

        logger.info("Notes updated to: \n" + newText)


def install():
    ############
    url = 'http://pepperusso.uk/scripts/notes/icon.png' # Url of your icon
    imageName = 'notes.png' # The icon will be saved using this name (include ext) in the icons folder of the current maya version (usually : documents/version/prefs/icons)

    name = 'Notes' # Name to use for the shelf button
    tooltip = 'Create notes in the scene' # Tooltip to use for the shelf button

    # Command of the shelf button.
    command = """import notes
notes.start()"""

    ############

    import maya.mel as mel
    import urllib, os

    ## Get current maya version
    version = cmds.about(version=True)

    ## Download Icon
    appPath = os.environ['MAYA_APP_DIR']
    path = os.path.join(appPath, version, "prefs/icons", imageName)
    urllib.urlretrieve(url, path)

    ## Add to current shelf
    topShelf = mel.eval('$nul = $gShelfTopLevel')
    currentShelf = cmds.tabLayout(topShelf, q=1, st=1)
    cmds.shelfButton(parent=currentShelf, i=path, c=command, label=name, annotation=tooltip)






def checkUpdates():
    import urllib
    url = "http://pepperusso.uk/scripts/notes/update.txt" # Current version of the script.
    update = urllib.urlopen(url).read()

    if update.split("\n")[0] > __version__:
        logger.info("\n".join(update.split("\n")[1:]))


