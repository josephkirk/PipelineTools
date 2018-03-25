try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

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
QListWidget {
    color: lightgray;
    font: bold;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #222222, stop: 1 #333333);
    show-decoration-selected: 1; /* make the selection span the entire width of the view */
}

QListWidget::item {
    bottom: 5px;
}
QListWidget::item:selected {
    padding-left: 5px;
}

QListWidget::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 darkgray, stop: 1 gray);
}

QListWidget::item:selected:active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 darkgray, stop: 1 gray);
}

QListWidget::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #333333, stop: 1 #444444);
}

QStatusBar {
    border-color: lightgray;
    border-width: 2px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgb(30,30,30), stop:1 rgb(40,40,40));
}
QStatusBar::item {
    border: 1px solid red;
    border-radius: 3px;
}
"""
def addDivider(widget, layout=None):
    line = QtWidgets.QFrame(widget)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    if layout:
        layout.addWidget(line)
    else:
        return widget

def labelGroup(name, widget, parent=None, returnLabel=False, *args, **kws):
    layout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(name)
    # print args, kws
    createWidget = widget(*args, **kws)
    layout.addWidget(label)
    layout.addWidget(createWidget)
    if parent:
        parent.addLayout(layout)
        result = (label, createWidget) if returnLabel else createWidget
        return result
    else:
        result = (label, createWidget, layout) if returnLabel else (createWidget, layout)
        return result

def multiLabelLayout(names, widget, groupLabel='', dir='horizontal', parent=None, *args, **kws):
    dirDict = {
        'horizontal': QtWidgets.QBoxLayout.LeftToRight,
        'vertical': QtWidgets.QBoxLayout.TopToBottom
    }
    layout = QtWidgets.QBoxLayout(dirDict[dir])
    if groupLabel:
        label = QtWidgets.QLabel(groupLabel)
        layout.addWidget(label)
    widgets = []
    for name in names:
        sublayout = QtWidgets.QHBoxLayout()
        sublabel = QtWidgets.QLabel(name)
        createWidget = widget(*args, **kws)
        sublayout.addWidget(sublabel)
        sublayout.addWidget(createWidget)
        layout.addLayout(sublayout)
        widgets.append(createWidget)
    if parent:
        parent.setSpacing(2)
        # parent.setStretch(0,1)
        parent.addLayout(layout)
        return tuple(widgets)
    else:
        return (tuple(widgets), layout)

def multiOptionsLayout(names, groupname='', parent=None, updateActions=[]):
    layout = QtWidgets.QHBoxLayout()
    if groupname:
        label = QtWidgets.QLabel(groupname)
        layout.addWidget(label)
    createWidgets = []
    for name in names:
        createWidget = QtWidgets.QCheckBox(name)
        layout.addWidget(createWidget)
        createWidgets.append(createWidget)
    if updateActions:
        for id, cc in enumerate(updateActions):
            try:
                createWidgets[id].stateChanged.connect(cc)
            except IndexError:
                pass
    if parent:
        parent.addLayout(layout)
        return tuple(createWidgets)
    else:
        return (tuple(createWidgets), layout)

def multiButtonsLayout(names, parent=None, actions=[]):
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
        # print tuple(createWidgets)
        return tuple(createWidgets)
    else:
        return (tuple(createWidgets), layout)

def buttonsGroup(groupnames, names, collums=2, parent=None, iconsPath=[], actions=[]):
    group = QtWidgets.QGroupBox(groupnames)
    layout = QtWidgets.QGridLayout()
    buttons = [QtWidgets.QPushButton(name) for name in names]
    for id, iconPath in enumerate(iconsPath):
        icon = QtGui.QIcon(iconPath)
        buttons[id].setIcon(icon)
        buttons[id].setText('')
        buttons[id].setIconSize(QtCore.QSize(28,28))
        buttons[id].setFixedSize(QtCore.QSize(28,28))
        buttons[id].setStyleSheet('QPushButton {border-style: none; border-width: 0px; background-color: rgba(0,0,0,0) } ')
    stack = buttons[:]
    row=0
    while stack:
        for collum in range(collums):
            if stack:
                button = stack.pop()
                layout.addWidget(button, row, collum)
        row += 1
    for id, action in enumerate(actions):
        buttons[id].clicked.connect(action)

    group.setLayout(layout)
    return group

def findIcon(icon):
    """
    Loop over all icon paths registered in the XBMLANGPATH environment 
    variable ( appending the tools icon path to that list ). If the 
    icon exist a full path will be returned.

    :param str icon: icon name including extention
    :return: icon path
    :rtype: str or None
    """
    paths = []

    # get maya icon paths
    if os.environ.get("XBMLANGPATH"):     
        paths = os.environ.get("XBMLANGPATH").split(os.pathsep)                                 

    # append tool icon path
    paths.insert(
        0,
        os.path.join(
            os.path.split(__file__)[0], 
            "icons" 
        ) 
    )
