import pymel.core as pm
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import os
import shutil
from PipelineTools import utilities as ul
from PipelineTools import hairOps as ho

from datetime import date
reload(ul)
reload(ho)
###Global Var
def addValue(v, t=None):
    if t:
        t = v
        print t
    else:
        print v
###Function
def batchExportCam():
    '''Export all Baked Cam to Fbx Files'''
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

def sendFileUI():
    if pm.window('SendFileUI2', ex=True):
        pm.deleteUI('SendFileUI2', window=True)
        pm.windowPref('SendFileUI2', remove=True)
    pm.window('SendFileUI2', t="SendFileUI")
    sendFileUI_dict = {}
    def sendFile(num=0, destdrive=""):
        for CH, subCH in sendFileUI_dict.iteritems():
            for subCHID, value in subCH.iteritems():
                sendFileDict = {}
                for v in value:
                    sendFileDict[v.getLabel()] = v.getValue()
                ul.sendFile(CH,
                            subCHID,
                            num=num,
                            destdrive=destdrive,
                            sendFile=sendFileDict)
    pm.columnLayout()
    pm.frameLayout(label="Character List:")
    #pm.gridLayout( numberOfColumns=4, cellWidthHeight=(120, 100))
    pm.rowColumnLayout(numberOfColumns=4,
                       columnWidth=[(1, 120), (2, 120), (3, 120), (4, 120)],
                       columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)],
                       rowSpacing=[1, 20])
    CHdirList = [d for d in pp('/'.join([pm.workspace.path, 'scenes/Model/CH'])).normpath().dirs()
                 if d.basename().split('_')[0].isdigit()]
    CHdirList.sort(key=lambda d:d.basename())
    for d in CHdirList:
        subDirectory = d.dirs()
        if (subDirectory
                and any([d.basename().split('_')[1] in subd.basename()
                     for subd in subDirectory])):
            chname=d.basename().split('_')[1]
            sendFileUI_dict[chname]={}
            pm.frameLayout(label=d.basename(),)
            for subd in subDirectory:
                if d.basename().split('_')[1] in subd.basename():
                    sendFileUI_dict[chname][subDirectory.index(subd)+1]=[]
                    pm.frameLayout(label=subd.basename(), cll=True, collapse=True)
                    pm.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 70), (2, 50)])
                    for l in ['hair',
                              'cloth',
                              'render',
                              'uv',
                              'zbr',
                              'tex',
                              'pattern',
                              '_common']:
                        sendFileUI_dict[chname][subDirectory.index(subd)+1].append(
                            pm.checkBox(label=l))
                pm.setParent('..')
                pm.setParent('..')
            pm.setParent('..')
    pm.setParent('..')
    pm.separator(style='shelf')
    pm.rowColumnLayout(numberOfColumns=4,
                       columnWidth=[(1, 120), (2, 120), (3, 120), (4, 120)],
                       columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)],
                       rowSpacing=[1,10])
    pm.text(label='number', align='right')
    sendFolderIDUI = pm.intField(value=1,min=1)
    pm.text(label='Destination', align='right')
    descDriveUI = pm.textField(text="")
    pm.setParent('..')
    pm.button(label='Send',c=lambda *args:sendFile(num=sendFolderIDUI.getValue(),
                                                   destdrive=descDriveUI.getText()))
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
    pm.button(label="SelectCtr", c=lambda *arg: ho.selHair())
    pm.popupMenu()
    pm.menuItem(label='Set pivot to root',
                c=lambda *arg: ho.selHair(setPivot=True))
    pm.menuItem(label='Set pivot to tip',
                c=lambda *arg: ho.selHair(pivot=-1, setPivot=True))
    pm.menuItem(label='Show all controls',
                c=lambda *arg: ho.ToggleHairCtrlVis(state='show'))
    pm.menuItem(label='Hide all controls',
                c=lambda *arg: ho.ToggleHairCtrlVis(state='hide'))
    pm.button(label="Create",
              c=lambda *arg: ho.makeHairMesh(
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
                c=lambda *arg: ho.selHair(
                    rebuild=[
                        True,
                        LDivsValUI.getValue(),
                        WDivsValUI.getValue()]))
    pm.menuItem(label='Rebuild also controls',
                c=lambda *arg: ho.selHair(
                    rebuild=[
                        True,
                        LDivsValUI.getValue(),
                        WDivsValUI.getValue()],
                    cShape=(
                        True,
                        cShapeOpUI.getValue(),
                        segmentWidthUI.getValue())))
    pm.button(label="Duplicate",
              c=lambda *arg: ho.dupHairMesh())
    pm.popupMenu()
    pm.menuItem(label='Mirror',
                c=lambda *arg: ho.dupHairMesh(mirror=True,
                                              axis=axisOpUI.getValue(),
                                              space=mirrorOpUI.getValue()))
    pm.button(label="RemoveHair",
              c=lambda *arg: ho.delHair())
    pm.popupMenu()
    pm.menuItem(label='RemoveControl',
                c=lambda *arg: ho.delHair(keepHair=True))
    pm.menuItem(label='RemoveAllControl',
                c=lambda *arg: ho.cleanHairMesh())
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
