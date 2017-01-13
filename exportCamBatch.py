import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
if "F:/Script/PipelineTools/" not in sys.path:
    sys.path.append("F:/Script/PipelineTools/")
import exportCam
Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
getFiles = pm.fileDialog2(cap="Select Files",fileFilter=Filters,fm=4)
if getFiles:
    mm.eval("paneLayout -e -m false $gMainPane")
    for f in getFiles:
        cm.file(f,open=True,loadSettings="Load no references",loadReferenceDepth='none',prompt=False,f=True)
        exportCam.exportCam()
    cm.file(f=True,new=True)
    mm.eval("paneLayout -e -m true $gMainPane")