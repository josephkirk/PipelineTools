import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
import os
import shutil
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
def SendFile(fPath=False, dPath=False, fromFile=True,sendFile=True,sendTex=True):
    if fromFile:
        fullPath = cm.file(q=1,sn=1).split("/")
        srcDrive = fullPath[0]
        if dPath:
            destDrive = dPath
        else:
            destDrive = fullPath[0]
    else:
        fullPath = fPath
    projectPath = "/".join(fullPath[1:fullPath.index("scenes")])
    fileVar= fullPath[len(fullPath)-2]
    filePath= fullPath[fullPath.index("Model"):len(fullPath)-2]
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
    if sendFile:
        try:
            ul.sysCop("/".join([sceneSrc,fileVar,sceneName]),"/".join([sceneDest,fileVar,sceneName]))
            if os.path.isdir("/".join([sceneSrc,fileVar,"rend"])):
                ul.sysCop("/".join([sceneSrc,fileVar,"rend"]),"/".join([sceneDest,fileVar,"rend"]))
        except (IOError,OSError) as why:
            print "scene CopyError\n",why
    if sendTex:
        try:
            ul.sysCop("/".join([texSrc,'_Common']),"/".join([texDest,'_Common']))
        except (IOError,OSError) as why:
            print "texture CopyError\n",why
    print "Finished"