from PipelineTools import ui
window = None
def show():
    global window
    if window is None:
        cont = ui.HierachyConverterController()
        window = ui.create_window(cont)
    _window.show()