import sys
import pymel.core as pm
from PySide2 import QtWidgets, QtCore
"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
### test decouple UI 
class ConverterWindow(QtWidgets.QMainWindow):
    #convert signal from UI to command
    convertClicked = QtCore.Signal(list)
def create_window():
    #init MainWindow
    win = ConverterWindow()
    win.setWindowTitle('demoUI')
    #Generate Widget
    container = QtWidgets.QWidget(win)
    label = QtWidgets.QLabel('Edit:',container)
    textbox = QtWidgets.QLineEdit(container)
    textbox2 = QtWidgets.QLineEdit(container)
    button = QtWidgets.QPushButton('OK', container)
    #Interaction
    def onclick():
        text_combo = [textbox.text(),textbox2.text()]
        win.convertClicked.emit(text_combo)
    button.clicked.connect(onclick)
    #Layout Widget
    layout = QtWidgets.QHBoxLayout(container)
    container.setLayout(layout)
    layout.addWidget(label)
    layout.addWidget(textbox)
    layout.addWidget(textbox2)
    layout.addWidget(button)
    win.setCentralWidget(container)
    return win

if __name__ =='__main__': # if run directly, do these code
    def onconvert(textList):
        for text in textList:
            print 'createSphere ', text
            pm.polySphere(name=text)
    app = QtWidgets.QApplication([])
    win = create_window()
    win.convertClicked.connect(onconvert)
    win.show()
    app.exec_()
#app.exec_()
#sys.exit(app.excec_())