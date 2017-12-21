#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
from __future__ import with_statement

import types
from .. import core
from ..project_specific import ns57
from pymel.core import *
# core._reload()

# Global Var
ul = core.ul
ru = core.rul
rcl = core.rcl
# Function
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
            ul.export_cameras_to_fbx()
        cm.file(f=True, new=True)
        mm.eval("paneLayout -e -m true $gMainPane")

# UI Class
class UITemplate:
    def __init__(self, name):
        self._name = name
        self._uiTemplate = uiTemplate('{}{}'.format(name, 'UITemplate'), force=True)
        self._uiTemplate.define(
            button, height=30, align='left', bgc=[0.15,0.25,0.35])
        self._uiTemplate.define(
            columnLayout, adjustableColumn=1,
            cal='right', cat =('both',0))
        self._uiTemplate.define(
            frameLayout, borderVisible=False,
            collapsable=False,
            cl=False, labelVisible=True,
            cc=Callback(self.reset_window_height),
            mh=2, mw=2, font='boldLabelFont',
            bgc=[0.2,0.2,0.2])
        self._uiTemplate.define(
            gridLayout,
            numberOfColumns=2, cw=140)
        self._uiTemplate.define(
            rowColumnLayout,
            rs=[(1, 1),],
            numberOfColumns=2,
            cw=[(1,50),],
            cal=[(1,'center'),],
            cat=[(1, 'both',1),],
            rat=[(1, 'top',1),])
        self.subframe = ul.partial(
            frameLayout,
            collapsable=False, la='center', li=60,
            bgs=True, bgc=[0.35]*3)
        self.smallbutton = ul.partial(button, h=30, bgc=[0.35,0.4,0.4])

    def reset_window_height(self):
        if window(self._name, exists=True):
            window(self._name,e=True, h=1)

    def define(self,*args,**kws):
        self._uiTemplate.define(*args, **kws)

    def get(self):
        return self._uiTemplate

class RigTools(object):
    def __init__(self):
        self._name = 'Jet Maya Tools'
        self._windowname = self._name.replace(' ','')+'Window'
        self.template = UITemplate(self._windowname)
        self.nodebase = []
        self.nodetrack = NodeTracker()
        self.fullbasetrack = []
        self.fullcreatedtrack = []
        self.ControlObClass = rcl.ControlObject()
        self.SkinSetterClass = SkinWeightSetter()
        self.window

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newname):
        self._name = newname
        self._windowname = self._name.replace(' ','')+'Window'

    @property
    def window(self):
        if window(self._windowname, exists=True):
            deleteUI(self._windowname)
            windowPref(self._windowname, remove=True)
        self._window = window(
            self._windowname, title=self._name,
            menuBar=True,
            rtf=True)
        self._windowSize = (1, 1)
        self._uiElement = {}
        return self._window

    @window.setter
    def window(self,newSize):
        self._windowSize = newSize

    def reset_window_height(self):
        #self._window.setSizeable(True)
        self._window.setHeight(1)

    def setUIValue(self, key, value):
        self._uiElement[key] = value
        print key, self._uiElement[key]

    def get_hair_system(self):
        hairSystem = ls(type='hairSystem')
        if hairSystem:
            self._uiElement['Hair System'].setText(hairSystem[-1].getParent().name())
            select(hairSystem[-1])

    def _delete_tracknode(self):
        scriptJob(ka=True)
        self.nodetrack.endTrack()
        del self.nodetrack

    def _ui_update(self):
        self.nodetrack.reset()
        #self.nodetrack.startTrack()
        print self.nodetrack.getNodes()

    def do_func(self, func, **kws):
        for kw,value in kws.items():
            if isinstance(value,types.MethodType):
                kws[kw] = value()
        self.nodebase = []
        for i in selected():
            self.nodebase.append(i)
            self.nodebase.extend(i.listRelatives(type='transform',ad=True))
        self.nodetrack.reset()
        self.nodetrack.startTrack()
        #self.ControlObClass.createControl()'
        sel=selected()
        if hasattr(self.ControlObClass, '_uiName'):
            if window(self.ControlObClass._uiName + 'Window', ex=True):
                if self._uiElement['useUIShape'].getValue():
                    kws['customShape'] = self.ControlObClass.createControl
        select(sel)
        func(**kws)
        # delete(kws['customShape'])
        self.nodetrack.endTrack()
        self.fullbasetrack.extend(self.nodebase)
        self.fullcreatedtrack.extend(self.nodetrack.getNodes())
        
    def delete_created_nodes(self , all=False):
        if all:
            self.nodebase = self.fullbasetrack
            trackNodes = self.fullcreatedtrack
        else:
            trackNodes = self.nodetrack.getNodes()
        if trackNodes:
            try:
                for node in trackNodes:
                    print node
                    if objExists(node):
                        condition = any([
                            c in self.nodebase
                            for c in node.listRelatives(type='transform',ad=True)]) \
                            if hasattr(node,'listRelatives') else False
                        if condition:
                            continue
                        if hasattr(node,'listRelatives'):
                            for c in node.listRelatives(type='transform',ad=True):
                                if c in trackNodes:
                                    trackNodes.remove(c)
                        delete(node)
                for node in self.nodebase:
                    if not node.getParent():
                        continue
                    if node.getParent() in self.nodebase:
                        continue
                    if 'offset' in node.getParent().name().lower():
                        ru.remove_parent(node)
            except (MayaNodeError,TypeError) as why:
                warning(why)


    def create_rig_util_ui(self):
            with columnLayout():
                with frameLayout(label='Tools:', cl=False): 
                    button(
                        label='Bone and Skin Tools',
                        ann='Utilities to help with skinning and bone creation',
                        c=Callback(self.SkinSetterClass.init_ui))

                with frameLayout(label='Create Control:',cl=False, font='boldLabelFont'):
                    center_text = ul.partial(text, align='center')
                    button(
                        label='Create Control Shape UI',
                        ann='Utilities to create NurbsCurve Shape for Control',
                        c=Callback(self.ControlObClass._showUI))
                    with columnLayout():
                        with self.template.subframe(label='Control Types', li=80):
                            with columnLayout(cat =('both',15)):
                                with gridLayout():
                                    self._uiElement['useLoc'] = checkBox(label='Connect using Locator')
                                    self._uiElement['useUIShape'] = checkBox(label='Use UI Shape')
                            with columnLayout():
                                with self.template.subframe(label='Single Bone Control'):
                                    with gridLayout():
                                        self.template.smallbutton(
                                            label='Prop Control',
                                            c=Callback(
                                                self.do_func,
                                                ru.create_prop_control,
                                                useLoc=self._uiElement['useLoc'].getValue,
                                                sl=True))
                                        self.template.smallbutton(
                                            label='Free Control',
                                            c=Callback(
                                                self.do_func,
                                                ru.create_free_control,
                                                useLoc=self._uiElement['useLoc'].getValue,
                                                sl=True))

                                with self.template.subframe(label='Bone Chain Control'):
                                    with gridLayout():
                                        self.template.smallbutton(
                                            label='Parent Control',
                                            c=Callback(
                                                self.do_func,
                                                ru.create_parent_control,
                                                useLoc=self._uiElement['useLoc'].getValue,
                                                sl=True))
                                        self.template.smallbutton(
                                            label='Aim Setup',
                                            c=Callback(
                                                ru.aim_setup,
                                                sl=True))

                                with self.template.subframe(label='Dynamic Chain Control'):
                                    with rowColumnLayout(
                                            rs=[(1,0),],
                                            numberOfColumns=2,
                                            columnWidth=[(1, 180), (2, 50)]):
                                        hairSysName = '{}_hairSystem'.format(
                                            ns57.get_character_infos()[-1]) \
                                            if ns57.get_character_infos() else 'hairSytem1'
                                        self._uiElement['Hair System'] = textFieldGrp(
                                            cl2=('right', 'right'),
                                            co2=(5, 10),
                                            ct2=('right','left'),
                                            cw2=(70, 100),
                                            label='Hair System :', text=hairSysName)
                                        self.template.smallbutton(
                                            label='Get',
                                            h=20,
                                            c=Callback(self.get_hair_system))
                                    button(
                                        label='Create',
                                        c=Callback(
                                            self.do_func,
                                            ru.create_long_hair,
                                            hairSystem=self._uiElement['Hair System'].getText,
                                            sl=True))

                                with self.template.subframe(label='IK Chain Control'):
                                    with rowColumnLayout(
                                            rs=[(1,0.1),],
                                            numberOfColumns=2,
                                            columnWidth=[(1, 180), (2, 50)]):
                                        self._uiElement['SHctlcount'] = intFieldGrp(
                                            numberOfFields=1,
                                            cl2=('right', 'right'),
                                            co2=(5, 10),
                                            ct2=('right','left'),
                                            cw2=(70, 100),
                                            label='Controls :', value1=2)

                                    button(
                                        label='Create Spline IK',
                                        c=Callback(
                                            self.do_func,
                                            ru.create_splineIK,
                                            midCtls=self._uiElement['SHctlcount'].getValue1,
                                            sl=True))
                                    separator()
                                    button(
                                        label='Create Simple IK',
                                        c=Callback(
                                            self.do_func,
                                            ru.create_simpleIK,
                                            sl=True))
                                    separator()
                                    button(
                                        label='Create Stretch Bone')
                                    separator()
                        button(
                            label='Delete Created Nodes',
                            c=Callback(
                                self.delete_created_nodes))
                        with popupMenu(b=3):
                            menuItem(
                                label='Delete All Created Nodes',
                                c=Callback(
                                    self.delete_created_nodes,
                                    all=True))
                        button(
                            label='Controller Tagging',
                            c=Callback(
                                ControlMetaUI.show))
              #scriptedPanel(type="nodeEditorPanel", label="Node Editor")

    def create_intergration_ui(self):
        with frameLayout(label='Intergration:', cl=False):
            with columnLayout():
                button(
                    label='Basic Intergration',
                    c=Callback(ns57.basic_intergration))
                with frameLayout(label='Visbility Connect:', cl=False):
                    with gridLayout(cw=140):
                        self._uiElement['visAtrName'] = textFieldGrp(
                            cl2=('right', 'right'),
                            co2=(0, 0),
                            ct2=('right','left'),
                            cw2=(35, 30),
                            label='Vis Name:', text='FullRigVis')
                        self.template.smallbutton(
                            label='Connect Single', c=lambda x:ru.connect_visibility(
                                attrname= self._uiElement['visAtrName'].getText(), sl=True))
                        self._uiElement['visEnumAtrName'] = textFieldGrp(
                            cl2=('right', 'right'),
                            co2=(0, 0),
                            ct2=('right','left'),
                            cw2=(35, 30),
                            label='Vis Name:', text='FullRigVis')
                        self.template.smallbutton(
                            label='Connect Multi', c=lambda x:ru.connect_visibility_enum(
                                enumAttr= self._uiElement['visEnumAtrName'].getText(), sl=True))
                with frameLayout(label='Utils:', cl=False):
                    with gridLayout(cw=140):
                        self.template.smallbutton(
                            label='Create SkinDeform',
                            c=Callback(ns57.create_skinDeform, sl=True))
                        self.template.smallbutton(
                            label='Create RenderMesh',
                            c=Callback(ns57.create_renderMesh, sl=True)) 
                        self.template.smallbutton(
                            label='Channel History OFF',
                            c=Callback(ru.toggleChannelHistory, False))
                        with popupMenu(b=3):
                            menuItem(label='Channel History ON', c=Callback(ru.toggleChannelHistory))
                        self.template.smallbutton(label='Deform Normal Off', c=Callback(ru.deform_normal_off))

    def create_util_ui(self):
        with columnLayout():
            with frameLayout(label='Rigging:', cl=False):
                with columnLayout():
                    with gridLayout(cw=150):
                        self.template.smallbutton(
                            label='Create Parent',
                            c=Callback(
                                ru.create_parent,
                                sl=True))
                        self.template.smallbutton(
                            label='Celete Parent',
                            c=Callback(
                                ru.remove_parent,
                                sl=True))
                        self.template.smallbutton(
                            label='Create bone',
                            c=Callback(
                                ru.create_joint,
                                sl=True))
                        self.template.smallbutton(
                            label='Create Offset bone',
                            c=Callback(
                                ru.create_offset_bone,
                                sl=True))
                        self.template.smallbutton(
                            label='create Loc',
                            c=Callback(
                                ru.create_loc_control,
                                connect=False,sl=True))
                        self.template.smallbutton(
                            label='create Loc control',
                            c=Callback(
                                ru.create_loc_control,
                                all=True,
                                sl=True))
                        self.template.smallbutton(
                            label='connect with Loc',
                            c=Callback(
                                ru.connect_with_loc,
                                all=True,
                                sl=True))
                        with popupMenu(b=3):
                            menuItem(label='translate only', c=Callback(
                                ru.connect_with_loc,
                                translate=True,
                                sl=True))
                            menuItem(label='rotate only', c=Callback(
                                ru.connect_with_loc,
                                rotate=True,
                                sl=True))
                        self.template.smallbutton(
                            label='vertex to Loc',
                            c=Callback(
                                ru.create_loc_on_vert,
                                sl=True))
                        self.template.smallbutton(
                            label='Connect Transform',
                            c=Callback(
                                ru.connect_transform,
                                all=True,
                                sl=True))
                        with popupMenu(b=3):
                            menuItem(
                                label='Connect Translate',
                                c=Callback(
                                    ru.connect_transform,
                                    translate=True, rotate=False, scale=False,
                                    sl=True))
                            menuItem(
                                label='Connect Rotate',
                                c=Callback(
                                    ru.connect_transform,
                                    translate=False, rotate=True, scale=False,
                                    sl=True))
                            menuItem(
                                label='Connect Scale',
                                c=Callback(
                                    ru.connect_transform,
                                    translate=False, rotate=False, scale=True,
                                    sl=True))
                        self.template.smallbutton(
                            label='Disconnect Transform',
                            c=Callback(
                                ru.disconnect_transform,
                                sl=True))
                        with popupMenu(b=3):
                            menuItem(
                                label='Disconnect Translate',
                                c=Callback(
                                    ru.disconnect_transform,
                                    attr='translate',
                                    sl=True))
                            menuItem(
                                label='Disconnect Rotate',
                                c=Callback(
                                    ru.disconnect_transform,
                                    attr='rotate',
                                    sl=True))
                            menuItem(
                                label='Disconnect Scale',
                                c=Callback(
                                    ru.disconnect_transform,
                                    attr='scale',
                                    sl=True))
                        self._uiElement['PCAddAttr'] = False
                        self.template.smallbutton(
                            label='multi Parent Constraint',
                            c=lambda x: ru.constraint_multi(
                                constraintType='Parent',
                                addChildAttr=self._uiElement['PCAddAttr'],
                                sl=True))
                        with popupMenu(b=3):
                            menuItem(
                                label='multi Point Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='Point',
                                    sl=True))
                            menuItem(
                                label='multi Orient Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='Orient',
                                    sl=True))
                            menuItem(
                                label='multi Point&Orient Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='PointOrient',
                                    sl=True))
                            menuItem(
                                label='multi Aim Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='Aim',
                                    sl=True))
                            menuItem(
                                label='multi Loc Point Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='LocP',
                                    sl=True))
                            menuItem(
                                label='multi Loc Orient Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='LocO',
                                    sl=True))
                            menuItem(
                                label='multi Loc Point&Orient Constraint', c=Callback(
                                    ru.constraint_multi,
                                    constraintType='LocOP',
                                    sl=True))
                            menuItem(
                                label='Add ParentFollow Attributes',
                                checkBox= self._uiElement['PCAddAttr'],
                                c=Callback(
                                    self.setUIValue,
                                    'PCAddAttr',
                                    not self._uiElement['PCAddAttr']))
            with frameLayout(label='Modeling', cl=False):
                with gridLayout(cw=150):
                    self.template.smallbutton(label='Selected to Curve',
                        c=Callback(
                            ul.convert_to_curve,
                            sl=True))
                    self.template.smallbutton(
                        label='Parent Shape',
                        c=Callback(
                            ul.parent_shape,
                            sl=True))
                    with popupMenu(b=3):
                        menuItem(   
                            label='Unparent Shape',
                            c=Callback(
                                ul.un_parent_shape,
                                sl=True))
                        menuItem(
                            c=Callback(
                                ul.parent_shape,
                                delete_src=False,
                                sl=True),
                            label='Keep source shape'
                        )
                        menuItem(
                            c=Callback(
                                ul.parent_shape,
                                delete_oldShape=False,
                                sl=True),
                            label='Keep target shape'
                        )
                        menuItem(
                            c=Callback(
                                ul.parent_shape,
                                delete_oldShape=False,
                                delete_src=False,
                                sl=True),
                            label='Keep both shape'
                        )
                    self.template.smallbutton(
                        label='Rename Shape',
                        c=Callback(
                            ul.rename_shape))
                    self.template.smallbutton(
                        label='Lock Transform',
                        c=Callback(
                            ul.lock_transform,
                            sl=True))
                    with popupMenu(b=3):
                        menuItem(
                            label='Unlock Transform',
                            c=Callback(
                                ul.lock_transform,
                                lock=False,
                                sl=True))
                    self.template.smallbutton(
                        label='Reset Transform',
                        c=Callback(
                            ul.reset_transform,
                            sl=True))
                    self.template.smallbutton(
                        label='Mirror Transform',
                        c=Callback(
                            ul.mirror_transform,
                            sl=True))
                    self.template.smallbutton(
                        label='Add Vray OpenSubdiv',
                        c=Callback(
                            ul.add_vray_opensubdiv,
                            sl=True))
                    self.template.smallbutton(
                        label='Clean Extra Attributes',
                        c=Callback(
                            ul.clean_attributes,
                            sl=True))

    def _init_ui(self):
        with self.window:
            with self.template.get():
                with menuBarLayout(bgc=[0.2,0.2,0.2]):
                    with menu(label='Option'):
                        menuItem( label='Reset' )
                self.tabLayout = tabLayout(
                    innerMarginWidth=5, innerMarginHeight=5)         
                with self.tabLayout:
                    self.create_rig_util_ui()
                    self.create_util_ui()
                    self.create_intergration_ui()
                with columnLayout():
                    helpLine()
        self.tabLayout.setTabLabelIndex((1,'Rig Tools'))
        self.tabLayout.setTabLabelIndex((2,'Utilities'))
        self.tabLayout.setTabLabelIndex((3,'Intergration'))
        self.nodetrack.startTrack()
        #self.ui_update()

    @classmethod
    def show(cls):
        cls()._init_ui()

class ControlMetaUI:
    def __init__(self):
        self._name = 'ControlMetaUI'
        self._title = 'Controller Meta Manager'
        self.template = UITemplate(self._name)
    
    @property
    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(
            self._name,
            title=self._title,
            rtf=True,
            width=10, height=10)
        return self._window

    def _initUI(self):
        with self.window:
            with self.template.get():
                with frameLayout(label='Control Tag:',cl=False):
                    with columnLayout():
                        with gridLayout(cw=130):
                            self.template.smallbutton(
                                label='Tag as controller',
                                c=Callback(
                                    ru.control_tagging,
                                    sl=True))
                            self.template.smallbutton(
                                label='Remove tag',
                                c=Callback(
                                    ru.control_tagging,
                                    remove=True,
                                    sl=True))
                            self.template.smallbutton(
                                label='Select all controllers',
                                c=Callback(
                                    ru.remove_all_control_tags,
                                    select=True))
                            with popupMenu(b=3):
                                menuItem(
                                    label='Select controller meta',
                                    c=Callback(
                                        ru.select_controller_metanode))
                            self.template.smallbutton(
                                label='Remove all tag',
                                c=Callback(
                                    ru.remove_all_control_tags))
                        button(
                                label='Reset all controllers transform',
                                c=Callback(
                                    ru.reset_controller_transform))

    @classmethod
    def show(cls):
        cls()._initUI()

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
                        button(
                            label="Create Send Folder",
                            c=lambda x: ns57.create_send_folder(
                                self.elements['version'].getValue()))
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
    '''Tools to set skin weight and transfer skinCluster
    '''
    def __init__(self):
        self._name = 'SkinWeightSetterUI'
        self._title = 'Skin Weight Setter'
        self.template = UITemplate(self._name)
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
        self.ui = {}

    @property
    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(
            self._name,
            title=self._title,
            rtf=True,
            width=10, height=10)
        return self._window

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

    def autoUpdateUI(self):
        jobNum = scriptJob( e= ["SelectionChanged",self.update_ui], parent = 'SkinWeightSetterUI')

    def update_ui(self):
        sel = selected()
        msg = [i.name().split('|')[-1] for i in sel if hasattr(i,'name')]
        self.ui['messageLine'].setLabel(','.join(msg))
        componentList = [c for c in sel if c.nodeType()=='mesh']
        if componentList:
            self.ui['dualInfo'].setLabel(','.join(['%s: %s'%(i[0],str(i[1])) for i in ru.dual_weight_setter(componentList, query=True)]))
        try:
            skinClster = ul.get_skin_cluster(sel[0])
            if skinClster:
                skinTypeVal =  skinClster.getSkinMethod()+1
                self.ui['skinType'].setSelect(skinTypeVal)
        except:
            pass
        if not sel:
            self.ui['messageLine'].setLabel('')

    def set_weight_threshold(self, *args):
        self.weight_threshold = (args[0], args[1])

    def set_skin_type(*args):
        ru.switch_skin_type(type=args[1], sl=True)
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
        ru.skin_weight_filter(
            min=self.weight_threshold[0],
            max=self.weight_threshold[1],
            select=True,
            sl=True)

    @showsHourglass
    def apply_weight(self):
        #if currentCtx() == 'artAttrSkinContext':
        #    mm.eval('artAttrSkinPaintModePaintSelect 0 artAttrSkinPaintCtx')
        #if not selected():
        #    select(self.last_selected, r=True)
        ru.skin_weight_setter(
            skin_value=self.weight_value,
            normalized=self.normalize,
            hierachy=self.hierachy,
            sl=True)
        # self.last_selection()
        self.preview_skin_weight()
        headsUpMessage("Weight Set!", time=0.2)

    @showsHourglass
    def apply_dual_weight(self):
        ru.dual_weight_setter(
            weight_value=self.dual_weight_value,
            sl=True)
        # self.last_selection()
        headsUpMessage("Dual Quarternion Weight Set!", time=0.2)

    def init_ui(self):
        with self.window:
            with self.template.get():
                with frameLayout(
                        label='Set Weight Tool',cl=False):
                    with columnLayout(adjustableColumn=1):
                        self.ui['skinType'] = optionMenu(
                            label='Skin Type:',
                            changeCommand=self.set_skin_type)
                        with self.ui['skinType']:
                            menuItem(label='Classis')
                            menuItem(label='Dual')
                            menuItem(label='Blend')
                        separator(height=10)

                        with rowColumnLayout(
                            numberOfColumns=2,
                            columnWidth=[(1, 320), (2, 120)]):
                            self.skin_weight_theshold = floatFieldGrp(
                                numberOfFields=2,
                                label='Weight Threshold:',
                                value1=self.weight_threshold[0], value2=self.weight_threshold[1],
                                cc=self.set_weight_threshold)
                            button(
                                label='Select Vertices',
                                annotation='Select Skin Vertex with weight within threshold',
                                c=Callback(self.select_skin_vertex))
                        separator(height=10)
                        with rowColumnLayout(
                            numberOfColumns=3,
                            columnWidth=[(1, 140), (2, 80)]):
                            text(label='Option: ', align='right')
                            checkBox(
                                label='Normalize',
                                annotation='if Normalize is uncheck, set all selected joint weight the same',
                                value=self.normalize,
                                cc=self.set_normalize_state)
                            checkBox(
                                label='Hierachy',
                                annotation='if Hierachy is check, set weight value for child Joint',
                                value=self.hierachy,
                                cc=self.set_hierachy_state)
                        self.skin_weight_slider_ui = floatSliderButtonGrp(
                            label='Skin Weight: ',
                            annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
                            field=True, precision=2,
                            value=self.weight_value,
                            minValue=0.0, maxValue=1.0,
                            cc=self.set_weight,
                            buttonLabel='Set',
                            bc=Callback(self.apply_weight),
                            image='playbackLoopingContinuous.png',
                            sbc=self.set_interactive_state)
                        separator(height=5, style='none')
                        with gridLayout(
                            numberOfColumns=self.weight_tick,
                            cellWidthHeight=(95, 30)):
                            weight_value = 1.0 / (self.weight_tick - 1)
                            for i in range(self.weight_tick):
                                button(
                                    label=str(weight_value * i),
                                    annotation='Set skin weight to %04.2f' % (
                                        weight_value * i),
                                    c=Callback(
                                        self.set_weight, weight_value * i))
                        separator(height=10)

                        self.dual_weight_slider_ui = floatSliderButtonGrp(
                            label='Dual Quarternion Weight: ',
                            annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
                            field=True, precision=2,
                            value=self.dual_weight_value,
                            minValue=0.0, maxValue=1.0,
                            cc=self.set_dual_weight,
                            buttonLabel='Set',
                            bc=Callback(self.apply_dual_weight),
                            image='playbackLoopingContinuous.png',
                            sbc=self.set_dual_interactive_state)
                        separator(height=5, style='none')

                        with gridLayout(
                            numberOfColumns=self.weight_tick,
                            cellWidthHeight=(95, 30)):
                            for i in range(self.weight_tick):
                                button(
                                    label=str(weight_value * i),
                                    annotation='Set dual quaternion weight to %04.2f' % (weight_value * i),
                                    c=Callback(
                                        self.set_dual_weight, weight_value * i))
                            self.ui['dualInfo']=text(label='',align='left')
                        #separator(height=5, style='none')

                with frameLayout(label='Utils', cl=False):
                        with gridLayout(
                                numberOfColumns=5,
                                cellWidth=140):
                            button(
                                label='add Influence',
                                annotation='add influence to skin mesh',
                                c=Callback(
                                    ru.add_joint_influence,
                                    sl=True))
                            button(
                                label='Freeze Skin Joint',
                                annotation='Freeze transform for joint connect to Skin Cluster',
                                c=Callback(
                                    ru.freeze_skin_joint,
                                    sl=True))
                            button(
                                label = 'Freeze Skin Joint Chain',
                                annotation='Freeze transform for joint Chain connect to Skin Cluster',
                                c = Callback(
                                    ru.freeze_skin_joint,
                                    hi=True,
                                    sl=True))
                            button(
                                label = 'Transfer Weight',
                                annotation='*Select 2 bone*. Transfer skin weight from one bone to another',
                                c=Callback(
                                    ru.move_skin_weight,
                                    sl=True))
                            button(
                                label = 'Transfer Weight Chain',
                                annotation='*Select 2 bone root*. Transfer skin weight from one bone Chain to another',
                                c = Callback(
                                        ru.move_skin_weight,
                                        hi=True,
                                        sl=True))
                            button(
                                label = 'Reset BindPose',
                                annotation='Reset skin bind pose',
                                c = Callback(
                                    ru.reset_bindPose_all))
                        separator(height=10, style='none')

                with frameLayout(label='Status', collapsable=False):
                    with columnLayout(adjustableColumn=1):
                        with rowColumnLayout(
                            numberOfColumns=2,
                            columnWidth=[(1,100), (2, 300)]):
                            text(label='Current Selection:',align='left')
                            self.ui['messageLine'] = text(
                                label='',
                                align='left')
                        separator(height=10, style='none')
                        self.ui['helpLine'] = helpLine(
                            annotation='copyright 2017 by Nguyen Phi Hung')

        self.autoUpdateUI()

    @classmethod
    def show(cls):
        cls().init_ui()

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
