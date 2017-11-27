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
reload(ru)


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
                pm.match_transform(self.offset, self.bone, pivots=True)
            pm.match_transform(self.control.node, self.bone, pivots=True)
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
            'NSphere': self.NSphere,
            'Rectangle': self.Rectangle
        }
        self._currentType = self._controlType.keys()[0]
        self._uiOption = {
            'group':True,
            'pre':False
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
                Gp = ru.group(control)
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

    #### Control Type
    @__setProperty__
    def Octa(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            step=4,
            sphere=True,
            radius=self.radius,
            length=0)
        print self
        return crv

    @__setProperty__
    def Pin(self, mode={'mirror': False, 'sphere': False}):
        newAxis = self._axis
        if mode['mirror']:
            newAxis = 'm' + self._axis
        else:
            newAxis = self._axis.replace('m', '')
        crv = ru.createPinCircle(
            self.name,
            axis=newAxis,
            sphere=mode['sphere'],
            radius=self.radius,
            step=self.step,
            length=self.length)
        return crv

    @__setProperty__
    def Circle(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=False,
            length=0)
        return crv

    @__setProperty__
    def Cylinder(self, mode={}):
        crv = ru.createPinCircle(
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
        crv = ru.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0)
        return crv

    @__setProperty__
    def Rectangle(self, mode={}):
        crv = ru.create_square(
            self.name,
            length=self.radius,
            width=self.length,
            offset=self.offset)
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

    def createControl(self):
        if pm.selected():
            newCtl = []
            for ob in pm.selected():
                ctl = self._controlType[self._currentType](**self._uiOption)
                newCtl.append(ctl)
                if ob:
                    if ctl.getParent():
                        ru.xformTo(ctl.getParent(), ob)
                    else:
                        ru.xformTo(ctl, ob)
        else:
            newCtl = self._controlType[self._currentType](**self._uiOption)
        return newCtl

    def changeControlShape(self, selectControl, *args):
        temp = self.createControl()
        #temp.setParent(selectControl.getParent())
        ru.xformTo(temp, selectControl)
        pm.delete(selectControl.getShape(), shape=True)
        pm.parent(temp[0].getShape(), selectControl, r=True, s=True)
        pm.delete(temp)
        return selectControl

    #### Ui contain
    @classmethod
    def show(cls):
        cls()._showUI()

    def _getUIValue(self, *args):
        self.name = self._uiElement['ctlName'].getText()
        self.color = self._uiElement['ctlColor'].getRgbValue()
        print self._uiElement['ctlAxis'].getValue()
        self.axis = self._uiElement['ctlAxis'].getValue()
        self.radius = self._uiElement['ctlRadius'].getValue()[0]
        self.length = self._uiElement['ctlLength'].getValue()[0]
        self.step = self._uiElement['ctlRes'].getValue()
        self.offset = self._uiElement['ctlOffset'].getValue()
        self._currentType = self._uiElement['ctlType'].getValue()
        for name, value in zip(self._uiElement['ctlOption'].getLabelArray4(),
                               self._uiElement['ctlOption'].getValueArray4()):
            self._uiOption[name] = value

    def _showUI(self, parent=None):
        self._uiName = 'CreateControlUI'
        self._windowSize = (250, 100)
        if pm.window(self._uiName + 'Window', ex=True):
            pm.deleteUI(self._uiName + 'Window', window=True)
            pm.windowPref(self._uiName + 'Window', remove=True)
        if parent is not None and isinstance(parent, pm.uitypes.Window):
            self._window = parent
        else:
            self._window = pm.window(
                self._uiName + 'Window', title=self._uiName,
                rtf=True, widthHeight=self._windowSize, sizeable=True)
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
                            label='Name:', text=self.name,
                            cc = self._getUIValue)
                        self._uiElement['ctlType'] = pm.optionMenu(label='Type:', cc = self._getUIValue)
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
                            value1=3.0,
                            cc = self._getUIValue)
                        self._uiElement['ctlRadius'] = pm.floatFieldGrp(
                            cl2=('left', 'right'),
                            co2=(0, 0),
                            cw2=(40, 30),
                            numberOfFields=1,
                            label='Radius:',
                            value1=0.5,
                            cc = self._getUIValue)
                        self._uiElement['ctlRes'] = pm.optionMenu(label='Step:', cc = self._getUIValue)
                        with self._uiElement['ctlRes']:
                            for ct in self._resolutions:
                                pm.menuItem(label=ct)
                    with pm.rowColumnLayout():
                        self._uiElement['ctlColor'] = pm.colorSliderGrp(
                            label='Color:',
                            rgb=(0, 0, 1),
                            co3=(0, 0, 0),
                            cw3=(30, 60, 60),
                            cl3=('left', 'center', 'right'),
                            cc = self._getUIValue)
                        self._uiElement['ctlAxis'] = pm.optionMenu(label='Axis:', cc = self._getUIValue)
                        with self._uiElement['ctlAxis']:
                            for ct in self._axisList:
                                pm.menuItem(label=ct)
                    self._uiElement['ctlOffset'] = pm.floatFieldGrp(
                        cl4=('left', 'center', 'center', 'center'),
                        co4=(0, 5, 0, 0),
                        cw4=(45, 50, 50, 50),
                        numberOfFields=3,
                        label='Offset:',
                        cc = self._getUIValue)
                    self._uiElement['ctlOption'] = pm.checkBoxGrp(
                        cl5=('left', 'center', 'center', 'center', 'center'),
                        co5=(0, 5, 0, 0, 0),
                        cw5=(45, 50, 50, 50, 50),
                        numberOfCheckBoxes=4,
                        label='Options:',
                        labelArray4=['group', 'setAxis', 'sphere', 'mirror'],
                        cc = self._getUIValue)
                    pm.button(label='Create', c=pm.Callback(self.createControl))
                    with pm.popupMenu(b=3):
                        pm.menuItem(label='Change Current Select', c=ul.do_function_on()(self.changeControlShape))
                        pm.menuItem(label='Set Color Select', c=ul.do_function_on()(self.setColor))
        self._getUIValue()
