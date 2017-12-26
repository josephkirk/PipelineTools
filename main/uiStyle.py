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