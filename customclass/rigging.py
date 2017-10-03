#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""

from ..main import utilities as ul
reload(ul)
import string

class FacialGuide(object):
    def __init__(self, name, guide_mesh=None, suffix='loc', root_suffix='Gp'):
        self._name = name
        self._suffix = suffix
        self._root_suffix = root_suffix
        self.name = '_'.join([name, suffix])
        self.root_name = '_'.join([self.name, root_suffix])
        self.constraint_name = '_'.join([self.root_name,'pointOnPolyConstraint1'])
        self.guide_mesh = ul.get_shape(guide_mesh)
        self._get()

    def __repr__(self):
        return self.name

    def __call__(self,*args, **kwargs):
        self._create(*args, **kwargs)
        return self.node
    
    def set_guide_mesh(self, guide_mesh):
        if pm.objExists(guide_mesh):
            self.guide_mesh = ul.get_shape(guide_mesh)

    def _create(self, pos=[0, 0, 0], parent=None):
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
                self.guide_mesh, self.node, mo=False,
                name=self.constraint_name)
            self.constraint.attr(self.guide_mesh.getParent().name()+'U0').set(closest_uv[0])
            self.constraint.attr(self.guide_mesh.getParent().name()+'V0').set(closest_uv[1])
            pm.select(closest_info['Closest Vertex'])
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
        self._name = name
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
        return self.node

    def name(self):
        return self.name

    def rename(self,new_name):
        self.name = '_'.join([new_name, self._suffix])
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

    def create(shape=None, pos=[0,0,0], parent=None, create_offset=True):
        if not self.node:
            self.node = pm.nt.Transform(name=self.name)
        if pm.objExists(shape):
            parent_shape(shape , self.node)
        if not self.offset and create_offset:
            self.offset = pm.nt.Transform(name='_'.join([self.name, 'offset', 'GP']))
            self.offset.setTranslation(self.node, space='world')
            self.node.setParent(self.offset)
        if not self.root:
            self.root = pm.nt.Transform(name='_'.join([self.name, 'GP']))
            self.root.setTranslation(self.node, space='world')
            if self.offset:
                self.offset.setParent(self.root)
            else:
                self.node.setParent(self.root)
            self.root.setParent(parent)

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
        pass

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
        if self.bone and self.control:
            for atr in self.connect_attrs:
                self.control.attr(atr) >> self.bone.attr(atr)

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

    def get_control(self):
        self.control = FacialControl(self._name)
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
    def bones(cls, name,offset_suffix='offset', root_suffix='Gp', suffix='bon', separator='_', directions=['Left','Right','Center','Root']):
        list_all = pm.ls('*%s*%s*'%(name,suffix), type='transform')
        allbone = []
        for ob in list_all:
            if root_suffix not in ob.name():
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
        return bones
class FacialEyeRig(object):
    pass

class FacialBonRig(object):
    offset_name = 'offset'
    bone_name = 'bon'
    alphabet = list(string.ascii_uppercase)
    def __init__(self):
        self._joints = {
            'eye':{'Left':alphabet[:4],
                   'SubLeft':alphabet[:4]},
            'eyebrow':{'Left':alphabet[:3]},
            'nose':{'Top':"", 'Left':alphabet[0]},
            'cheek':{'Left':alphabet[:3]},
            'jaw':{'Root':"", 'Top':""},
            'lip':{'Center':alphabet[:2], 'Left':alphabet[:3]},
            'teeth':{'Lower':"", 'Upper':""},
            'tongue':{
                'Root':"",
                'Center':([i+'Root' for i in alphabet[:4]]+alphabet[:4]),
                'Left':alphabet[:4]}}
        self._get()
    def _get(self):
        self.joints = {}
        for name,variations in self._joints.items():
            self.joints[name] = {}
            for variation in variations:
                offset_bon = '_'.join([name+variation, self.offset_name, self.bone_name])
                bon_name = '_'.join([name+variation, self.bone_name])
                try:
                    self.joints[name]['offset'] = pm.PyNode(offset_bon)
                    self.joints[name]['joint'] = pm.PyNode(bon_name)
                except:
                    print offset_bon,' or', bon_name, ' is not exist'
                    raise

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
        self.facebs = get_blendshape_target(self.facebs_name)
        if self.facebs:
            self.facebs_def ={}
            self.facebs_def[misc] = []
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
                self.facebs_def[misc].append(bs)
        else:
            print "no blendShape with name" % self.facebs_name
        return self.facebs_def

    def connect_bs_controller(self):
        facepart = self.facepart_name
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
                print '%s.%s >> %s.%s' %(ctl_name,bs_target,self.facebs(),bs_target)
        #print bs_controller
