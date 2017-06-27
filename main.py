import pymel.core as pm
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import os
import shutil
from PipelineTools import utilities as ul
from datetime import date
reload(ul)
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
    #
    pm.frameLayout(label="Character List:")
    pm.rowColumnLayout(numberOfColumns=4,
                       columnWidth=[(1, 120), (2, 120), (3, 120), (4, 120)],
                       columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)],
                       rowSpacing=[1, 20])
    CHdirList = [d for d in pp('/'.join([pm.workspace.path, 'scenes/Model/CH'])).normpath().dirs()
                 if d.basename().split('_')[0].isdigit()]
    CHdirList.sort(key=lambda d:d.basename())
    for d in CHdirList:
        subDirectory = d.dirs()
        subDirectory.sort()
        if (subDirectory
                and any([d.basename().split('_')[1] in subd.basename()
                     for subd in subDirectory])):
            chname=d.basename().split('_')[1]
            sendFileUI_dict[chname]={}
            pm.frameLayout(label=d.basename())
            for subd in subDirectory:
                if d.basename().split('_')[1] in subd.basename():
                    sendFileUI_dict[chname][subDirectory.index(subd)+1]=[]
                    pm.frameLayout(label=subd.basename(), cll=True, collapse=True)
                    pm.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 70), (2, 50)])
                    sendFileUI_dict[chname][subDirectory.index(subd)+1].append(
                            pm.checkBox(label='Send'))
                    pm.text(label="")
                    pm.separator(style='in')
                    pm.separator(style='in')
                    for l in ['hair',
                              'cloth',
                              'xgen',
                              'uv',
                              'zbr',
                              'tex',
                              'pattern',
                              '_common']:
                        sendFileUI_dict[chname][subDirectory.index(subd)+1].append(
                            pm.checkBox(label=l))
                    pm.setParent('..')
                    pm.separator(style='out')
                    pm.setParent('..')
                    #pm.separator(style='out')
            pm.setParent('..')
    pm.setParent('..')
    def getDir(dirname, keyList):
        dirList = [d for d in pp('/'.join([pm.workspace.path, 'scenes/Model', dirname])).normpath().dirs()]
        dirList.sort(key=lambda d:d.basename())
        for d in dirList:
            dname = d.basename()
            sendFileUI_dict[dname]=[]
            pm.frameLayout(label=d.basename(), cll=True, collapse=True)
            pm.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 70), (2, 50)])
            sendFileUI_dict[dname].append(
                    pm.checkBox(label='Send'))
            pm.text(label="")
            pm.separator(style='in')
            pm.separator(style='in')
            for l in keyList:
                sendFileUI_dict[dname].append(
                    pm.checkBox(label=l))
            pm.setParent('..')
            pm.separator(style='out')
                    #pm.separator(style='out')
            pm.setParent('..')
    pm.frameLayout(label="BG List:")
    pm.rowColumnLayout(numberOfColumns=4,
                       columnWidth=[(1, 120), (2, 120), (3, 120), (4, 120)],
                       columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)],
                       rowSpacing=[1, 20])
    getDir("BG",["scene", "tex", "psd"])
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

def sendCurrentFileUI():
    if pm.window('SendCurrentFileUI', ex=True):
        pm.deleteUI('SendCurrentFileUI', window=True)
        pm.windowPref('SendCurrentFileUI', remove=True)
    pm.window('SendCurrentFileUI', t="Send current file")
    pm.columnLayout(adjustableColumn=1)
    pm.rowColumnLayout(
        numberOfColumns=2,
        columnWidth=[(1, 90), (2, 90)])
    pm.text(label='Destination :', align='right')
    descDriveUI = pm.textField(text="N")
    pm.text(label='Version :', align='right')
    sendFolderIDUI = pm.intField(value=1,min=1)
    pm.text(label='')
    pm.button(label="Send",
              c=lambda *arg: ul.send_current_file(
                drive=descDriveUI.getText(),
                version=sendFolderIDUI.getValue()))
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
