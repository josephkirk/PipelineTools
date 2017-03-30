import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
import os
import shutil
from PipelineTools import utilities as ul
reload(ul)
from datetime import date
###Global Var
def addValue(v, t=None):
    if t:
        t = v
        print t
    else:
        print v
###Function
def batchExportCam():
    Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    getFiles = pm.fileDialog2(cap="Select Files", fileFilter=Filters, fm=4)
    if getFiles:
        mm.eval("paneLayout -e -m false $gMainPane")
        for f in getFiles:
            cm.file(
                f,
                open=True,
                loadSettings="Load no references",
                loadReferenceDepth='none',
                prompt=False, f=True)
            ul.exportCam()
        cm.file(f=True, new=True)
        mm.eval("paneLayout -e -m true $gMainPane")
def SendFile(num="",
             fPath=False,
             dPath=False,
             fromFile=True,
             sendFile=True,
             sendUV=True,
             sendZbr=True,
             sendTex=False,
             sendPattern=False,
             sendCommon=False):
    if fromFile:
        fullPath = cm.file(q=1, sn=1).split("/")
        srcDrive = fullPath[0]
        if dPath:
            destDrive = dPath
        else:
            destDrive = fullPath[0]
    else:
        fullPath = fPath
    projectPath = "/".join(fullPath[1:fullPath.index("scenes")])
    fileVar = fullPath[len(fullPath)-2]
    filePath = fullPath[fullPath.index("Model"):len(fullPath)-2]
    #filePath.append(fileVar)
    scenePath = "/".join([projectPath, u"scenes"]+filePath)
    texPath = "/".join([projectPath, u"sourceimages"]+filePath)
    sceneName = fullPath[len(fullPath)-1]
    today = date.today()
    todayFolder = "%s%02d%02d" % (str(today.year)[2:], today.month, today.day)
    if num:
        todayFolder += "_"+num
    sceneSrc = "/".join([srcDrive, scenePath])
    texSrc = "/".join([srcDrive, texPath])
    sceneDest = "/".join([destDrive, "to", todayFolder, scenePath])
    texDest = "/".join([destDrive, "to", todayFolder, texPath])
    # function

    ###Execution
    if sendFile:
        try:
            ul.sysCop(
                "/".join([sceneSrc, fileVar, sceneName]),
                "/".join([sceneDest, fileVar, sceneName]))
            if os.path.isdir("/".join([sceneSrc, fileVar, "rend"])):
                ul.sysCop(
                    "/".join([sceneSrc, fileVar, "rend"]),
                    "/".join([sceneDest, fileVar, "rend"]))
            else:
                return
        except (IOError, OSError) as why:
            print "scene CopyError\n", why
    if sendUV:
        try:
            if os.path.isdir("/".join([texSrc, fileVar, "uv"])):
                ul.sysCop(
                    "/".join([texSrc, fileVar, "uv"]),
                    "/".join([texDest, fileVar, "uv"]))
            else:
                return
        except (IOError, OSError) as why:
            print "uv CopyError\n", why
    if sendZbr:
        try:
            if os.path.isdir("/".join([texSrc, fileVar, "zbr"])):
                ul.sysCop(
                    "/".join([texSrc, fileVar, "zbr"]),
                    "/".join([texDest, fileVar, "zbr"]))
            else:
                return
        except (IOError, OSError) as why:
            print "zbr CopyError\n", why
    if sendTex:
        try:
            ul.sysCop(texSrc, texDest)
            print "Finished send Texture"
        except (IOError, OSError) as why:
            print "texture CopyError\n", why
    if sendPattern:
        try:
            if os.path.isdir("/".join([texSrc, fileVar, "pattern"])):
                ul.sysCop(
                    "/".join([texSrc, fileVar, "pattern"]),
                    "/".join([texDest, fileVar, "pattern"]))
            else:
                return
        except (IOError, OSError) as why:
            print "Pattern CopyError\n", why
    if sendCommon:
        try:
            ul.sysCop(
                "/".join([texSrc, fileVar, '_Common']),
                "/".join([texDest, fileVar, '_Common']))
            print "Finished send Common"
        except (IOError, OSError) as why:
            print "texture CopyError\n", why
    print "/"*2+"Ssjp-010/scc/NS57"+'/to/'+todayFolder

def SendFileUI():
    if pm.window('SendFileUI', ex=True):
        pm.deleteUI('SendFileUI', window=True)
        pm.windowPref('SendFileUI', remove=True)
    pm.window('SendFileUI', t="SendFileUI")
    pm.frameLayout(label="SendFile")
    pm.columnLayout(adjustableColumn=1)
    pm.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 90), (2, 100)])
    pm.text(label="Number: ", align='right')
    numUI = pm.textField(text="")
    pm.text(label="Send File: ", align='right')
    sendFilecbUI = pm.checkBox(label="   ", value=True)
    pm.text(label="Send UV: ", align='right')
    sendUVcbUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Send Zbr: ", align='right')
    sendZbrcbUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Send Textures: ", align='right')
    sendTexcbUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Send Patterns: ", align='right')
    sendPatterncbUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Send _Commmon: ", align='right')
    sendTexCommoncbUI = pm.checkBox(label="   ", value=False)
    pm.text(label="", align='right')
    pm.button(label="Send",
              c=lambda *arg: SendFile(
                  num=numUI.getText(),
                  sendFile=sendFilecbUI.getValue(),
                  sendTex=sendTexcbUI.getValue(),
                  sendPattern=sendPatterncbUI.getValue(),
                  sendUV=sendUVcbUI.getValue(),
                  sendZbr=sendZbrcbUI.getValue(),
                  sendCommon=sendTexCommoncbUI.getValue()))
    pm.showWindow()
def makeHairUI():
    shapeType = ['circle','triangle','square']
    axisType = ['x', 'y', 'z']
    mirrorType = ['world', 'local']
    if pm.window('MakeHairUI', ex=True):
        pm.deleteUI('MakeHairUI', window=True)
        pm.windowPref('MakeHairUI', remove=True)
    pm.window('MakeHairUI', t="MakeHairUI")
    pm.frameLayout(label="Create Hair Parameters")
    pm.columnLayout(adjustableColumn=1)
    pm.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 90), (2, 100)])
    pm.text(label="Name: ", align='right')
    hairNameUI = pm.textField(text="HairMesh#")
    pm.text(label="Material: ", align='right')
    matNameUI = pm.textField(text="SY_mtl_hairSG")
    pm.text(label="CreaseSet: ", align='right')
    hsSetNameUI = pm.textField(text="hairCrease")
    #pm.text(label="PointCreaseSet: ",align='right')
    #hpSetNameUI=pm.textField(text="hairPointCrease")
    pm.text(label="Length Divs: ", align='right')
    LDivsValUI = pm.intField(value=7, min=4)
    pm.text(label="Width Divs: ", align='right')
    WDivsValUI = pm.intField(value=4, min=4)
    pm.text(label="Segments: ", align='right')
    segmentValUI = pm.intField(value=4, min=2)
    pm.text(label="Width: ", align='right')
    segmentWidthUI = pm.floatField(value=1, min=0.01)
    pm.text(label="Delete Curves: ", align='right')
    DelCurveUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Reverse: ", align='right')
    RevCurveUI = pm.checkBox(label="   ", value=False)
    pm.text(label="Control Type: ", align='right')
    cShapeOpUI = pm.optionMenu()
    for st in shapeType:
        pm.menuItem(label=st)
    pm.text(label="Mirror Type: ", align='right')
    mirrorOpUI = pm.optionMenu()
    for mt in mirrorType:
        pm.menuItem(label=mt)
    pm.text(label="Mirror Axis: ", align='right')
    axisOpUI = pm.optionMenu()
    for ax in axisType:
        pm.menuItem(label=ax)
    pm.button(label="SelectCtr", c=lambda *arg: ul.selHair())
    pm.popupMenu()
    setPivotUI = pm.menuItem(label='SetPivot',
                             c=lambda *arg: ul.selHair(setPivot=True))
    pm.menuItem(label='Show/Hide Control',
                c=lambda *arg: ul.hideHairCtrl())
    pm.menuItem(label='show/Hide AllControl',
                c=lambda *arg: ul.hideHairCtrl(allHide=True))
    pm.button(label="Create",
              c=lambda *arg: ul.makeHairMesh(
                  name=hairNameUI.getText(),
                  mat=matNameUI.getText(),
                  cSet=hsSetNameUI.getText(),
                  reverse=RevCurveUI.getValue(),
                  lengthDivs=LDivsValUI.getValue(),
                  widthDivs=WDivsValUI.getValue(),
                  Segments=segmentValUI.getValue(),
                  width=segmentWidthUI.getValue(),
                  curveDel=DelCurveUI.getValue(),
                  cShape=cShapeOpUI.getValue()))
    pm.popupMenu()
    pm.menuItem(label='Rebuild',
                c=lambda *arg: ul.selHair(
                    rebuild=[
                        True,
                        LDivsValUI.getValue(),
                        WDivsValUI.getValue()]))
    pm.menuItem(label='RebuildalsoControls',
                c=lambda *arg: ul.selHair(
                    rebuild=[
                        True,
                        LDivsValUI.getValue(),
                        WDivsValUI.getValue()],
                    cShape=(
                        True,
                        cShapeOpUI.getValue(),
                        segmentWidthUI.getValue())))
    pm.button(label="Duplicate",
              c=lambda *arg: ul.dupHairMesh())
    pm.popupMenu()
    pm.menuItem(label='Mirror',
                c=lambda *arg: ul.dupHairMesh(mirror=True,
                                              axis=axisOpUI.getValue(),
                                              space=mirrorOpUI.getValue()))
    pm.button(label="RemoveHair",
              c=lambda *arg: ul.delHair())
    pm.popupMenu()
    pm.menuItem(label='RemoveControl',
                c=lambda *arg: ul.delHair(keepHair=True))
    pm.menuItem(label='RemoveAllControl',
                c=lambda *arg: ul.cleanHairMesh())
    pm.setParent('..')
    pm.showWindow()

def mirrorUVui():
    if pm.window('MirrorUVUI', ex=True):
        pm.deleteUI('MirrorUVUI', window=True)
        pm.windowPref('MirrorUVUI', remove=True)
    pm.window('MirrorUVUI', t="Mirror UI")
    pm.columnLayout(adjustableColumn=1)
    pm.rowColumnLayout(
        numberOfColumns=3,
        columnWidth=[(1, 90), (2, 90), (3, 60)])
    mirrorDirID = pm.radioCollection()
    pm.radioButton(label="Left", select=True)
    pm.radioButton(label="Right")
    pm.button(label="Mirror",
              c=lambda *arg: ul.mirrorUV(
                  dir=pm.radioButton(mirrorDirID.getSelect(),
                                     q=1, l=1)))
    pm.setParent('..')
    pm.showWindow()
