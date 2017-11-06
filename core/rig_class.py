#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
import os
import pymel.core as pm
import general_utils as ul
import rigging_utils as ru
import string
import math
from pymel.util.enum import Enum
from PipelineTools.packages.Red9.core import Red9_Meta as meta

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#reload(ul)
#print meta
log.info('Rig Class Initilize')
class HairRigMeta(meta.MetaRig):
    pass

class SecondaryRigMeta(meta.MetaRig):
    pass
class CHRig(object):
    def __init__(self, name='', hikName='CH'):
        self.node = meta.MetaHIKCharacterNode(hikName)
        self.node.setascurrentcharacter()
        self.node.select()
        self.hikProperty = self.node.getHIKPropertyStateNode()
        self.hikControl = self.node.getHIKControlSetNode()
        # self.character.lockState = False
        # pm.lockNode(hikName,lock=False)
        self.node.addAttr('CharacterName', name)
        self.node.addAttr('BuildBy','{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')))
        self.node.addAttr('Branch',os.environ.get('USERDOMAIN'))
        self.node.addAttr('BuildDate',pm.date())
        self.node.addAttr('FacialRig', attrType='messageSimple')
        self.node.addAttr('HairRig', attrType='messageSimple')
        self.node.addAttr('SecondaryRig', attrType='messageSimple')

class FacialRigMeta(meta.MetaRig):
    '''
    Facial Rig MetaNode
    to get this node use pt.rc.meta.getMetaNodes(mClass='FacialRigMeta')
    '''
    def __init__(self,*args,**kws):
        super(FacialRigMeta, self).__init__(*args, **kws) 
        self.lockState = False
        self.mSystemRoot = False
        
    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType','FacialRig', l=True)
        self.addAttr('CharacterName','')
        self.addAttr('BuildBy','{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')), l=True)
        self.addAttr('Branch',os.environ.get('USERDOMAIN'), l=True)
        self.addAttr('BuildDate',pm.date(), l=True)
        ###### Model information Attributes
        self.addAttr('FaceGp', attrType='messageSimple')
        self.addAttr('EyeGp', attrType='messageSimple')
        self.addAttr('FaceRigGp', attrType='messageSimple')
        self.addAttr('FaceDeformGp', attrType='message')
        self.addAttr('FacialTargetPath', "")
        ###### Bone Information Attributes
        self.addAttr('HeadBone', attrType='messageSimple')
        self.addAttr('FacialBone', attrType='messageSimple')
        self.addAttr('EyeBone', attrType='messageSimple')
        ###### Control Hook
        # self.addAttr('BlendshapeCtl', attrType='messageSimple')
        # self.addAttr('FacialCtl', attrType='message')
        # self.addAttr('EyeCtl', attrType='messageSimple')
        # self.addAttr('TongueCtl', attrType='messageSimple')
        # self.addAttr('JawCtl', attrType='messageSimple')

    def connectToPrimary():
        pass

    def getBlendShapeSystem(self):
        BS = self.addSupportMetaNode('BlendshapeCtl', nodeName='facial_panel')
        BS.connectChild('facial_panel','BSPanel')
        BS.connectChild('brow_ctl','BrowBSControl')
        BS.connectChild('eye_ctl','EyeBSControl')
        BS.connectChild('mouth_ctl','EyeBSControl')

    def getProperty(self):
        #### connect FaceRigGp to facialGp
        if pm.objExists('facialGp'):
            self.FaceRigGp = 'facialGp'
        #### connect facialGroup
        facialGps = []
        for gp in ['facial','facialGuide','jawDeform','eyeDeform','orig']:
            if pm.objExists(gp):
                facialGps.append(gp)
        self.FaceDeformGp = facialGps
        #### get facialTarget External
        scenedir = pm.sceneName().dirname()
        dir = scenedir.parent
        bsdir = pm.util.common.path(dir+'/facialtarget/facialtarget.mb')
        if bsdir.isfile():
            self.FacialTargetPath = bsdir.replace(pm.workspace.path+'/', '')

    def build(self):
        pass

class SecondaryRigMeta(meta.MetaRig):
    '''
    Secondary Rig MetaNode
    to get this node use pt.rc.meta.getMetaNodes(mClass='SecondaryRigMeta')
    '''
    def __init__(self,*args,**kws):
        super(SecondaryRigMeta, self).__init__(*args, **kws) 
        self.lockState = False
        self.mSystemRoot = False
        
    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType','SecondaryRig', l=True)
        self.addAttr('CharacterName','')
        self.addAttr('BuildBy','{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')), l=True)
        self.addAttr('Branch',os.environ.get('USERDOMAIN'), l=True)
        self.addAttr('BuildDate',pm.date(), l=True)
        ###### Model information Attributes
        self.addAttr('secSkinDeformGp', attrType='messageSimple')
        ###### Bone Information Attributes
        self.addAttr('HairControlSet', attrType='messageSimple')
        self.addAttr('ClothControlSet', attrType='messageSimple')
        ###### Control Hook
        self.addAttr('ctlGp', attrType='messageSimple')
        self.addAttr('bonGp', attrType='message')
        self.addAttr('miscGp', attrType='messageSimple')
        # self.addAttr('TongueCtl', attrType='messageSimple')
        # self.addAttr('JawCtl', attrType='messageSimple')

    def connectToPrimary():
        pass

    def getProperty(self):
        #### connect FaceRigGp to facialGp
        if pm.ls('_secSkinDeform'):
            self.secSkinDeformGp = pm.ls('_secSkinDeform')[0]
        if pm.objExists('miscGp'):
            self.miscGp = ul.get_node('miscGp')
            self.bonGp = ul.get_node('bonGp')
            self.ctlGp = ul.get_node('ctlGp')

    def build(self):
        pass

class HairRigMeta(meta.MetaRig):
    '''
    Secondary Rig MetaNode
    to get this node use pt.rc.meta.getMetaNodes(mClass='SecondaryRigMeta')
    '''
    def __init__(self,*args,**kws):
        super(HairRigMeta, self).__init__(*args, **kws) 
        self.lockState = False
        self.mSystemRoot = False
        
    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType','HairRigMeta', l=True)

    def connectToPrimary():
        pass

    def getProperty(self):
        pass

    def build(self):
        pass

class ClothRigMeta(meta.MetaRig):
    '''
    Secondary Rig MetaNode
    to get this node use meta.getMetaNodes(mClass='SecondaryRigMeta')
    '''
    def __init__(self,*args,**kws):
        #if meta.getMetaNodes(mClass='ClothRigMeta'):
        #    super(ClothRigMeta, self).__init__(meta.getMetaNodes(mClass='ClothRigMeta')) 
        #else:
        super(ClothRigMeta, self).__init__(*args, **kws) 
        self.lockState = False
        self.mSystemRoot = False
        self.controlOb = ControlObject('control')
    @property
    def controlObject(self,*args,**kwargs):
        return self.controlOb
    @controlObject.setter
    def controlObject(self,*args,**kwargs):
        self.controlOb = ControlObject(*args,**kwargs)

    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType','ClothRigMeta', l=True)

    def connectToPrimary():
        pass

    def getProperty(self):
        pass

    def build(self):
        pass

class FacialGuide(object):
    def __init__(self, name, guide_mesh=None, suffix='loc', root_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._root_suffix = root_suffix
        self.name = '_'.join([name, suffix])
        self.root_name = '_'.join([self.name, root_suffix])
        self.constraint_name = '_'.join([self.root_name,'pointOnPolyConstraint1'])
        self.guide_mesh = guide_mesh
        self._get()

    def __repr__(self):
        return self.name

    def __call__(self,*args, **kwargs):
        self.create(*args, **kwargs)
        return self.node
    
    def set_guide_mesh(self, guide_mesh):
        if pm.objExists(guide_mesh):
            guide_mesh = ul.get_node(guide_mesh)
            self.guide_mesh = ul.get_shape(guide_mesh)
        else:
            'object {} does not contain shape'.format(guide_mesh)

    def create(self, pos=[0, 0, 0], parent=None):
        self.node = pm.spaceLocator(name=self.name)
        if pm.objExists(self.root_name):
            self.root = pm.PyNode(self.root_name)
        else:
            self.root = pm.nt.Transform(name=self.root_name)
        self.node.setParent(self.root)
        self.root.setTranslation(pos, space='world')
        self.root.setParent(parent)

    def set_constraint(self, target = None):
        if all([self.guide_mesh, self.guide_mesh, self.root]):
            pm.delete(self.constraint)
            if target is None:
                target = self.root
            closest_uv = ul.get_closest_component(target, self.guide_mesh)
            self.constraint = pm.pointOnPolyConstraint(
                self.guide_mesh, self.root, mo=False,
                name=self.constraint_name)
            self.constraint.attr(self.guide_mesh.getParent().name()+'U0').set(closest_uv[0])
            self.constraint.attr(self.guide_mesh.getParent().name()+'V0').set(closest_uv[1])
            #pm.select(closest_info['Closest Vertex'])
        else:
            pm.error('Please set guide mesh')

    def _get(self):
        self.node = ul.get_node(self.name)
        self.root = ul.get_node(self.root_name)
        self.constraint = ul.get_node(self.constraint_name)
        return self.node

    @classmethod
    def guides(cls, name='eye',root_suffix='Gp', suffix='loc', separator='_'):
        list_all = pm.ls('*%s*%s*'%(name,suffix), type='transform')
        guides = []
        for ob in list_all:
            if root_suffix not in ob.name():
                ob_name = ob.name().split(separator)
                guide =  cls(ob_name[0], suffix=suffix, root_suffix=root_suffix)
                guides.append(guide)
        return guides

class FacialControl(object):
    def __init__(self, name, suffix='ctl', offset_suffix='offset', root_suffix='Gp'):
        self._suffix = suffix
        self._offset_suffix = offset_suffix
        self._root_suffix = root_suffix
        self.rename(name)
        self.attr_connect_list = ['translate', 'rotate', 'scale']
        self._get()
    
    def __repr__(self):
        return self.name

    def __call__(self, *args, **kwargs):
        self.create(*args, **kwargs)
        return self

    def name(self):
        return self.name

    def rename(self,new_name):
        self._name = new_name
        self.name = '_'.join([self._name, self._suffix])
        self.offset_name = '_'.join([self._name, self._offset_suffix])
        self.root_name = '_'.join([self._name, self._root_suffix])
        try:
            if self.node:
                pm.rename(self.node, self.name)
                print self.node
            if self.offset:
                pm.rename(self.offset, self.offset_name)
                print self.offset
            if self.root:
                pm.rename(self.root, self.root_name)
                print self.root
        except:
            pass

    def create(self, shape=None, pos=[0,0,0], parent=None, create_offset=True):
        if not self.node:
            if shape:
                self.node = pm.nt.Transform(name=self.name)
                shape = ul.get_node(shape)
                ul.parent_shape(shape, self.node)
            else:
                self.node = pm.sphere(ax=(0,1,0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False, n=self.name)[0]
        self.node.setTranslation(pos,'world')
        self.WorldPosition = self.node.getTranslation('world')
        self.shape = ul.get_shape(self.node)
        for atr in ['castsShadows','receiveShadows','holdOut','motionBlur','primaryVisibility','smoothShading','visibleInReflections','visibleInRefractions','doubleSided']:
            self.shape.attr(atr).set(0)
        if not self.offset and create_offset:
            self.offset = pm.nt.Transform(name=self.offset_name)
            self.offset.setTranslation(self.WorldPosition, space='world')
            self.node.setParent(self.offset)
        if not self.root:
            self.root = pm.nt.Transform(name=self.root_name)
            self.root.setTranslation(self.WorldPosition, space='world')
            if self.offset:
                self.offset.setParent(self.root)
            else:
                self.node.setParent(self.root)
            self.root.setParent(parent)
        return self.node

    def delete(self):
        pass

    def create_guide(self, *args, **kwargs):
        self.guide = FacialGuide(self._name, *args, **kwargs)
        return self.guide

    def set_constraint(self):
        if self.guide and self.root:
            self.constraint = pm.pointConstraint(self.guide, self.root, o=(0,0,0), w=1)

    def set(self, new_node, rename=True):
        if pm.objExists(new_node):
            self.node = pm.PyNode(new_node)
            if rename:
                pm.rename(new_node, self.name)
            self._get()

    def get_output(self):
        results = {}
        for atr in self.attr_connect_list:
            results[atr] = self.node.attr(atr).outputs()
        return results

    def _get(self):
        self.node = ul.get_node(self.name)
        self.offset = ul.get_node(self.offset_name)
        self.root = ul.get_node(self.root_name)
        self.guide = self.create_guide()
    
    @classmethod
    def controls(cls, name,offset_suffix='offset', root_suffix='Gp', suffix='ctl', separator='_'):
        list_all = pm.ls('*%s*%s*'%(name,suffix), type='transform')
        controls = []
        for ob in list_all:
            if root_suffix not in ob.name():
                ob_name = ob.name().split(separator)
                control =  cls(ob_name[0], offset_suffix=offset_suffix, suffix=suffix, root_suffix=root_suffix)
                controls.append(control)
        return controls

class FacialBone(object):
    def __init__(self, name, suffix='bon', offset_suffix='offset', ctl_suffix='ctl', root_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._offset_suffix = offset_suffix
        self._ctl_suffix = ctl_suffix
        self.name = '_'.join([self._name, suffix])
        self.offset_name = '_'.join([self._name, self._offset_suffix, self._suffix])
        self.connect_attrs = [
            'translate',
            'rotate',
            'scale']
        self.control_name = self.name.replace(suffix, ctl_suffix)
        self._get()

    def __repr__(self):
        return self.name

    def __call__(self,new_bone=None, pos=[0,0,0], parent=None, create_control=False):
        if pm.objExists(newBone):
            newBone = pm.PyNode(new_bone)
            pm.rename(newBone, self.name)
            self._set(newBone, pos=pos, parent=parent)
        else:
            if self._get():
                self._set(self.bone)
            else:
                newBone = pm.nt.Joint()
                newBone.setTranslation(pos, space='world')
                newBone.setParent(parent)
                self.__call__(newBone=newBone)
        if create_control:
            self.create_control()
        return self.bone

    def create_offset(self, pos=[0,0,0], space='world', reset_pos=False, parent=None):
        boneParent = self.bone.getParent()
        if boneParent and self._offset_suffix in boneParent.name():
            self.offset_bone = boneParent
        elif pm.objExists(self.offset_name):
            self.offset_bone = pm.PyNode(self.offset_name)
            self.offset_bone.setParent(boneParent)
            self.bone.setParent(self.offset_bone)
            reset_transform(self.bone)
        else:
            self.offset_bone = pm.nt.Joint(name=self.offset_name)
            self.bone.setParent(self.offset_bone)
            if reset_pos:
                reset_transform(self.bone)
            self.offset_bone.setTranslation(pos, space=space)
            if parent:
                self.offset_bone.setParent(parent)
            else:
                self.offset_bone.setParent(parent)
        return self.offset_bone

    def create_control(self, shape=None, parent=None):
        self.get_control()
        self.control.create()

    def is_connected(self):
        if self.control:
            connect_state = []
            for atr in self.connect_attrs:
                input = self.bone.attr(atr).inputs()
                if input:
                    if input[0] == self.control:
                        connect = True
                    else:
                        connect = False
                    print '%s connection to %s is %s'%(atr, self.control_name, connect)
                    connect_state.append((atr, connect))
        return connect_state

    def connect(self):
        if self.bone and self.control.node:
            if self.offset:
                pm.matchTransform(self.offset,self.bone,pivots=True)    
            pm.matchTransform(self.control.node,self.bone,pivots=True)
            self.control.node.translate >> self.bone.translate
        else:
            'object {} or {} is not exists'.format(self.bone, self.control.node)

    def set_control(self, control_ob, rename=True):
        if pm.objExists(control_ob):
            self.control = pm.PyNode(control_ob)
            if rename:
                pm.rename(self.control, self.control_name)
        else:
            self.create_control()
        self.connect()
        self.is_connected()
        return self.control

    def get_control(self, other_name=None):
        control_name = self._name
        if other_name and any([isinstance(other_name,t) for t in [str,unicode]]):
            control_name = other_name
        self.control = FacialControl(control_name)
        return self.control

    def _get(self):
        self.bone = ul.get_node(self.name)
        #if self.bone:
        #    self._set(self.bone)
        self.offset = ul.get_node(self.offset_name)
        self.get_control()
        return self.bone

    def _set(self, bone):
        self.bone = bone
        self.create_offset(
            pos=self.bone.getTranslation(space='world'),
            reset_pos=True)

    @classmethod
    def bones(
        cls,
        names = ['eye','cheek','nose','lip'],
        offset_suffix='offset', root_suffix='Gp',
        suffix='bon', separator='_',
        directions=['Left','Right','Center','Root']):
        '''get all Bone'''
        # class facialbones(Enum):
        for name in names:
            list_all = pm.ls('*%s*%s*'%(name,suffix), type='transform')
            # print list_all
            allbone = []
            for ob in list_all:
                if root_suffix not in ob.name() and offset_suffix not in ob.name():
                    ob_name = ob.name().split(separator)
                    bone =  cls(ob_name[0], offset_suffix=offset_suffix, suffix=suffix, root_suffix=root_suffix)
                    allbone.append(bone)
            bones = {}
            bones['All'] = allbone
            for direction in directions:
                bones[direction] = []
                for bone in allbone:
                    if direction in bone.name:
                        bones[direction].append(bone)
            yield bones
class FacialEyeRig(object):
    pass

class FacialRig(object):
    pass

class FacialBsRig(object):
    def __init__(self):
        self.facebs_name = 'FaceBaseBS'
        self.control_name = "ctl"
        self.joint_name = 'bon'
        self.bs_names = ['eyebrow', 'eye', 'mouth']
        self.ctl_names = ['brow', 'eye', 'mouth']
        self.direction_name = ['Left', 'Right']
    
    def facectl(self,value=None):
        if value is not None:
            if isinstance(value,list):
                self.ctl_names = value
        self.ctl_fullname = ['_'.joint([ctl_name,'ctl']) for ctl_name in ctl_names]
        self.ctl = []
        def create_bs_ctl():
            pass
        try:
            for ctl_name in self.ctl_fullname:
                ctl = PyNode(ctl)
                self.ctl.append(ctl)
        except:
            create_bs_ctl(ctl)
    def facebs(self,value=None):
        if value is not None:
            self.facebs_name = value
        self.facebs = ul.get_blendshape_target(self.facebs_name)
        if self.facebs:
            self.facebs_def ={}
            self.facebs_def['misc'] = []
            for bs in self.facebs[0]:
                for bs_name in bs_def:
                    for direction in direction_name:
                        if bs.startswith(bs_name):
                            if not self.facebs_def.has_key(bs_name):
                                self.facebs_def[bs_name] ={}
                            if bs.endswith(direction[0]):
                                if not self.facebs_def[bs_name].has_key(direction): 
                                    self.facebs_def[bs_name][direction] = []
                                self.facebs_def[bs_name][direction].append(bs)
                            else:
                                self.facebs_def[bs_name] = []
                                self.facebs_def[bs_name].append(bs)
            else:
                self.facebs_def['misc'].append(bs)
        else:
            print "no blendShape with name" % self.facebs_name
        return self.facebs_def

    def connect_bs_controller(self):
        facepart = self.facebs()
        bs_control_name = ["_".join([n, self.control_name])
                           for n in facepart[:3]]
        def create_bs_list(part, bs_name_list, add_dir=False):
            bs_list = [
                '_'.join([part, bs])
                for bs in bs_name_list]
            if add_dir is True:
                bs_list = self.add_direction(bs_list)
            return bs_list
        bs_controller = {}
        eyebrow = facepart[0].replace(facepart[1],'')
        bs_controller[
            '_'.join([eyebrow,self.control_name])
            ] = create_bs_list(
            facepart[0],
            self.eyebs_name[:3],
            True)
        bs_controller[
            '_'.join([facepart[1],self.control_name])
            ] = create_bs_list(
            facepart[1],
            self.eyebs_name[1:],
            True)
        bs_controller[
            '_'.join([facepart[2],self.control_name])
            ] = create_bs_list(
            facepart[2],
            self.mouthbs_name,
        )
        for ctl_name,bs_targets in bs_controller.items():
            for bs_target in bs_targets:
                print '%s.%s >> %s.%s' %(ctl_name,bs_target,self.facebs_name,bs_target)
        #print bs_controller

class ControlObject(object):
    '''Class to create Control'''
    def __init__(
            self,
            name,
            suffix='ctl',
            radius=1 ,
            res='high',
            length=2.0,
            axis='XY',
            offset= 0.0,
            color='red'):
        self._suffix = suffix
        self.name = '{}_{}'.format(name,suffix)
        self.radius = radius
        self.length = length
        self._resolutions = {
            'low':4,
            'mid':8,
            'high':24
        }
        self.axis = axis
        self._colorData = {
            'white':pm.dt.Color.white,
            'red':pm.dt.Color.red,
            'green':pm.dt.Color.green,
            'blue':pm.dt.Color.blue,
            'yellow':[1,1,0,0],
            'cyan':[0,1,1,0],
            'violet':[1,0,1,0],
            'orange':[1,0.5,0,0],
            'pink':[1,0,0.5,0],
            'jade':[0,1,0.5,0]
        }
        self.offset = offset
        self.step = res
        self.color = color
        self.controls = {}
        self.controls['all'] = []
        self.controlGps = []
        log.info('Control Object class name:{} initialize'.format(name))
        log.debug('\n'.join(['{}:{}'.format(key,value) for key,value in self.__dict__.items()]))
    ####Define Property
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, newoffset):
        assert any([isinstance(newoffset,typ) for typ in [float,int]]), "Offset must be of type float"
        self._offset = newoffset
    @property
    def color(self):
        return pm.dt.Color(self._color)
    @color.setter
    def color(self, newcolor):
        if isinstance(newcolor,str):
            assert (self._colorData.has_key(newcolor)), "color data don't have '%s' color.\nAvailable color:%s"%(newcolor,','.join(self._colorData))
            self._color = self._colorData[newcolor]
        if any([isinstance(newcolor,typ) for typ in [list,set,tuple]]):
            assert (len(newcolor)>3), 'color must be a float4 of type list,set or tuple'
            self._color = pm.dt.Color(newcolor)
    @property
    def step(self):
        return self._step
    @step.setter
    def step(self, newres):
        assert (self._resolutions.has_key(newres)), "step resolution value not valid.\nValid Value:%s"%self._resolutions
        self._step = self._resolutions[newres]
    #@property
    #def res(self):
    
    #decorator
    def __dotoAllControl__(func):
        ''''''
        @ul.wraps(func)
        def wrapper(self,*args, **kws):
            result=func(*args, **kws)
            return result
        return wrapper
    def __setProperty__(func):
        '''Wraper that make keywords argument of control type function
        to tweak class Attribute'''
        @ul.wraps(func)
        def wrapper(self,*args, **kws):
            #### store Class Attribute Value
            oldValue = {}
            oldValue['offset'] = self.offset
            oldValue['res'] = self.step
            oldValue['color'] = self.color
            fkws = func.__defaults__[0]
            #### Assign Keyword Argument value to Class Property value 
            log.debug('Assign KeyWord to ControlObject Class Propety')
            if kws.has_key('offset'):
                self.offset = kws['offset']
                log.debug('{} set to {}'.format('offset',kws['offset']))
            if kws.has_key('res'):
                self.step = kws['res']
                log.debug('{} set to {}'.format('res',kws['res']))
            if kws.has_key('color'):
                self.color = kws['color']
                log.debug('{} set to {}'.format('color',kws['color']))
            
            for key, value in kws.items():
                if self.__dict__.has_key(key):
                    oldValue[key] = self.__dict__[key]
                    self.__dict__[key] = value
                    log.debug('{} set to {}'.format(key,value))
                if fkws.has_key(key):
                    fkws[key] = value

            if kws.has_key('group'):
                groupControl = kws['group']
            elif kws.has_key('grp'):
                groupControl = kws['grp']
            else:
                groupControl = True
            if kws.has_key('prefixControlName'):
                prefixName = kws['prefixControlName']
            elif kws.has_key('pre'):
                prefixName = kws['pre']
            else:
                prefixName = False

            #### Create and Modify Control object
            control = func(self,mode=fkws)
            if prefixName is True:
                control.rename('_'.join([func.__name__,self.name]))
            self.controls['all'].append(control)
            if not self.controls.has_key(func.__name__):
                self.controls[func.__name__] = []
            self.controls[func.__name__].append(control)
            self.setColor(control=control)
            log.info('Control of type:{} name {} created along {}'.format(func.__name__, control.name(), self.axis))
            if groupControl is True:
                Gp = self.group(control)
                self.controlGps.append(Gp)

            #### reset Class Attribute Value to __init__ value
            for key,value in oldValue.items():
                self.__dict__[key] = value
                if key == 'offset':
                    self._offset = value
                if key == 'res':
                    self._step = value
                if key == 'color':
                    self._color = value
            return control
        return wrapper

    #### static function
    @staticmethod
    def createPinCircle(
            name,
            createCurve=True,
            axis='XY',
            sphere=False,
            cylinder=False,
            offset=[0,0,0],
            radius=1.0,
            length=3.0,
            height=2,
            step=20.0,
            maxAngle=360.0):
        '''Master function to create all curve control'''
        log.debug('''create Control with value:\n
            name: {}\n
            create Curve: {}\n
            axis: {}\n
            sphere: {}\n
            offset: {}\n
            radius: {}\n
            length: {}\n
            step: {}\n
            max Angle: {}'''.format(name,createCurve,axis,sphere,offset,radius,length,step,maxAngle))
        maxAngle = maxAngle/180.0*math.pi
        inc = maxAngle/step
        pointMatrix=[]
        theta = 0
        if length>0:
            pointMatrix.append([0,0])
            pointMatrix.append([0,length])
            offset = [offset[0],-radius-length-offset[1],offset[2]]
        #print offset
        while theta<=maxAngle:
            if length>0:
                x = (-offset[0] + radius*math.sin(theta))
                y = (offset[1] + radius*math.cos(theta))*-1.0
            else:
                x = (offset[0] + radius*math.cos(theta))
                y = (offset[1] + radius*math.sin(theta))
            pointMatrix.append([x,y])
            #print "theta angle {} produce [{},{}]".format(round(theta,2),round(x,4),round(y,4))
            theta+=inc
        if not createCurve:
            return pointMatrix
        axisData = {}
        axisData['XY'] = [[x,y,offset[2]] for x,y in pointMatrix]
        axisData['rXY'] = [[y,x,offset[2]] for x,y in pointMatrix]
        axisData['-XY'] = [[-x,-y,offset[2]] for x,y in pointMatrix]
        axisData['-rXY'] = [[-y,-x,offset[2]] for x,y in pointMatrix]
        axisData['XZ'] = [[x,offset[2],y] for x,y in pointMatrix]
        axisData['rXZ'] = [[y,offset[2],x] for x,y in pointMatrix]
        axisData['-XZ'] = [[-x,offset[2],-y] for x,y in pointMatrix]
        axisData['-rXZ'] = [[-y,offset[2],-x] for x,y in pointMatrix]
        axisData['YZ'] = [[offset[2],x,y] for x,y in pointMatrix]
        axisData['rYZ'] = [[offset[2],y,x] for x,y in pointMatrix]
        axisData['-YZ'] = [[offset[2],-x,-y] for x,y in pointMatrix]
        axisData['-rYZ'] = [[offset[2],-y,-x] for x,y in pointMatrix]
        axisData['mXY'] = axisData['XY'] + axisData['-XY']
        axisData['mrXY'] = axisData['rXY'] + axisData['-rXY']
        axisData['mXZ'] = axisData['XZ'] + axisData['-XZ']
        axisData['mrXZ'] = axisData['rXZ'] + axisData['-rXZ']
        axisData['mYZ'] = axisData['YZ'] + axisData['-YZ']
        axisData['mrYZ'] = axisData['rYZ'] + axisData['-rYZ']
        axisData['all'] = axisData['XY']+axisData['XZ']+axisData['rXZ']+axisData['-XY']+axisData['-XZ']+axisData['-rXZ'] 
        if sphere:
            axisData['all'] = []
            for ax in axisData:
                if ax is not 'all':
                    axisData['all'].extend(axisData[ax])
        newname = name
        try:
            assert (axisData.has_key(axis)), "Wrong Axis '%s'.\nAvailable axis: %s"%(axis, ','.join(axisData))
            finalPointMatrix = axisData[axis]
        except AssertionError as why:
            finalPointMatrix = axisData['XY']
            log.error(str(why)+'\nDefault to XY')
        if sphere and not length>0:
            quarCircle = len(pointMatrix)/4+1
            finalPointMatrix = axisData['XY']+axisData['XZ']+axisData['XY'][:quarCircle]+axisData['YZ']
        if cylinder and not length>0:
            newpMatrix = []
            pMatrix = pointMatrix
            newpMatrix.extend([[x,0,y] for x,y in pMatrix[:len(pMatrix)/4+1]])
            newpMatrix.extend([[x,height,y] for x,y in pMatrix[:len(pMatrix)/4+1][::-1]])
            newpMatrix.extend([[x,0,y] for x,y in pMatrix[::-1][:len(pMatrix)/2+1]])
            newpMatrix.extend([[x,height,y] for x,y in pMatrix[::-1][len(pMatrix)/2:-len(pMatrix)/4+1]])
            newpMatrix.extend([[x,0,y] for x,y in pMatrix[len(pMatrix)/4:len(pMatrix)/2+1]])
            newpMatrix.extend([[x,height,y] for x,y in pMatrix[len(pMatrix)/2:-len(pMatrix)/4+1]])
            newpMatrix.append([newpMatrix[-1][0],0,newpMatrix[-1][2]])
            newpMatrix.extend([[x,height,y] for x,y in pMatrix[-len(pMatrix)/4:]])
            finalPointMatrix = newpMatrix
        key = range(len(finalPointMatrix))
        crv = pm.curve(name=newname, d=1, p=finalPointMatrix, k=key)
        log.debug(crv)
        return crv

    @staticmethod
    def group(ob):
        '''group control under newTransform'''
        Gp = pm.nt.Transform(name=ob+'Gp')
        ob.setParent(Gp)
        log.info('group {} under {}'.format(ob,Gp))
        return Gp

    #### Control Type
    @__setProperty__
    def Octa(self,mode={}):
        crv = self.createPinCircle(
            self.name,
            step=4,
            sphere=True,
            radius=self.radius,
            length=0)
        return crv

    @__setProperty__
    def Pin(self,mode={'mirror':False,'sphere':False}):
        newAxis = self.axis
        if mode['mirror']:
            newAxis = 'm'+self.axis
        else:
            newAxis = self.axis.replace('m','')
        crv = self.createPinCircle(
            self.name,
            axis=newAxis,
            sphere=mode['sphere'],
            radius=self.radius,
            step=self.step,
            offset=[0,0,self.offset],
            length=self.length)
        return crv

    @__setProperty__
    def Circle(self,mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self.axis,
            radius=self.radius,
            step=self.step,
            sphere=False,
            offset=[0,0,self.offset],
            length=0)
        return crv

    @__setProperty__
    def Cylinder(self,mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self.axis,
            radius=self.radius,
            step=self.step,
            cylinder=True,
            offset=[0,0,self.offset],
            height=self.length,
            length=0)
        return crv
    @__setProperty__
    def NSphere(self,mode={'shaderName':'control_mtl'}):
        crv = pm.sphere(r=self.radius, n=self.name)
        #### set invisible to render
        crvShape = crv[0].getShape()
        crvShape.castsShadows.set(False)
        crvShape.receiveShadows.set(False)
        crvShape.motionBlur.set(False)
        crvShape.primaryVisibility.set(False)
        crvShape.smoothShading.set(False)
        crvShape.visibleInReflections.set(False)
        crvShape.visibleInRefractions.set(False)
        crvShape.doubleSided.set(False)
        #### set Shader
        shdr_name = '{}_{}'.format(mode['shaderName'], self.name)
        sg_name = '{}{}'.format(shdr_name,'SG')
        if pm.objExists(shdr_name) or pm.objExists(sg_name):
            try:
                pm.delete(shdr_name)
                pm.delete(sg_name)
            except:
                pass
        shdr,sg = pm.createSurfaceShader('surfaceShader')
        pm.rename(shdr, shdr_name)
        pm.rename(sg, sg_name)
        shdr.outColor.set(self.color.rgb)
        shdr.outTransparency.set([self.color.a for i in range(3)])
        pm.sets(sg, fe=crv[0])
        return crv[0]

    @__setProperty__
    def Sphere(self,mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self.axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0)
        return crv
    #### control method
    def getControls(self):
        msg = ['{} contain controls:'.format(self.name)]
        for key,ctls in self.controls.items():
            msg.append('+'+key)
            for ctl in ctls:
                msg.append('--'+ctl)
        log.info('\n'.join(msg))
        return self.controls
    def setAxis(self, control=None, axis=''):
        if axis:
            self.axis = axis
        #print self.axis
        if self.axisData.has_key(self.axis):
            control.setRotation(self.axisData[self.axis])
            #print control.getRotation()
            pm.makeIdentity(control, apply=True)
            if not control:
                for control in self.controls:
                    self.setAxis(control)
        else:
            print 'set Axis along %s not possible'%self.axis

    def setColor(self, control=None):
        try:
            control.overrideEnabled.set(True)
            control.overrideRGBColors.set(True)
            control.overrideColorRGB.set(self.color)
            sg= control.shadingGroups()[0] if control.shadingGroups() else None
            if sg:
                shdr = sg.inputs()[0]
                shdr.outColor.set(self.color.rgb)
                shdr.outTransparency.set([self.color.a for i in range(3)])
        except AttributeError as why:
            log.error(why)

    def deleteControl(self,id=None, deleteGp=False):
        if id and id<len(self.controls):
            pm.delete(self.controls[id])
            return self.control[id]
        pm.delete(self.controls)
        if deleteGp:
            pm.delete(self.controlGps)

    def changeShape(self,ctl,ctlType,**kws):
        controlType = {
            'Pin':self.Pin,
            'Circle':self.Circle,
            'Octa':self.Octa,
            'Cylinder':self.Cylinder,
            'Sphere':self.Sphere,
            'NSphere':self.NSphere
        }
        kws['group'] = False
        temp = controlType[ctlType](**kws)
        pm.select(cl=True)
        ul.parent_shape(temp,ctl)
            #ru.connectTransform(control,joint,**atrConnect)
        #return controller
    def createFreeJointControl(self,bones,**kws):
        for bone in bones:
            bonepos = bone.getTranslation('world')
            bonGp = pm.nt.Transform(name=bone.name()+'Gp')
            bonGp.setTranslation(bonepos, 'world')
            pm.makeIdentity(bonGp, apply=True)
            bone.setParent(bonGp)
            ctl = self.Sphere(name=bone.name().replace('bon', 'ctl'),**kws)
            ctlGp = ctl.getParent()
            #ctl.setParent(ctlGp)
            ctlGp.setTranslation(bonepos, 'world')
            pm.makeIdentity(ctlGp, apply=True)
            for atr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                ctl.attr(atr) >> bonGp.attr(atr)

    def createParentJointControl(self, bones,**kws):
        for bone in bones:
            if 'offset' not in bone.getParent().name():
                ru.createOffsetJoint(bone)
            bonematrix = bone.getMatrix(worldSpace=True)
            name = bone.name().split('|')[-1].split('_')[0]
            ctl = self.Pin(name=name+'_ctl',**kws)
            ctlGp = ctl.getParent()
            ctlGp.rename(name+'_ctlGp')
            #ctl.setParent(ctlGp)
            ctlGp.setMatrix(bonematrix,worldSpace=True)
            # ctl.rotate.set(offsetRotate)
            # pm.makeIdentity(ctl,apply=True)
            for atr in ['translate', 'rotate', 'scale']:
                ctl.attr(atr) >> bone.attr(atr)

meta.registerMClassInheritanceMapping()
# meta.registerMClassNodeMapping(nodeTypes='transform')