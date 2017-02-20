import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
from PipelineTools import utilities as ul
from datetime import date
def batchExportCam():
    Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    getFiles = pm.fileDialog2(cap="Select Files",fileFilter=Filters,fm=4)
    if getFiles:
        mm.eval("paneLayout -e -m false $gMainPane")
        for f in getFiles:
            cm.file(f,open=True,loadSettings="Load no references",loadReferenceDepth='none',prompt=False,f=True)
            ul.exportCam()
        cm.file(f=True,new=True)
        mm.eval("paneLayout -e -m true $gMainPane")
def SendFile(fPath=False, dPath=False, fromFile=True):
    if fromFile:
        fullPath = cm.file(q=1,sn=1).split("/")
        srcDrive = fullPath[0]
        if dPath:
            destDrive = dPath
        else:
            destDrive = fullPath[0]
    else:
        fullPath = fPath
    projectPath = os.path.join(fullPath[1:fullPath.index("scenes")])
    fileVar= fullPath[len(fullPath)-1]
    filePath= fullPath[fullPath.index("Model"):len(fullPath)-2]
    scenePath = os.path.join([projectPath,u"scenes"]+filePath)
    texPath = os.path.join([projectPath,u"sourceimages"]+filePath)
    sceneName= fullPath[len(fullPath)-1]
    today = date.today()
    todayFolder = "%s%02d%02d" % (str(today.year)[2:],today.month,today.day)
    sceneSrc = os.path.join([srcDrive,scenePath])
    texSrc= os.path.join([srcDrive,texPath])
    sceneDest = os.path.join([destDrive,"to",todayFolder,scenePath])
    texDest = os.path.join([destDrive,"to",todayFolder,texPath])
    # function

    ###Execution
    try:
        ul.sysCop(os.path.join([sceneSrc,fileVar,sceneName]),os.path.join([sceneDest,fileVar,sceneName]))
        if os.path.isdir(os.path.join([sceneSrc,fileVar,"rend"])):
            ul.sysCop(os.path.join([sceneSrc,fileVar,"rend"]),os.path.join([sceneDest,fileVar,"rend"]))
        print os.listdir(sceneDest)
    except:
        print "scene CopyError"
    try:
        ul.sysCop(os.path.join([texSrc,'_Common']),os.path.join([texDest,'_Common']))
    except:
        print "texture CopyError"