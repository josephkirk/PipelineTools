#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""

import pymel.core as pm
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import os
import shutil
import utilities as ul
from datetime import date
#reload(ul)

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

# class skin_weight_setter_UI(object):
#     def __init__(self):
#         self.ui = {}
#         self.ui_value = [(0.0, 0.1), # skin_weight threshold filter
#                          1.0, # skin_weight
#                          0.0] #dual_weight
#         self.weight_tick = 5
#         self.init_ui()
    
#     def update_ui_value(self):
#         for index, (key, value) in enumerate(self.ui.iteritems()):
#             if key is not 'main':
#                 try:
#                     self.ui_value[index-1] = value.getValue()
#                 except:
#                     self.ui_value.append(value.getValue())

#     def set_value(self, *args, **kwargs):
#         if args:
#             if args[0] in self.ui.keys():
#                 self.ui[args[0]].setValue(args[1])
#                 self.update_ui_value()
#             return
#         if kwargs:
#             for key,value in kwargs.iteritems():
#                 if key in self.ui.keys():
#                     self.ui[key].setValue(value)
#             self.update_ui_value()
#             return
    
#     def set_interactive(self,func,**kwargs):
#         for kwarg in kwargs:
#             if kwarg in self.ui.keys():
#                 if self.ui_value[index][1]:
#                     self.ui[kwarg].changeCommand(pm.Callback(func,**kwargs))
#             else:
#                 self.ui[kwarg].changeCommand('pass')

#     @pm.showsHourglass
#     def apply_weight(self,**kwargs):
#         if all([k in kwargs.keys() for k in ['query','filter']]):
#             ul.skin_weight_filter(
#                 min_weight=self.ui_value[0][0],
#                 max_weight=self.ui_value[0][1],
#                 select=True)
#             return
#         if 'dualweight' in kwargs.keys():
#             ul.dual_weight_setter(weight_value=self.ui_value[2])
#             return
#         ul.skin_weight_setter(skin_value=self.ui_value[1])

#     def init_ui(self):
#         def increasement_set(*args,**kwargs):
#             pm.separator(height=5, style='none')
#             pm.gridLayout( numberOfColumns=self.weight_tick, cellWidthHeight=(95, 30))
#             weight_value = 1.0/(self.weight_tick-1)
#             key = str(args[0])
#             key_name = ' '.join(key.split('_'))
#             for i in range(self.weight_tick):
#                 pm.button(
#                 label=str(weight_value*i),
#                 annotation='Set %s value to %04.2f'%(key_name, weight_value*i),
#                 c=pm.Callback(self.set_value, key, weight_value*i))
#             pm.setParent('..')
#         if pm.window('SkinWeightSetterUI', ex=True):
#             pm.deleteUI('SkinWeightSetterUI', window=True)
#             pm.windowPref('SkinWeightSetterUI', remove=True)
#         self.ui['main'] = pm.window('SkinWeightSetterUI', t="Skin Weight Setter")
#         pm.columnLayout(adjustableColumn=1)
#         pm.rowColumnLayout(
#             numberOfColumns=2,
#             columnWidth=[(1, 328), (2, 60)])
#         self.ui['skin_weight_filter'] = pm.floatFieldGrp(
#             numberOfFields=2,
#             label='Skin Weight Threshold: ',
#             value1=self.ui_value[0][0],
#             value2=self.ui_value[0][1])
#         pm.button(
#             label='Get', annotation='Select vertices with skin weight within threshold',
#             c=pm.Callback(self.apply_weight, query=True, filter=True))
#         #)
#         pm.setParent('..')
#         pm.separator(height=10, style='in')
#         self.ui['skin_weight_slider'] = pm.floatSliderButtonGrp(
#             label='Skin Weight: ',
#             annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
#             field=True, precision=2, value=self.ui_value[1], minValue=0.0, maxValue=1.0,
#             buttonLabel='Set', bc=pm.Callback(self.apply_weight),
#             image='playbackLoopingContinuous.png')
#         increasement_set('skin_weight_slider')
#         pm.separator(height=10, style='none')
#         self.ui['dual_weight_slider'] = pm.floatSliderButtonGrp(
#             label='Dual Quarternion Weight: ',
#             annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
#             field=True, precision=2, value=self.ui_value[2],
#             minValue=0.0, maxValue=1.0,
#             #cc=self.set_dual_weight,
#             buttonLabel='Set', bc=pm.Callback(self.apply_weight,dualweight=True),
#             image='playbackLoopingContinuous.png')
#         increasement_set('dual_weight_slider')
#         pm.separator(height=10, style='in')
#         pm.helpLine()
#         pm.showWindow()

class skin_weight_setter_UI(object):
    def __init__(self):
        self.skin_type = 'Classic'
        self.last_selected = []
        self.weight_value = 1.0
        self.normalize = True
        self.hierachy = False
        self.dual_weight_value = 0.0
        self.interactive = False
        self.weight_threshold = (0.0,0.1)
        self.dual_interactive = False
        self.weight_tick=5
        self.init_ui()
    
    def last_selection(self):
        self.last_selected = pm.selected()
        return self.last_selected

    def preview_skin_weight(self):
        get_joint = pm.ls(self.last_selection(), type='joint', orderedSelection=True)
        if not get_joint:
            return
        if pm.currentCtx() != 'artAttrSkinContext':
             mm.eval('artAttrSkinToolScript 3;')
        lastJoint = pm.artAttrSkinPaintCtx(pm.currentCtx(), query=True, influence=True)
        #pm.artAttrSkinPaintCtx(pm.currentCtx(), edit=True, influence=get_joint[0])
        mm.eval('''
        artAttrSkinToolScript 3;
        artSkinInflListChanging "%s" 0;
        artSkinInflListChanging "%s" 1;
        artSkinInflListChanged artAttrSkinPaintCtx;
        artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;'''
        %(lastJoint, unicode(get_joint[0])))

    def set_weight_threshold(self,*args):
        self.weight_threshold = (args[0], args[1])

    def set_skin_type(*args):
        # print args
        ul.switch_skin_type(type=args[1])
        pm.headsUpMessage("Skin type set to %s"%args[1], time=0.2)
    
    def set_interactive_state(self):
        self.interactive = False if self.interactive else True
        pm.headsUpMessage("Interactive %s"%self.interactive, time=0.2)

    def set_dual_interactive_state(self):
        self.dual_interactive = False if self.dual_interactive else True
        pm.headsUpMessage("Interactive %s"%self.dual_interactive, time=0.2)
    
    def set_weight(self, value):
        self.weight_value = round(value,2)
        self.skin_weight_slider_ui.setValue(self.weight_value)
        if self.interactive:
            self.apply_weight()
    
    def set_normalize_state(self,value):
        self.normalize = False if self.normalize else True
        pm.headsUpMessage("Normalize %s"%self.normalize, time=0.2)
    
    def set_hierachy_state(self,value):
        self.hierachy = False if self.hierachy else True
        pm.headsUpMessage("Hierachy %s"%self.hierachy, time=0.2)

    def set_dual_weight(self, value):
        self.dual_weight_value = round(value,2)
        self.dual_weight_slider_ui.setValue(self.dual_weight_value)
        if self.dual_interactive:
            self.dual_weight_setter()

    def select_skin_vertex(self):
        ul.skin_weight_filter(
            min=self.weight_threshold[0],
            max=self.weight_threshold[1],
            select=True)

    @pm.showsHourglass
    def apply_weight(self):
        if pm.currentCtx() == 'artAttrSkinContext':
            mm.eval('artAttrSkinPaintModePaintSelect 0 artAttrSkinPaintCtx')
        if not pm.selected():
            pm.select(self.last_selected,r=True)
        ul.skin_weight_setter(
            skin_value=self.weight_value,
            normalized = self.normalize,
            hierachy=self.hierachy)
        self.last_selection()
        self.preview_skin_weight()
        pm.headsUpMessage("Weight Set!", time=0.2)

    @pm.showsHourglass
    def apply_dual_weight(self):
        if not pm.selected():
            pm.select(self.last_selected)
        ul.dual_weight_setter(weight_value=self.dual_weight_value)
        self.last_selection()
        pm.headsUpMessage("Dual Quarternion Weight Set!", time=0.2)

    def init_ui(self):
        if pm.window('SkinWeightSetterUI', ex=True):
            pm.deleteUI('SkinWeightSetterUI', window=True)
            pm.windowPref('SkinWeightSetterUI', remove=True)
        pm.window('SkinWeightSetterUI', t="Skin Weight Setter")
        pm.columnLayout(adjustableColumn=1)
        pm.optionMenu( label='Skin Type:', changeCommand=self.set_skin_type )
        pm.menuItem( label='Classis' )
        pm.menuItem( label='Dual' )
        pm.menuItem( label='Blend' )
        #pm.setParent('..')
        pm.separator(height=10)
        pm.rowColumnLayout(
            numberOfColumns=2,
            columnWidth=[(1, 320), (2, 120)])
        self.skin_weight_theshold = pm.floatFieldGrp(
            numberOfFields=2,
            label='Weight Threshold:',
            value1=self.weight_threshold[0], value2=self.weight_threshold[1],
            cc=self.set_weight_threshold)
        pm.button(label='Select Vertices', c=pm.Callback(self.select_skin_vertex))
        pm.setParent('..')
        pm.separator(height=10)
        pm.rowColumnLayout(
            numberOfColumns=3,
            columnWidth=[(1, 140), (2, 80)])
        pm.text(label='Option: ', align='right')
        pm.checkBox(
            label='Normalize', annotation='if Normalize is uncheck, set all selected joint weight the same',
            value=self.normalize, cc=self.set_normalize_state)
        pm.checkBox(
            label='Hierachy', annotation='if Hierachy is check, set weight value for child Joint',
            value=self.hierachy, cc=self.set_hierachy_state)
        pm.setParent('..')
        self.skin_weight_slider_ui = pm.floatSliderButtonGrp(
            label='Skin Weight: ', annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
            field=True, precision=2, value=self.weight_value, minValue=0.0, maxValue=1.0,cc=self.set_weight,
            buttonLabel='Set', bc=pm.Callback(self.apply_weight),
            image='playbackLoopingContinuous.png', sbc=self.set_interactive_state)
        pm.separator(height=5, style='none')
        pm.gridLayout( numberOfColumns=self.weight_tick, cellWidthHeight=(95, 30))
        weight_value = 1.0/(self.weight_tick-1)
        for i in range(self.weight_tick):
            pm.button(
                label=str(weight_value*i),
                annotation='Set skin weight to %04.2f'%(weight_value*i),
                c=pm.Callback(self.set_weight,weight_value*i))
        pm.setParent('..')
        pm.separator(height=10)
        self.dual_weight_slider_ui = pm.floatSliderButtonGrp(
            label='Dual Quarternion Weight: ', annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
            field=True, precision=2, value=self.dual_weight_value, minValue=0.0, maxValue=1.0,cc=self.set_dual_weight,
            buttonLabel='Set', bc=pm.Callback(self.apply_dual_weight),
            image='playbackLoopingContinuous.png', sbc=self.set_dual_interactive_state)
        pm.separator(height=5, style='none')
        pm.gridLayout( numberOfColumns=self.weight_tick, cellWidthHeight=(95, 30))
        for i in range(self.weight_tick):
            pm.button(
                label=str(weight_value*i),
                annotation='Set dual quaternion weight to %04.2f'%(weight_value*i),
                c=pm.Callback(self.set_dual_weight, weight_value*i))
        pm.setParent('..')
        pm.separator(height=10, style='none')
        pm.helpLine(annotation='copyright 2018 by Nguyen Phi Hung')
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
