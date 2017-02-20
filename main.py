import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
from PipelineTools import Utilities as ul
def batchExportCam():
    Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    getFiles = pm.fileDialog2(cap="Select Files",fileFilter=Filters,fm=4)
    if getFiles:
        mm.eval("paneLayout -e -m false $gMainPane")
        for f in getFiles:
            cm.file(f,open=True,loadSettings="Load no references",loadReferenceDepth='none',prompt=False,f=True)
            ul.exportCam.exportCam()
        cm.file(f=True,new=True)
        mm.eval("paneLayout -e -m true $gMainPane")
def SendFile(fPath=False, dPath=False, fromFile=True):
    if fromFile:
        fullPath = cmds.file(q=1,sn=1).split("/")
        srcDrive = fullPath[0]
        if dPath:
            destDrive = dPath
        else:
            destDrive = fullPath[0]
    else:
        fullPath = fPath
    projectPath = "/".join(fullPath[1:fullPath.index("scenes")])
    filePath= fullPath[fullPath.index("Model"):len(fullPath)-1]
    scenePath = "/".join([projectPath,u"scenes"]+filePath)
    texPath = "/".join([projectPath,u"sourceimages"]+filePath)
    sceneName= fullPath[len(fullPath)-1]
    today = date.today()
    todayFolder = "%s%02d%02d" % (str(today.year)[2:],today.month,today.day)
    sceneSrc = "/".join([srcDrive,scenePath])
    texSrc= "/".join([srcDrive,texPath])
    sceneDest = "/".join([destDrive,"to",todayFolder,scenePath])
    texDest = "/".join([destDrive,"to",todayFolder,texPath])
    # function

    ###Execution
    try:
        ul.sysCop("/".join([sceneSrc,sceneName]),"/".join([sceneDest,sceneName]))
        if os.path.isdir("/".join([sceneSrc,"rend"])):
            ul.sysCop("/".join([sceneSrc,"rend"]),"/".join([sceneDest,"rend"]))
        print os.listdir(sceneDest)
    except:
        print "scene CopyError"
    try:
        ul.sysCop("/".join([texSrc,'_Common']),"/".join([texDest,'_Common']))
    except:
        print "texture CopyError"