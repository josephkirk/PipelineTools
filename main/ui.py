#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
from __future__ import with_statement

import maya.cmds as cm
import maya.mel as mm
from pymel.core import *

from ..core import general_utils as ul
from ..core import rigging_utils as rig

reload(ul)


###Global Var
###Function
def batch_export_cam():
    '''Export all Baked Cam to Fbx Files'''
    Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    getFiles = fileDialog2(cap="Select Files", fileFilter=Filters, fm=4)
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

class RigTools:
    def __init__(self):
        self._name = 'Rig Tools'
        self._windowname = self._name.replace(' ','')+'Window'
    @classmethod
    def show(cls):
        cls._init_ui()
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newname):
        self._name = newname
        self._windowname = self._name.replace(' ','')+'Window'

    @property
    def window(self):
        if pm.window(self._windowname, exists=True):
            pm.deleteUI(self._name)
            pm.windowPref(self._name, remove=True)
        self._window = pm.window(
            self._windowname, title=self._title,
            rtf=True, sizeable=False)
        return self._window

    @property
    def template(self):
        self._template = pm.uiTemplate(self._windowname.replace('Window', 'UITemplate'), force=True)
        return self._template

    def create_rig_util_ui(self):
        with pm.frameLayout(label='Utils:'):
            pm.button(label='Basic Intergration', c=pm.Callback(ru.basic_intergration))
            pm.button(label='Create Prop Control', c=pm.Callback(self._do6))
            pm.button(label='Create Parent Control', c=pm.Callback(self._do5))
            pm.button(label='Create Short Hair Control', c=pm.Callback(ru.create_short_hair_simple))
            pm.button(label='Create Single Short Hair Control', c=pm.Callback(ru.create_short_hair_single))
            pm.button(label='Create Long Hair Control', c=pm.Callback(HairRig))
            with pm.rowColumnLayout(rs=[(1,0),]):
                smallbutton = ul.partial(pm.button,h=30)
                smallbutton(label='create Parent', c=pm.Callback(ru.create_parent))
                smallbutton(label='delete Parent', c=pm.Callback(ru.remove_parent))
                smallbutton(label='Parent Shape', c=pm.Callback(ul.parent_shape))
                smallbutton(label='create Offset bone', c=pm.Callback(ru.createOffsetJoint))
                smallbutton(label='create Loc', c=pm.Callback(ru.create_loc_control, connect=False))
                smallbutton(label='create Loc control', c=pm.Callback(ru.create_loc_control))
                smallbutton(label='connect with Loc', c=pm.Callback(ru.connect_with_loc))
                smallbutton(label='vertex to Loc', c=pm.Callback(ru.create_loc_on_vert))
                smallbutton(label='connect Transform', c=pm.Callback(ru.connectTransform))
                with pm.popupMenu(b=3):
                    pm.menuItem(label='connect Translate', c=pm.Callback(
                        ru.connectTransform,
                        translate=True, rotate=False, scale=False))
                    pm.menuItem(label='connect Rotate', c=pm.Callback(
                        ru.connectTransform,
                        translate=False, rotate=True, scale=False))
                    pm.menuItem(label='connect Scale', c=pm.Callback(
                        ru.connectTransform,
                        translate=False, rotate=False, scale=True))
                smallbutton(label='disconnect Transform', c=pm.Callback(ru.connectTransform,disconnect=True))
            smallbutton(label='multi Parent Constraint', c=pm.Callback(ru.contraint_multi, constraintType='Parent'))
            with pm.popupMenu(b=3):
                pm.menuItem(label='multi Point Constraint', c=pm.Callback(
                    ru.contraint_multi,
                    constraintType='Point'))
                pm.menuItem(label='multi Orient Constraint', c=pm.Callback(
                    ru.contraint_multi,
                    constraintType='Orient'))
                pm.menuItem(label='multi Point&Orient Constraint', c=pm.Callback(
                    ru.contraint_multi,
                    constraintType='PointOrient'))
                pm.menuItem(label='multi Aim Constraint', c=pm.Callback(
                    ru.contraint_multi,
                    constraintType='Aim'))
            with pm.rowColumnLayout():
                self._uiElement['visAtrName'] = pm.textFieldGrp(
                    cl2=('left', 'right'),
                    co2=(0, 0),
                    cw2=(40, 100),
                    label='Vis Attribute Name:', text='FullRigVis')
                smallbutton(
                    label='Connect Visibility', c=lambda x:ru.connect_visibility(
                        attrname= self._uiElement['visAtrName'].getText()))
            with pm.rowColumnLayout():
                pm.button(label='Channel History ON', c=pm.Callback(ru.toggleChannelHistory,True))
                with pm.popupMenu(b=3):
                    pm.menuItem(label='Channel History OFF', c=pm.Callback(ru.toggleChannelHistory,False))
                pm.button(label='Deform Normal Off', c=pm.Callback(ru.deform_normal_off))

    def init_ui(self):
        with self.window:
            with self.template:
                with frameLayout(label='FacialRig'):
                    pass
                with frameLayout(label='SecondaryRig'):
                    pass
                self.create_rig_util_ui()

class SendCurrentFile(object):
    def __init__(self):
        self._name = 'SendCurrentFileUI'
        self._title = 'Send Current File Window'
        self._set()

    def __call__(self):
        return self.window

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def name(self):
        return self._name

    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(self._name, title=self._title, rtf=True, width=10, height=10, sizeable=False)
        return self._window

    def info(self):
        print 'self:', self
        print '__str__:', self.__str__()
        print '__repr__:', self.__repr__()
        print 'window:', self.window(), type(self.window())
        print 'name:', self.name()
        if window(self.name(), ex=True):
            print self.name(), 'exists'

    def _set(self):
        self.window()
        self.template = uiTemplate('SendCurrentFileUITemplate', force=True)
        self.template.define(button, width=100, height=40, align='left')
        self.template.define(frameLayout, borderVisible=False, labelVisible=True)
        self.template.define(rowColumnLayout, numberOfColumns=3, columnWidth=[(1, 90), (2, 90), (3, 90)])
        self.elements = {}
        # self.window().closeCommand(self.window().delete)

    def get_state(self):
        pass

    def set_state(self, state):
        pass

    def restore(self):
        pass

    def save_state(self):
        pass

    def show(self):
        scene_name = sceneName()
        with self.window():
            with self.template:
                with frameLayout(label='Sending {}'.format(scene_name.dirname())):
                    with columnLayout(adjustableColumn=1):
                        with frameLayout(label='Scene Options'):
                            with rowColumnLayout():
                                self.elements['scene'] = checkBox(label='scene', value=True)
                                self.elements['lastest'] = checkBox(label='Get lastest', value=True)
                                self.elements['render'] = checkBox(label='render', value=True)
                        with frameLayout(label='SourceImages Options'):
                            with rowColumnLayout():
                                self.elements['tex'] = checkBox(label='tex', value=True)
                                self.elements['extras'] = {}
                                for label in ['psd',
                                              'zbr',
                                              'uv',
                                              'pattern']:
                                    self.elements['extras'][label] = checkBox(label=label, value=False)
                                self.elements['extras']['psd'].setValue(True)
                        with frameLayout(label='"to" folder number'):
                            with rowColumnLayout(numberOfColumns=2):
                                text(label='Suffix:')
                                self.elements['suffix'] = textField(text='_vn')
                                text(label='Number:')
                                self.elements['version'] = intField(value=1, min=1)
                        button(label="Send", c=Callback(self.send))
                        # self.window().setResizeToFitChildren(True)

    def get_value(self):
        self.results = {}
        for key, value in self.elements.items():
            if isinstance(value, dict):
                self.results[key] = []
                for subkey, subvalue in value.items():
                    if subvalue.getValue():
                        self.results[key].append(subkey)
            else:
                try:
                    self.results[key] = value.getValue()
                except:
                    self.results[key] = value.getText()
        return self.results

    def send(self, *args, **kwargs):
        kwargs = self.get_value()
        print kwargs
        ul.send_current_file(**kwargs)


class FacialRig(object):
    def __init__(self):
        self._name = 'FacialRigUI'
        self._title = 'Facial Rig Window'
        self.window = window(self._name, title=self._title)
        self.__set()

    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(self._name, title=self._title, rtf=True, width=10, height=10, sizeable=False)
        return self._window

    def info(self):
        print 'self:', self
        print '__str__:', self.__str__()
        print '__repr__:', self.__repr__()
        print 'window:', self.window(), type(self.window())
        print 'name:', self.name()
        if window(self.name(), ex=True):
            print self.name(), 'exists'

    def _set(self):
        self.window()
        self.template = uiTemplate('SendCurrentFileUITemplate', force=True)
        self.template.define(button, width=100, height=40, align='left')
        self.template.define(frameLayout, borderVisible=False, labelVisible=True)
        self.template.define(rowColumnLayout, numberOfColumns=3, columnWidth=[(1, 90), (2, 90), (3, 90)])
        self.elements = {}

    def show(self):
        with self.window():
            with self.template:
                with frameLayout(label='Sending {}'.format(scene_name.dirname())):
                    with columnLayout(adjustableColumn=1):
                        button(label="Rig It", c=Callback(self.apply))

    def apply(*args, **kwargs):
        rig.create_facial_rig()


class SkinWeightSetter(object):
    def __init__(self):
        self.skin_type = 'Classic'
        self.last_selected = []
        self.weight_value = 1.0
        self.normalize = True
        self.hierachy = False
        self.dual_weight_value = 0.0
        self.interactive = False
        self.weight_threshold = (0.0, 0.1)
        self.dual_interactive = False
        self.weight_tick = 5
        self.init_ui()

    def last_selection(self):
        self.last_selected = selected()
        return self.last_selected

    def preview_skin_weight(self):
        get_joint = ls(self.last_selection(), type='joint', orderedSelection=True)
        if not get_joint:
            return
        if currentCtx() != 'artAttrSkinContext':
            mm.eval('artAttrSkinToolScript 3;')
        lastJoint = artAttrSkinPaintCtx(currentCtx(), query=True, influence=True)
        # artAttrSkinPaintCtx(currentCtx(), edit=True, influence=get_joint[0])
        mm.eval('''
        artAttrSkinToolScript 3;
        artSkinInflListChanging "%s" 0;
        artSkinInflListChanging "%s" 1;
        artSkinInflListChanged artAttrSkinPaintCtx;
        artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;'''
                % (lastJoint, unicode(get_joint[0])))

    def set_weight_threshold(self, *args):
        self.weight_threshold = (args[0], args[1])

    def set_skin_type(*args):
        # print args
        ul.switch_skin_type(type=args[1])
        headsUpMessage("Skin type set to %s" % args[1], time=0.2)

    def set_interactive_state(self):
        self.interactive = False if self.interactive else True
        headsUpMessage("Interactive %s" % self.interactive, time=0.2)

    def set_dual_interactive_state(self):
        self.dual_interactive = False if self.dual_interactive else True
        headsUpMessage("Interactive %s" % self.dual_interactive, time=0.2)

    def set_weight(self, value):
        self.weight_value = round(value, 2)
        self.skin_weight_slider_ui.setValue(self.weight_value)
        if self.interactive:
            self.apply_weight()

    def set_normalize_state(self, value):
        self.normalize = False if self.normalize else True
        headsUpMessage("Normalize %s" % self.normalize, time=0.2)

    def set_hierachy_state(self, value):
        self.hierachy = False if self.hierachy else True
        headsUpMessage("Hierachy %s" % self.hierachy, time=0.2)

    def set_dual_weight(self, value):
        self.dual_weight_value = round(value, 2)
        self.dual_weight_slider_ui.setValue(self.dual_weight_value)
        if self.dual_interactive:
            self.dual_weight_setter()

    def select_skin_vertex(self):
        ul.skin_weight_filter(
            min=self.weight_threshold[0],
            max=self.weight_threshold[1],
            select=True)

    @showsHourglass
    def apply_weight(self):
        if currentCtx() == 'artAttrSkinContext':
            mm.eval('artAttrSkinPaintModePaintSelect 0 artAttrSkinPaintCtx')
        if not selected():
            select(self.last_selected, r=True)
        ul.skin_weight_setter(
            skin_value=self.weight_value,
            normalized=self.normalize,
            hierachy=self.hierachy)
        self.last_selection()
        self.preview_skin_weight()
        headsUpMessage("Weight Set!", time=0.2)

    @showsHourglass
    def apply_dual_weight(self):
        if not selected():
            select(self.last_selected)
        ul.dual_weight_setter(weight_value=self.dual_weight_value)
        self.last_selection()
        headsUpMessage("Dual Quarternion Weight Set!", time=0.2)

    def init_ui(self):
        if window('SkinWeightSetterUI', ex=True):
            deleteUI('SkinWeightSetterUI', window=True)
            windowPref('SkinWeightSetterUI', remove=True)
        window('SkinWeightSetterUI', t="Skin Weight Setter")
        columnLayout(adjustableColumn=1)
        optionMenu(label='Skin Type:', changeCommand=self.set_skin_type)
        menuItem(label='Classis')
        menuItem(label='Dual')
        menuItem(label='Blend')
        # setParent('..')
        separator(height=10)
        rowColumnLayout(
            numberOfColumns=2,
            columnWidth=[(1, 320), (2, 120)])
        self.skin_weight_theshold = floatFieldGrp(
            numberOfFields=2,
            label='Weight Threshold:',
            value1=self.weight_threshold[0], value2=self.weight_threshold[1],
            cc=self.set_weight_threshold)
        button(label='Select Vertices', c=Callback(self.select_skin_vertex))
        setParent('..')
        separator(height=10)
        rowColumnLayout(
            numberOfColumns=3,
            columnWidth=[(1, 140), (2, 80)])
        text(label='Option: ', align='right')
        checkBox(
            label='Normalize', annotation='if Normalize is uncheck, set all selected joint weight the same',
            value=self.normalize, cc=self.set_normalize_state)
        checkBox(
            label='Hierachy', annotation='if Hierachy is check, set weight value for child Joint',
            value=self.hierachy, cc=self.set_hierachy_state)
        setParent('..')
        self.skin_weight_slider_ui = floatSliderButtonGrp(
            label='Skin Weight: ',
            annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
            field=True, precision=2, value=self.weight_value, minValue=0.0, maxValue=1.0, cc=self.set_weight,
            buttonLabel='Set', bc=Callback(self.apply_weight),
            image='playbackLoopingContinuous.png', sbc=self.set_interactive_state)
        separator(height=5, style='none')
        gridLayout(numberOfColumns=self.weight_tick, cellWidthHeight=(95, 30))
        weight_value = 1.0 / (self.weight_tick - 1)
        for i in range(self.weight_tick):
            button(
                label=str(weight_value * i),
                annotation='Set skin weight to %04.2f' % (weight_value * i),
                c=Callback(self.set_weight, weight_value * i))
        setParent('..')
        separator(height=10)
        self.dual_weight_slider_ui = floatSliderButtonGrp(
            label='Dual Quarternion Weight: ',
            annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
            field=True, precision=2, value=self.dual_weight_value, minValue=0.0, maxValue=1.0, cc=self.set_dual_weight,
            buttonLabel='Set', bc=Callback(self.apply_dual_weight),
            image='playbackLoopingContinuous.png', sbc=self.set_dual_interactive_state)
        separator(height=5, style='none')
        gridLayout(numberOfColumns=self.weight_tick, cellWidthHeight=(95, 30))
        for i in range(self.weight_tick):
            button(
                label=str(weight_value * i),
                annotation='Set dual quaternion weight to %04.2f' % (weight_value * i),
                c=Callback(self.set_dual_weight, weight_value * i))
        setParent('..')
        separator(height=10, style='none')
        helpLine(annotation='copyright 2018 by Nguyen Phi Hung')
        showWindow()


def mirror_uv():
    if window('MirrorUVUI', ex=True):
        deleteUI('MirrorUVUI', window=True)
        windowPref('MirrorUVUI', remove=True)
    window('MirrorUVUI', t="Mirror UI")
    columnLayout(adjustableColumn=1)
    rowColumnLayout(
        numberOfColumns=3,
        columnWidth=[(1, 90), (2, 90), (3, 60)])
    mirrorDirID = radioCollection()
    radioButton(label="Left", select=True)
    radioButton(label="Right")
    button(label="Mirror",
           c=lambda *arg: ul.mirrorUV(
               dir=radioButton(mirrorDirID.getSelect(),
                               q=1, l=1)))
    setParent('..')
    showWindow()
