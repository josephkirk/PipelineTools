from PySide2 import QtGui
from lib import QuixelController
class _GCProtector(object):
    widgets = []

app = QtGui.QApplication.instance()
if not app:
    app = QtGui.QApplication([])

def main():
    controller = QuixelController.QuixelColorsController(_GCProtector)
    _GCProtector.widgets.append(controller)
    print(_GCProtector.widgets)

if __name__ == '__main__':
    main()
