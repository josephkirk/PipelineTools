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
import math
from pymel.util.enum import Enum
from ..packages.Red9.core import Red9_Meta as meta
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
reload(ul)


# print meta
# log.info('Rig Class Initilize')
class CHRig(meta.MetaHIKCharacterNode):
    def __init__(self, name='', hikName='CH'):
        super(FacialRigMeta, self).__init__(hikname, **kws)
        self.setascurrentcharacter()
        self.select()
        self.hikProperty = self.getHIKPropertyStateNode()
        self.hikControl = self.getHIKControlSetNode()
        # self.character.lockState = False
        # pm.lockNode(hikName,lock=False)
        self.addAttr('CharacterName', name)
        self.addAttr('BuildBy', '{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')))
        self.addAttr('Branch', os.environ.get('USERDOMAIN'))
        self.addAttr('BuildDate', pm.date())
        self.addAttr('FacialRig', attrType='messageSimple')
        self.addAttr('HairRig', attrType='messageSimple')
        self.addAttr('SecondaryRig', attrType='messageSimple')
        log.info('%s Initilize' % self.__str__)

    def getFacialRig(self):
        pass

    def getSecondaryRig(self):
        pass


class FacialRigMeta(meta.MetaRig):
    '''
    Facial Rig MetaNode
    to get this node use pt.rc.meta.getMetaNodes(mClass='FacialRigMeta')
    '''

    def __init__(self, *args, **kws):
        super(FacialRigMeta, self).__init__(*args, **kws)
        self.lockState = False
        self.mSystemRoot = False

    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType', 'FacialRig', l=True)
        self.addAttr('CharacterName', '')
        self.addAttr('BuildBy', '{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')), l=True)
        self.addAttr('Branch', os.environ.get('USERDOMAIN'), l=True)
        self.addAttr('BuildDate', pm.date(), l=True)
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
        BS.connectChild('facial_panel', 'BSPanel')
        BS.connectChild('brow_ctl', 'BrowBSControl')
        BS.connectChild('eye_ctl', 'EyeBSControl')
        BS.connectChild('mouth_ctl', 'EyeBSControl')

    def getProperty(self):
        #### connect FaceRigGp to facialGp
        if pm.objExists('facialGp'):
            self.FaceRigGp = 'facialGp'
        #### connect facialGroup
        facialGps = []
        for gp in ['facial', 'facialGuide', 'jawDeform', 'eyeDeform', 'orig']:
            if pm.objExists(gp):
                facialGps.append(gp)
        self.FaceDeformGp = facialGps
        #### get facialTarget External
        scenedir = pm.sceneName().dirname()
        dir = scenedir.parent
        bsdir = pm.util.common.path(dir + '/facialtarget/facialtarget.mb')
        if bsdir.isfile():
            self.FacialTargetPath = bsdir.replace(pm.workspace.path + '/', '')

    def build(self):
        pass


class SecondaryRigMeta(meta.MetaRig):
    '''
    Secondary Rig MetaNode
    to get this node use pt.rc.meta.getMetaNodes(mClass='SecondaryRigMeta')
    '''

    def __init__(self, *args, **kws):
        super(SecondaryRigMeta, self).__init__(*args, **kws)
        self.lockState = False
        self.mSystemRoot = False

    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType', 'SecondaryRig', l=True)
        self.addAttr('CharacterName', '')
        self.addAttr('BuildBy', '{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')), l=True)
        self.addAttr('Branch', os.environ.get('USERDOMAIN'), l=True)
        self.addAttr('BuildDate', pm.date(), l=True)
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

    def __init__(self, *args, **kws):
        super(HairRigMeta, self).__init__(*args, **kws)
        self.lockState = False
        self.mSystemRoot = False

    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType', 'HairRigMeta', l=True)

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

    def __init__(self, *args, **kws):
        # if meta.getMetaNodes(mClass='ClothRigMeta'):
        #    super(ClothRigMeta, self).__init__(meta.getMetaNodes(mClass='ClothRigMeta')) 
        # else:
        super(ClothRigMeta, self).__init__(*args, **kws)
        self.lockState = False
        self.mSystemRoot = False
        self.controlOb = ControlObject('control')

    @property
    def controlObject(self, *args, **kwargs):
        return self.controlOb

    @controlObject.setter
    def controlObject(self, *args, **kwargs):
        self.controlOb = ControlObject(*args, **kwargs)

    def __bindData__(self):
        '''
        build Attribute
        '''
        ###### MetaNode information Attributes
        self.addAttr('RigType', 'ClothRigMeta', l=True)

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
        self.constraint_name = '_'.join([self.root_name, 'pointOnPolyConstraint1'])
        self.guide_mesh = guide_mesh
        self._get()

    def __repr__(self):
        return self.name

    def __call__(self, *args, **kwargs):
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

    def set_constraint(self, target=None):
        if all([self.guide_mesh, self.guide_mesh, self.root]):
            pm.delete(self.constraint)
            if target is None:
                target = self.root
            closest_uv = ul.get_closest_component(target, self.guide_mesh)
            self.constraint = pm.pointOnPolyConstraint(
                self.guide_mesh, self.root, mo=False,
                name=self.constraint_name)
            stripname = self.guide_mesh.getParent().name().split('|')[-1]
            self.constraint.attr(stripname + 'U0').set(closest_uv[0])
            self.constraint.attr(stripname + 'V0').set(closest_uv[1])
            # pm.select(closest_info['Closest Vertex'])
        else:
            pm.error('Please set guide mesh')

    def _get(self):
        self.node = ul.get_node(self.name)
        self.root = ul.get_node(self.root_name)
        self.constraint = ul.get_node(self.constraint_name)
        return self.node

    @classmethod
    def guides(cls, name='eye', root_suffix='Gp', suffix='loc', separator='_'):
        list_all = pm.ls('*%s*%s*' % (name, suffix), type='transform')
        guides = []
        for ob in list_all:
            if root_suffix not in ob.name():
                ob_name = ob.name().split(separator)
                guide = cls(ob_name[0], suffix=suffix, root_suffix=root_suffix)
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

    def rename(self, new_name):
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

    def create(self, shape=None, pos=[0, 0, 0], parent=None, create_offset=True):
        if not self.node:
            if shape:
                self.node = pm.nt.Transform(name=self.name)
                shape = ul.get_node(shape)
                ul.parent_shape(shape, self.node)
            else:
                self.node = \
                    pm.sphere(ax=(0, 1, 0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False,
                              n=self.name)[0]
        self.node.setTranslation(pos, 'world')
        self.WorldPosition = self.node.getTranslation('world')
        self.shape = ul.get_shape(self.node)
        for atr in ['castsShadows', 'receiveShadows', 'holdOut', 'motionBlur', 'primaryVisibility', 'smoothShading',
                    'visibleInReflections', 'visibleInRefractions', 'doubleSided']:
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
        assert self.guide, 'Control object for %s do not have guide locator'%self.name
        assert self.root, 'Control object for %s do not have root'%self.name
        self.constraint = pm.pointConstraint(self.guide, self.root, o=(0, 0, 0), w=1)
    
    def delete_constraint(self):
        if self.constraint:
            pm.delete(self.constraint)
    
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
        if self.root:
            searchConstraint = self.root.listConnections(type=pm.nt.PointConstraint)
            if searchConstraint:
                self.constraint = searchConstraint[0]
            else:
                self.constraint = None

    @classmethod
    def controls(cls, name, offset_suffix='offset', root_suffix='Gp', suffix='ctl', separator='_'):
        list_all = pm.ls('*%s*%s*' % (name, suffix), type='transform')
        controls = []
        for ob in list_all:
            if root_suffix not in ob.name():
                ob_name = ob.name().split(separator)
                control = cls(ob_name[0], offset_suffix=offset_suffix, suffix=suffix, root_suffix=root_suffix)
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

    def __call__(self, new_bone=None, pos=[0, 0, 0], parent=None, create_control=False):
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

    def create_offset(self, pos=[0, 0, 0], space='world', reset_pos=False, parent=None):
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
                    print '%s connection to %s is %s' % (atr, self.control_name, connect)
                    connect_state.append((atr, connect))
        return connect_state

    def connect(self):
        if self.bone and self.control.node:
            if self.offset:
                pm.matchTransform(self.offset, self.bone, pivots=True)
            pm.matchTransform(self.control.node, self.bone, pivots=True)
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
        if other_name and any([isinstance(other_name, t) for t in [str, unicode]]):
            control_name = other_name
        self.control = FacialControl(control_name)
        return self.control

    def _get(self):
        self.bone = ul.get_node(self.name)
        # if self.bone:
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
            names=['eye', 'cheek', 'nose', 'lip'],
            offset_suffix='offset', root_suffix='Gp',
            suffix='bon', separator='_',
            directions=['Left', 'Right', 'Center', 'Root']):
        '''get all Bone'''
        # class facialbones(Enum):
        for name in names:
            list_all = pm.ls('*%s*%s*' % (name, suffix), type='transform')
            # print list_all
            allbone = []
            for ob in list_all:
                if root_suffix not in ob.name() and offset_suffix not in ob.name():
                    ob_name = ob.name().split(separator)
                    bone = cls(ob_name[0], offset_suffix=offset_suffix, suffix=suffix, root_suffix=root_suffix)
                    allbone.append(bone)
            bones = {}
            bones['All'] = allbone
            for direction in directions:
                bones[direction] = []
                for bone in allbone:
                    if direction in bone.name:
                        bones[direction].append(bone)
            yield (name,bones)


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

    def facectl(self, value=None):
        if value is not None:
            if isinstance(value, list):
                self.ctl_names = value
        self.ctl_fullname = ['_'.joint([ctl_name, 'ctl']) for ctl_name in ctl_names]
        self.ctl = []

        def create_bs_ctl():
            pass

        try:
            for ctl_name in self.ctl_fullname:
                ctl = PyNode(ctl)
                self.ctl.append(ctl)
        except:
            create_bs_ctl(ctl)

    def facebs(self, value=None):
        if value is not None:
            self.facebs_name = value
        self.facebs = ul.get_blendshape_target(self.facebs_name)
        if self.facebs:
            self.facebs_def = {}
            self.facebs_def['misc'] = []
            for bs in self.facebs[0]:
                for bs_name in bs_def:
                    for direction in direction_name:
                        if bs.startswith(bs_name):
                            if not self.facebs_def.has_key(bs_name):
                                self.facebs_def[bs_name] = {}
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
        eyebrow = facepart[0].replace(facepart[1], '')
        bs_controller[
            '_'.join([eyebrow, self.control_name])
        ] = create_bs_list(
            facepart[0],
            self.eyebs_name[:3],
            True)
        bs_controller[
            '_'.join([facepart[1], self.control_name])
        ] = create_bs_list(
            facepart[1],
            self.eyebs_name[1:],
            True)
        bs_controller[
            '_'.join([facepart[2], self.control_name])
        ] = create_bs_list(
            facepart[2],
            self.mouthbs_name,
        )
        for ctl_name, bs_targets in bs_controller.items():
            for bs_target in bs_targets:
                print '%s.%s >> %s.%s' % (ctl_name, bs_target, self.facebs_name, bs_target)
                # print bs_controller


class ControlObject(object):
    '''Class to create Control'''

    def __init__(
            self,
            name='ControlObject',
            suffix='ctl',
            radius=1,
            res='high',
            length=2.0,
            axis='XY',
            offset=0.0,
            color='red'):
        self._suffix = suffix
        self._name = '{}_{}'.format(name, suffix)
        self._radius = radius
        self._length = length
        self._axis = axis
        self._offset = offset
        self._step = res
        self._color = color
        self.controls = {}
        self.controls['all'] = []
        self.controlGps = []

        self._resolutions = {
            'low': 4,
            'mid': 8,
            'high': 24
        }
        self._axisList = ['XY', 'XZ', 'YZ']
        self._axisList.extend([a[::-1] for a in self._axisList])  ## add reverse asxis
        self._axisList.extend(['-%s' % a for a in self._axisList])  ## add minus axis
        self._colorData = {
            'white': pm.dt.Color.white,
            'red': pm.dt.Color.red,
            'green': pm.dt.Color.green,
            'blue': pm.dt.Color.blue,
            'yellow': [1, 1, 0, 0],
            'cyan': [0, 1, 1, 0],
            'violet': [1, 0, 1, 0],
            'orange': [1, 0.5, 0, 0],
            'pink': [1, 0, 0.5, 0],
            'jade': [0, 1, 0.5, 0]
        }
        self._controlType = {
            'Pin': self.Pin,
            'Circle': self.Circle,
            'Octa': self.Octa,
            'Cylinder': self.Cylinder,
            'Sphere': self.Sphere,
            'NSphere': self.NSphere
        }
        self._uiElement = {}
        log.info('Control Object class name:{} initialize'.format(name))
        log.debug('\n'.join(['{}:{}'.format(key, value) for key, value in self.__dict__.items()]))

    ####Define Property
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        if self._suffix not in newName:
            self._name = '{}_{}'.format(newName, self._suffix)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, newradius):
        assert any([isinstance(newradius, typ) for typ in [float, int]]), "radius must be of type float"
        self._radius = newradius

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, newlength):
        assert any([isinstance(newlength, typ) for typ in [float, int]]), "length must be of type float"
        self._length = newlength

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, newoffset):
        if any([isinstance(newoffset, typ) for typ in [list, set, tuple]]):
            assert (len(newoffset) == 3), 'offset must be a float3 of type list,set or tuple'
            self._offset = newoffset

    @property
    def color(self):
        return pm.dt.Color(self._color)

    @color.setter
    def color(self, newcolor):
        if isinstance(newcolor, str):
            assert (self._colorData.has_key(newcolor)), "color data don't have '%s' color.\nAvailable color:%s" % (
                newcolor, ','.join(self._colorData))
            self._color = self._colorData[newcolor]
        if any([isinstance(newcolor, typ) for typ in [list, set, tuple]]):
            assert (len(newcolor) >= 3), 'color must be a float4 or float3 of type list,set or tuple'
            self._color = pm.dt.Color(newcolor)

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, newaxis):
        if isinstance(newaxis, str) or isinstance(newaxis, unicode):
            assert (newaxis in self._axisList), "axis data don't have '%s' axis.\nAvailable axis:%s" % (
                newaxis, ','.join(self._axisData))
            self._axis = newaxis

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, newres):
        assert (
            self._resolutions.has_key(newres)), "step resolution value not valid.\nValid Value:%s" % self._resolutions
        self._step = self._resolutions[newres]

    # @property
    # def res(self):

    # decorator
    # @ul.error_alert
    def __setProperty__(func):
        '''Wraper that make keywords argument of control type function
        to tweak class Attribute'''

        @ul.wraps(func)
        def wrapper(self, *args, **kws):
            # store Class Attribute Value
            oldValue = {}
            oldValue['offset'] = self.offset
            oldValue['res'] = self.step
            oldValue['color'] = self.color
            fkws = func.__defaults__[0]
            # Assign Keyword Argument value to Class Property value
            log.debug('Assign KeyWord to ControlObject Class Propety')
            if 'offset' in kws:
                self.offset = kws['offset']
                log.debug('{} set to {}'.format('offset', offset))
            if 'res' in kws:
                self.step = kws['res']
                log.debug('{} set to {}'.format('res', res))
            if 'color' in kws:
                self.color = kws['color']
                log.debug('{} set to {}'.format('color', color))

            for key, value in kws.items():
                if self.__dict__.has_key(key):
                    oldValue[key] = self.__dict__[key]
                    self.__dict__[key] = value
                    log.debug('{} set to {}'.format(key, value))
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
            control = func(self, mode=fkws)
            if prefixName is True:
                control.rename('_'.join([func.__name__, self.name]))
            self.controls['all'].append(control)
            if not self.controls.has_key(func.__name__):
                self.controls[func.__name__] = []
            self.controls[func.__name__].append(control)
            if kws.has_key('setAxis') and kws['setAxis'] is True:
                self.setAxis(control, self.axis)
            self.setColor(control, self.color)
            control.setTranslation(self.offset, 'world')
            pm.makeIdentity(control, apply=True)
            log.info('Control of type:{} name {} created along {}'.format(func.__name__, control.name(), self._axis))
            if groupControl is True:
                Gp = self.group(control)
                self.controlGps.append(Gp)
            else:
                pm.xform(control, pivots=(0, 0, 0), ws=True, dph=True, ztp=True)

            #### reset Class Attribute Value to __init__ value
            for key, value in oldValue.items():
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
            offset=[0, 0, 0],
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
            max Angle: {}'''.format(name, createCurve, axis, sphere, offset, radius, length, step, maxAngle))
        maxAngle = maxAngle / 180.0 * math.pi
        inc = maxAngle / step
        pointMatrix = []
        theta = 0
        if length > 0:
            pointMatrix.append([0, 0])
            pointMatrix.append([0, length])
            offset = [offset[0], -radius - length - offset[1], offset[2]]
        # print offset
        while theta <= maxAngle:
            if length > 0:
                x = (-offset[0] + radius * math.sin(theta))
                y = (offset[1] + radius * math.cos(theta)) * -1.0
            else:
                x = (offset[0] + radius * math.cos(theta))
                y = (offset[1] + radius * math.sin(theta))
            pointMatrix.append([x, y])
            # print "theta angle {} produce [{},{}]".format(round(theta,2),round(x,4),round(y,4))
            theta += inc
        if not createCurve:
            return pointMatrix
        axisData = {}
        axisData['XY'] = [[x, y, offset[2]] for x, y in pointMatrix]
        axisData['YX'] = [[y, x, offset[2]] for x, y in pointMatrix]
        axisData['-XY'] = [[-x, -y, offset[2]] for x, y in pointMatrix]
        axisData['-YX'] = [[-y, -x, offset[2]] for x, y in pointMatrix]
        axisData['XZ'] = [[x, offset[2], y] for x, y in pointMatrix]
        axisData['ZX'] = [[y, offset[2], x] for x, y in pointMatrix]
        axisData['-XZ'] = [[-x, offset[2], -y] for x, y in pointMatrix]
        axisData['-ZX'] = [[-y, offset[2], -x] for x, y in pointMatrix]
        axisData['YZ'] = [[offset[2], x, y] for x, y in pointMatrix]
        axisData['ZY'] = [[offset[2], y, x] for x, y in pointMatrix]
        axisData['-YZ'] = [[offset[2], -x, -y] for x, y in pointMatrix]
        axisData['-ZY'] = [[offset[2], -y, -x] for x, y in pointMatrix]
        axisData['mXY'] = axisData['XY'] + axisData['-XY']
        axisData['mYX'] = axisData['YX'] + axisData['-YX']
        axisData['mXZ'] = axisData['XZ'] + axisData['-XZ']
        axisData['mZX'] = axisData['ZX'] + axisData['-ZX']
        axisData['mYZ'] = axisData['YZ'] + axisData['-YZ']
        axisData['mZY'] = axisData['ZY'] + axisData['-ZY']
        axisData['all'] = axisData['XY'] + axisData['XZ'] + axisData['ZX'] + axisData['-XY'] + axisData['-XZ'] + \
                          axisData['-ZX']
        newname = name
        try:
            assert (axisData.has_key(axis)), "Wrong Axis '%s'.\nAvailable axis: %s" % (axis, ','.join(axisData))
            finalPointMatrix = axisData[axis]
        except AssertionError as why:
            finalPointMatrix = axisData['XY']
            log.error(str(why) + '\nDefault to XY')
        if sphere and not cylinder and not length > 0:
            quarCircle = len(pointMatrix) / 4 + 1
            finalPointMatrix = axisData['XY'] + axisData['XZ'] + axisData['XY'][:quarCircle] + axisData['YZ']
        elif sphere and not cylinder and length > 0:
            if axis[-1] == 'X':
                finalPointMatrix = axisData['YX'] + axisData['ZX']
            elif axis[-1] == 'Y':
                finalPointMatrix = axisData['XY'] + axisData['ZY']
            elif axis[-1] == 'Z':
                finalPointMatrix = axisData['XZ'] + axisData['YZ']
        elif cylinder and not sphere and not length > 0:
            newpMatrix = []
            pMatrix = pointMatrix
            newpMatrix.extend([[x, 0, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1]])
            newpMatrix.extend([[x, height, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1][::-1]])
            newpMatrix.extend([[x, 0, y] for x, y in pMatrix[::-1][:len(pMatrix) / 2 + 1]])
            newpMatrix.extend([[x, height, y] for x, y in pMatrix[::-1][len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
            newpMatrix.extend([[x, 0, y] for x, y in pMatrix[len(pMatrix) / 4:len(pMatrix) / 2 + 1]])
            newpMatrix.extend([[x, height, y] for x, y in pMatrix[len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
            newpMatrix.append([newpMatrix[-1][0], 0, newpMatrix[-1][2]])
            newpMatrix.extend([[x, height, y] for x, y in pMatrix[-len(pMatrix) / 4:]])
            finalPointMatrix = newpMatrix
        key = range(len(finalPointMatrix))
        crv = pm.curve(name=newname, d=1, p=finalPointMatrix, k=key)
        log.debug(crv)
        return crv

    @staticmethod
    def group(ob):
        '''group control under newTransform'''
        Gp = pm.nt.Transform(name=ob + 'Gp')
        ob.setParent(Gp)
        log.info('group {} under {}'.format(ob, Gp))
        return Gp

    #### Control Type
    @__setProperty__
    def Octa(self, mode={}):
        crv = self.createPinCircle(
            self.name,
            step=4,
            sphere=True,
            radius=self.radius,
            length=0)
        return crv

    @__setProperty__
    def Pin(self, mode={'mirror': False, 'sphere': False}):
        newAxis = self._axis
        if mode['mirror']:
            newAxis = 'm' + self._axis
        else:
            newAxis = self._axis.replace('m', '')
        crv = self.createPinCircle(
            self.name,
            axis=newAxis,
            sphere=mode['sphere'],
            radius=self.radius,
            step=self.step,
            length=self.length)
        return crv

    @__setProperty__
    def Circle(self, mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=False,
            length=0)
        return crv

    @__setProperty__
    def Cylinder(self, mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            cylinder=True,
            height=self.length,
            length=0,
        )
        return crv

    @__setProperty__
    def NSphere(self, mode={'shaderName': 'control_mtl'}):
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
        sg_name = '{}{}'.format(shdr_name, 'SG')
        if pm.objExists(shdr_name) or pm.objExists(sg_name):
            try:
                pm.delete(shdr_name)
                pm.delete(sg_name)
            except:
                pass
        shdr, sg = pm.createSurfaceShader('surfaceShader')
        pm.rename(shdr, shdr_name)
        pm.rename(sg, sg_name)
        shdr.outColor.set(self.color.rgb)
        shdr.outTransparency.set([self.color.a for i in range(3)])
        pm.sets(sg, fe=crv[0])
        return crv[0]

    @__setProperty__
    def Sphere(self, mode={}):
        crv = self.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0)
        return crv

    #### control method
    def getControls(self):
        msg = ['{} contain controls:'.format(self.name)]
        for key, ctls in self.controls.items():
            msg.append('+' + key)
            for ctl in ctls:
                msg.append('--' + ctl)
        log.info('\n'.join(msg))
        return self.controls

    def setAxis(self, control, axis='XY'):
        axisData = {}
        axisData['XY'] = [0, 0, 90]
        axisData['YX'] = [0, 0, -90]
        axisData['XZ'] = [0, 90, 0]
        axisData['ZX'] = [0, -90, 0]
        axisData['YZ'] = [90, 0, 0]
        axisData['ZY'] = [-90, 0, 0]
        assert (axis in axisData), "set axis data don't have '%s' axis.\nAvailable axis:%s" % (axis, ','.join(axisData))
        control.setRotation(axisData[axis])
        # print control.getRotation()
        pm.makeIdentity(control, apply=True)
        if not control:
            for control in self.controls:
                self.setAxis(control)

    def setColor(self, control, newColor):
        self.color = newColor
        try:
            control.overrideEnabled.set(True)
            control.overrideRGBColors.set(True)
            control.overrideColorRGB.set(self.color)
            sg = control.shadingGroups()[0] if control.shadingGroups() else None
            if sg:
                shdr = sg.inputs()[0]
                shdr.outColor.set(self.color.rgb)
                shdr.outTransparency.set([self.color.a for i in range(3)])
        except AttributeError as why:
            log.error(why)

    def deleteControl(self, id=None, deleteGp=False):
        if id and id < len(self.controls):
            pm.delete(self.controls[id])
            return self.control[id]
        pm.delete(self.controls)
        if deleteGp:
            pm.delete(self.controlGps)

    def createControl(self, ctlType, **kws):
        assert self._controlType.has_key(ctlType), 'Control Type %s is not valid' % ctlType
        newCtl = self._controlType[ctlType](**kws)
        return newCtl

    def changeControlShape(self, selectControl, ctlType, **kws):
        kws['group'] = False
        temp = self.createControl(ctlType, **kws)
        temp.setParent(selectControl.getParent())
        temp.setMatrix(selectControl.getMatrix(ws=True), ws=True)
        pm.delete(selectControl.getShape(), shape=True)
        pm.parent(temp.getShape(), selectControl, r=True, s=True)
        pm.delete(temp)
        return selectControl

    def createPropJointControl(self, bones, **kws):
        ctls = []
        for bone in bones:
            bonepos = bone.getMatrix(ws=True)
            kws['name'] = bone.name().replace('bon', 'ctl')
            ctl = self.Octa(**kws)
            ctls.append(ctl)
            ctlGp = ctl.getParent()
            # ctl.setParent(ctlGp)
            ctlGp.setMatrix(bonepos, ws=True)
            # pm.makeIdentity(ctlGp, apply=True)
            pm.parentConstraint(ctl, bone, mo=True)
        pm.select(ctls)
        return ctls

    def createFreeJointControl(self, bones, **kws):
        ctls = []
        for bone in bones:
            bonepos = bone.getTranslation('world')
            bonename = bone.name().split('|')[-1].split('_')[0]
            if not bone.getParent() or bone.getParent().name() != (bone.name() + 'Gp'):
                oldParent = bone.getParent()
                bonGp = pm.nt.Transform(name=bonename + '_bonGp')
                bonGp.setTranslation(bonepos, 'world')
                pm.makeIdentity(bonGp, apply=True)
                bone.setParent(bonGp)
                bonGp.setParent(oldParent)
            else:
                bonGp = bone.getParent()
            self.name = bonename.replace('bon', 'ctl')
            ctl = self.Sphere(**kws)
            ctls.append(ctl)
            ctlGp = ctl.getParent()
            # ctl.setParent(ctlGp)
            ctlGp.setTranslation(bonepos, 'world')
            pm.makeIdentity(ctlGp, apply=True)
            for atr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                ctl.attr(atr) >> bonGp.attr(atr)
        pm.select(ctls)
        return ctls

    def createParentJointControl(self, bones, **kws):
        ctls = []
        for bone in bones:
            if not bone.getParent() or 'offset' not in bone.getParent().name():
                ru.createOffsetJoint(bone, cl=True)
            bonematrix = bone.getMatrix(worldSpace=True)
            name = bone.name().split('|')[-1].split('_')[0]
            ctl = self.Pin(name=name + '_ctl', **kws)
            ctlGp = ctl.getParent()
            ctlGp.rename(name + '_ctlGp')
            ctlGp.setMatrix(bonematrix, worldSpace=True)
            if ctls:
                ctlGp.setParent(ctls[-1])
            ctls.append(ctl)
            for atr in ['translate', 'rotate', 'scale']:
                ctl.attr(atr) >> bone.attr(atr)
        pm.select(ctls)
        return ctls

    #### Ui contain
    @classmethod
    def show(cls):
        cls()._showUI()

    # def _setUIValue(self, uiName, *args,**kwargs):
    #     print args, kwargs
    #     self._uiElement[uiName] = args[0]
    #     log.info('%s set to %s'%(uiName, str(args[0])))

    def _getUIValue(self):
        self.name = self._uiElement['ctlName'].getText()
        self.color = self._uiElement['ctlColor'].getRgbValue()
        print self._uiElement['ctlAxis'].getValue()
        self.axis = self._uiElement['ctlAxis'].getValue()
        self.radius = self._uiElement['ctlRadius'].getValue()[0]
        self.length = self._uiElement['ctlLength'].getValue()[0]
        self.step = self._uiElement['ctlRes'].getValue()
        self.offset = self._uiElement['ctlOffset'].getValue()

    def _do(self):
        self._getUIValue()
        ctlType = self._uiElement['ctlType'].getValue()
        kws = {}
        for name, value in zip(self._uiElement['ctlOption'].getLabelArray4(),
                               self._uiElement['ctlOption'].getValueArray4()):
            kws[name] = value
        print kws, ctlType
        self.createControl(ctlType, **kws)

    def _do2(self):
        if pm.selected():
            sels = pm.selected()
            self._getUIValue()
            ctlType = self._uiElement['ctlType'].getValue()
            kws = {}
            for name, value in zip(self._uiElement['ctlOption'].getLabelArray4(),
                                   self._uiElement['ctlOption'].getValueArray4()):
                kws[name] = value
            print kws, ctlType
            for sel in sels:
                self.changeControlShape(sel, ctlType, **kws)

    def _do3(self):
        self._getUIValue()
        if pm.selected():
            sels = pm.selected()
            for sel in sels:
                self.setColor(sel, self.color)

    def _do4(self):
        self._getUIValue()
        if pm.selected():
            sels = pm.selected()
            self.createFreeJointControl(sels, group=True)

    def _do5(self):
        self._getUIValue()
        if pm.selected():
            sels = pm.selected()
            self.createParentJointControl(
                sels, group=True,
                mirror=self._uiElement['ctlOption'].getValueArray4()[-1])

    def _do6(self):
        self._getUIValue()
        if pm.selected():
            sels = pm.selected()
            self.createPropJointControl(
                sels, group=True)

    def _showUI(self, parent=None):
        self._uiName = 'CreateControlUI'
        self._windowSize = (250, 10)
        if pm.window(self._uiName + 'Window', ex=True):
            pm.deleteUI(self._uiName + 'Window', window=True)
            pm.windowPref(self._uiName + 'Window', remove=True)
        if parent is not None and isinstance(parent, pm.uitypes.Window):
            self._window = parent
        else:
            self._window = pm.window(
                self._uiName + 'Window', title=self._uiName,
                rtf=True, widthHeight=self._windowSize, sizeable=False)
        self._uiTemplate = pm.uiTemplate('CreateControlUITemplace', force=True)
        self._uiTemplate.define(pm.button, width=5, height=40, align='left')
        self._uiTemplate.define(pm.columnLayout, adjustableColumn=1, w=10)
        self._uiTemplate.define(pm.frameLayout, borderVisible=True, labelVisible=True, width=self._windowSize[0])
        self._uiTemplate.define(
            pm.rowColumnLayout,
            rs=[(1, 5), ],
            adj=True, numberOfColumns=2,
            cal=[(1, 'left'), ],
            columnWidth=[(1, 100), (2, 100)])
        with self._window:
            with self._uiTemplate:
                with pm.frameLayout(label='Create Control'):
                    with pm.rowColumnLayout():
                        self._uiElement['ctlName'] = pm.textFieldGrp(
                            cl2=('left', 'right'),
                            co2=(0, 0),
                            cw2=(40, 100),
                            label='Name:', text=self.name)
                        self._uiElement['ctlType'] = pm.optionMenu(label='Type:')
                        with self._uiElement['ctlType']:
                            for ct in self._controlType:
                                pm.menuItem(label=ct)
                    with pm.rowColumnLayout(
                            numberOfColumns=3,
                            columnWidth=[(1, 10), ]):
                        self._uiElement['ctlLength'] = pm.floatFieldGrp(
                            cl2=('left', 'right'),
                            co2=(0, 0),
                            cw2=(40, 30),
                            numberOfFields=1,
                            label='Length:',
                            value1=3.0)
                        self._uiElement['ctlRadius'] = pm.floatFieldGrp(
                            cl2=('left', 'right'),
                            co2=(0, 0),
                            cw2=(40, 30),
                            numberOfFields=1,
                            label='Radius:',
                            value1=0.5)
                        self._uiElement['ctlRes'] = pm.optionMenu(label='Step:')
                        with self._uiElement['ctlRes']:
                            for ct in self._resolutions:
                                pm.menuItem(label=ct)
                    with pm.rowColumnLayout():
                        self._uiElement['ctlColor'] = pm.colorSliderGrp(
                            label='Color:',
                            rgb=(0, 0, 1),
                            co3=(0, 0, 0),
                            cw3=(30, 60, 60),
                            cl3=('left', 'center', 'right'))
                        self._uiElement['ctlAxis'] = pm.optionMenu(label='Axis:')
                        with self._uiElement['ctlAxis']:
                            for ct in self._axisList:
                                pm.menuItem(label=ct)
                    self._uiElement['ctlOffset'] = pm.floatFieldGrp(
                        cl4=('left', 'center', 'center', 'center'),
                        co4=(0, 5, 0, 0),
                        cw4=(45, 50, 50, 50),
                        numberOfFields=3,
                        label='Offset:')
                    self._uiElement['ctlOption'] = pm.checkBoxGrp(
                        cl5=('left', 'center', 'center', 'center', 'center'),
                        co5=(0, 5, 0, 0, 0),
                        cw5=(45, 50, 50, 50, 50),
                        numberOfCheckBoxes=4,
                        label='Options:',
                        labelArray4=['group', 'setAxis', 'sphere', 'mirror'])
                    pm.button(label='Create', c=pm.Callback(self._do))
                    with pm.popupMenu(b=3):
                        pm.menuItem(label='Change Current Select', c=pm.Callback(self._do2))
                        pm.menuItem(label='Set Color Select', c=pm.Callback(self._do3))
                        pm.menuItem(label='Create Free Control', c=pm.Callback(self._do4))
                        pm.menuItem(label='Create Prop Control', c=pm.Callback(self._do6))
                        pm.menuItem(label='Create Parent Control', c=pm.Callback(self._do5))
                        pm.menuItem(label='Create Short Hair Control', c=pm.Callback(self._do5))
                        pm.menuItem(label='Create Long Hair Control', c=pm.Callback(HairRig))
                    with pm.frameLayout(label='Utils:'):
                        pm.button(label='Basic Intergration', c=pm.Callback(ru.basic_intergration))
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
                                    translate=True, rotate=False, Scale=False))
                                pm.menuItem(label='connect Rotate', c=pm.Callback(
                                    ru.connectTransform,
                                    translate=False, rotate=True, Scale=False))
                                pm.menuItem(label='connect Scale', c=pm.Callback(
                                    ru.connectTransform,
                                    translate=False, rotate=False, Scale=True))
                            smallbutton(label='disconnect Transform', c=pm.Callback(ru.connectTransform,disconnect=True))
                        with pm.rowColumnLayout():
                            pm.button(label='toggle Channel History', c=pm.Callback(ru.toggleChannelHistory))
                            pm.button(label='Deform Normal Off', c=pm.Callback(ru.deform_normal_off))
        self._getUIValue()


class HairRig:
    def getJointChainList(self, top):

        selList = pm.selected()
        pm.select(top, hi=True)
        chainList = pm.selected(type='joint')
        pm.select(selList, r=True)

        for chain in chainList:
            if len(chain.getChildren()) > 1:
                pm.displayError('%s has more than one child.' % chain)
                return False

        return chainList

    def lockXformAttrs(self, node, isShown):

        attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

        for attr in attrList:
            node.attr(attr).lock()
            node.attr(attr).setKeyable(isShown)
            node.attr(attr).showInChannelBox(isShown)

    def makeOctaController(self, name):

        pntMatrix = [
            [0, 1, 0], [1, 0, 0], [0, 0, -1],
            [0, 1, 0], [-1, 0, 0], [0, 0, -1],
            [0, -1, 0], [1, 0, 0], [0, 0, 1],
            [-1, 0, 0], [0, -1, 0], [0, 0, 1], [0, 1, 0]]

        crv = pm.curve(d=1, p=pntMatrix, n=name)

        return crv

    def makePinController(self, name):

        rd = 0.5
        lt = 2.0
        hw = math.sqrt(2.0) / 4.0

        pntMatrix = [
            [0, 0, 0],
            [0, lt - rd, 0], [-hw, lt - hw, 0],
            [-rd, lt, 0], [-hw, lt + hw, 0],
            [0, lt + rd, 0], [hw, lt + hw, 0],
            [rd, lt, 0], [hw, lt - hw, 0],
            [0, lt - rd, 0]]

        crv = pm.curve(d=1, p=pntMatrix, n=name)

        return crv

    def makeCircleController(self, name):

        return pm.circle(nr=[1, 0, 0], r=1.0, n=name, ch=False)[0]

    def makeXformController(self, name, axisName, joint):

        circle = pm.circle(n=name, ch=1, o=1, nr=[1, 0, 0], d=1, s=8, r=2.0)[0]
        axis = pm.group(circle, n=axisName)

        circle.attr('overrideEnabled').set(1)
        circle.attr('overrideColor').set((self.colrPLTval))

        const = pm.parentConstraint(joint, axis)
        pm.delete(const)

        return (axis, circle)

    def assignHair(self, crv, hairSystem):

        pm.select(crv, r=1)
        pm.mel.source('DynCreateHairMenu.mel')  # C:/Program Files/Autodesk/Maya(ver)/scripts/startup/

        if hairSystem is None:

            oldAllList = pm.ls(type='hairSystem')
            pm.mel.assignNewHairSystem()
            newAllList = pm.ls(type='hairSystem')

            hairSystem = (list(set(newAllList) - set(oldAllList))[0]).getParent()

        else:
            pm.mel.assignHairSystem(hairSystem)

        follicle = list(set(hairSystem.getShapes()[0].inputs()).intersection(set(crv[0].getShapes()[0].outputs())))[0]
        # follicle = hairSystem.getShapes()[0].attr('inputHair[%s]'%id).inputs()[0]
        hcrv = follicle.attr('outCurve').outputs()[0]

        pm.rename(hcrv, 'outputCurve#')

        return (follicle, hcrv, hairSystem)

    def makeGroupIfNotExist(self, grpName, isHidden):

        if not pm.objExists(grpName):
            grp = pm.group(n=grpName, em=1)
            if isHidden:
                pm.hide(grp)
        else:
            grp = pm.PyNode(grpName)

        return grp

    def makeJointHair(self, sel, hairSystem):

        simDuped = pm.duplicate(sel, n='sim_%s' % sel.nodeName())[0]
        mixDuped = pm.duplicate(sel, n='mix_%s' % sel.nodeName())[0]
        wgtDuped = pm.duplicate(sel, n='weight_%s' % sel.nodeName())[0]

        selJointList = self.getJointChainList(sel)
        simJointList = self.getJointChainList(simDuped)
        mixJointList = self.getJointChainList(mixDuped)
        wgtJointList = self.getJointChainList(wgtDuped)

        if not (selJointList and simJointList and mixJointList):
            return False

        num = len(selJointList)
        pos = sel.getTranslation(space='world')
        ctrlGrp = pm.group(n='%s_ctrls#' % sel.nodeName(), em=1)

        axis, circle = self.makeXformController('%s_top_ctrl#' % sel.nodeName(), '%s_top_ctrl_axis#' % sel.nodeName(),
                                                selJointList[0])
        circle.addAttr('space', at='enum', en='World:Local', k=1, dv=self.dnspRBGval - 1)
        circle.addAttr('ctrl_size', at='double', k=1, dv=1.0)
        circle.attr('ctrl_size') >> circle.attr('scaleX')
        circle.attr('ctrl_size') >> circle.attr('scaleY')
        circle.attr('ctrl_size') >> circle.attr('scaleZ')

        pntMatrix = []

        skclList = list(set(sel.outputs(type='skinCluster')))

        for i in xrange(num):

            if i != 0:
                pm.rename(simJointList[i], 'sim_%s' % simJointList[i].nodeName())
                pm.rename(mixJointList[i], 'mix_%s' % mixJointList[i].nodeName())

            pos = selJointList[i].getTranslation(space='world')
            ofstJoint = pm.rename(pm.insertJoint(mixJointList[i]), mixJointList[i].nodeName().replace('mix', 'offset'))

            pntMatrix.append(pos)

            attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            for attr in attrList:
                simJointList[i].attr(attr) >> mixJointList[i].attr(attr)

            pm.parentConstraint(ofstJoint, selJointList[i], mo=True)

            mixJointList[i].attr('radius').set(0.0)
            ofstJoint.attr('radius').set(0.0)

            if not (i == num - 1 and not self.pctlCBXval):

                ''' # If on, no controllers will be created to the joints which does't have any skinCluster
				for skcl in skclList:
					if selJointList[i] in skcl.getInfluence():
						break
				else:
					continue
				'''

                if self.ctshRBGval == 1:
                    ctrl = self.makeCircleController('%s_ctrl' % selJointList[i].nodeName())
                elif self.ctshRBGval == 2:
                    ctrl = self.makePinController('%s_ctrl' % selJointList[i].nodeName())
                elif self.ctshRBGval == 3:
                    ctrl = self.makeOctaController('%s_ctrl' % selJointList[i].nodeName())

                ctrl.attr('overrideEnabled').set(1)
                ctrl.attr('overrideColor').set((self.colrPLTval))

                ctrlAxis = pm.group(ctrl, n='%s_ctrl_axis' % selJointList[i].nodeName())
                ctrlAxis.attr('rotatePivot').set([0, 0, 0])
                ctrlAxis.attr('scalePivot').set([0, 0, 0])

                circle.attr('ctrl_size') >> ctrl.attr('scaleX')
                circle.attr('ctrl_size') >> ctrl.attr('scaleY')
                circle.attr('ctrl_size') >> ctrl.attr('scaleZ')

                pm.parentConstraint(mixJointList[i], ctrlAxis)
                pm.parentConstraint(ctrl, ofstJoint)
                pm.parent(ctrlAxis, ctrlGrp)

            # Pour weights to simJointList temporarily

            for skcl in skclList:

                if selJointList[i] in skcl.getInfluence():

                    skcl.addInfluence(wgtJointList[i], wt=0)
                    inflList = skcl.getInfluence()

                    isMaintainMax = skcl.attr('maintainMaxInfluences').get()
                    maxInfl = skcl.attr('maxInfluences').get()

                    isFullInfl = False
                    if isMaintainMax and maxInfl == len(inflList):
                        isFullInfl = True
                        skcl.attr('maintainMaxInfluences').set(False)

                    for infl in inflList:
                        if infl == selJointList[i] or infl == wgtJointList[i]:
                            infl.attr('lockInfluenceWeights').set(False)
                        else:
                            infl.attr('lockInfluenceWeights').set(True)

                    for geo in skcl.getGeometry():
                        pm.skinPercent(skcl, geo.verts, nrm=True, tv=[selJointList[i], 0])

                    skcl.removeInfluence(selJointList[i])

                    if isFullInfl:
                        skcl.attr('maintainMaxInfluences').set(True)

        crv1d = pm.curve(d=1, p=pntMatrix)
        crv = pm.fitBspline(crv1d, ch=1, tol=0.001)

        follicle, hcrv, hairSystem = self.assignHair(crv, hairSystem)

        follicleGrp = follicle.getParent()
        curveGrp = hcrv.getParent()

        ikhandle = \
            pm.ikHandle(sj=simJointList[0], ee=simJointList[num - 1], c=hcrv, createCurve=0, solver='ikSplineSolver')[0]

        # Pour back

        for i in xrange(num):

            for skcl in skclList:

                if wgtJointList[i] in skcl.getInfluence():

                    skcl.addInfluence(selJointList[i], wt=0)
                    inflList = skcl.getInfluence()

                    isMaintainMax = skcl.attr('maintainMaxInfluences').get()
                    maxInfl = skcl.attr('maxInfluences').get()

                    isFullInfl = False
                    if isMaintainMax and maxInfl == len(inflList):
                        isFullInfl = True
                        skcl.attr('maintainMaxInfluences').set(False)

                    for infl in inflList:
                        if infl == selJointList[i] or infl == wgtJointList[i]:
                            infl.attr('lockInfluenceWeights').set(False)
                        else:
                            infl.attr('lockInfluenceWeights').set(True)

                    for geo in skcl.getGeometry():
                        pm.skinPercent(skcl, geo.verts, nrm=True, tv=[wgtJointList[i], 0])

                    for infl in inflList:
                        infl.attr('lockInfluenceWeights').set(False)

                    attrList = [wgtJointList[i].attr('message'), wgtJointList[i].attr('bindPose')]
                    for attr in attrList:
                        for dst in pm.connectionInfo(attr, dfs=True):
                            dst = pm.Attribute(dst)
                            if dst.node().type() == 'dagPose':
                                attr // dst

                    if isFullInfl:
                        skcl.attr('maintainMaxInfluences').set(True)

        pm.delete(wgtJointList)

        simGrp = pm.group(simJointList[0], follicle, n='sim_joints#')
        xformer = pm.group(simGrp, mixJointList[0], selJointList[0], n='%s_transformer#' % sel.nodeName())

        hcrv.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
        hcrv.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))
        ctrlGrp.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
        ctrlGrp.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))
        simGrp.attr('scalePivot').set(selJointList[0].getTranslation(space='world'))
        simGrp.attr('rotatePivot').set(selJointList[0].getTranslation(space='world'))

        mixJointList[0].attr('template').set(1)
        hcrv.attr('template').set(1)
        hairSystem.attr('iterations').set(20)
        xformer.attr('scalePivot').set(axis.getTranslation())
        xformer.attr('rotatePivot').set(axis.getTranslation())

        wcnst = pm.parentConstraint(circle, hcrv, mo=True)
        lcnst = pm.parentConstraint(circle, xformer, mo=True)

        rev = pm.shadingNode('reverse', asUtility=True)
        circle.attr('space') >> wcnst.attr('%sW0' % wcnst.getTargetList()[0])
        circle.attr('space') >> rev.attr('inputX')
        rev.attr('outputX') >> lcnst.attr('%sW0' % lcnst.getTargetList()[0])

        pm.delete(follicleGrp, curveGrp, crv1d)
        pm.hide(simGrp)

        crvGrp = self.makeGroupIfNotExist('hairSystemOutputCurves', 0)
        ikGrp = self.makeGroupIfNotExist('hairSystemIKHandles', 1)
        nodesGrp = self.makeGroupIfNotExist('hairSystemNodes', 1)

        pm.parent(hcrv, crvGrp)
        pm.parent(ikhandle, ikGrp)

        if hairSystem.getParent() != nodesGrp:
            pm.parent(hairSystem, nodesGrp)

        if not pm.objExists(self.topName):
            topGrp = pm.group(n=self.topName, em=1)
            pm.parent(nodesGrp, ikGrp, crvGrp, xformer, axis, ctrlGrp, topGrp)
        else:
            pm.parent(xformer, axis, ctrlGrp, self.topName)

        topNode = pm.PyNode(self.topName)

        self.lockXformAttrs(topNode, False)
        self.lockXformAttrs(ctrlGrp, False)
        self.lockXformAttrs(crvGrp, False)
        self.lockXformAttrs(ikGrp, False)
        self.lockXformAttrs(nodesGrp, False)

        pm.select(topNode, r=1)

        self.selList.pop(0)

        windowName = 'hairSystem_Window'

        if pm.window(windowName, ex=1):
            pm.deleteUI(windowName)

        if self.selList:
            self.dialog(self.selList[0])

        pm.displayInfo('"Make Joint Hair" has been successfully done.')

        return True

    def getTopGroupFromHair(self, hs):

        prnt = hs.getParent()
        if prnt:
            grnp = prnt.getParent()
            if grnp:
                top = grnp.getParent()
                if top:
                    return top

        return False

    def getTopJointFromHair(self, hs, isBake):

        jntList = []

        for flc in hs.outputs(type='follicle', sh=True):
            crv = flc.outputs(type='nurbsCurve', sh=True)
            if crv:
                ikh = crv[0].outputs(type='ikHandle', sh=True)
                if ikh:
                    simjnt = ikh[0].inputs(type='joint')
                    if simjnt:
                        if isBake:
                            jnt = simjnt[0].attr('translateX').outputs(type='joint')
                        else:
                            jnt = simjnt[0].attr('radius').outputs(type='joint')
                        if jnt:
                            jntList.append(jnt[0])

        return jntList

    def bake(self):

        opmTxt = self.hsysOPM.getValue()
        isAll = self.alhsCBX.getValue()

        if isAll:
            hsList = pm.ls(type='hairSystem')

        else:
            hsList = pm.ls(opmTxt, r=True)[0].getShapes()

        for hs in hsList:

            if isAll:
                topList = [self.getTopGroupFromHair(hs)]

            else:
                topList = self.getTopJointFromHair(hs, True)

            if not topList:
                pm.displayError('The top node not found.')
                return False

            else:
                dagList = pm.ls(topList, dag=True)
                allMixJntList = pm.ls('*mix*', type='joint', r=True)
                mixJntList = list(set(dagList) & set(allMixJntList))

                if not mixJntList:
                    continue

                ncls = hs.inputs(type='nucleus')[0]

                for mixJnt in mixJntList:
                    simJnt = mixJnt.attr('tx').inputs()
                    if simJnt:
                        simJnt = simJnt[0]
                        if simJnt.nodeType() == 'joint':
                            simJnt.attr('radius') >> mixJnt.attr('radius')  # This is for the unbaking

                if self.tmrgRBG.getSelect() == 1:
                    min = pm.env.getMinTime()
                    max = pm.env.getMaxTime()
                else:
                    min = self.stedIFG.getValue1()
                    max = self.stedIFG.getValue2()

                ncls.attr('enable').set(True)

                pm.bakeResults(mixJntList, sm=True, t=[min, max], ral=False, mr=True,
                               at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

                ncls.attr('enable').set(False)

                pm.displayInfo('Successfully baked.')

    def unbake(self):

        opmTxt = self.hsysOPM.getValue()
        isAll = self.alhsCBX.getValue()

        if isAll:
            hsList = pm.ls(type='hairSystem')

        else:
            hsList = pm.ls(opmTxt, r=True)[0].getShapes()

        for hs in hsList:

            if isAll:
                topList = [self.getTopGroupFromHair(hs)]

            else:
                topList = self.getTopJointFromHair(hs, False)

            if not topList:
                pm.displayError('The top node not found.')
                return False

            else:
                dagList = pm.ls(topList, dag=True)
                allMixJntList = pm.ls('*mix*', type='joint', r=True)
                mixJntList = list(set(dagList) & set(allMixJntList))

                if not mixJntList:
                    continue

                ncls = hs.inputs(type='nucleus')[0]

                for mixJnt in mixJntList:

                    ancvList = mixJnt.inputs(type='animCurve')
                    pm.delete(ancvList)
                    simJnt = mixJnt.attr('radius').inputs()

                    if simJnt:
                        simJnt = simJnt[0]
                        simJnt.attr('radius') // mixJnt.attr('radius')
                        simJnt.attr('tx') >> mixJnt.attr('tx')
                        simJnt.attr('ty') >> mixJnt.attr('ty')
                        simJnt.attr('tz') >> mixJnt.attr('tz')
                        simJnt.attr('rx') >> mixJnt.attr('rx')
                        simJnt.attr('ry') >> mixJnt.attr('ry')
                        simJnt.attr('rz') >> mixJnt.attr('rz')

                ncls.attr('enable').set(True)

                pm.displayInfo('Successfully unbaked.')

    def clickedDialogButton(self, window, sel, isNew):

        if isNew:
            self.makeJointHair(sel, None)
        else:
            self.currentHsysVal = self.exhsOPM.getValue()

            print self.currentHsysVal

            self.makeJointHair(sel, pm.PyNode(self.exhsOPM.getValue()))

            # self.ui()

    def dialog(self, sel):

        hsysList = pm.ls(type='hairSystem')

        windowName = 'hairSystem_Window'

        if pm.window(windowName, ex=1):
            pm.deleteUI(windowName)

        window = pm.window(windowName, title=sel.nodeName(), mb=1)

        with window:

            formLOT = pm.formLayout()
            with formLOT:
                self.exhsOPM = pm.optionMenu(label='')

                for hsys in hsysList:
                    pm.menuItem(l=hsys.getParent().shortName())

                if 'currentHsysVal' in dir(self):
                    self.exhsOPM.setValue(self.currentHsysVal)

                self.wrngTXT = pm.text(l='HairSystem can be shared.\nShould the selected HairSystem be used?',
                                       align='left')
                self.usesBTN = pm.button(l='Use selected', w=90,
                                         c=pm.Callback(self.clickedDialogButton, window, sel, 0))
                self.crtnBTN = pm.button(l='Create new', w=90, c=pm.Callback(self.clickedDialogButton, window, sel, 1))

            formLOT.attachForm(self.exhsOPM, 'top', 5)
            formLOT.attachForm(self.exhsOPM, 'left', 20)
            formLOT.attachForm(self.wrngTXT, 'top', 30)
            formLOT.attachForm(self.wrngTXT, 'left', 20)
            formLOT.attachForm(self.usesBTN, 'top', 70)
            formLOT.attachForm(self.usesBTN, 'left', 20)
            formLOT.attachForm(self.crtnBTN, 'top', 70)
            formLOT.attachForm(self.crtnBTN, 'left', 130)

    def conditionBranch(self):

        self.selList = pm.selected(type='joint')
        self.topName = 'hairSystem'

        if not self.selList:
            pm.displayError('Select joints.')
            return False

        if pm.ls(type='hairSystem'):
            self.dialog(self.selList[0])
        else:
            self.makeJointHair(self.selList[0], None)
            # pm.select('%s*_transformer1'%self.name,r=True)
            # pm.group(name='%s_bonGp'%self.name)
            # pm.select('%s*top_ctrl_axis1'%self.name,r=True)
            # pm.group(name='%s_top_ctrl_axis'%self.name)
            # pm.select('%s*ctrls1'%self.name,r=True)
            # pm.group(name='%s_ctlGp'%self.name)

    def __init__(self, putToLeaf=False, colorOveride=True, dynamicSpace=1, ctlShape=1):
        # self.name = name
        self.pctlCBXval = putToLeaf
        self.colrPLTval = True
        self.dnspRBGval = dynamicSpace
        self.ctshRBGval = ctlShape
        self.conditionBranch()


meta.registerMClassInheritanceMapping()
# meta.registerMClassNodeMapping(nodeTypes='transform')
